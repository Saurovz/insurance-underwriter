# Navigate to your project root first
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
cd ../../..
