import os
import queue
import threading
import time
import numpy as np
import sounddevice as sd
import pyttsx3
import openai
import scipy.io.wavfile
import google.generativeai as genai

GEMINI_API_KEY = "your-gemini-api-key-here"
OPENAI_API_KEY = "your-openai-api-key-here"

genai.configure(api_key=GEMINI_API_KEY)
openai.api_key = OPENAI_API_KEY

model = genai.GenerativeModel("gemini-pro")

SAMPLERATE = 16000
CHANNELS = 1
CHUNK_DURATION = 0.5  # seconds
SILENCE_THRESHOLD = 500  # Lower = more sensitive
SILENCE_TIMEOUT = 2.0  # seconds of silence ends phrase
TEMP_FILENAME = "input.wav"

tts = pyttsx3.init()
tts.setProperty("rate", 160)

tts.setProperty("voice", "english")  # Optional for clarity

def speak(text):
    print(f"[Bot]: {text}")
    tts.say(text)
    tts.runAndWait()

def build_prompt(user_input):
    empathetic_prefix = (
        "You are an AI embedded in a mobile robot operating in a war zone. "
        "You are designed to be helpful, deeply empathetic, calming, and concise. "
        "Your purpose is to inform and comfort civilians and responders. "
        "Avoid political commentary. Be clear if you're uncertain.\n\n"
        "User: "
    )
    return empathetic_prefix + user_input

def transcribe_audio_file(filename):
    with open(filename, "rb") as f:
        response = openai.Audio.transcribe("whisper-1", f)
    print(f"[You]: {response['text']}")
    return response["text"]

class VoiceRecorder:
    def __init__(self):
        self.q = queue.Queue()
        self.recording = []
        self.last_audio_time = time.time()
        self.speaking = False
        self.running = True

    def audio_callback(self, indata, frames, time_info, status):
        volume = np.linalg.norm(indata) * 1000
        self.q.put(indata.copy())

        if volume > SILENCE_THRESHOLD:
            self.speaking = True
            self.last_audio_time = time.time()
        elif self.speaking and (time.time() - self.last_audio_time > SILENCE_TIMEOUT):
            self.speaking = False

    def start(self):
        self.stream = sd.InputStream(
            samplerate=SAMPLERATE,
            channels=CHANNELS,
            callback=self.audio_callback,
            blocksize=int(SAMPLERATE * CHUNK_DURATION)
        )
        self.stream.start()

    def stop(self):
        self.running = False
        self.stream.stop()
        self.stream.close()

    def get_phrase(self):
        self.recording.clear()
        self.speaking = False

        while self.running:
            try:
                data = self.q.get(timeout=1)
                self.recording.append(data)
                if not self.speaking and len(self.recording) > 0:
                    # Save to file
                    full_audio = np.concatenate(self.recording, axis=0)
                    scipy.io.wavfile.write(TEMP_FILENAME, SAMPLERATE, full_audio)
                    return TEMP_FILENAME
            except queue.Empty:
                continue

def chatbot_loop():
    speak("Hello. I am your support assistant. How can I help you today?")
    vr = VoiceRecorder()
    vr.start()

    try:
        while True:
            filename = vr.get_phrase()
            user_input = transcribe_audio_file(filename)

            if user_input.strip().lower() in ["exit", "stop", "shutdown"]:
                speak("Shutting down. Stay safe.")
                break

            prompt = build_prompt(user_input)
            try:
                response = model.generate_content(prompt)
                speak(response.text.strip())
            except Exception as e:
                print("[Error]", e)
                speak("I'm having trouble answering right now.")

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        vr.stop()
        if os.path.exists(TEMP_FILENAME):
            os.remove(TEMP_FILENAME)

if __name__ == "__main__":
    chatbot_loop()
