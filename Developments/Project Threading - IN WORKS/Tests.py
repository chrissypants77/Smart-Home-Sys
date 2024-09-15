import tkinter as tk
import threading
import speech_recognition as sr

root = tk.Tk()
root.title("Speech Recognition App")


def toggle_recognition():
    global recognizing
    if not recognizing:
        # Start recognition thread
        recognizing = True
        threading.Thread(target=run_recognition).start()
        start_button.config(text="Stop Recognition")
    else:
        # Stop recognition thread
        recognizing = False
        start_button.config(text="Start Recognition")


def run_recognition():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        while recognizing:
            try:
                audio = recognizer.listen(source, timeout=3)
                result = recognizer.recognize_google(audio)
                result_var.set(f"Recognition Result: {result}")
            except sr.UnknownValueError:
                result_var.set("Speech Recognition could not understand audio")
            except sr.RequestError as e:
                result_var.set(f"Could not request results from Google Speech Recognition service; {e}")


label = tk.Label(root, text="Speech Recognition:")
label.pack()

result_var = tk.StringVar()
result_label = tk.Label(root, textvariable=result_var)
result_label.pack()

recognizing = False  # Flag to track if recognition is currently running

start_button = tk.Button(root, text="Start Recognition", command=toggle_recognition)
start_button.pack()


root.mainloop()