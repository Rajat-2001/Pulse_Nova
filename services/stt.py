# services/stt.py
from faster_whisper import WhisperModel  # using faster-whisper for STT
import tempfile

# Initialize model (you can change size as needed)
model = WhisperModel("large-v2")  # or "medium-v2" for smaller

def audio_to_text(audio_file):
    """
    Convert uploaded audio file to text.
    audio_file: UploadFile from FastAPI
    """
    # Save the uploaded audio to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(audio_file.file.read())
        temp_path = temp_audio.name

    # Transcribe using Faster-Whisper
    segments, info = model.transcribe(temp_path)
    text = " ".join([segment.text for segment in segments])

    return text