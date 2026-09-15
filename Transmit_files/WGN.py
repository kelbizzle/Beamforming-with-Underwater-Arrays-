import os
import numpy as np
from scipy.io import wavfile

def generate_wgn(duration, fs=44100):
    """
    Generates a White Gaussian Noise (WGN) signal.
    
    Parameters:
    duration (float): Length of the noise in seconds
    fs (int): Sampling rate in Hz (default: 44100)
    
    Returns:
    t (ndarray): Time array
    signal (ndarray): Generated WGN signal array
    """
    total_samples = int(fs * duration)
    
    # Generate standard normal distribution (mean=0, stdev=1)
    # np.random.randn creates perfect Gaussian noise
    signal = np.random.randn(total_samples)
    
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    return t, signal

# --- Interactive CLI Execution ---
if __name__ == "__main__":
    print("=== White Gaussian Noise Generator ===\n")
    
    # Helper to safely handle numeric input
    def get_numeric_input(prompt, cast_type=float, default=None):
        while True:
            user_input = input(prompt).strip()
            if not user_input and default is not None:
                return default
            try:
                return cast_type(user_input)
            except ValueError:
                print(f"Invalid input. Please enter a valid {cast_type.__name__}.")

    # Gather inputs
    duration = get_numeric_input("Enter noise duration in seconds [default: 2.0]: ", float, 2.0)
    sampling_rate = get_numeric_input("Enter sampling rate in Hz [default: 44100]: ", int, 44100)
    
    # Prompt for file name
    filename = input("Enter the desired filename for the .wav file [default: wgn_output.wav]: ").strip()
    if not filename:
        filename = "wgn_output.wav"
    if not filename.endswith(".wav"):
        filename += ".wav"

    print("\nGenerating White Gaussian Noise...")
    
    # Generate the signal
    time_axis, wgn_signal = generate_wgn(duration=duration, fs=sampling_rate)
    
    # Safe 16-bit PCM normalization
    # Crucial for WGN because standard deviation scaling means peaks can occasionally spike high
    if np.max(np.abs(wgn_signal)) > 0:
        normalized_signal = wgn_signal / np.max(np.abs(wgn_signal))
    else:
        normalized_signal = wgn_signal

    audio_data = np.int16(normalized_signal * 32767)
    
    # Save file
    wavfile.write(filename, sampling_rate, audio_data)
    
    print("\n=== Success! ===")
    print(f"Saved file as: {os.path.abspath(filename)}")
    print(f"Total audio duration: {time_axis[-1]:.3f} seconds")