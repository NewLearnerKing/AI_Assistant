import subprocess
import platform
import psutil
import time

def execute_command(command: str) -> str:
    try:
        start_time = time.time()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout if result.stdout else result.stderr
        elapsed_time = time.time() - start_time
        print(f"[SystemControl] Executed command: {command}, Output: {output.strip()}, Time: {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Executed command: {command}, Output: {output.strip()}, Time: {elapsed_time:.3f}s\n")
        return output.strip()
    except subprocess.TimeoutExpired:
        print(f"[SystemControl] Command timed out: {command}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Command timed out: {command}\n")
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        print(f"[SystemControl] Error executing command: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Error executing command: {e}\n")
        return f"Error: {e}"

def get_system_info(task: str) -> str:
    system = platform.system()
    try:
        if task == "check_cpu":
            if system == "Windows":
                return execute_command("wmic cpu get loadpercentage")
            elif system in ["Linux", "Darwin"]:
                return execute_command("top -bn1 | grep 'Cpu(s)'")
        elif task == "check_memory":
            memory = psutil.virtual_memory()
            return f"Total: {memory.total // (1024 ** 3)} GB, Used: {memory.used // (1024 ** 3)} GB, Free: {memory.free // (1024 ** 3)} GB"
        elif task == "list_processes":
            if system == "Windows":
                return execute_command("tasklist")
            elif system in ["Linux", "Darwin"]:
                return execute_command("ps aux")
        print(f"[SystemControl] Unsupported task: {task}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Unsupported task: {task}\n")
        return "Unsupported task"
    except Exception as e:
        print(f"[SystemControl] Error in system info: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Error in system info: {e}\n")
        return f"Error: {e}"

def automate_process(task: str) -> str:
    try:
        if task == "backup_files":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backups/backup_{timestamp}"
            execute_command(f"mkdir {backup_dir}")
            return execute_command(f"cp -r ./data/* {backup_dir}")
        print(f"[SystemControl] Unsupported automation task: {task}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Unsupported automation task: {task}\n")
        return "Unsupported automation task"
    except Exception as e:
        print(f"[SystemControl] Error in automation: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[SystemControl] Error in automation: {e}\n")
        return f"Error: {e}"