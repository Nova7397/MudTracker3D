import requests
import time
import csv
from datetime import datetime
from picamera2 import Picamera2
from libcamera import controls
from PIL import Image
import libcamera

# OctoPrint API details
API_KEY = 'E9FBFC206F274E6A8927EAD651D06753'
OCTOPRINT_URL = 'http://192.168.0.102/api/job'
GCODE_URL = 'http://192.168.0.102/api/files/local/'  # Endpoint to retrieve the G-code file

from datetime import datetime 
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

import os

# Define the path where you want to create the folder
folder_path = "path/to/new/folder"
gcode_content = None
gcode_lines = None

PHOTO_DIR = f'/home/user/camera_project/{timestamp}_output/'
CSV_FILE = f'/home/user/camera_project/{timestamp}_output/timelapse_log.csv'


# Create the folder
try:
    os.makedirs(PHOTO_DIR)
    print(f"Folder '{PHOTO_DIR}' created successfully.")
except FileExistsError:
    print(f"Folder '{PHOTO_DIR}' already exists.")
# File paths

# Initialize the camera
picam2 = Picamera2()

# Configure the camera for still image capture

still_config = picam2.create_still_configuration(
    main={"size": (4608, 2592)}, # scale down the image, but maintain the full field of view
    raw={'size': (4608, 2592)},
    buffer_count=2,
    transform=libcamera.Transform(rotation=180)
    # controls={'FrameRate': 50},
)
picam2.configure(still_config)

# Set manual shutter speed and let the camera adjust the ISO automatically
# Shutter speed is in microseconds (e.g., 20000 microseconds = 1/50 sec)
# ISO is shown as AnalogueGain (e.g., Gain 2.0 is approximately ISO 200, Gain 4.0 = ISO 400)
picam2.set_controls({"ExposureTime": 2000}) 

# Start the camera
picam2.start()

# Set the focus lens position to minimum (0.0 is the minimum, 1.0 is the maximum)
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 10})

# Interval for taking photos (in seconds)
PHOTO_INTERVAL = 1

def get_printer_status():
    """Get the current status of the printer (e.g., Printing, Paused, etc.)."""
    headers = {'X-Api-Key': API_KEY}
    try:
        response = requests.get(OCTOPRINT_URL, headers=headers)
        data = response.json()
        return data['state']
    except Exception as e:
        print(f"Error fetching printer status: {e}")
        return None

def get_current_gcode():
    """Fetch the current G-code being executed based on the file position."""
    headers = {'X-Api-Key': API_KEY}
    global gcode_lines
    global gcode_content

    try:
        # Send a request to get job data from the OctoPrint API
        response = requests.get(OCTOPRINT_URL, headers=headers)
        data = response.json()  # Parse the response as JSON
        
        # Debug: Print the full API response
        # print(f"get_current_gcode API Response: {data}")
        
        # Get file position and file path from the response
        file_position = data.get('progress', {}).get('filepos', None)
        file_path = data.get('job', {}).get('file', {}).get('path', None)
        
        if file_position is None or file_path is None:
            print(f"File position or path missing: file_position={file_position}, file_path={file_path}")
            return None
        
        if(gcode_lines == None):
            # Construct the URL to access the raw G-code file
            gcode_file_url = f"http://192.168.0.102/downloads/files/local/{file_path}?download=true"

            # Debug: Print G-code file URL
            print(f"Raw G-code File URL: {gcode_file_url}")
            
            # Get the raw G-code file content
            gcode_response = requests.get(gcode_file_url, headers=headers)
            gcode_content = gcode_response.text
            
            # Debug: Print the first 500 characters of the G-code file for verification
            # print(f"Raw G-code File Content (first 500 chars):\n{gcode_content[:500]}")

            # Find the G-code command at the current file position
            gcode_lines = gcode_content.splitlines()
        
        # print(gcode_lines)
        newline_before = gcode_content.rfind('\n', 0, file_position) 
        #Search from the start to the index
        #Find the new line after the given index
        newline_after = gcode_content.find('\n', 0, file_position) 
        #Search from the index to the end of the string
        new_gcode = gcode_content[newline_before + 1 : newline_after]
        print(new_gcode)
        
        # print(gcode_lines)
        byte_count = 0
        for line in gcode_lines:
            byte_count += len(line) + 1  # +1 for newline character
            if byte_count >= file_position:
                current_gcode = line.strip()
                break
        
        # Debug: Print the found G-code
        print(f"Current G-code: {current_gcode}")
        return current_gcode
    
    except Exception as e:
        print(f"Error fetching current G-code: {e}")
        return None
    
    print(f"API Response: {data}")

def capture_photo(timestamp):
    """Capture a photo using picamera2 and save it with a timestamp."""
    photo_filename = f'{PHOTO_DIR}image_{timestamp}.jpg'
    try:
        picam2.capture_file(photo_filename)
        return photo_filename
    except Exception as e:
        print(f"Error capturing photo: {e}")
        return None

def log_to_csv(photo_location, timestamp, gcode):
    """Log photo location, timestamp, and G-code to a CSV file."""
    print(f"Logging to CSV: {photo_location}, {timestamp}, {gcode}")  # Debugging line
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([photo_location, timestamp, gcode])

def start_timelapse():
    """Start the timelapse when the printer starts printing."""
    print("Starting timelapse...")

    # Open CSV file and write header if necessary
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['photo_location', 'timestamp', 'gcode'])

    while True:
        printer_status = get_printer_status()

        if printer_status == "Printing":
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            photo_location = capture_photo(timestamp)
            rotate_image_180(photo_location)
            gcode = get_current_gcode()

            if photo_location and gcode:
                log_to_csv(photo_location, timestamp, gcode)

            time.sleep(PHOTO_INTERVAL)  # Wait for the next photo
        elif printer_status != "Printing" and printer_status != "Paused":
            print("Printing finished or stopped.")
            break

        time.sleep(1)  # Check printer status every second

def rotate_image_180(file_path):
    with Image.open(file_path) as img:
    # Rotate the image by 180 degrees
        rotated_img = img.rotate(0)
    # Save the rotated image (optional, if you want to save it)
    rotated_img.save(file_path)

def main():
    """Main function to monitor printer status and trigger timelapse."""
    print("Waiting for the printer to start printing...")

    while True:
        status = get_printer_status()

        if status == "Printing":
            start_timelapse()

        time.sleep(5)  # Check printer status every 5 seconds


    
if __name__ == '__main__':
    main()

# Stop the camera when the program ends
picam2.stop()
print("Finished capturing photos.")


