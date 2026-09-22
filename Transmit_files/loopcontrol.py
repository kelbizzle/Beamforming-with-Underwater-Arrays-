import os
import glob
import time
from pathlib import Path
import sounddevice as sd
import soundfile as sf

# Set path based on the file path I have set on the RPI
# The dir goes DSP -> python or DSP -> WAV
BASE_DIR = Path.home() / "DSP"
WAV_DIR = BASE_DIR / "WAV"
INTERVAL_SECONDS = 15 * 60  # Set to loop through the files every 15 minutes

def play_file(filepath):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Playing: {filepath.name}")
    try:
        data, fs = sf.read(filepath)
        sd.play(data, fs)
        sd.wait()  # Wait until the audio file finishes playing
    except Exception as err:
        print(f"Error playing {filepath.name}: {err}")

def run_playback_cycle():
    # Grab all .wav files sorted alphabetically
    wav_files = sorted(list(WAV_DIR.glob("*.wav")))
    
    if not wav_files:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No .wav files found in {WAV_DIR}")
        return

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting playback cycle ({len(wav_files)} files)...")
    for wav_path in wav_files:
        play_file(wav_path)
        time.sleep(10.0)  # 1-second pause between different tones
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Completed cycle.")

def main():
    print(f"Directory: {WAV_DIR}")
    print(f"Loop Interval: Every {INTERVAL_SECONDS / 60:.1f} minutes\n")

    while True:
        cycle_start = time.time()
        
        run_playback_cycle()
        
        # Calculate how much time is left in the 15-minute window
        elapsed = time.time() - cycle_start
        sleep_duration = max(0, INTERVAL_SECONDS - elapsed)
        
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Sleeping for {sleep_duration / 60:.2f} minutes until next cycle...\n")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    main()