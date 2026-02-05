
import os
import sys

# Tell the script where ffmpeg/bin folder is
ffmpeg_path = r"C:\Users\sauthakur\Downloads\ffmpeg\bin" 
os.environ["PATH"] += os.pathsep + ffmpeg_path

import whisper

from moviepy import VideoFileClip

def extract_audio(video_path, output_audio_path):
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Extract the audio
        audio = video.audio
        
        # Write the audio to a file
        audio.write_audiofile(output_audio_path)
        
        # Close the files to free up memory
        audio.close()
        video.close()
        
        print(f"Success! Audio saved to: {output_audio_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def extract_audio_snippet(video_path, output_audio_path, start_sec=0, end_sec=30):
    try:
        # Load the video
        video = VideoFileClip(video_path)
        
        # Trim the video to the first 30 seconds
        # (Note: Use .subclip() if you are on an older version of MoviePy)
        snippet = video.subclipped(start_sec, end_sec)
        
        # Extract and save the audio from the snippet
        snippet.audio.write_audiofile(output_audio_path)
        
        # Clean up
        snippet.close()
        video.close()
        
        print(f"Success! First {end_sec} seconds saved to: {output_audio_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

def translate_to_english(audio_path):
    try:
        # Load the model ("base" is fast, "medium" is more accurate for Hindi)
        print("Loading AI model... (this may take a moment)")
        model = whisper.load_model("medium")
        
        # The 'task="translate"' tells AI: "Listen to the Hindi,etc, but write it in English."
        print("Translating audio...")
        result = model.transcribe(audio_path, task="translate")
        
        # Output the translated text
        print("\n--- Translation ---")
        print(result["text"])
        
        # Optional: Save to a text file
        #with open("translation.txt", "w", encoding="utf-8") as f:
        #    f.write(result["text"])
            
    except Exception as e:
        print(f"An error occurred: {e}")


#STT
import speech_recognition as sr

def transcribe_speech():
    # Initialize the recognizer
    recognizer = sr.Recognizer()

    # Use the microphone as the audio source
    with sr.Microphone() as source:
        print(">>> Adjusting for ambient noise... please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        
        print(">>> Listening... (speak now)")
        try:
            # Listen for the first phrase and extract it into audio data
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print(">>> Recognizing...")

            # Use Google Web Speech API to transcribe the audio
            # language='en-US' can be changed (e.g., 'es-ES', 'fr-FR')
            text = recognizer.recognize_google(audio_data, language='en-US')
            print(f">>> You said: {text}")
            
        except sr.WaitTimeoutError:
            print(">>> Error: Listening timed out while waiting for phrase.")
        except sr.UnknownValueError:
            print(">>> Error: Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            print(f">>> Error: Could not request results; {e}")
   
def record_speech():
    recognizer = sr.Recognizer()
    while(1):
        try:            
            with sr.Microphone() as source:
                print(">>> Adjusting for ambient noise... please wait.")
                recognizer.adjust_for_ambient_noise(source, duration=0.2)
            
                print(">>> Listening... (speak now)")
                try:
                    audio_data = recognizer.listen(source, timeout=2)
                    #print(">>> Recognizing...")
                    text = recognizer.recognize_google(audio_data, language='en-US')
                    #print(f">>> You said: {text}")
                    return text
                except Exception as e:
                    print(f">>> An error occurred: {e}")
                    return None
        except sr.RequestError as e:
            print(f">>> Could not request results; {e}")
            #return None
        except sr.UnknownValueError as e:
            print(f">>> Could not understand audio; {e}")
    return

def main():
    print("Hello from video2text!") 
    
    source = r".\videos\Doc1.mp4"
    target = r".\videos\audio\Doc1.mp3"
    
    #Extract_audio("my_video.mp4", "extracted_audio.mp3")
    #extract_audio(source, target)

    #Extract from 0:00 to 0:30 seconds
    #extract_audio_snippet(r".\videos\Monotonous.mp4", r".\videos\audio\Monotonous_intro.mp3", 0, 30)

    # Usage
    #translate_to_english(target)

    #transcribe_speech()

    # Doctor;s advice
    # while(1):
    #     text = record_speech()
    #     if text:
    #         # Check for exit keywords
    #         if text.lower() in ["stop", "exit", "thank you", "goodbye"]:
    #             print(">>> Exiting program...")
    #             break  # This breaks the while loop
    #         with open("output.txt", "a", encoding="utf-8") as f:
    #             f.write(text + "\n")
    #         print(f">>> You said: {text}")


if __name__ == "__main__":
    main()
