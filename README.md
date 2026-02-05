* Create Proj
from cmd prompt> uv init Video2Text

* Virtual Env Creation & Activation
Open the Project in VSC. IN terminal window
    >cd Video2Text
    >uv venv
    >.venv\Scripts\activate

* Install the PreRequisites
    uv add moviepy     //To Convert video to audio (mp4 to mp3)
    uv add openai-whisper

    //For SST
    uv add SpeechRecognition
    uv add PyAudio


* FFmpeg Installation
    - Required for whisper to work
    - from https://github.com/btbn/ffmpeg-builds/releases
      get ffmpeg-master-latest-win64-gpl-shared.zip
    - Unzip and add below code so that whisper can find the path
        import os
        import sys
        # Tell the script where your ffmpeg/bin folder is
        ffmpeg_path = r"C:\Users\sauthakur\Downloads\ffmpeg\bin" 
        os.environ["PATH"] += os.pathsep + ffmpeg_path  

* Run
python main.py

* Models download and delete to recover space
-  model = whisper.load_model("medium")
   -Based on Model Type : "base, medium, turbo, etc"
      they will be downloaded once & used
   -Models are placed in user-profile cache and is acccessible from Win+R 
      %USERPROFILE%\.cache\whisper
      and can be deleted from here   

   
TODO
    -Build the Chat
    -Detect and Print Language spoken + (Gender of the Patient)
    -Generate the Prescription & voiceOut the advice

The FLOW
  1. Patient installs Dr-mobile-app, uploads Adhaar+Video with name,age,complication in his <lang> 
      <** Not implemented>
  2. Dr, on receiving the detail, parse the video, understand the complication, chat with the text 
       & voice out the advice in <eng> which is translated to text and Dr can manually edit it too.
  3. Based on Dr's advice, Prescription & Advice Audio in the patient's language
                          are generated and notified for follow-up actions
