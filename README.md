<!-- # Navigate to your project root first
cd usecase.ai

# Step 1: Landing Page setup
cd src/landingzone
npm install

# Step 2: Insurance Backend setup
cd ../AI_Insurance_Underwriter/Backend
uv venv
source .venv/bin/activate
uv sync

# Step 3: Insurance Frontend setup
cd ../Frontend
npm install

# Step 4: Video Transcriber Backend setup
cd ../../videotranscriber/Backend
uv venv
source .venv/bin/activate
uv sync

# Step 5: Video Transcriber Frontend setup
cd ../Frontend
npm install

# Done! Go back to root
cd ../../.. -->

# Project Setup Guide

This README provides step‑by‑step instructions to set up all services and applications in this repository.

---

# 📦 Prerequisites

Before starting, ensure you have the following installed on your system:

* **Node.js** (v18 or later recommended)
* **npm** (comes with Node.js)
* **Python** (3.10 or later recommended)
* **uv** (Python package manager)
* **Git**

Verify installations:

```bash
node -v
npm -v
python --version
uv --version
```

---

# 🚀 Project Initial Setup

Navigate to the project root directory first:

```bash
cd usecase.ai
```

---

# 1️⃣ Landing Page Setup

```bash
cd src/landingzone
npm install
```

This installs all required frontend dependencies for the landing page.

---

# 2️⃣ Insurance Underwriter — Backend Setup

```bash
cd ../AI_Insurance_Underwriter/Backend

# Create virtual environment
uv venv

# Activate environment (Linux / Mac)
# source .venv/bin/activate

# Activate environment (Windows)
.venv\Scripts\Activate

# Install dependencies
uv sync

# Once all dependencies installed 
deactivate
```

---

# 3️⃣ Insurance Underwriter — Frontend Setup

```bash
cd ../Frontend
npm install
```

Installs React / frontend dependencies like node_modules, etc.

---

# 4️⃣ Video Transcriber — Backend Setup

```bash
cd ../../videotranscriber/Backend

# Create virtual environment
uv venv

# Activate environment (Linux / Mac)
# source .venv/bin/activate

# Activate environment (Windows)
.venv\Scripts\Activate

# Install dependencies
uv sync

# Once all dependencies installed 
deactivate
```

---
# 5️⃣ Video Transcriber — FFmpeg Installation & Setup
Required for OpenAi-Whisper model to work

From https://github.com/btbn/ffmpeg-builds/releases
 - Get ffmpeg-master-latest-win64-gpl-shared.zip
 - Unzip and add below code so that whisper can find the path

```bash
import os
import sys
# Tell the script where your ffmpeg/bin folder is located; for eg,
  ffmpeg_path = r"C:\Users\sauthakur\Downloads\ffmpeg\bin" 
  os.environ["PATH"] += os.pathsep + ffmpeg_path  
 ```

---

# 6️⃣ Video Transcriber — Frontend Setup

```bash
cd ../Frontend
npm install
```

Installs all required frontend packages like node_modules for the Video Transcriber application.

---

# 7️⃣ Hugging face — API keys setup
Project uses quite a number of AI models(LLM) for various activities including
  - sentence_transformer("all-MiniLM-L6-v2")
  - conversational ("mistralai/Mistral-7B-Instruct-v0.2")
  - TRANSLATION ("ai4bharat/indictrans2-en-indic-1B")
  - MEDITRON ("mistralai/Mistral-7B-Instruct-v0.2")
  - TTS ("facebook/mms-tts-hin")
    
API-key is setup as below:
* Insurance Underwriter

```bash
Add .env file in
  src\AI_Insurance_Underwriter\Backend\src\insurance_underwriter\config\.env
 with content
   HUGGINGFACE_API_KEY = "xyzabc"
```

* Video Transcriber

```bash
Add .env file in
  src\videotranscriber\Backend\.env
 with content
   HUGGINGFACE_API_KEY = "xyzabc"
```  
---
# 8️⃣ OpenAI-Whisper LLM Model setup

-This model is used to convert Audio to Text

-It is downloaded locally as part of the dependencies in pyproject.toml

-And is placed in user-profile cache. It is acccessible as: 

```bash
  Win+R 
  %USERPROFILE%\.cache\whisper
```
* Downloaded Model occupies space. To recover space, delete the model from the folder path 

---

# ✅ Setup Complete

Return to the project root:

```bash
cd ../../..
```

All services are now installed and ready for development.

---

## Run the Complete Application

After returning to the project root, run the following command to start all services together:

```bash
.\run-all.bat
```

---

## Terminal Windows while Run

5 Command Windows open running application on different port:
 - 2 for Insurance_Underwriter(FE & BE) + 2 for Video_Transciber(FE & BE ) + 1 for LandingPage(FE)

-Landing Page:             http://localhost:3000
-Insurance App:            http://localhost:5173
-Video Transcriber:        http://localhost:3002
-Insurance API:            http://localhost:8000
-Video API:                http://localhost:8001


<img width="300" height="150" alt="image" src="https://github.com/user-attachments/assets/0adb6df5-4e91-48a8-8ab3-6f56de49b54b" />
<img width="700" height="150" alt="image" src="https://github.com/user-attachments/assets/8e075566-2f43-423d-843f-a6650f007411" />

<img width="300" height="150" alt="image" src="https://github.com/user-attachments/assets/d8cc8382-5a41-4e0e-bbd4-22f9f7a2208b" />
<img width="700" height="147" alt="image" src="https://github.com/user-attachments/assets/21860ef6-c547-4420-b83b-47ddaac5b6ee" />

<img width="300" height="150" alt="image" src="https://github.com/user-attachments/assets/1167db5f-91b2-498f-ad94-b124beb56f6d" />

---


---

**Project is now ready to use. Happy Coding! 🚀**

---



# 📬 Landing Page

<img width="1294" height="847" alt="image" src="https://github.com/user-attachments/assets/b0665601-4038-4be9-af70-d55eeb7f97a3" />


If you face setup issues, verify:

* Python / Node versions
* Virtual environment activation
* Dependency installation logs
