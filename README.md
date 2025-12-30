# Jarvis Personal Assistant

## 📌 Overview

**Jarvis Personal Assistant** is an **AI-powered desktop assistant** that interacts with users via **voice commands**, processes tasks both **offline and online**, and maintains a **personal memory**.  
It integrates **speech recognition, text-to-speech, and intelligent responses**, making it capable of running commands, remembering personal facts, providing time/date info, telling jokes, and chatting with OpenAI’s GPT models.

This project focuses on **usability, automation, and AI integration**, making it suitable for **desktop productivity, learning, and demonstration purposes**.

---

## 🚀 Features

* Voice interaction (speech-to-text and text-to-speech)  
* Offline speech recognition using **Whisper** or **Vosk**  
* Online AI responses via **OpenAI GPT API**  
* Personal memory for remembering user facts and notes  
* Run local commands (e.g., open apps, open websites, tell time/date)  
* Fun interactions: jokes, greetings, and conversational replies  
* Fully customizable backend settings through **.env** file  

---

## 🛠 Technologies Used

* **Python 3.11+**  
* **OpenAI API** (online chat)  
* **Whisper** (offline STT)  
* **Vosk** (offline STT alternative)  
* **SpeechRecognition** / **SoundDevice** / **PyAudio** (audio capture)  
* **pyttsx3** (offline TTS)  
* **dotenv** (.env configuration)  
* **NumPy** / **SciPy** (audio processing)  


```

## 📁 Project Structure

Jarvis-Personal-Assistant/

│

├── jarvis.py # Main assistant script

├── requirements.txt # Python dependencies

├── memory.json # Stores remembered facts and notes

├── notes.txt # Optional text notes

├── models/ # Optional STT models (Vosk/Whisper)

│ └── vosk-small-en/

├── .env.example # Example environment variables

├── README.md

└── LICENSE


```


## ⚙️ Installation Guide (Step-by-Step)



### 1️⃣ Clone the Repository

```
bash
git clone https://github.com/Developeradill/Jarvis-Personal-Assistant/tree/main
cd Jarvis-Personal-Assistant


```

2️⃣ Create Virtual Environment (Recommended)

python -m venv venv

venv\Scripts\activate

source venv/bin/activate

---



3️⃣ Install Required Libraries

pip install -r requirements.txt


---


4️⃣ Configure Environment Variables

Copy .env.example to .env and set your values:


OPENAI_API_KEY=your_api_key_here

TTS_RATE=170

TTS_VOLUME=1.0

STT_BACKEND=whisper

WHISPER_MODEL_SIZE=tiny

VOSK_MODEL_DIR=./models/vosk-small-en

FORCE_LANGUAGE=

---


---

5️⃣ Run the Application

python jarvis.py

---

6️⃣ How to Interact


Press Enter to start speaking

Speak your command or question clearly

Jarvis will respond via voice and print the reply


---

Supported features:


Ask about time/date

Run apps (open notepad, open calculator)

Open websites (open youtube)

Take notes (take note Buy groceries)

Remember facts (remember that my favorite color is blue)

Chat and get intelligent replies using OpenAI

---


**🔮 Future Improvements**


Multi-language support for offline STT

Integration with calendars, reminders, and notifications

More advanced local command execution

GUI interface for easier configuration

Improved AI interaction with conversation context memory


---

**👨‍💻 Author**

**Adil Khan**

Computer Systems Engineer

AI & Desktop Assistant Developer

---

📜 License

This project is licensed under the MIT License.


⭐ If you find this project useful, give it a star on GitHub!

```

If you want, I can also **write a short, catchy repository description and topics/tags** for GitHub so it looks very professional on your profile.  
Do you want me to do that next?

```
