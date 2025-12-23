from moviepy.video.io.VideoFileClip import VideoFileClip
from services.audio_service import audio_to_text
import subprocess 
import ffmpeg

def video_to_text(video_path):
    audio_path = extract_audio(video_path)
    return audio_to_text(audio_path)


def extract_audio(video_path, audio_path="audio.wav"):
    (
        ffmpeg
        .input(video_path)
        .output(audio_path, ac=1, ar="16k")
        .overwrite_output()
        .run(quiet=True)
    )
    return audio_path
