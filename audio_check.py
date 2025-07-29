import numpy as np
import matplotlib.pyplot as plt
import librosa
import os
import json
from tqdm import tqdm
import soundfile as sf


def load_audio(path):
    data, rate = librosa.load(path)
    data = librosa.to_mono(data)  # Convert to mono if stereo
    return rate, data  # Keep stereo if present


def get_duration(rate, data):
    duration = len(data) / rate
    return duration

# def crop_audio(rate, data):
#     start = 0
#     end = len(data)
#     duration = len(data) // rate + 1
#     mask = [False] * (duration)
#     for i in range(0, duration):
#         y = (data[i*rate:min((i + 1)*rate,len(data))] > 0.01).sum()
#         if y > 4000:
#             mask[i] = True
#             # print(i, ':', y)
            
#     # print('mask', mask)
    
#     for i in range(0, duration - 10):
#         if all(mask[i:i + 10]):
#             start = i * rate
#             break
    
#     for i in range(0, duration - 10):
#         if all(mask[duration - i - 10:duration - i]):
#             # print('end', i)
#             end = (duration - i) * rate
#             break
    
#     # print('----------------')
#     # print(start/rate, end/rate)
    
#     return data[start:end] if end > start else data

def crop_audio(rate, data, window=50, method='max'):
    duration = len(data) // rate
    data = data[:duration * rate]
    
    max_window = 0
    position = 0
    
    if method == 'max':
        # max
        prefix = np.zeros(duration + 1)
        for i in range(0, duration):
            prefix[i + 1] = np.abs(data[i*rate: (i + 1)*rate]).max() + prefix[i]
            
        for i in range(0, duration - window + 1):
            this_window = prefix[i + window] - prefix[i]
            if this_window > max_window:
                max_window = this_window
                position = i
        # print('position:', position)
        
    elif method == 'rms':    
        # rms
        prefix = np.zeros(duration + 1)
        for i in range(0, duration):
            prefix[i + 1] = np.sqrt(np.mean(data[i*rate: (i + 1)*rate] ** 2)) + prefix[i]
            
        for i in range(0, duration - window + 1):
            this_window = prefix[i + window] - prefix[i]
            if this_window > max_window:
                max_window = this_window
                position = i
        # print('position:', position)
    else:
        raise ValueError("Method must be 'max' or 'rms'")
    
    return data[position * rate:(position + window) * rate]

def peak_normalize(data):
    peak = np.max(np.abs(data))
    return data / peak if peak != 0 else data


# def check_zero_sequences(data, min_length=100):
#     if data.ndim == 1:
#         channels = [data]
#     else:
#         channels = [data[:, 0], data[:, 1]]

#     for ch in channels:
#         zero_mask = (ch == 0)
#         if not zero_mask.any():
#             continue
#         zero_run = np.diff(np.where(np.concatenate(([zero_mask[0]],
#                                                     zero_mask[:-1] != zero_mask[1:],
#                                                     [True])))[0])[::2]
#         if any(run >= min_length for run in zero_run):
#             return False
#     return True


# def apply_fft(data, rate):
#     if data.ndim == 1:
#         channels = [data]
#     else:
#         channels = [data[:, 0], data[:, 1]]

#     for idx, ch in enumerate(channels):
#         n = len(ch)
#         fft_result = np.fft.fft(ch)
#         freq = np.fft.fftfreq(n, d=1 / rate)
#         magnitude = np.abs(fft_result)

#         plt.plot(freq[:n // 2], magnitude[:n // 2], label=f'Channel {idx + 1}')

#     plt.xlabel('Frequency (Hz)')
#     plt.ylabel('Magnitude')
#     plt.title('FFT Spectrum')
#     plt.grid()
#     plt.legend()
#     plt.show()


def load_labels(label_path='label.json'):
    with open(label_path, 'r') as f:
        data = json.load(f)
        vin_set = {entry['vin']:entry['status'] for entry in data['_default'].values()}
        return vin_set


# === Main processing ===

if __name__ == '__main__':

    AUDIO_DIR = './audio'  # Directory containing audio files
    count = 0
    total = 0
    vin_set = load_labels()
    
    target_length = 50
    target_rate = 22050
    target_dir = './data'
    
    target_label = {}
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    for filename in tqdm(os.listdir(AUDIO_DIR)):
        if filename.endswith('.wav'):
            total += 1
            path = os.path.join(AUDIO_DIR, filename)

            # load audio file
            try:
                rate, data = load_audio(path)
            except Exception as e:
                print(f'Skipping file due to error when loading: {filename} ({e})')
                continue

            # check VIN
            vin = filename[:17]
            if vin not in vin_set:
                print(f'Skipping {filename} due to unknown VIN: {vin}')
                continue
            
            # check duration
            duration = get_duration(rate, data)
            if duration < 50:
                print(f'Skipping {filename} due to short duration ({duration:.2f}s)')
                continue
            
            # downsample if necessary
            if rate != target_rate:
                data = librosa.resample(data, orig_sr=rate, target_sr=target_rate)
                rate = target_rate
                
            # crop audio
            data = crop_audio(rate, data, window=50, method='rms')
            
            # normalize audio
            data = peak_normalize(data)
            
            # save processed audio
            target_path = os.path.join(target_dir, vin + '.wav')
            sf.write(target_path, data, rate, 'PCM_32')
            
            target_label[vin] = vin_set[vin]
            
    with open(os.path.join(target_dir, 'label.json'), 'w') as f:
        json.dump(target_label, f, indent=4)
    print(f'Total valid audio files: {count}, out of {total} checked.')
