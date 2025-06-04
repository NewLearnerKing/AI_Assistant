from core.task_manager import route_command
from modules.voice_interface import speak, listen
from modules.wakeword_detector import wait_for_wake_word
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()

def notify(message: str, email: str = os.getenv("EMAIL_ADDRESS")):
    msg = MIMEText(message)
    msg['Subject'] = 'Sanya Notification'
    msg['From'] = os.getenv("EMAIL_ADDRESS")
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(os.getenv("EMAIL_ADDRESS"), os.getenv("EMAIL_PASSWORD"))
            server.sendmail(os.getenv("EMAIL_ADDRESS"), email, msg.as_string())
        print(f"[Notification] Sent email: {message}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[Notification] Sent email: {message}\n")
    except Exception as e:
        print(f"[Notification] Error sending email: {e}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"[Notification] Error sending email: {e}\n")

def schedule_task(task: callable, interval_minutes: int):
    schedule.every(interval_minutes).minutes.do(task)
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)
    threading.Thread(target=run_schedule, daemon=True).start()
    print(f"[Schedule] Scheduled task to run every {interval_minutes} minutes")
    with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"[Schedule] Scheduled task to run every {interval_minutes} minutes\n")

def run_assistant():
    greeting = "Hello Sir. I am Sanya, Your Systematic Artificial Neural Yielded Assistant. How can I help you today?"
    speak(greeting)
    print(greeting)
    with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"{greeting}\n")

    # Example: Schedule a task to notify every 60 minutes
    def check_status():
        notify("Sanya is running smoothly.")
    schedule_task(check_status, 60)

    while True:
        wait_for_wake_word()
        speak("Yes sir.", 1)
        user_input = listen()
        print(f"You: {user_input}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"You: {user_input}\n")

        exit_phrases = ["exit", "quit", "bye", "goodbye", "thank you", "your work is done", "you can go", "well done"]

        if any(phrase in user_input.lower() for phrase in exit_phrases):
            goodbye = "Goodbye Sir. Have a great day."
            speak(goodbye, 2)
            print(f"Sanya: {goodbye}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"Sanya: {goodbye}\n")
            break

        response = route_command(user_input)
        speak(response)
        print(f"Sanya: {response}")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write(f"Sanya: {response}\n")

if __name__ == "__main__":
    run_assistant()