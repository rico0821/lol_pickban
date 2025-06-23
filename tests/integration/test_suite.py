import requests
import time
import subprocess
import sys
import os
from pathlib import Path
import psutil
from datetime import datetime
import yaml

# Set project root to the parent directory of 'tests'
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / 'tests' / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TRACEABILITY_PATH = PROJECT_ROOT / 'tests' / 'traceability.yaml'

# Always use these ports for integration tests
BACKEND_PORT = 5001
FRONTEND_PORT = 3001
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

def kill_process_on_port(port):
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} ({proc.name()}) using port {port}.")
                    proc.kill()
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def cleanup_old_logs(max_logs=10):
    logs = sorted(LOGS_DIR.glob('*.log'), key=os.path.getmtime, reverse=True)
    for log in logs[max_logs:]:
        try:
            log.unlink()
        except Exception:
            pass

def get_log_file_path():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return LOGS_DIR / f"integration_{timestamp}.log"

class TeeLogger:
    def __init__(self, log_path):
        self.log_file = open(log_path, 'w', encoding='utf-8')
    def log(self, msg):
        print(msg)
        self.log_file.write(msg + '\n')
        self.log_file.flush()
    def close(self):
        self.log_file.close()

def run_all_tests(logger):
    # Load traceability matrix
    with open(TRACEABILITY_PATH, 'r', encoding='utf-8') as f:
        traceability = yaml.safe_load(f)
    required_ids = {item['id'] for item in traceability}
    covered_ids = set()

    # Kill any process using the test ports
    logger.log(f"Ensuring ports {BACKEND_PORT} and {FRONTEND_PORT} are free...")
    kill_process_on_port(BACKEND_PORT)
    kill_process_on_port(FRONTEND_PORT)
    logger.log("Ports are now free.")

    # Start backend
    logger.log(f"Starting backend on port {BACKEND_PORT}...")
    env = os.environ.copy()
    env["LOL_PICKBAN_PORT"] = str(BACKEND_PORT)
    backend_proc = subprocess.Popen([
        sys.executable, "-m", "backend.app"
    ], cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', env=env)
    time.sleep(5)
    if backend_proc.poll() is not None:
        logger.log("Backend failed to start.")
        logger.log(backend_proc.communicate()[0])
        return False, backend_proc, None
    logger.log("Backend started.")

    # Start frontend
    logger.log(f"Starting frontend on port {FRONTEND_PORT}...")
    frontend_dir = PROJECT_ROOT / "frontend"
    env["PORT"] = str(FRONTEND_PORT)
    env["LOL_PICKBAN_FRONTEND_PORT"] = str(FRONTEND_PORT)
    is_windows = sys.platform == "win32"
    frontend_proc = subprocess.Popen([
        "npm.cmd" if is_windows else "npm", "start"
    ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', shell=is_windows, env=env)
    # Wait for frontend
    logger.log("Waiting for frontend to be ready...")
    max_wait = 90
    start = time.time()
    frontend_ready = False
    while time.time() - start < max_wait:
        try:
            resp = requests.get(FRONTEND_URL, timeout=2)
            if resp.status_code == 200:
                frontend_ready = True
                break
        except Exception:
            time.sleep(2)
        if frontend_proc.poll() is not None:
            logger.log("Frontend process terminated early.")
            logger.log(frontend_proc.communicate()[0])
            return False, backend_proc, frontend_proc
    if not frontend_ready:
        logger.log("Frontend did not start in time.")
        return False, backend_proc, frontend_proc
    logger.log("Frontend started.")

    # Run tests
    results = {}
    try:
        # Backend health
        logger.log("Testing backend health...")
        resp = requests.get(f'{BACKEND_URL}/api/data', timeout=10)
        results['backend_api_health'] = resp.status_code == 200 and resp.json().get('message') == 'Hello from Flask!'
        logger.log(f"backend_api_health: {results['backend_api_health']}")
        covered_ids.add('backend-health')
        # Champions
        logger.log("Testing /api/champions...")
        resp = requests.get(f'{BACKEND_URL}/api/champions', timeout=20)
        results['get_champions_api'] = resp.status_code == 200 and 'champions' in resp.json()
        logger.log(f"get_champions_api: {results['get_champions_api']}")
        covered_ids.add('get-champions')
        # Frontend
        logger.log("Testing frontend accessibility...")
        resp = requests.get(FRONTEND_URL, timeout=10)
        results['frontend_accessibility'] = resp.status_code == 200
        logger.log(f"frontend_accessibility: {results['frontend_accessibility']}")
        covered_ids.add('frontend-access')
    except Exception as e:
        logger.log(f"Test error: {e}")
    # Print summary
    logger.log("\n--- Test Summary ---")
    for k, v in results.items():
        logger.log(f"{k}: {'PASS' if v else 'FAIL'}")
    logger.log("---------------------\n")
    # Meta-check: ensure all required ids are covered
    missing = required_ids - covered_ids
    if missing:
        logger.log(f"FAIL: The following required features/endpoints were NOT tested: {sorted(missing)}")
        all_passed = False
    else:
        logger.log("All required features/endpoints were tested.")
        all_passed = all(results.values())
    cleanup_old_logs(10)
    return all_passed, backend_proc, frontend_proc

def auto_commit_and_push(logger):
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT_ROOT, check=True)
        commit_result = subprocess.run([
            "git", "commit", "-m", "chore: auto-commit after successful integration test suite"
        ], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if commit_result.returncode == 0:
            logger.log("Committed changes after successful tests.")
        else:
            logger.log("No changes to commit.")
        push_result = subprocess.run(["git", "push"], cwd=PROJECT_ROOT, capture_output=True, text=True)
        if push_result.returncode == 0:
            logger.log("Pushed changes to remote.")
        else:
            logger.log(f"Push failed: {push_result.stderr}")
    except Exception as e:
        logger.log(f"[WARN] Auto-commit/push failed: {e}")

def main():
    log_path = get_log_file_path()
    logger = TeeLogger(log_path)
    try:
        all_passed, backend_proc, frontend_proc = run_all_tests(logger)
        if all_passed:
            logger.log("All tests passed. Servers left running for manual inspection.")
            auto_commit_and_push(logger)
        else:
            logger.log("Some tests failed. Servers left running for debugging.")
    finally:
        logger.close()

if __name__ == "__main__":
    main() 