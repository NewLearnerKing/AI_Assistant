import sounddevice as sd
import numpy as np
from openwakeword.model import Model
import os

wake_model = Model(
    wakeword_models=[os.path.join("custom_wake_word", "sanya", "sanya.onnx")]
)

samplerate = 16000
frame_duration = 1.0  # in seconds
frame_length = int(samplerate * frame_duration)

def wait_for_wake_word():
    print("🟢 Wake word listener active...")
    with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
        log_file.write("🟢 Wake word listener active...\n")
    with sd.InputStream(channels=1, samplerate=samplerate, dtype='int16', blocksize=frame_length) as stream:
        while True:
            audio_data, _ = stream.read(frame_length)
            audio = np.squeeze(audio_data)

            prediction = wake_model.predict(audio)
            print(prediction)
            with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                log_file.write(f"{prediction}\n")
            if prediction.get("sanya", 0) > 0.4:
                print("🔊 Wake word 'Sanya' detected!")
                with open("logs/sanya.log", "a", encoding="utf-8") as log_file:
                    log_file.write("🔊 Wake word 'Sanya' detected!\n")
                return