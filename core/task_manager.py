from core.llm import ask_llm
from modules.file_control import create_file, edit_file, read_file, batch_create_files, search_files, delete_file, copy_file
from modules.system_control import execute_command, get_system_info, automate_process
from modules.code_executor import run_python_script, test_python_script, serve_web_app
from modules.app_launcher import open_app
import os
import subprocess
import json
import time
from duckduckgo_search import DDGS

def route_command(command: str) -> str:
    response = ask_llm(command)
    
    if isinstance(response, dict) and "error" in response:
        return f"Error: {response['error']}"

    if isinstance(response, dict) and "task" in response:
        task = response["task"]
        if task == "create_file":
            return create_file(response.get("filename"), response.get("content", ""))
        elif task == "edit_file":
            return edit_file(response.get("filename"), response.get("content"), response.get("append", False))
        elif task == "read_file":
            return read_file(response.get("filename"))
        elif task == "batch_create_files":
            return batch_create_files(response.get("files", []))
        elif task == "search_files":
            return "\n".join(search_files(response.get("pattern", "*"), response.get("directory", ".")))
        elif task == "delete_file":
            return delete_file(response.get("filename"))
        elif task == "copy_file":
            return copy_file(response.get("src"), response.get("dst"))
        elif task == "execute_command":
            return execute_command(response.get("command"))
        elif task == "get_system_info":
            return get_system_info(response.get("info_type"))
        elif task == "automate_process":
            return automate_process(response.get("process"))
        elif task == "open_app":
            return open_app(command)
        elif task == "code_project":
            return handle_code_project(response)
        elif task == "web_search":
            query = response.get("query")
            if not query:
                return "Please provide a search query."
            try:
                with DDGS() as ddgs:
                    results = [r for r in ddgs.text(query, max_results=3)]
                if not results:
                    return "No results found."
                summary = "\n".join([f"- {r['title']}: {r['body']}" for r in results])
                print(f"[TaskManager] Web search results for '{query}':\n{summary}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[TaskManager] Web search results for '{query}':\n{summary}\n")
                return f"Search results for '{query}':\n{summary}"
            except Exception as e:
                print(f"[TaskManager] Web search error: {str(e)}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[TaskManager] Web search error: {str(e)}\n")
                return f"Error searching the web: {str(e)}"
        else:
            return "Unknown task."
    return response.get("reply", "I couldn't process that command.")


def handle_code_project(response: dict) -> str:
    try:
        language = response.get("language", "python")
        steps = response.get("steps", [])
        files = response.get("files", [])
        run = response.get("run", False)
        test = response.get("test", False)

        # Create a project directory
        project_name = "project_" + str(int(time.time()))
        project_dir = os.path.join("projects", project_name)
        os.makedirs(project_dir, exist_ok=True)
        print(f"[TaskManager] Created project directory: {project_dir}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[TaskManager] Created project directory: {project_dir}\n")

        # Initial file creation
        initial_files = {}
        for file in files:
            filename = file.get("filename")
            content = file.get("content", "")
            full_path = os.path.join(project_dir, os.path.normpath(filename))  # Normalize path
            create_file(full_path, content)
            initial_files[filename] = full_path

        result = f"Project '{project_name}' created.\n"

        # Iterate over steps
        for i, step in enumerate(steps, 1):
            step_desc = step["step"] if isinstance(step, dict) else step
            step_output = step.get("output", "Generate relevant code") if isinstance(step, dict) else "Generate relevant code"
            print(f"[TaskManager] Processing step {i}: {step_desc}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[TaskManager] Processing step {i}: {step_desc}\n")

            existing_files = search_files("*", project_dir)
            file_contents = {os.path.basename(f): read_file(f) for f in existing_files}

            step_prompt = f"Complete step {i}: {step_desc}\nExpected output: {step_output}\nExisting files: {json.dumps(file_contents)}\nGenerate the required content and return it in a code_project task. Do not prompt the user."
            step_response = ask_llm(step_prompt, iteration=i, previous_response=json.dumps(file_contents))

            if "error" in step_response:
                result += f"\nStep {i} failed: {step_response['error']}"
                continue

            if "task" in step_response and step_response["task"] == "code_project":
                new_files = step_response.get("files", [])
                for file in new_files:
                    filename = file.get("filename")
                    content = file.get("content", "")
                    full_path = os.path.join(project_dir, os.path.normpath(filename))
                    # Append or replace based on step logic
                    if os.path.exists(full_path):
                        existing_content = read_file(full_path)
                        if content and not content.startswith(existing_content):  # Avoid overwriting unrelated content
                            content = existing_content + "\n" + content
                    create_file(full_path, content)
                result += f"\nStep {i} completed: Updated {len(new_files)} files."
            else:
                result += f"\nStep {i} response: {step_response.get('reply', 'No reply.')}"

        # Run and test logic remains the same
        if run:
            if language == "python":
                main_file = next((f for f in search_files("*.py", project_dir)), None)
                if main_file:
                    full_path = os.path.join(project_dir, main_file)
                    exec_result = run_python_script(full_path)
                    if exec_result["success"]:
                        result += f"\nExecution Output:\n{exec_result['output']}"
                    else:
                        result += f"\nExecution Failed:\n{exec_result['error']}"
            elif language == "web":
                web_result = serve_web_app(project_dir)
                if web_result["success"]:
                    result += f"\nWeb app is running at {web_result['url']}"
                    result += f"\nValidation: {web_result['validation']}"
                else:
                    result += f"\nFailed to serve web app: {web_result['validation']}"

        if test:
            if language == "python" and run:
                main_file = next((f for f in search_files("*.py", project_dir)), None)
                if main_file:
                    full_path = os.path.join(project_dir, main_file)
                    test_cases = [
                        {"input": "5", "expected": "120"},
                        {"input": "0", "expected": "1"}
                    ]
                    test_result = test_python_script(full_path, test_cases)
                    if test_result["passed"]:
                        result += "\nTest Passed: All test cases passed."
                    else:
                        result += f"\nTest Failed:\n{test_result['feedback']}"
                        fix_response = ask_llm(f"Fix the script based on: {test_result['feedback']}", iteration=len(steps) + 1)
                        if "task" in fix_response and fix_response["task"] == "edit_file":
                            edit_file(full_path, fix_response["content"])
                            test_result = test_python_script(full_path, test_cases)
                            if test_result["passed"]:
                                result += "\nFixed: All test cases passed."
                            else:
                                result += f"\nFix Failed:\n{test_result['feedback']}"
            elif language == "web":
                pass

        return result

    except Exception as e:
        print(f"[TaskManager] Error in code project: {str(e)}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[TaskManager] Error in code project: {str(e)}\n")
        return f"Error in code project: {str(e)}"