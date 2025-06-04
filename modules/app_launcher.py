# modules/app_launcher.py
import subprocess
import platform

def open_app(command: str) -> str:
    try:
        app_name = command.split("open app")[-1].strip()

        if platform.system() == "Windows":
            subprocess.Popen(app_name, shell=True)
        elif platform.system() == "Linux":
            subprocess.Popen([app_name])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            return "Unsupported OS"

        return f"Trying to open {app_name}..."
    except Exception as e:
        return f"Error launching app: {e}"
