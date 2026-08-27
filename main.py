import speech_recognition as sr
import pyttsx3
import os
import sys
import threading
import customtkinter as ctk
# Core Engine Setup
# ---------------------------------------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 

# ---------------------------------------------------------
# UI and Logic Functions
# ---------------------------------------------------------
def update_display(text, sender="JARVIS"):
    """Updates the text box in the UI."""
    display_box.configure(state="normal")
    display_box.insert("end", f"{sender}: {text}\n\n")
    display_box.configure(state="disabled")
    display_box.see("end")

def speak(text):
    """Speaks the text and updates the UI."""
    update_display(text, "JARVIS")
    engine.say(text)
    engine.runAndWait()

def process_audio():
    """Runs the listening and executing logic in a separate thread."""
    # Disable the button while listening
    listen_button.configure(state="disabled", text="Listening...")
    
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1) 
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio).lower()
            update_display(command, "You")
            execute_command(command)
        except sr.UnknownValueError:
            update_display("Could not understand audio.", "System")
        except sr.WaitTimeoutError:
            update_display("Listening timed out.", "System")
        except sr.RequestError:
            update_display("Network error.", "System")

    # Re-enable the button
    listen_button.configure(state="normal", text="Activate JARVIS")

def execute_command(command):
    """Routes the command to local device actions."""
    if "open calculator" in command:
        speak("Opening the calculator.")
        os.system("calc.exe") # Use "open -a Calculator" for Mac, "gnome-calculator" for Linux
    elif "shut down" in command or "exit" in command:
        speak("Powering down. Goodbye.")
        app.quit()
        sys.exit()
    elif command != "":
        speak("I heard you, but I don't know how to do that yet.")

def trigger_listening():
    """Starts the audio processing thread when the button is clicked."""
    threading.Thread(target=process_audio, daemon=True).start()

# ---------------------------------------------------------
# UI Configuration
# ---------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("500x600")
app.title("JARVIS Interface")

# Title Label
title_label = ctk.CTkLabel(app, text="J.A.R.V.I.S.", font=ctk.CTkFont(size=30, weight="bold"))
title_label.pack(pady=(20, 10))

# Text Display Box
display_box = ctk.CTkTextbox(app, width=450, height=400, font=ctk.CTkFont(size=14))
display_box.pack(pady=10)
display_box.insert("0.0", "System Output Log...\n\n")
display_box.configure(state="disabled")

# Listen Button
listen_button = ctk.CTkButton(app, text="Activate JARVIS", font=ctk.CTkFont(size=16), height=50, command=trigger_listening)
listen_button.pack(pady=20)

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    # Start the UI loop
    app.mainloop()