import google.generativeai as genai
import os
import json
import re
from datetime import datetime
import pytz

from core.memory_manager import MemoryManager

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")
memory = MemoryManager()

def reason(prompt: str) -> list:
    reasoning_prompt = f"""
    You are Sanya, an intelligent assistant. Break down the following prompt into a list of actionable steps.
    Return the steps in JSON format: {{ "steps": ["step 1", "step 2", ...] }}
    Prompt: "{prompt}"
    """
    try:
        response = model.generate_content(reasoning_prompt).text.strip()
        print(f"[LLM] Raw reasoning response: {response}")  # Debug log
        response = re.sub(r'^```json\s*|\s*```$', '', response).strip()
        response = re.sub(r'\\(?![nrt"\\])', '', response)  # Remove invalid escapes
        if not response.startswith("{"):
            raise json.JSONDecodeError("No JSON object found", response, 0)
        return json.loads(response).get("steps", [])
    except json.JSONDecodeError as e:
        print(f"[LLM] Reasoning error (JSON Decode): {str(e)}. Using default steps.")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[LLM] Reasoning error (JSON Decode): {str(e)}. Raw response: {response}\n")
        return ["1. Analyze the prompt", "2. Generate initial code", "3. Test and refine"]
    except Exception as e:
        print(f"[LLM] Reasoning error: {str(e)}. Using default steps.")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[LLM] Reasoning error: {str(e)}\n")
        return ["1. Analyze the prompt", "2. Generate initial code", "3. Test and refine"]

def ask_llm(prompt: str, iteration: int = 0, previous_response: str = None) -> dict:
    try:
        steps = reason(prompt) if iteration == 0 else []
        if steps and iteration == 0:
            print(f"[LLM] Reasoning steps: {steps}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"[LLM] Reasoning steps: {steps}\n")
            for step in steps:
                print(f"[LLM] Processing step: {step}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[LLM] Processing step: {step}\n")

        short_term_context = memory.get_short_term_context(context_window=memory.last_topic)
        long_term_context = memory.search_long_term_memory(prompt)
        memory_context = "\n\n".join([
            "[SHORT-TERM MEMORY CONTEXT]\n" + short_term_context,
            "[LONG-TERM MEMORY CONTEXT]\n" + long_term_context,
        ])

        ist = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(ist)
        date_str = current_time.strftime("%B %d, %Y")
        time_str = current_time.strftime("%I:%M %p")
        # Prepare the prompt with iteration context
        iteration_context = ""
        if previous_response:
            iteration_context = f"\nPrevious Response:\n{previous_response}\n\nNow refine or proceed with the next step."

        full_prompt = f"""
        You are Sanya, an intelligent assistant. You MUST reply in strict JSON format for action commands, or natural language if the user is just asking something general.
        For a JSON format, return only the JSON object (e.g., {{ "task": "create_file", "filename": ..., "content": ... }}).
        If the user says:
        - "Create a file..." → reply as JSON: {{ "task": "create_file", "filename": ..., "content": ... }}
        - "Open app..." → reply as JSON: {{ "task": "open_app", "app": ... }}
        - "Execute command..." → reply as JSON: {{ "task": "execute_command", "command": ... }}
        - "Check CPU usage" → reply as JSON: {{ "task": "get_system_info", "info_type": "check_cpu" }}
        - "What's the date today" → reply naturally: "Today's date is {date_str}."
        - "What's the time" → reply naturally: "The current time is {time_str}."
        - "Write a Python script for..." → break down the task into steps, generate the script, and reply as JSON: {{ "task": "code_project", "language": "python", "steps": [...], "files": [{{"filename": ..., "content": ...}}], "run": true, "test": true }}
        - "Create a web app for..." → break down the task into steps, generate HTML/CSS/JS files, and reply as JSON: {{ "task": "code_project", "language": "web", "steps": [...], "files": [{{"filename": ..., "content": ...}}], "run": true, "test": true }}
        - "Edit the script..." → update the specified file and reply as JSON: {{ "task": "edit_file", "filename": ..., "content": ... }}
        - "Search for..." → reply as JSON: {{ "task": "web_search", "query": ... }}
        
        Here is your memory context:
        {memory_context}

        {iteration_context}
        
        Now respond to: "{prompt}"
        """.strip()

        response = model.generate_content(full_prompt)
        reply = response.text.strip()

        if reply.startswith("{"):
            return json.loads(reply)
        elif reply.startswith("```json"):
            return json.loads(reply[7:-3])
        else:
            memory.append_to_short_term("user", prompt)
            memory.append_to_short_term("assistant", reply)
            return {"reply": reply}

    except Exception as e:
        print(f"[LLM] Error: {str(e)}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[LLM] Error: {str(e)}\n")
        return {"error": str(e)}

def classify_message(text):
    classification_prompt = f"""
    You are a classifier bot. Analyze the following message for its topic and importance based on context, intent, and sentiment.
    Return a single JSON object in the format: {{"topic": "<topic>", "important": true or false}}
    Consider topics like "time", "date", "personal information", "positive feedback", "behavior instruction", "personal preference", "coding", "web development", "system control", or "unknown" if unsure.
    Mark as important if the message involves personal details, feedback, instructions, coding requests, or critical tasks.
    Message: "{text}"
    """
    try:
        response = model.generate_content(classification_prompt).text.strip()
        match = re.search(r'\{.*?\}', response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"[LLM] Classification error: {str(e)}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[LLM] Classification error: {str(e)}\n")
    return {"topic": "unknown", "important": False}