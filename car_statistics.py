import os
from collections import defaultdict
from datetime import datetime

# Path to the directory containing the .wav files
AUDIO_DIR = './audio'

# Dictionary to hold lists of file sizes per day
sizes_per_day = defaultdict(list)

for filename in os.listdir(AUDIO_DIR):
    if filename.endswith('.wav'):
        try:
            parts = filename.rstrip('.wav').split('-')
            if len(parts) >= 6:
                date_str = '-'.join(parts[1:4])  # Extract YYYY-MM-DD
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                filepath = os.path.join(AUDIO_DIR, filename)
                size_bytes = os.path.getsize(filepath)
                size_mb = size_bytes / (1024 * 1024)
                sizes_per_day[date].append(size_mb)
        except Exception as e:
            print(f'Skipping file due to error: {filename} ({e})')

# Print results
print(f'{"Date":<12} {"Count":<6} {"Avg Size (MB)":>15} {"Min (MB)":>10} {"Max (MB)":>10}')
print('-' * 60)
for date in sorted(sizes_per_day):
    sizes = sizes_per_day[date]
    count = len(sizes)
    avg_size = sum(sizes) / count
    min_size = min(sizes)
    max_size = max(sizes)
    print(f'{date} {count:<6} {avg_size:15.2f} {min_size:10.2f} {max_size:10.2f}')


import json
from collections import Counter

# Load your JSON string (replace this with loading from file if needed)

# Parse the JSON string
with open('label.json', 'r') as f:
    data = json.load(f)

# Extract the relevant dictionary
records = data['_default']

# Count statuses
status_counter = Counter(entry['status'] for entry in records.values())

# Print counts for statuses 0 to 3

states = ['normal', 'squeak', 'rattle', 's&r']

for i in range(4):
    print(f'{states[i]}: {status_counter.get(i, 0)}')
