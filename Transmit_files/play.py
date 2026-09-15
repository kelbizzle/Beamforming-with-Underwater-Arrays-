import os
import sys
import sounddevice as sd
import soundfile as sf

def play_wav_file(filename):
    """Loads and plays a .wav audio file."""
    # Ensure the file actually exists before trying to read it
    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' could not be found.")
        return

    print(f"Loading '{filename}'...")
    try:
        # soundfile automatically handles the sample rate and formatting
        data, fs = sf.read(filename)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    print(f"Playing audio ({len(data)/fs:.2f} seconds)...")
    print("Press Ctrl+C to stop playback.")
    
    try:
        # Play the audio data back-to-back
        sd.play(data, fs)
        # Block the script from exiting until the audio finishes playing
        sd.wait()
        print("Playback finished.")
    except KeyboardInterrupt:
        sd.stop()
        print("\nPlayback stopped by user.")
    except Exception as e:
        print(f"An error occurred during playback: {e}")

if __name__ == "__main__":
    print("=== Wav File Player ===\n")
    
    # Check if a filename was provided as a command-line argument: python play.py my_file.wav
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        # Otherwise, ask the user dynamically
        target_file = input("Enter the path/name of the .wav file to play: ").strip()
    
    # Quick quality-of-life fix if you forget to type the extension
    if target_file and not target_file.lower().endswith(".wav"):
        target_file += ".wav"
        
    if target_file:
        play_wav_file(target_file)
    else:
        print("No file specified. Exiting.")