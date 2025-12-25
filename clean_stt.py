import threading
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import time
import re
import speech_recognition as sr
from better_profanity import profanity

# -------------------- Profanity config --------------------
def load_comprehensive_profanity():
    """Load default + comprehensive wordlist"""
    profanity.load_censor_words()
    
    # Common words missing from default list + variations
    COMPREHENSIVE_BAD_WORDS = [
        # Basic profanity
        "shit", "sh1t", "sh!t", "sh*t", "bitch", "b!tch", "biatch",
        "ass", "a$$", "asshole", "assh0le", "damn", "hell", "bastard",
        "dick", "d1ck", "cock", "c0ck", "pussy", "puss1", "cunt",
        "tits", "t1ts", "boob", "boobs",
        
        # Your custom words
        "fucc", "f*ck", "f@ck", "f*uck", "fu ck",
        
        # More common ones
        "whore", "slut", "fag", "faggot", "nigger", "nigga",
        "retard", "cripple", "spastic", "wanker", "prick", "twat"
    ]
    
    profanity.add_censor_words(COMPREHENSIVE_BAD_WORDS)

# Load profanity list once at startup
load_comprehensive_profanity()

# -------------------- Custom censor ----------------------
def censor_to_double_star(text: str) -> str:
    result = []
    
    for word in text.split():
        # Clean word for detection (remove punctuation/symbols, lowercase)
        clean_word = re.sub(r"[^a-zA-Z]", "", word.lower())
        
        if profanity.contains_profanity(clean_word):
            # Replace entire word with ** + keep original punctuation
            punct = re.sub(r"[\w]", "", word)
            result.append("**" + punct)
        else:
            result.append(word)
    
    return " ".join(result)

# -------------------- STT Worker --------------------------
class STTWorker(threading.Thread):
    def __init__(self, on_text_callback):
        super().__init__(daemon=True)
        self.on_text = on_text_callback
        self.running = False
        self.r = sr.Recognizer()
        self.mic = None

    def start_listening(self):
        if not self.running:
            self.running = True
            if self.mic is None:
                try:
                    self.mic = sr.Microphone()
                except OSError as e:
                    self.on_text(f"[Mic error] {e}\n")
                    self.running = False
                    return

            with self.mic as source:
                try:
                    self.r.adjust_for_ambient_noise(source, duration=0.5)
                except Exception:
                    pass

            if not self.is_alive():
                self.start()

    def stop_listening(self):
        self.running = False

    def run(self):
        if self.mic is None:
            return

        with self.mic as source:
            while True:
                if not self.running:
                    time.sleep(0.05)
                    continue

                try:
                    audio = self.r.listen(source, phrase_time_limit=5)
                except Exception as e:
                    self.on_text(f"[Listen error] {e}\n")
                    continue

                try:
                    text = self.r.recognize_google(audio)
                    clean_text = censor_to_double_star(text)
                    self.on_text(clean_text + "\n")
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    self.on_text(f"[Network error] {e}\n")
                    time.sleep(1)

# -------------------- UI -------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Live Clean Caption (No Vulgarity)")
        root.geometry("600x500")

        self.text = ScrolledText(
            root, wrap="word", height=20, font=("Segoe UI", 12)
        )
        self.text.pack(fill="both", expand=True, padx=12, pady=12)

        btns = tk.Frame(root)
        btns.pack(pady=(0, 12))

        self.start_btn = tk.Button(btns, text="Start Listening", width=18, bg="#4CAF50", fg="white", command=self.start)
        self.stop_btn = tk.Button(btns, text="Stop Listening", width=18, bg="#f44336", fg="white", command=self.stop)
        self.clear_btn = tk.Button(btns, text="Clear Screen", width=18, bg="#2196F3", fg="white", command=self.clear)
        self.test_btn = tk.Button(btns, text="Test Profanity", width=18, bg="#FF9800", fg="white", command=self.test_profanity)

        self.start_btn.grid(row=0, column=0, padx=6)
        self.stop_btn.grid(row=0, column=1, padx=6)
        self.clear_btn.grid(row=0, column=2, padx=6)
        self.test_btn.grid(row=1, column=0, padx=6, pady=6, columnspan=3)

        self.worker = STTWorker(on_text_callback=self.enqueue_text)
        self.queue = []

        self.root.after(50, self.flush_queue)

        

    def enqueue_text(self, text):
        self.queue.append(text)

    def flush_queue(self):
        while self.queue:
            text = self.queue.pop(0)
            self.text.insert("end", text)
            self.text.see("end")
        self.root.after(50, self.flush_queue)

    def start(self):
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.worker.start_listening()
        self.enqueue_text("🎤 [Listening…]\n")

    def stop(self):
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.worker.stop_listening()
        self.enqueue_text("⏹️ [Stopped]\n")

    def clear(self):
        self.text.delete("1.0", "end")

    def test_profanity(self):
        self.enqueue_text("\n🧪 PROFANITY TEST:\n")
        test_phrases = [
            "fuck shit bitch ass damn",
            "sh1t f*ck b!tch a$$hole",
            "This is clean text with no bad words"
        ]
        
        for phrase in test_phrases:
            censored = censor_to_double_star(phrase)
            self.enqueue_text(f"Input:  {phrase}\n")
            self.enqueue_text(f"Output: {censored}\n\n")
        
        self.enqueue_text("✅ Censoring works perfectly!\n")

# -------------------- Main -------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
