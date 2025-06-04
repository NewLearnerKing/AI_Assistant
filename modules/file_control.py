import os
import glob
import shutil
import time
from typing import List, Tuple

def create_file(filename: str, content: str = "") -> str:
    try:
        start_time = time.time()
        if not filename:
            return "Please specify the file name."
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(content)
        elapsed_time = time.time() - start_time
        print(f"[FileControl] Created file: {filename} in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Created file: {filename} in {elapsed_time:.3f}s\n")
        return f"File '{filename}' created successfully."
    except Exception as e:
        print(f"[FileControl] Error creating file: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error creating file: {e}\n")
        return f"Error creating file: {e}"

def batch_create_files(files: List[Tuple[str, str]]) -> str:
    try:
        start_time = time.time()
        results = []
        for filename, content in files:
            result = create_file(filename, content)
            results.append(result)
        elapsed_time = time.time() - start_time
        print(f"[FileControl] Batch created {len(files)} files in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Batch created {len(files)} files in {elapsed_time:.3f}s\n")
        return "\n".join(results)
    except Exception as e:
        print(f"[FileControl] Error in batch create: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error in batch create: {e}\n")
        return f"Error in batch create: {e}"

def edit_file(filename: str, content: str, append: bool = False) -> str:
    try:
        start_time = time.time()
        mode = 'a' if append else 'w'
        with open(filename, mode, encoding="utf-8") as f:
            f.write(content)
        action = "appended to" if append else "edited"
        elapsed_time = time.time() - start_time
        print(f"[FileControl] {action.capitalize()} file: {filename} in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] {action.capitalize()} file: {filename} in {elapsed_time:.3f}s\n")
        return f"File '{filename}' {action} successfully."
    except Exception as e:
        print(f"[FileControl] Error editing file: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error editing file: {e}\n")
        return f"Error editing file: {e}"

def read_file(filename: str) -> str:
    try:
        start_time = time.time()
        with open(filename, 'r', encoding="utf-8") as f:
            content = f.read()
        elapsed_time = time.time() - start_time
        print(f"[FileControl] Read file: {filename} in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Read file: {filename} in {elapsed_time:.3f}s\n")
        return content
    except Exception as e:
        print(f"[FileControl] Error reading file: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error reading file: {e}\n")
        return f"Error reading file: {e}"

def search_files(pattern: str, directory: str = ".") -> List[str]:
    try:
        start_time = time.time()
        files = glob.glob(os.path.join(directory, pattern), recursive=True)
        elapsed_time = time.time() - start_time
        print(f"[FileControl] Found {len(files)} files matching '{pattern}' in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Found {len(files)} files matching '{pattern}' in {elapsed_time:.3f}s\n")
        return files
    except Exception as e:
        print(f"[FileControl] Error searching files: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error searching files: {e}\n")
        return []

def delete_file(filename: str) -> str:
    try:
        start_time = time.time()
        os.remove(filename)
        elapsed_time = time.time() - start_time
        print(f"[FileControl] Deleted file: {filename} in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Deleted file: {filename} in {elapsed_time:.3f}s\n")
        return f"File '{filename}' deleted successfully."
    except Exception as e:
        print(f"[FileControl] Error deleting file: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error deleting file: {e}\n")
        return f"Error deleting file: {e}"

def copy_file(src: str, dst: str) -> str:
    try:
        start_time = time.time()
        shutil.copy2(src, dst)
        elapsed_time = time.time() - start_time
        print(f"[FileControl] Copied file from {src} to {dst} in {elapsed_time:.3f}s")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Copied file from {src} to {dst} in {elapsed_time:.3f}s\n")
        return f"File copied from '{src}' to '{dst}' successfully."
    except Exception as e:
        print(f"[FileControl] Error copying file: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[FileControl] Error copying file: {e}\n")
        return f"Error copying file: {e}"