import time
from pylsl import StreamOutlet, StreamInfo
import numpy as np


fs = 512
n_channels = 16
chunk_rate = 16

# Setup
stream_name = 'RDS'
outlet_info = StreamInfo(stream_name, 'EEG', n_channels, fs, 'float32', 'RDS01')
outlet = StreamOutlet(outlet_info)

# Go
while True:
    data = np.random.uniform(-1000, 1000, size=(int(fs/chunk_rate), n_channels))
    outlet.push_chunk(data)
    time.sleep(1/chunk_rate)
    print('.', end='', flush=True)