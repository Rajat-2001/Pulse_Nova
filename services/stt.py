from faster_whisper import WhisperModel
import tempfile
import subprocess
import os

model = WhisperModel("large-v2")

def audio_to_text(audio_file):
    # ✅ Save uploaded file with original extension
    filename = getattr(audio_file, 'filename', 'audio.webm') or 'audio.webm'
    suffix = os.path.splitext(filename)[-1] or '.webm'
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
        temp_audio.write(audio_file.file.read())
        temp_path = temp_audio.name

    # ✅ Always convert to WAV 16kHz mono — what Whisper likes
    wav_path = temp_path.replace(suffix, '.wav')
    result = subprocess.run([
        'ffmpeg', '-y',        # overwrite if exists
        '-i', temp_path,       # input file
        '-ar', '16000',        # 16kHz sample rate
        '-ac', '1',            # mono
        '-c:a', 'pcm_s16le',   # proper WAV encoding
        wav_path
    ], capture_output=True, text=True)

    # ✅ Debug — print ffmpeg output if something goes wrong
    if result.returncode != 0:
        print(f"❌ ffmpeg error: {result.stderr}")
        return "Sorry, I couldn't process that audio file."

    print(f"✅ Audio converted to WAV: {wav_path}")

    # ✅ Transcribe the converted WAV
    segments, info = model.transcribe(wav_path)
    text = " ".join([segment.text for segment in segments])

    # Cleanup temp files
    os.unlink(temp_path)
    os.unlink(wav_path)

    print(f"✅ Transcribed: {text}")
    return text if text.strip() else "Sorry, I couldn't understand the audio."