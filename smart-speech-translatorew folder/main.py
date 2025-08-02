#Smart Speech Translator (ML Based)

import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import pygame
import os
import time
import tempfile
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

# Initialize Pygame mixer for audio
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Languages dictionary (for Google Translate compatibility)
language_codes = {
    "English": "en",
    "Telugu": "te",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "French": "fr",
    "Spanish": "es",
    "German": "de",
    "Chinese": "zh-cn",
    "Japanese": "ja"
}

# ML training data
training_data = [
    ("hi", "greeting"),
    ("hello", "greeting"),
    ("how are you", "greeting"),
    ("what is your name", "question"),
    ("what time is it", "question"),
    ("translate this", "command"),
    ("please speak", "command"),
    ("tell me something", "command")
]
X_train, y_train = zip(*training_data)
vectorizer = CountVectorizer()
X_vectors = vectorizer.fit_transform(X_train)
model = MultinomialNB()
model.fit(X_vectors, y_train)

# Initialize translator
translator = Translator()

# GUI window
root = tk.Tk()
root.title("ML-Based Speech Translator")
root.geometry("520x640")
root.configure(bg="#f0f4ff")  # Light background

# Add a styled header
tk.Label(root, text="🌍 Smart Speech Translator", font=("Helvetica", 16, "bold"), fg="#003366", bg="#f0f4ff").pack(pady=10)

# Language Selection
frame = tk.Frame(root, bg="#f0f4ff")
frame.pack(pady=10)

style = ttk.Style()
style.theme_use("default")
style.configure("TCombobox", padding=5, font=("Arial", 11))

speak_label = tk.Label(frame, text="🎤 Speak Language:", font=("Arial", 12), bg="#f0f4ff")
speak_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
speak_lang = ttk.Combobox(frame, values=list(language_codes.keys()), width=20)
speak_lang.set("English")
speak_lang.grid(row=0, column=1, pady=5)

trans_label = tk.Label(frame, text="🌐 Translate To:", font=("Arial", 12), bg="#f0f4ff")
trans_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
trans_lang = ttk.Combobox(frame, values=list(language_codes.keys()), width=20)
trans_lang.set("Telugu")
trans_lang.grid(row=1, column=1, pady=5)

# Output display box
output_box = tk.Label(root, text="", font=("Arial", 11), wraplength=450, bg="#ffffff", fg="black", relief="groove", bd=2, padx=10, pady=10)
output_box.pack(pady=10)

# Function to play audio using pygame
def play_audio(text, lang):
    try:
        tts = gTTS(text=text, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
            filename = tmpfile.name
        tts.save(filename)
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            root.update()
        pygame.mixer.music.unload()
        os.remove(filename)
    except Exception as e:
        output_box.config(fg="red", text=f"\u274C Error playing audio:\n{e}")

# Function: Predict intent
def predict_intent(text):
    vect = vectorizer.transform([text])
    return model.predict(vect)[0]

# Speech-to-Text + Translate + Speak
def translate_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        output_box.config(fg="blue", text="Listening...")
        root.update()
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language=language_codes[speak_lang.get()])
            intent = predict_intent(text)
            trans = translator.translate(text, src=language_codes[speak_lang.get()], dest=language_codes[trans_lang.get()])
            output_box.config(fg="green", text=f"\u2705 Intent: {intent}\nYou said ({speak_lang.get()}): {text}\n\U0001F310 Translated to {trans_lang.get()}: {trans.text}")
            play_audio(trans.text, language_codes[trans_lang.get()])
        except sr.WaitTimeoutError:
            output_box.config(fg="red", text="\u274C Listening timed out.")
        except Exception as e:
            output_box.config(fg="red", text=f"\u274C Error: {e}")

# Text-to-Speech
def speak_typed_text():
    text = typed_entry.get()
    if text.strip():
        output_box.config(fg="green", text=f"\U0001F3A4 Speaking: {text}")
        play_audio(text, language_codes[trans_lang.get()])
    else:
        messagebox.showwarning("Warning", "Please enter some text to speak.")

# Buttons & Entry
btn1 = tk.Button(root, text="▶ Speak & Translate", bg="#4a90e2", fg="white", font=("Arial", 12, "bold"), command=translate_speech)
btn1.pack(pady=10)

typed_entry = tk.Entry(root, font=("Arial", 12), width=40)
typed_entry.pack(pady=10)

btn2 = tk.Button(root, text="\U0001F50A Speak Typed Text", bg="#28a745", fg="white", font=("Arial", 12, "bold"), command=speak_typed_text)
btn2.pack(pady=5)

root.mainloop()
