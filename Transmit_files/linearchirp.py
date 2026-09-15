import numpy as np
import scipy.io.wavfile as wav


def generate_linear_chirp(start_freq, end_freq, duration, sample_rate=44100, amplitude=0.4):

    # Create the time array
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # Calculate the chirp rate (k)
    k = (end_freq - start_freq) / duration

    # Calculate the continuous phase
    phase = 2 * np.pi * (start_freq * t + 0.5 * k * t**2)

    # Generate the continuous cosine wave
    chirp_signal = amplitude * np.cos(phase)

    return t, chirp_signal


if __name__ == "__main__":

    try:
        # Get inputs for chirp
        f_start = float(input("Enter starting frequency (Hz): "))
        f_end = float(input("Enter ending frequency (Hz): "))
        secs = float(input("Enter duration (seconds): "))
        sr = 44100

        # Get the output filename
        output_filename = input("Enter output filename (e.g., my_chirp): ").strip()

        # Default name (if not given)
        if not output_filename:
            output_filename = "chirp"

        # Automatically append .wav if it's missing
        if not output_filename.endswith(".wav"):
            output_filename += ".wav"

        # Generate the audio data
        time_axis, audio_data = generate_linear_chirp(f_start, f_end, secs, sr, amplitude=0.4)

        # Convert to 16-bit PCM integers
        audio_int16 = (audio_data * 32767).astype(np.int16)

        # Save to disk
        wav.write(output_filename, sr, audio_int16)

        print(f"\nSuccess! Chirp saved as '{output_filename}'")
        print(f"Swept from {f_start} Hz to {f_end} Hz over {secs} seconds.")

    except ValueError:
        print("\nError: Please enter valid numbers for frequencies and duration.")