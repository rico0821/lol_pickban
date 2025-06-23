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
        self.frontend_process = None
        self.test_results = {}

    def start_backend_server(self) -> bool:
        """Start the backend server for testing."""
        print("Starting Backend Server...")
        backend_app_path = PROJECT_ROOT / "backend" / "app.py"
        if not backend_app_path.exists():
            print(f"Backend app not found at: {backend_app_path}")
            return False
            
        try:
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_app_path)],
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

    def start_frontend_server(self) -> bool:
        """Start the frontend server for testing."""
        print("\nStarting Frontend Server...")
        frontend_dir = PROJECT_ROOT / "frontend"
        if not frontend_dir.exists():
            print(f"❌ Frontend directory not found: {frontend_dir}")
            return False

        try:
            # Use shell=True for npm.cmd compatibility on Windows
            is_windows = sys.platform == "win32"
            self.frontend_process = subprocess.Popen(
                ["npm.cmd" if is_windows else "npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                shell=is_windows
            )
            
            # Poll the server to see if it's ready
            print("...waiting for frontend server to be ready...")
            max_wait_time = 60
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                try:
                    response = requests.get("http://localhost:3000", timeout=2)
                    if response.status_code == 200:
                        print("Frontend server is up and running.")
                        return True
                except requests.ConnectionError:
                    time.sleep(2) # Server not ready yet
                
                if self.frontend_process.poll() is not None:
                    # Process terminated prematurely
                    stdout, stderr = self.frontend_process.communicate()
                    print("❌ Frontend server process terminated prematurely. Logs:")
                    if stdout: print(f"--- STDOUT ---\n{stdout}")
                    if stderr: print(f"--- STDERR ---\n{stderr}")
                    return False

            print(f"❌ Frontend server failed to start within {max_wait_time} seconds.")
            return False
                
        except Exception as e:
            print(f"❌ An error occurred while starting the frontend server: {e}")
            return False

    def cleanup_servers(self):
        """Stop all running servers."""
        if self.backend_process:
            print("Stopping backend server...")
            self.backend_process.terminate()
            self.backend_process.wait()
            print("Backend server stopped.")
        
        if self.frontend_process:
            print("Stopping frontend server...")
            self.frontend_process.terminate()
            self.frontend_process.wait()
            print("Frontend server stopped.")
    
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

    def test_frontend_accessibility(self) -> bool:
        """Test frontend accessibility."""
        print("\nTesting Frontend Accessibility...")
        try:
            response = requests.get('http://localhost:3000', timeout=10)
            if response.status_code == 200:
                print("✅ Frontend accessibility check passed.")
                return True
            else:
                print(f"❌ Frontend accessibility check failed. Status: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Frontend not accessible: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Runs all tests and returns the overall result."""
        # Start servers first
        backend_ready = self.start_backend_server()
        frontend_ready = self.start_frontend_server()

        # Run backend tests
        if backend_ready:
            self.test_results['backend_api_health'] = self.test_backend_api_health()
        else:
            self.test_results['backend_api_health'] = False
        
        # Run frontend tests
        if frontend_ready:
            self.test_results['frontend_accessibility'] = self.test_frontend_accessibility()
        else:
            self.test_results['frontend_accessibility'] = False

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