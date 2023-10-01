import openai
import os
from moviepy.editor import VideoFileClip
import tempfile

openai.api_key = '.'

def transcribe(video_file_path):
    # Load the video clip
    video_clip = VideoFileClip(video_file_path)

    # Extract the audio from the video
    audio_file = video_clip.audio
    print("b4 transcribe")
    try:
         # Create a temporary audio file to save the extracted audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            audio_file.write_audiofile(temp_audio_file.name)

        # Read the temporary audio file and transcribe it
        with open(temp_audio_file.name, "rb") as audio_file:
            transcribed_text = openai.Audio.transcribe("whisper-1", audio_file)

        return transcribed_text

    except Exception as e:
        # Handle API request errors here
        # You can log the error or return an error response
        print(f"Error: {e}")
        return "Transcription error"

def get_size(file_path):
    # Get the size of the video in bytes
    file_size = os.path.getsize(file_path)
    # Convert the size to megabytes with one decimal place
    size_mb = round(file_size / (1024 * 1024), 1)
    file_size = f"{size_mb} MB"
    return file_size