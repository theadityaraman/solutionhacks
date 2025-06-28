import google.generativeai as genai
import speech_recognition as sr
import pyttsx3

genai.configure(api_key="YOUR_GEMINI_API_KEY")  
model = genai.GenerativeModel("gemini-pro")

recognizer = sr.Recognizer()
tts = pyttsx3.init()
tts.setProperty('rate', 150)

print("🎤 Speak into the mic... Press Ctrl+C to stop.")

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

            user_input = recognizer.recognize_google(audio)
            print(f"🗣 You said: {user_input}")

            response = model.generate_content(user_input)
            reply = response.text.strip()
            print(f"🤖 Gemini: {reply}")

            tts.say(reply)
            tts.runAndWait()

    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
    except KeyboardInterrupt:
        print("\n🛑 Exiting. Goodbye!")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
