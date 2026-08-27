import os
import time
import asyncio
import threading
from pathlib import Path
import speech_recognition as sr
import pyttsx3
import pygame
from config import JARVIS_VOICE, JARVIS_SPEECH_RATE, JARVIS_PITCH, TEMP_AUDIO_DIR

# Initialize pygame audio mixer for edge-tts playback
try:
    pygame.mixer.init()
    HAS_PYGAME = True
except Exception:
    HAS_PYGAME = False

# Fallback pyttsx3 offline engine
try:
    fallback_engine = pyttsx3.init()
    voices = fallback_engine.getProperty('voices')
    if voices:
        fallback_engine.setProperty('voice', voices[0].id)
    fallback_engine.setProperty('rate', 175)
except Exception:
    fallback_engine = None

class VoiceEngine:
    def __init__(self, voice: str = JARVIS_VOICE, rate: str = JARVIS_SPEECH_RATE, pitch: str = JARVIS_PITCH):
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.is_speaking = False
        self.is_listening = False
        self._lock = threading.Lock()

    async def _generate_edge_tts(self, text: str, output_path: str):
        """Generates crisp neural TTS using edge-tts."""
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=self.rate, pitch=self.pitch)
        await communicate.save(output_path)

    def speak(self, text: str, on_start=None, on_finish=None):
        """
        Speaks the given text using high-definition neural TTS with fallback.
        Runs synchronously in the calling thread or can be called from worker threads.
        """
        if not text or not text.strip():
            return

        with self._lock:
            self.is_speaking = True
            if on_start:
                try:
                    on_start(text)
                except Exception:
                    pass

            audio_file = str(TEMP_AUDIO_DIR / f"tts_{int(time.time() * 1000)}.mp3")
            success = False

            # 1. Try High Quality Edge-TTS
            try:
                # Run edge-tts in event loop
                asyncio.run(self._generate_edge_tts(text, audio_file))
                
                if HAS_PYGAME and os.path.exists(audio_file):
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(20)
                    pygame.mixer.music.unload()
                    success = True
            except Exception as e:
                # Print debug info if edge-tts fails
                # Fallback to local pyttsx3
                success = False

            # 2. Fallback to pyttsx3 if edge-tts not available or network error
            if not success and fallback_engine:
                try:
                    fallback_engine.say(text)
                    fallback_engine.runAndWait()
                except Exception:
                    pass

            # Cleanup temp file
            if os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception:
                    pass

            self.is_speaking = False
            if on_finish:
                try:
                    on_finish()
                except Exception:
                    pass

    def listen(self, timeout: int = 5, phrase_limit: int = 10, on_listen_start=None) -> str:
        """
        Captures speech from the default microphone and transcribes it via Google STT.
        """
        self.is_listening = True
        if on_listen_start:
            try:
                on_listen_start()
            except Exception:
                pass

        transcription = ""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
                transcription = self.recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            transcription = ""
        except sr.UnknownValueError:
            transcription = ""
        except Exception:
            transcription = ""
        finally:
            self.is_listening = False

    def listen_for_wake_word(self, wake_words=None, stop_event=None, on_wake=None):
        """
        Continuously listens in the background for wake phrases (e.g., 'hey jarvis', 'jarvis').
        When detected, calls on_wake callback.
        """
        if wake_words is None:
            wake_words = ["jarvis", "hey jarvis", "wake up jarvis", "hello jarvis"]

        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 280
        recognizer.dynamic_energy_threshold = True

        while stop_event and not stop_event.is_set():
            if self.is_speaking or self.is_listening:
                time.sleep(0.3)
                continue

            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.4)
                    audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
                    
                if stop_event and stop_event.is_set():
                    break

                text = recognizer.recognize_google(audio).lower().strip()
                if any(w in text for w in wake_words):
                    if on_wake and not self.is_speaking and not self.is_listening:
                        on_wake(text)
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                pass
            except Exception:
                time.sleep(0.5)

# Global Voice Engine Instance
jarvis_voice = VoiceEngine()

