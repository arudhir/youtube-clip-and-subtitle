#!/usr/bin/env python
import argparse
import os
import subprocess
from datetime import datetime, timedelta

def get_video_id(youtube_url):
    # Extracts the video ID from the YouTube URL.
    import re
    match = re.search(r'v=([^&#]+)', youtube_url)
    return match.group(1) if match else None

def download_video(youtube_url, output_path):
    # Downloads the best quality video using yt-dlp.
    subprocess.run(["yt-dlp", "-f", "bestvideo[ext=webm]+bestaudio[ext=webm]/best[ext=webm]", "--merge-output-format", "webm", "-o", output_path, youtube_url], check=True)

def trim_video(input_path, start_time, end_time, output_path):
    # Trims the video between the specified start and end times using ffmpeg.
    subprocess.run(["ffmpeg", "-i", input_path, "-ss", start_time, "-to", end_time, "-c", "copy", output_path], check=True)

def transcribe_video(input_path, srt_path):
    # Transcribes the video in English and generates SRT subtitles using Whisper.
    subprocess.run(["whisper", input_path, "--output_format", "srt", "--language", "en"], stdout=open(srt_path, 'w'), check=True)

def burn_subtitles(input_path, subtitle_path, output_path):
    # Burns the subtitles into the video.
    subprocess.run([
        "ffmpeg",
        "-i", input_path,
        "-vf", f"subtitles='{subtitle_path}'",
        "-c:a", "copy",
        output_path
    ], check=True)

def main():
    parser = argparse.ArgumentParser(description="Download, trim, transcribe, and hard-burn subtitles into a YouTube video.")
    parser.add_argument("--youtube-url", required=True, help="YouTube video URL")
    parser.add_argument("--start-time", required=True, help="Start time in HH:MM:SS format")
    parser.add_argument("--end-time", required=True, help="End time in HH:MM:SS format")
    parser.add_argument("--custom-name", help="Custom name for the output directory and files")
    parser.add_argument("--offset", type=int, default=0, help="Time offset in seconds for subtitle adjustment")

    args = parser.parse_args()

    video_id = get_video_id(args.youtube_url)
    base_name = args.custom_name if args.custom_name else video_id
    output_dir = f"{base_name}_output"
    os.makedirs(output_dir, exist_ok=True)

    original_video_path = os.path.join(output_dir, f"{video_id}.webm")
    trimmed_video_path = os.path.join(output_dir, f"{base_name}_trimmed.webm")
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    # adjusted_srt_path = os.path.join(output_dir, f"{base_name}_adjusted.srt")
    final_video_path = os.path.join(output_dir, f"{base_name}_final.webm")

    print("Downloading video...")
    download_video(args.youtube_url, original_video_path)

    print("Trimming video...")
    trim_video(original_video_path, args.start_time, args.end_time, trimmed_video_path)

    print("Transcribing video...")
    transcribe_video(trimmed_video_path, srt_path)

    # Placeholder for the burn_subtitles function call; implement burning subtitles as needed.
    print("Burning subtitles into video...")
    burn_subtitles(trimmed_video_path, srt_path, final_video_path)


    print(f"Process complete. Final video with subtitles is located at {final_video_path}")

if __name__ == "__main__":
    main()

