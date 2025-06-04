# modules/voice_interface.py
import speech_recognition as sr
from TTS.api import TTS
import sounddevice as sd
import numpy as np
import threading
import queue
import re
import uuid
from modules.mood_manager import MoodManager

recognizer = sr.Recognizer()
tts = TTS(model_name="tts_models/en/jenny/jenny")
default_wav_greet = tts.tts("Yes sir.")
default_wav_goodbye = tts.tts("Goodbye Sir. Have a great day.")

# Shared components
speak_queue = queue.Queue()
queue_condition = threading.Condition()
speak_interrupt = threading.Event()
audio_lock = threading.Lock()
play_token = None
producer_thread = None
consumer_thread = None


def _play_queue(token):
    while True:
        try:
            wav_chunk = speak_queue.get(timeout=0.1)
        except queue.Empty:
            if speak_interrupt.is_set() or token != play_token:
                break
            continue

        if speak_interrupt.is_set() or token != play_token:
            break
        if wav_chunk is None:
            break

        with audio_lock:
            sd.play(np.array(wav_chunk), samplerate=tts.synthesizer.output_sample_rate)

        duration = len(wav_chunk) / tts.synthesizer.output_sample_rate
        waited = 0
        while waited < duration:
            if speak_interrupt.is_set() or token != play_token:
                with audio_lock:
                    sd.stop()
                break
            sd.sleep(50)
            waited += 0.05

        if speak_interrupt.is_set() or token != play_token:
            break

    with audio_lock:
        sd.stop()
    with speak_queue.mutex:
        speak_queue.queue.clear()
    speak_interrupt.clear()


def reset_audio_state():
    global producer_thread, consumer_thread

    speak_interrupt.set()
    stop_all_audio()

    with queue_condition:
        speak_queue.put(None)
        queue_condition.notify_all()

    if producer_thread and producer_thread.is_alive():
        producer_thread.join(timeout=0.2)
    if consumer_thread and consumer_thread.is_alive():
        consumer_thread.join(timeout=0.2)

    with speak_queue.mutex:
        speak_queue.queue.clear()

    speak_interrupt.clear()

mood_manager = MoodManager()

def speak(text, flag=0):
    global producer_thread, consumer_thread, play_token

    # Adjust text based on mood
    text = mood_manager.adjust_response(text)
    mood = mood_manager.current_mood

    print(f"[Audio] Speaking: {text} (flag={flag}, mood={mood})")
    with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
        log_file.write(f"[Audio] Speaking: {text} (flag={flag}, mood={mood})\n")

    reset_audio_state()

    new_token = uuid.uuid4()
    play_token = new_token
    this_token = play_token

    if flag != 0:
        default_greet(flag)
        return

    sentences = re.split(r'(?<=[.!?]) +', text)

    def enqueue_sentences():
        print("[Audio] Starting enqueue_sentences thread")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write("[Audio] Starting enqueue_sentences thread\n")
        for sentence in sentences:
            if speak_interrupt.is_set() or play_token != this_token:
                print("[Audio] Enqueue interrupted or token mismatch, exiting")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write("[Audio] Enqueue interrupted or token mismatch, exiting\n")
                return
            try:
                # Simulate emotion by adjusting TTS parameters (placeholder)
                wav_chunk = tts.tts(sentence)
                print(f"[Audio] Generated TTS for: {sentence} (mood={mood})")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[Audio] Generated TTS for: {sentence} (mood={mood})\n")
            except Exception as e:
                print(f"[Audio] TTS error: {e}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[Audio] TTS error: {e}\n")
                return
            if speak_interrupt.is_set() or play_token != this_token:
                print("[Audio] Enqueue interrupted or token mismatch after TTS, exiting")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write("[Audio] Enqueue interrupted or token mismatch after TTS, exiting\n")
                return
            with queue_condition:
                speak_queue.put(wav_chunk)
                print(f"[Audio] Queued sentence: {sentence}")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"[Audio] Queued sentence: {sentence}\n")

        with queue_condition:
            speak_queue.put(None)
            print("[Audio] Enqueue complete, added None to queue")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write("[Audio] Enqueue complete, added None to queue\n")

    producer_thread = threading.Thread(target=enqueue_sentences, daemon=True)
    consumer_thread = threading.Thread(target=_play_queue, args=(this_token,), daemon=True)

    producer_thread.start()
    consumer_thread.start()


def default_greet(flag):
    wav_np = np.array(default_wav_greet if flag == 1 else default_wav_goodbye)
    with audio_lock:
        sd.play(wav_np, samplerate=tts.synthesizer.output_sample_rate)
        sd.wait()


def listen():
    with sr.Microphone() as source:
        print("🎤 Listening...")
        with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
            log_file.write("🎤 Listening...\n")
        audio = recognizer.listen(source)
        try:
            transcript = recognizer.recognize_google(audio)
            print(f"Transcript: {transcript}")
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"Transcript: {transcript}\n")
            return transcript
        except sr.UnknownValueError:
            error_msg = "Sorry, I didn't catch that."
            print(error_msg)
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"{error_msg}\n")
            return error_msg
        except sr.RequestError:
            error_msg = "Speech service is down."
            print(error_msg)
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"{error_msg}\n")
            return error_msg


def stop_all_audio():
    with audio_lock:
        sd.stop()
        sd.sleep(100)
