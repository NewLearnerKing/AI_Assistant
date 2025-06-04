import subprocess
import os
import sys
import http.server
import socketserver
import threading
import time
import io
from contextlib import redirect_stdout, redirect_stderr

def run_python_script(script_path: str, timeout: int = 30) -> dict:
    """
    Executes a Python script and captures its output and errors.
    Returns a dict with 'output', 'error', and 'success' keys.
    """
    try:
        # Redirect stdout and stderr to capture output
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            process = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
        stdout_output = stdout.getvalue() + process.stdout
        stderr_output = stderr.getvalue() + process.stderr
        success = process.returncode == 0
        result = {
            "output": stdout_output.strip(),
            "error": stderr_output.strip() if not success else "",
            "success": success
        }
        print(f"[CodeExecutor] Ran Python script: {script_path}\nResult: {result}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[CodeExecutor] Ran Python script: {script_path}\nResult: {result}\n")
        return result
    except subprocess.TimeoutExpired:
        result = {"output": "", "error": "Script execution timed out after 30 seconds.", "success": False}
        print(f"[CodeExecutor] Timeout: {script_path}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[CodeExecutor] Timeout: {script_path}\n")
        return result
    except Exception as e:
        result = {"output": "", "error": f"Error running script: {str(e)}", "success": False}
        print(f"[CodeExecutor] Error: {str(e)}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[CodeExecutor] Error: {str(e)}\n")
        return result

def test_python_script(script_path: str, test_cases: list) -> dict:
    """
    Tests a Python script with provided test cases.
    Test cases should be a list of dicts: [{"input": ..., "expected": ...}]
    Returns a dict with 'results', 'passed', and 'feedback' keys.
    """
    try:
        # For simplicity, we'll modify the script to accept input and compare output
        # In a real scenario, we'd use unit tests or a testing framework
        results = []
        passed = True
        feedback = []

        # Read the script content to check for a main function
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # For this example, we'll assume the script has a function we can call
        # In a more advanced setup, we can use `unittest` or `pytest`
        for test_case in test_cases:
            test_input = test_case.get("input")
            expected = test_case.get("expected")

            # Execute the script with input (simplified for demonstration)
            # In practice, we'd modify the script to accept input or use a testing framework
            result = run_python_script(script_path)
            actual_output = result["output"]

            test_passed = str(actual_output) == str(expected)
            results.append({
                "input": test_input,
                "expected": expected,
                "actual": actual_output,
                "passed": test_passed
            })
            if not test_passed:
                passed = False
                feedback.append(f"Test failed for input {test_input}: expected {expected}, got {actual_output}")

        test_result = {
            "results": results,
            "passed": passed,
            "feedback": "\n".join(feedback) if feedback else "All tests passed."
        }
        print(f"[CodeExecutor] Test results for {script_path}: {test_result}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[CodeExecutor] Test results for {script_path}: {test_result}\n")
        return test_result
    except Exception as e:
        result = {"results": [], "passed": False, "feedback": f"Error testing script: {str(e)}"}
        print(f"[CodeExecutor] Test error: {str(e)}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[CodeExecutor] Test error: {str(e)}\n")
        return result

def serve_web_app(project_dir: str, port: int = 8000) -> dict:
    """
    Serves a web app from the project directory and validates its structure.
    Returns a dict with 'url', 'success', and 'validation' keys.
    """
    try:
        # Change to project directory
        original_dir = os.getcwd()
        os.chdir(project_dir)

        # Check for index.html
        index_file = "index.html"
        if not os.path.exists(index_file):
            os.chdir(original_dir)
            return {"url": "", "success": False, "validation": "index.html not found."}

        # Validate HTML structure
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
        validation = []
        if "<html>" not in content or "</html>" not in content:
            validation.append("Missing <html> tags.")
        if "<head>" not in content or "</head>" not in content:
            validation.append("Missing <head> tags.")
        if "<body>" not in content or "</body>" not in content:
            validation.append("Missing <body> tags.")

        # Start a simple HTTP server
        Handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", port), Handler)
        
        def serve():
            print(f"[CodeExecutor] Serving web app at http://localhost:{port}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[CodeExecutor] Serving web app at http://localhost:{port}\n")
            httpd.serve_forever()

        server_thread = threading.Thread(target=serve, daemon=True)
        server_thread.start()

        # Wait briefly to ensure the server starts
        time.sleep(1)

        os.chdir(original_dir)
        return {
            "url": f"http://localhost:{port}",
            "success": True,
            "validation": "\n".join(validation) if validation else "Web app structure looks valid."
        }
    except Exception as e:
        os.chdir(original_dir)
        result = {"url": "", "success": False, "validation": f"Error serving web app: {str(e)}"}
        print(f"[CodeExecutor] Serve error: {str(e)}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[CodeExecutor] Serve error: {str(e)}\n")
        return result

def stop_web_server(httpd):
    """
    Stops the web server.
    """
    if httpd:
        httpd.shutdown()
        httpd.server_close()
        print("[CodeExecutor] Web server stopped.")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write("[CodeExecutor] Web server stopped.\n")