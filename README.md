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
source .venv/bin/activate

# Activate environment (Windows PowerShell)
# .venv\Scripts\Activate.ps1

# Install dependencies
uv sync
```

---

# 3️⃣ Insurance Underwriter — Frontend Setup

```bash
cd ../Frontend
npm install
```

Installs React / frontend dependencies for the Insurance Underwriter module.

---

# 4️⃣ Video Transcriber — Backend Setup

```bash
cd ../../videotranscriber/Backend

# Create virtual environment
uv venv

# Activate environment (Linux / Mac)
source .venv/bin/activate

# Activate environment (Windows PowerShell)
# .venv\Scripts\Activate.ps1

# Install dependencies
uv sync
```

---
# 5️⃣ Video Transcriber — FFmpeg Installation & Setup
Required for whisper to work

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

Installs all required frontend packages for the Video Transcriber application.

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

**Project is now ready to use. Happy Coding! 🚀**

---



# 📬 Support

If you face setup issues, verify:

* Python / Node versions
* Virtual environment activation
* Dependency installation logs
