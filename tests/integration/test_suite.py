import requests
import time
import subprocess
import sys
import os
from pathlib import Path

# Set project root to the parent directory of 'tests'
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

class TestSuite:
    """A simple, initial test suite for the backend."""
    
    def __init__(self):
        self.backend_process = None
        self.test_results = {}

    def start_backend_server(self) -> bool:
        """Start the backend server for testing."""
        print("Starting Backend Server...")
        # We run as a module to ensure correct package resolution
        backend_module = "backend.app"
            
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, "-m", backend_module],
                cwd=PROJECT_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            time.sleep(5) # Give the server a moment to start
            
            if self.backend_process.poll() is not None:
                # Process terminated, which means it failed to start
                stdout, stderr = self.backend_process.communicate()
                print("Backend server failed to start. Logs:")
                if stdout: print(f"--- STDOUT ---\n{stdout}")
                if stderr: print(f"--- STDERR ---\n{stderr}")
                return False
            
            print("Backend server started successfully.")
            return True
                
        except Exception as e:
            print(f"An error occurred while starting the backend server: {e}")
            return False

    def cleanup_servers(self):
        """Stop all running servers."""
        if self.backend_process:
            print("Stopping backend server...")
            self.backend_process.terminate()
            self.backend_process.wait()
            print("Backend server stopped.")
    
    def test_backend_api_health(self) -> bool:
        """Test the backend's /api/data health endpoint."""
        print("\nTesting Backend API Health...")
        
        try:
            response = requests.get('http://127.0.0.1:5000/api/data', timeout=10)
            if response.status_code == 200 and response.json()['message'] == 'Hello from Flask!':
                print("✅ Backend API health check passed.")
                return True
            else:
                print(f"❌ Backend API health check failed. Status: {response.status_code}, Body: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Backend API not accessible: {e}")
            return False

    def test_get_champions_api(self) -> bool:
        """Tests the /api/champions endpoint."""
        print("\nTesting /api/champions endpoint...")
        try:
            response = requests.get('http://localhost:5000/api/champions', timeout=20) # Increased timeout for external API call
            if response.status_code != 200:
                print(f"❌ Champions endpoint failed with status {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            if 'data' not in data or not isinstance(data['data'], dict):
                print("❌ Champions endpoint response is missing 'data' dictionary.")
                return False
            
            if 'Aatrox' not in data['data']:
                print("❌ Champions endpoint response does not contain expected champion data (Aatrox).")
                return False

            print("✅ /api/champions endpoint test passed.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ /api/champions endpoint not accessible: {e}")
            return False

    def run_playwright_tests(self) -> bool:
        """Runs the Playwright E2E tests."""
        print("\nRunning Playwright E2E tests...")
        frontend_dir = PROJECT_ROOT / "frontend"
        try:
            is_windows = sys.platform == "win32"
            process = subprocess.run(
                ["npx.cmd" if is_windows else "npx", "playwright", "test"],
                cwd=frontend_dir,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120 # Give Playwright plenty of time to run
            )

            if process.returncode == 0:
                print("✅ Playwright tests passed.")
                print(process.stdout)
                return True
            else:
                print("❌ Playwright tests failed.")
                print(process.stdout)
                print(process.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("❌ Playwright tests timed out.")
            return False
        except Exception as e:
            print(f"❌ An error occurred while running Playwright tests: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Runs all tests and returns the overall result."""
        # Start backend server
        backend_ready = self.start_backend_server()

        # Run backend tests
        if backend_ready:
            self.test_results['backend_api_health'] = self.test_backend_api_health()
            self.test_results['get_champions_api'] = self.test_get_champions_api()
        else:
            self.test_results['backend_api_health'] = False
            self.test_results['get_champions_api'] = False
        
        # Run Playwright E2E tests. It will manage its own frontend server
        # but requires the backend to be running.
        if backend_ready:
            self.test_results['playwright_e2e_tests'] = self.run_playwright_tests()
        else:
            self.test_results['playwright_e2e_tests'] = False

        # Check results
        all_tests_passed = all(self.test_results.values())
        
        return all_tests_passed

def main():
    """Main execution block."""
    suite = TestSuite()
    all_passed = False
    try:
        all_passed = suite.run_all_tests()
    except Exception as e:
        print(f"\nAn uncaught exception occurred: {e}")
    finally:
        suite.cleanup_servers()

    print("\n--- Test Summary ---")
    for test, result in suite.test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test}: {status}")
    print("--------------------\n")

    if not all_passed:
        print("Some tests failed.")
        sys.exit(1)
    else:
        print("All tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main() 