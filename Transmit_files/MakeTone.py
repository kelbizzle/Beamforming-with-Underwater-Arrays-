import numpy as np
import scipy.io.wavfile as wav


def generate_linear_chirp(
    start_freq, end_freq, duration, sample_rate=44100, amplitude=0.5
):

    # 1. Create the time array
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)

    # 2. Calculate the chirp rate (k)
    # This is how much the frequency needs to change per second
    k = (end_freq - start_freq) / duration

    # 3. Calculate the continuous phase
    # Integrating (f0 + k*t) yields (f0*t + 0.5*k*t^2)
    phase = 2 * np.pi * (start_freq * t + 0.5 * k * t**2)

    # 4. Generate the continuous cosine wave
    chirp_signal = amplitude * np.cos(phase)

    return t, chirp_signal

if __name__ == "__main__":

    f_start = 5000
    f_end = 5000
    secs = 10
    sr = 44100

    # Generate the audio data
    time_axis, audio_data = generate_linear_chirp(f_start, f_end, secs, sr, amplitude=0.4)

    # Convert to 16-bit PCM integers so standard media players can read it
    audio_int16 = (audio_data * 32767).astype(np.int16)

    # Save to disk
    output_filename = "Tone.wav"
    wav.write(output_filename, sr, audio_int16)

    print(f"Success! Chirp saved as '{output_filename}'")
    print(f"Swept from {f_start}Hz to {f_end}Hz over {secs} seconds.")