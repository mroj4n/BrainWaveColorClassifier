"""
Script to record EEG data for a given image.
An image is displayed in full screen and EEG data is recorded while the image is visible.
EEG data is pulled from OpenBCI GUI using LSL.
Time Series Flt from OpenBCI Gui was used with this script
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
import cv2
import os

# Constants
IMAGE_TO_SHOW = "images\\green.png"
DATA_DIR = "..//Dataset//data" # Directory to store the recorded data
WARM_UP_TIME = 30  # Duration to warm up the EEG device in seconds
SAMPLING_RATE = 200
TIME_TO_SHOW = 600 #seconds

# Resolve an EEG stream
# Use LSL dumbass
print("Looking for an EEG stream...")
streams = resolve_stream('type', 'EEG')
inlet = StreamInlet(streams[0])

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Function to record EEG data for a given image
def record_data_for_image(image_path):
    # Extract base name for subdirectory
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    subdir_name = f"{image_name}_brainWaves"  # Subdirectory name for storing data
    subdir_path = os.path.join(DATA_DIR, subdir_name)
    if not os.path.exists(subdir_path):
        os.makedirs(subdir_path)

    # Load and display the image in full screen
    cv2.namedWindow('Image', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Image', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    print(f"Showing image {image_path}")
    image = cv2.imread(image_path)
    if image is None:
        raise Exception(f"Could not load image {image_path}")
    cv2.imshow('Image', image)
    cv2.waitKey(1)  # Necessary for the image to be displayed

    # Warm-up: Read EEG data, Without this, the first few seconds of EEG data are usually noisy
    warm_up_time = time.time()
    while time.time() - warm_up_time < WARM_UP_TIME:
        inlet.pull_sample()

    # Record EEG data while the image is visible
    start_time = time.time()
    eeg_data = []
    eeg_timestamps = []
    # while (time.time() - start_time < TIME_TO_SHOW): # used earlier, decided to use sampling rate instead
    while (len(eeg_data) < TIME_TO_SHOW * SAMPLING_RATE):
        sample, timestamp = inlet.pull_sample()
        eeg_data.append(sample)
        eeg_timestamps.append(timestamp)
        
    if len(eeg_data) > TIME_TO_SHOW * SAMPLING_RATE:
       eeg_data = eeg_data[:TIME_TO_SHOW * SAMPLING_RATE]
       eeg_timestamps = eeg_timestamps[:TIME_TO_SHOW * SAMPLING_RATE]

    # Save the EEG data
    data_file_path = os.path.join(subdir_path, f"{int(time.time())}.npy")
    timestamps_file_path = data_file_path + "_timestamps.npy"
    np.save(data_file_path, np.array(eeg_data))
    np.save(timestamps_file_path, np.array(eeg_timestamps))
    print(f"Data saved to {data_file_path}")

    # Close the image window
    cv2.destroyAllWindows()


record_data_for_image(IMAGE_TO_SHOW)