import numpy as np
import matplotlib.pyplot as plt
import librosa
import os
import json
from tqdm import tqdm
import soundfile as sf
from audio_prepare import *


# === Main processing ===

if __name__ == '__main__':

    AUDIO_DIR = './audio'  # Directory containing audio files
    count = 0
    total = 0
    
    fault = 0
    
    vin_set = load_labels()
    
    qls_set = set()
    with open('qls.csv', 'r') as f:
        f.readline() # skip header
        for line in f.readlines():
            qls_set.add(line[:7])
    
    target_length = 50
    target_rate = 32000
    
    
    # target_dir = '-'.join(['./data-cnn', data_start])
    target_dir = './data-cnn-qls-all'
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    target_label = {}
           
    
    for filename in tqdm(os.listdir(AUDIO_DIR)):
        if filename.endswith('.wav'): # and data_start <= filename[18:28] <= data_end:
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
            date = filename[18:28]
            
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
            target_path = os.path.join(target_dir, filename)
            sf.write(target_path, data, rate, 'PCM_32')
            
            if vin[-7:] in qls_set:
                target_label[vin] = 1
                fault += 1
            else:
                target_label[vin] = 0
            
            count += 1
            
    
    with open(os.path.join(target_dir, 'label.json'), 'w') as f:
        json.dump(target_label, f)
    
    print(f'Total valid audio files: {count}, out of {total} checked.')
    print(f'Total fault cases: {fault}, out of {total} checked.')
