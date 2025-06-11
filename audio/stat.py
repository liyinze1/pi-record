import os
from collections import defaultdict
from datetime import datetime

# Path to the directory containing the .wav files
AUDIO_DIR = './'  # Replace with actual path

# Dictionary to store counts per day
counts_per_day = defaultdict(int)

for filename in os.listdir(AUDIO_DIR):
    if filename.endswith('.wav'):
        try:
            # Extract the timestamp part: YYYY-MM-DD-HH-MM-SS
            parts = filename.rstrip('.wav').split('-')
            if len(parts) >= 6:
                date_str = '-'.join(parts[1:4])  # ['2024', '12', '11'] -> '2024-12-11'
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                counts_per_day[date] += 1
        except Exception as e:
            print(f'Skipping file due to error: {filename} ({e})')

# Print the results
for date in sorted(counts_per_day):
    print(f'{date}: {counts_per_day[date]} audio files')
