import numpy as np
import wave

volume = 0.5  # range [0.0, 1.0]
fs = 48000  # sampling rate, Hz
duration = 120.0  # duration in seconds
f = 200.0  # sine frequency, Hz

# Generate samples, note conversion to float32 array
samples = (np.sin(2 * np.pi * np.arange(fs * duration) * f / fs)).astype(np.float32)

# Scale the samples by volume and convert to 16-bit PCM for saving as .wav
scaled_samples = (volume * samples * 2147483647).astype(np.int32)

# Duplicate samples for both left and right channels
stereo_samples = np.column_stack((scaled_samples, scaled_samples))

# Save to a .wav file
filename = 'sine.wav'
with wave.open(filename, 'wb') as wav_file:
    wav_file.setnchannels(2)  # Set to 2 channels for stereo
    wav_file.setsampwidth(4)  # 4 bytes for 32-bit PCM
    wav_file.setframerate(fs)
    wav_file.writeframes(stereo_samples.tobytes())

print(f'Stereo sine wave file saved successfully as {filename}')
