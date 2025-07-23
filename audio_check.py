import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
import os
import json
from tqdm import tqdm


def load_audio(path):
    data, rate = sf.read(path)
    return rate, data  # Keep stereo if present


def get_duration(rate, data):
    duration = len(data) / rate
    return duration


def peak_normalize(data):
    if data.ndim == 1:
        peak = np.max(np.abs(data))
        return data / peak if peak != 0 else data
    else:
        peak = np.max(np.abs(data))
        return data / peak if peak != 0 else data


def check_zero_sequences(data, min_length=100):
    if data.ndim == 1:
        channels = [data]
    else:
        channels = [data[:, 0], data[:, 1]]

    for ch in channels:
        zero_mask = (ch == 0)
        if not zero_mask.any():
            continue
        zero_run = np.diff(np.where(np.concatenate(([zero_mask[0]],
                                                    zero_mask[:-1] != zero_mask[1:],
                                                    [True])))[0])[::2]
        if any(run >= min_length for run in zero_run):
            return False
    return True


def apply_fft(data, rate):
    if data.ndim == 1:
        channels = [data]
    else:
        channels = [data[:, 0], data[:, 1]]

    for idx, ch in enumerate(channels):
        n = len(ch)
        fft_result = np.fft.fft(ch)
        freq = np.fft.fftfreq(n, d=1 / rate)
        magnitude = np.abs(fft_result)

        plt.plot(freq[:n // 2], magnitude[:n // 2], label=f'Channel {idx + 1}')

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('FFT Spectrum')
    plt.grid()
    plt.legend()
    plt.show()


def load_labels(label_path='label.json'):
    with open(label_path, 'r') as f:
        data = json.load(f)
        vin_set = {entry['vin']:entry['status'] for entry in data['_default'].values()}
        return vin_set


# === Main processing ===

AUDIO_DIR = './audio'  # Directory containing audio files
count = 0
total = 0
vin_set = load_labels()

DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    
for filename in tqdm(os.listdir(AUDIO_DIR)):
    if filename.endswith('.wav'):
        total += 1
        path = os.path.join(AUDIO_DIR, filename)

        try:
            rate, data = load_audio(path)
        except Exception as e:
            print(f'Skipping file due to error when loading: {filename} ({e})')
            continue

        vin = filename[:17]
        duration = get_duration(rate, data)
        if duration < 50:
            print(f'Skipping {filename} due to short duration ({duration:.2f}s)')
            continue

        data = peak_normalize(data)

        if not check_zero_sequences(data):
            print(f'Skipping {filename} due to long zero sequence')
            continue

        # Uncomment this to visualize FFT:
        # apply_fft(data, rate)

        if vin not in vin_set:
            print(f'Skipping {filename} due to missing VIN in labels')
            continue
        
        status = vin_set[vin]

        filename = os.path.join(DATA_DIR, f'{status}-{vin}.npy')
        np.save(filename, data)
        # print(f'Saved processed audio to {filename}')
        count += 1

print(f'Total valid audio files: {count}, out of {total} checked.')
