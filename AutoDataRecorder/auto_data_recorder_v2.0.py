import requests
import time
import csv
import os
from datetime import datetime
from picamera2 import Picamera2
from libcamera import controls

# OctoPrint API details
API_KEY = 'E9FBFC206F274E6A8927EAD651D06753'
OCTOPRINT_URL = 'http://192.168.0.102/api/job'
PHOTO_INTERVAL = 1
gcode_lines = None

# Setup folder and file paths
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
PHOTO_DIR = f'/home/user/camera_project/{timestamp}_output/'
CSV_FILE = os.path.join(PHOTO_DIR, 'timelapse_log.csv')
os.makedirs(PHOTO_DIR, exist_ok=True)

# Initialize and configure the camera with 180-degree rotation built-in
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(
    main={"size": (4608, 2592)}, 
    buffer_count=2, 
    transform=libcamera.Transform(rotation=180)  # Rotates image by 180 degrees
))
picam2.set_controls({"ExposureTime": 2000, "AfMode": controls.AfModeEnum.Manual, "LensPosition": 10})
picam2.start()

def get_printer_status():
    """Fetch the current status of the printer."""
    try:
        response = requests.get(OCTOPRINT_URL, headers={'X-Api-Key': API_KEY})
        return response.json().get('state')
    except Exception as e:
        print(f"Error fetching printer status: {e}")
        return None

def get_current_gcode():
    """Fetch the G-code command based on the current file position."""
    global gcode_lines
    try:
        response = requests.get(OCTOPRINT_URL, headers={'X-Api-Key': API_KEY})
        data = response.json()
        file_position = data.get('progress', {}).get('filepos')
        file_path = data.get('job', {}).get('file', {}).get('path')
        
        if file_position is None or file_path is None:
            return None

        if gcode_lines is None:
            gcode_file_url = f"http://192.168.0.102/downloads/files/local/{file_path}?download=true"
            gcode_lines = requests.get(gcode_file_url, headers={'X-Api-Key': API_KEY}).text.splitlines()

        byte_count = 0
        for line in gcode_lines:
            byte_count += len(line) + 1  # +1 for newline
            if byte_count >= file_position:
                return line.strip()
    except Exception as e:
        print(f"Error fetching G-code: {e}")
    return None

def capture_photo(timestamp):
    """Capture a photo using picamera2."""
    photo_filename = os.path.join(PHOTO_DIR, f'image_{timestamp}.jpg')
    try:
        picam2.capture_file(photo_filename)  # Photo is already rotated by 180 degrees
        return photo_filename
    except Exception as e:
        print(f"Error capturing photo: {e}")
        return None

def log_to_csv(photo_location, timestamp, gcode):
    """Log photo location, timestamp, and G-code to a CSV file."""
    with open(CSV_FILE, mode='a', newline='') as file:
        csv.writer(file).writerow([photo_location, timestamp, gcode])

def start_timelapse():
    """Start the timelapse when the printer starts printing."""
    with open(CSV_FILE, mode='w', newline='') as file:
        csv.writer(file).writerow(['photo_location', 'timestamp', 'gcode'])

    while get_printer_status() == "Printing":
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        photo_location = capture_photo(timestamp)
        gcode = get_current_gcode()
        if photo_location and gcode:
            log_to_csv(photo_location, timestamp, gcode)
        time.sleep(PHOTO_INTERVAL)

def main():
    """Main function to monitor printer status and start timelapse."""
    print("Waiting for the printer to start printing...")
    while True:
        if get_printer_status() == "Printing":
            start_timelapse()
            break
        time.sleep(5)

if __name__ == '__main__':
    main()

# Stop the camera when done
picam2.stop()
print("Finished capturing photos.")
