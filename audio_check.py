import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os
import json


def load_audio(path):
    data, rate = sf.read(path)
    if data.ndim > 1:
        data = data.mean(axis=1)  # Convert to mono
    return rate, data

def get_duration(rate, data):
    duration = len(data) / rate
    # print(f'Audio duration: {duration:.2f} seconds')
    return duration

def peak_normalize(data):
    peak = np.max(np.abs(data))
    if peak == 0:
        print('Audio is silent.')
        return data
    normalized = data / peak
    # print(f'Peak normalization applied. Max amplitude: {np.max(np.abs(normalized)):.3f}')
    return normalized

def check_zero_sequences(data, min_length=100):
    zero_mask = (data == 0)
    zero_run = np.diff(np.where(np.concatenate(([zero_mask[0]],
                                                zero_mask[:-1] != zero_mask[1:],
                                                [True])))[0])[::2]
    if any(run >= min_length for run in zero_run):
        return False
    else:
        return True

def apply_fft(data, rate):
    n = len(data)
    fft_result = np.fft.fft(data)
    freq = np.fft.fftfreq(n, d=1/rate)
    magnitude = np.abs(fft_result)

    plt.plot(freq[:n//2], magnitude[:n//2])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('FFT Spectrum')
    plt.grid()
    plt.show()
    
def load_labels():
    with open('label.json', 'r') as f:
        data = json.load(f)
        # Extract VINs into a set
        vin_set = {entry['vin'] for entry in data['_default'].values()}
        # Print the VINs
        return vin_set
    return {}



AUDIO_DIR = './audio'  # Directory containing audio files
count = 0
total = 0
vin_set = load_labels()

for filename in os.listdir(AUDIO_DIR):
    if filename.endswith('.wav'):
        total += 1
        try:
            # Load audio file
            rate, data = load_audio(os.path.join(AUDIO_DIR, filename))
        except Exception as e:
            print(f'Skipping file due to error when loading: {filename} ({e})')
            continue
        vin = filename[:17]
        duration = get_duration(rate, data)
        if duration < 50:
            print(f'Skipping {filename} due to short duration, duration: {duration:.2f} seconds')
            continue
        data = peak_normalize(data)
        if not check_zero_sequences(data):
            print(f'Skipping {filename} due to long zero sequence')
            continue
        # apply_fft(data, rate)
        if vin not in vin_set:
            print(f'Skipping {filename} due to missing VIN in labels')
            continue
        count += 1

print(f'Total valid audio files: {count}, out of {total} checked.')
