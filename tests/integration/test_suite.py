import sys
print("STARTING TEST SUITE (very top of file)")
import os
import requests
import time as pytime
import subprocess
from pathlib import Path
import psutil
from datetime import datetime
import yaml
from bs4 import BeautifulSoup
import threading
import queue
import socket
import signal
import textwrap
import time

try:
    print("All imports completed")
except Exception as e:
    print(f"Early import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# --- Constants ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
LOGS_DIR = PROJECT_ROOT / 'tests' / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
TRACEABILITY_PATH = PROJECT_ROOT / 'tests' / 'traceability.yaml'
BACKEND_PORT = 5001
FRONTEND_PORT = 3001
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"

# --- Logging ---
class TeeLogger:
    def __init__(self, log_path):
        self.log_file = open(log_path, 'w', encoding='utf-8')
    def log(self, msg, to_console=False):
        if to_console:
            print(msg)
        self.log_file.write(msg + '\n')
        self.log_file.flush()
    def close(self):
        self.log_file.close()

# --- Utility Functions ---
def get_log_file_path():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return LOGS_DIR / f"integration_{timestamp}.log"

def cleanup_old_logs(max_logs=10):
    logs = sorted(LOGS_DIR.glob('*.log'), key=os.path.getmtime, reverse=True)
    for log in logs[max_logs:]:
        try:
            log.unlink()
        except Exception:
            pass

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0

def kill_and_wait_for_ports(ports, logger):
    """For each port: check for process, kill if found, wait 3s. No loop, no repeated check."""
    for port in ports:
        logger.log(f"[DIAG] Checking for any process using port {port} before kill attempt...")
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.connections(kind='inet'):
                    if conn.laddr.port == port:
                        logger.log(f"Killing process {proc.pid} ({proc.name()}) using port {port}.")
                        proc.kill()
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        logger.log(f"[DIAG] Waiting 3 seconds for port {port} to be released...")
        time.sleep(3)

# --- Test Runners ---
def start_backend(logger, env):
    logger.log(f"Starting backend on port {BACKEND_PORT}...", to_console=True)
    env_backend = env.copy()
    if "PORT" in env_backend:
        del env_backend["PORT"]
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "backend.app"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        env=env_backend
    )
    backend_ready = False
    backend_start_time = time.time()
    backend_health_url = f"http://127.0.0.1:{BACKEND_PORT}/api/data"
    while time.time() - backend_start_time < 30:
        if backend_proc.poll() is not None:
            logger.log("Backend failed to start (process exited).", to_console=True)
            try:
                backend_output = backend_proc.communicate(timeout=5)[0]
                logger.log("--- Backend process output ---")
                logger.log(backend_output)
                logger.log("--- End of backend process output ---")
            except Exception as e:
                logger.log(f"Error reading backend process output: {e}")
            if backend_proc:
                backend_proc.kill()
            sys.exit(1)
        try:
            resp = requests.get(backend_health_url, timeout=1)
            if resp.status_code == 200:
                backend_ready = True
                break
        except Exception:
            pass
        pytime.sleep(0.5)
    if not backend_ready:
        logger.log("Backend did not become ready in 30 seconds.", to_console=True)
        try:
            backend_output = backend_proc.communicate(timeout=5)[0]
            logger.log("--- Backend process output ---")
            logger.log(backend_output)
            logger.log("--- End of backend process output ---")
        except Exception as e:
            logger.log(f"Error reading backend process output: {e}")
        if backend_proc:
            backend_proc.kill()
        sys.exit(1)
    logger.log("Backend started and is healthy.", to_console=True)
    return backend_proc

def start_frontend(logger, env, is_windows):
    frontend_dir = PROJECT_ROOT / "frontend"
    frontend_start_time = time.time()
    logger.log(f"[TIMER] Starting frontend process at {frontend_start_time:.2f}", to_console=True)
    if is_windows:
        frontend_cmd = ["cmd", "/c", "npm.cmd", "run", "dev", "--", "--port", str(FRONTEND_PORT)]
    else:
        frontend_cmd = ["npm", "run", "dev", "--", "--port", str(FRONTEND_PORT)]
    logger.log(f"[DEBUG] Frontend start command: {frontend_cmd}")
    logger.log(f"[DEBUG] Frontend env PORT: {env.get('PORT')}")
    logger.log(f"[DEBUG] Frontend env PATH: {env.get('PATH')}")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', shell=False, env=env)
    # Non-blocking output reading setup
    def enqueue_output(out, q):
        for line in iter(out.readline, ''):
            q.put(line)
        out.close()
    q_out = queue.Queue()
    t_out = threading.Thread(target=enqueue_output, args=(frontend_proc.stdout, q_out))
    t_out.daemon = True
    t_out.start()
    logger.log("Waiting for frontend to be ready...", to_console=True)
    frontend_ready = False
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        time.sleep(5)
        try:
            resp = requests.get(FRONTEND_URL, timeout=5)
            logger.log(f"[frontend-health-check] Attempt {attempt}: HTTP {resp.status_code}")
            if resp.status_code == 200:
                frontend_ready = True
                logger.log("Frontend health check passed: HTTP 200 OK.", to_console=True)
                break
            else:
                logger.log(f"Frontend health check failed: HTTP {resp.status_code}.", to_console=True)
        except Exception as e:
            logger.log(f"Frontend health check failed on attempt {attempt}: {e}", to_console=True)
    if not frontend_ready:
        logger.log("Frontend did not become ready after 3 health checks. Aborting.", to_console=True)
        frontend_proc.kill()
        sys.exit(1)
    logger.log("Frontend started.", to_console=True)
    return frontend_proc

# --- Main Test Logic ---
def run_all_tests(logger):
    print("[DEBUG] Entered run_all_tests")
    # Load traceability matrix
    with open(TRACEABILITY_PATH, 'r', encoding='utf-8') as f:
        traceability = yaml.safe_load(f)
    required_ids = {item['id'] for item in traceability}
    covered_ids = set()

    # Port cleanup
    logger.log(f"Ensuring ports 3001 and 5001 are free...")
    kill_and_wait_for_ports([3001, 5001], logger)
    logger.log("Ports 3001 and 5001 are now free.")

    # Prepare env
    frontend_dir = PROJECT_ROOT / "frontend"
    env = os.environ.copy()
    env["PORT"] = str(FRONTEND_PORT)
    env["LOL_PICKBAN_FRONTEND_PORT"] = str(FRONTEND_PORT)
    is_windows = sys.platform == "win32"

    # Log current working directory and package.json contents
    logger.log(f"[DEBUG] Current working directory: {os.getcwd()}")
    try:
        with open(frontend_dir / 'package.json', 'r', encoding='utf-8') as f:
            logger.log(f"[DEBUG] frontend/package.json contents:\n{f.read()}")
    except Exception as e:
        logger.log(f"[DEBUG] Error reading package.json: {e}")

    # Start backend and frontend
    backend_proc = start_backend(logger, env)
    frontend_proc = start_frontend(logger, env, is_windows)

    # --- ACTUAL TESTS ---
    all_passed = True

    # Test GET /api/data
    logger.log("Testing backend /api/data endpoint...")
    try:
        resp = requests.get(f"{BACKEND_URL}/api/data", timeout=5)
        if resp.status_code == 200 and resp.json().get("message") == "Hello from Flask!":
            logger.log("Backend /api/data test PASSED.")
        else:
            logger.log(f"Backend /api/data test FAILED. Status: {resp.status_code}, Body: {resp.text}")
            all_passed = False
    except Exception as e:
        logger.log(f"Backend /api/data test EXCEPTION: {e}")
        all_passed = False

    # Test GET /api/champions
    logger.log("Testing backend /api/champions endpoint...")
    try:
        resp = requests.get(f"{BACKEND_URL}/api/champions", timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("success") and isinstance(data.get("champions"), list) and len(data["champions"]) > 0:
            logger.log(f"Backend /api/champions test PASSED. Count: {data['count']}")
        else:
            logger.log(f"Backend /api/champions test FAILED. Status: {resp.status_code}, Body: {resp.text}")
            all_passed = False
    except Exception as e:
        logger.log(f"Backend /api/champions test EXCEPTION: {e}")
        all_passed = False

    # Test frontend-backend integration: fetch /api/champions and render
    logger.log("Testing frontend-backend integration: /api/champions rendering...")
    try:
        html = requests.get(FRONTEND_URL, timeout=10).text
        soup = BeautifulSoup(html, 'html.parser')
        # Try to find at least one champion name in the HTML
        resp = requests.get(f"{BACKEND_URL}/api/champions", timeout=10)
        data = resp.json()
        champion_names = [c['name'] for c in data.get('champions', []) if isinstance(c, dict) and 'name' in c]
        found = False
        for name in champion_names:
            if soup.body and soup.body.find(string=name):
                found = True
                break
        if found:
            logger.log("Frontend-backend integration test PASSED: At least one champion name rendered.")
        else:
            logger.log("Frontend-backend integration test FAILED: No champion names found in frontend HTML.")
            all_passed = False
    except Exception as e:
        logger.log(f"Frontend-backend integration test EXCEPTION: {e}")
        all_passed = False

    cleanup_old_logs(10)
    print("[DEBUG] run_all_tests complete")
    return all_passed, backend_proc, frontend_proc

# --- Main Entrypoint ---
def main():
    try:
        log_path = get_log_file_path()
        print(f"[INFO] Integration log file: {log_path}")
        logger = TeeLogger(log_path)
        print("[DEBUG] Logger created")
    except Exception as e:
        print(f"[FATAL] Could not create logger or log file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    try:
        # Add a hard timeout for the whole test suite
        import threading
        import time
        timeout_seconds = 60  # 1 minute
        watchdog_proc = None
        if sys.platform == 'win32':
            import tempfile
            watchdog_code = textwrap.dedent(f'''
import os, sys, time, signal
parent_pid = int(sys.argv[1])
timeout = int(sys.argv[2])
log_path = sys.argv[3]
time.sleep(timeout)
try:
    with open(log_path, 'a') as f:
        f.write("""[watchdog] ERROR: Test suite timed out. Killing all child processes and exiting.\n""")
except Exception:
    pass
try:
    if os.name == 'nt':
        import psutil
        parent = psutil.Process(parent_pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    else:
        os.kill(parent_pid, signal.SIGKILL)
except Exception:
    pass
sys.exit(2)
''')
            with tempfile.NamedTemporaryFile('w', delete=False, suffix='.py') as f:
                f.write(watchdog_code)
                watchdog_path = f.name
            log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'watchdog_timeout.log')
            watchdog_proc = subprocess.Popen([
                sys.executable, watchdog_path, str(os.getpid()), str(timeout_seconds), log_path
            ])
        else:
            import signal
            def sigalrm_handler(signum, frame):
                print("[watchdog] ERROR: Test suite timed out. Killing all child processes and exiting.")
                sys.exit(2)
            signal.signal(signal.SIGALRM, sigalrm_handler)
            signal.alarm(timeout_seconds)
        print("[DEBUG] About to run all tests")
        all_passed, backend_proc, frontend_proc = run_all_tests(logger)
        print("[DEBUG] run_all_tests returned")
        if all_passed:
            logger.log("All tests passed. Servers left running for manual inspection.")
            # auto_commit_and_push(logger)  # Uncomment if you want auto-commit
        else:
            logger.log("Some tests failed. Servers left running for debugging.")
    finally:
        logger.log("[LOG COMPLETE]")
        logger.close()
        if sys.platform == 'win32' and 'watchdog_proc' in locals() and watchdog_proc:
            watchdog_proc.terminate()
        elif sys.platform != 'win32':
            import signal
            signal.alarm(0)

if __name__ == "__main__":
    main() 