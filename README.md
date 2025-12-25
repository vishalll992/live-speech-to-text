# Clean STT

Clean STT is a real-time speech-to-text desktop application that listens through your microphone and displays live captions while automatically masking abusive language.  
Every detected profane word is replaced with `**` for consistent, clean output.

Built using **Python**, **Tkinter**, and **SpeechRecognition**.

---

## Features

- 🎙️ Real-time speech recognition
- 🧹 Automatic profanity detection
- 🔒 Deterministic censoring (every abusive word → `**`)
- 🖥️ Simple desktop GUI using Tkinter
- ⚡ Responsive UI with background audio processing
- 🧩 Custom profanity word support

---

## How It Works

1. Audio is captured from the system microphone.
2. Speech is converted to text using Google Speech Recognition.
3. Each word is checked using `better-profanity`.
4. Any abusive word is replaced with `**`.
5. Clean text is displayed live in the application window.

---

## Requirements

- Python 3.8 or higher
- Microphone (default system input)

### Python Libraries

- `SpeechRecognition`
- `better-profanity`
- `pyaudio`
- `tkinter` (comes with Python)

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/clean-stt.git
cd clean-stt
