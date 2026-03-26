# services/tts.py
from gtts import gTTS
import os
import uuid

AUDIO_OUTPUT_DIR = "data/audio"  # where generated audios will be stored

# Make sure folder exists
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

def text_to_audio(text):
    """
    Convert text to speech and save audio file.
    Returns the path to the audio file.
    """
    filename = f"{uuid.uuid4().hex}.mp3"  # unique file name
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)

    tts = gTTS(text=text, lang="en")
    tts.save(filepath)

    return filepath