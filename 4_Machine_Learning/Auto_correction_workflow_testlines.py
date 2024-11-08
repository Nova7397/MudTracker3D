# This code is used for close loop auto-correction workflow, test with line printing

import os
import time
import re
import torch
import numpy as np
import pandas as pd
from PIL import Image
from datetime import datetime
from scipy import stats
from model.network_module import ParametersClassifier
from data.data_module_wholeworkflow import ParametersDataModule
from train_config import preprocess
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import paramiko
import requests
from scp import SCPClient
import threading
import sys
import re
import csv

########### Rasperry pi taking image ##############

# Create SSH client
def create_ssh_client(server, user, password):
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(server, username=user, password=password)
    return ssh_client

# Function to clear images from the Raspberry Pi directory
def clear_raspberry_pi_images():
    global ssh
    if ssh:
        try:
            # Delete all files in raspberry_pi_image_dir
            ssh.exec_command(f'rm -rf {raspberry_pi_image_dir}/*')
            print("All images in Raspberry Pi directory deleted.")
        except Exception as e:
            print(f"Failed to clear images: {e}")

# Transfer images from Raspberry Pi to the laptop
def transfer_images():
    scp.get(raspberry_pi_image_dir, download_dir, recursive=True)
    print("Images transferred successfully.")

# Start and stop timelapse functions
def start_timelapse():
    global ssh
    if ssh:
        try:
            print("Starting timelapse capture on Raspberry Pi...")
            stdin, stdout, stderr = ssh.exec_command(f'python3 {timelapse_script} &')
            print("Timelapse started.")
        except Exception as e:
            print(f"Failed to start timelapse: {e}")

def stop_timelapse():
    ssh.exec_command("pkill -f take_timelapse.py")

# Upload and start printing the G-code
def upload_gcode(gcode_file_path, gcode_filename):
    with open(gcode_file_path, 'rb') as file:
        headers = {'X-Api-Key': api_key}
        files = {'file': (gcode_filename, file, 'application/octet-stream')}
        response = requests.post(octoprint_url + "files/local", headers=headers, files=files)
        return response.status_code == 201

def start_print(gcode_filename):
    headers = {'X-Api-Key': api_key, 'Content-Type': 'application/json'}
    data = {"command": "select", "print": True}
    response = requests.post(octoprint_url + f"files/local/{gcode_filename}", headers=headers, json=data)
    return response.status_code == 204

def get_printer_status():
    headers = {'X-Api-Key': api_key}
    response = requests.get(octoprint_url + "job", headers=headers)
    return response.json().get("state")

# Function to clear next_gcode_folder
def clear_next_gcode_folder():
    for file in os.listdir(next_gcode_folder):
        file_path = os.path.join(next_gcode_folder, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
            print(f"Deleted {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

# execute_print_workflow
def execute_print_workflow(gcode_file_path, gcode_filename):
    global ssh, scp, timelapse_running
    # Clear Raspberry Pi images before starting the print
    clear_raspberry_pi_images()
    time.sleep(10) #
    print("clear raspberry_pi_image 2s time sleep over")

    # Upload G-code and start print
    if upload_gcode(gcode_file_path, gcode_filename) and start_print(gcode_filename):
        print(f"Printing '{gcode_filename}' started.")
        
        # Delete next_gcode file in the folder
        clear_next_gcode_folder()

        # Wait for 10 seconds before starting the timelapse
        time.sleep(10)
        print("clear next gcode 10s time sleep over")
        # Start timelapse
        ssh = create_ssh_client(raspberry_pi_ip, raspberry_pi_user, raspberry_pi_password)
        scp = SCPClient(ssh.get_transport())
        start_timelapse()
        timelapse_running = True
        
        # Monitor printing status
        while True:
            status = get_printer_status()
            print(f"Current printer status: {status}")
            if status in ["Finishing"]:
                stop_timelapse()
                timelapse_running = False
                transfer_images()
                break
            time.sleep(1)
    print("execute_print_workflow over")

# GUI for G-code selection
def select_gcode():
    selected_file = gcode_var.get()
    if selected_file:
        gcode_file_path = os.path.join(gcode_folder, selected_file)
        execute_print_workflow(gcode_file_path, selected_file)
    else:
        messagebox.showwarning("Selection Error", "Please select a G-code file.")

def execute_gcode():

    current_files = {f for f in os.listdir(next_gcode_folder) if f.endswith('.gcode')}
    print(str(current_files))
    for gcode_file in current_files:
        gcode_file_path = os.path.join(next_gcode_folder, gcode_file)
        execute_print_workflow(gcode_file_path, gcode_file)


######## Delete empty print images ###########

def delete_images(input_folder):
    while True:
        # Get the list of image files in the input folder
        image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        # Check if there are more than 14 images
        if len(image_files) >= 12: #12
            # Sort the files numerically based on their names
            image_files.sort(key=lambda x: int(os.path.splitext(x)[0]))  # Extract numeric part for sorting

            # Delete the first 2 images
            for img in image_files[:2]:
                os.remove(os.path.join(input_folder, img))
                print(f"Deleted: {img}")

            # Delete the last 2 images
            for img in image_files[-2:]:
                os.remove(os.path.join(input_folder, img))
                print(f"Deleted: {img}")

            break  # Exit the loop after deleting images
        
        

#######PRECROPPED IMAGE ############

# Function to crop and resize images using the center point as the crop center
def crop_and_resize_images(input_folder, output_folder, target_resolution=(1280, 720), center_point=(1166, 720)):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate over all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            # Open the image
            with Image.open(input_file_path) as img:
                # Original resolution
                width, height = img.size

                # Define the cropping box around the center point (x, y)
                target_width, target_height = target_resolution

                # Calculate the left, top, right, and bottom based on the center point
                left = center_point[0] - target_width // 2
                top = center_point[1] - target_height // 2
                right = center_point[0] + target_width // 2
                bottom = center_point[1] + target_height // 2

                # Ensure the crop box stays within the image boundaries
                if left < 0:
                    left = 0
                    right = target_width
                if right > width:
                    right = width
                    left = width - target_width
                if top < 0:
                    top = 0
                    bottom = target_height
                if bottom > height:
                    bottom = height
                    top = height - target_height

                # Crop the image
                cropped_img = img.crop((left, top, right, bottom))

                # Resize the cropped image to the target resolution
                resized_img = cropped_img.resize(target_resolution, Image.LANCZOS)

                # Save the processed image to the output folder
                resized_img.save(output_file_path)

                print(f"Processed and saved: {filename}")

# Function to monitor the folder and process images once the number reaches 8
def process_images_when_ready(input_folder, output_folder, target_resolution=(1280, 720), center_point=(1166, 720)):
    
    while True:

     # Check the number of images in the input folder
     image_count = len([f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
    
     if image_count >= 8:
        # Process the images if there are at least 8 in the folder
         print(f"Found {image_count} images. Starting the processing...")
         crop_and_resize_images(input_folder, output_folder, target_resolution, center_point)
         break
        
     
####### PREPROCESS IMAGE ############

def make_dirs(path):
    try:
        os.makedirs(path)
    except:
        pass

# Custom function to visualize and save images
def visualize_batch(batch, df, save_dir, dataset_std, dataset_mean):
    images, labels = batch
    batch_size = len(images)

    # Adjust image paths according to the total dataset, not just the batch
    image_filenames = df['img_path'].values[:len(images)]

    for i, (img, label) in enumerate(zip(images, labels)):
        print(f"Processing image {i+1}/{batch_size}")
        img = img.permute(1, 2, 0)  # Permute to (H, W, C) format for plotting
        img = img * torch.tensor(dataset_std) + torch.tensor(dataset_mean)  # Denormalize
        img = img.clamp(0, 1)

        # Convert to numpy for saving
        img_np = img.numpy()

        # Save each image individually
        output_filename = os.path.basename(image_filenames[i])
        output_path = os.path.join(save_dir, f"{output_filename}")

        plt.imsave(output_path, img_np)
        print(f"Saved image: {output_path}")


# Function to delete all files in the output folder
def delete_files_in_folder(folder_path):
    try:
        # Loop through the files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Check if it's a file and then delete it
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted {file_path}")
        print("All files in the folder have been deleted.")
    except Exception as e:
        print(f"Error occurred while deleting files: {e}")



################# Predict labels ####################
# this part goes in the loop directly

#########Decision on next Gcode ###############


def get_lh_and_e_values(filename):
    """Extracts LH (layer height) and E (extrusion rate) values from a filename."""
    match = re.search(r'LH(\d+\.\d+)_E(\d+\.\d+)', filename)
    if match:
        lh_value = float(match.group(1))
        e_value = float(match.group(2))
        return lh_value, e_value
    return None, None

def choose_input_filename(filenames, current_filename, layer_height_class, extrusion_class):
    """Chooses the appropriate input filename based on the provided class values."""
    current_lh, current_e = get_lh_and_e_values(current_filename)
    
    # Parse LH and E values from all filenames
    parsed_files = [(f, *get_lh_and_e_values(f)) for f in filenames if get_lh_and_e_values(f) is not None]
    
    # Sort parsed files based on LH and E values
    parsed_files = sorted(parsed_files, key=lambda x: (x[1], x[2]))  # Sort by LH and then by E
    
    # Filtering based on conditions
    valid_files = []

    if layer_height_class == 0:
        if extrusion_class == 0:
            # Choose next file with LH > current LH and E > current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh > current_lh and e > current_e]
        elif extrusion_class == 1:
            # Choose next file with LH > current LH and E = current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh > current_lh and e == current_e]
        elif extrusion_class == 2:
            # Choose previous file with LH > current LH and E < current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh > current_lh and e < current_e]
    
    elif layer_height_class == 1:
        if extrusion_class == 0:
            # Choose next file with LH = current LH and E > current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh == current_lh and e > current_e]
        elif extrusion_class == 2:
            # Choose previous file with LH = current LH and E < current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh == current_lh and e < current_e]
    
    elif layer_height_class == 2:
        if extrusion_class == 0:
            # Choose previous file with LH < current LH and E > current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh < current_lh and e > current_e]
            
        elif extrusion_class == 1:
            # Choose file with LH < current LH and E = current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh < current_lh and e == current_e]
            
        elif extrusion_class == 2:
            # Choose file with LH < current LH and E < current E
            valid_files = [(f, lh, e) for f, lh, e in parsed_files if lh < current_lh and e < current_e]

    if not valid_files:
        # Return an error if no valid file is found
        print("No valid input filename found based on the given criteria. Saving CSV with last parameter...")
        # Define the CSV output path
        csv_filename = current_filename.replace('.gcode', '.csv')  # Change .gcode to .csv
        csv_output_path = os.path.join(csv_folder, csv_filename)
    
        # Write the CSV file
        with open(csv_output_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header
            csvwriter.writerow(['layer_height', 'extrusion'])
            # Write the current values
            csvwriter.writerow([current_lh, current_e])
    
        print(f"CSV file has been saved to {csv_output_path}.")
        return None
    
    elif layer_height_class == 2 and extrusion_class == 2:
        # Return the last match when both layer_height_class and extrusion_class are 2
        return valid_files[-1][0]
    
    elif layer_height_class == 2 and extrusion_class == 1:
        # Return the first match for other cases
        return valid_files[-1][0]
    
    elif layer_height_class == 2 and extrusion_class == 0:
        # Return the first match for other cases
        return valid_files[-1][0]
    
    elif layer_height_class == 1 and extrusion_class == 1:
        # Define the CSV output path
        csv_filename = current_filename.replace('.gcode', '.csv')  # Change .gcode to .csv
        csv_output_path = os.path.join(csv_folder, csv_filename)
    
        # Write the CSV file
        with open(csv_output_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header
            csvwriter.writerow(['layer_height', 'extrusion'])
            # Write the current values
            csvwriter.writerow([current_lh, current_e])
    
        print(f"CSV file has been saved to {csv_output_path}.")
    
    elif layer_height_class == 1 and extrusion_class == 0:
        # Return the first match for other cases
        return valid_files[0][0]
    
    elif layer_height_class == 1 and extrusion_class == 2:
        # Return the first match for other cases
        return valid_files[-1][0]    
    
    elif layer_height_class == 0 and extrusion_class == 1:
        # Return the first match for other cases
        return valid_files[0][0] 
    
    elif layer_height_class == 0 and extrusion_class == 0:
        # Return the first match for other cases
        return valid_files[0][0] 
    
    elif layer_height_class == 0 and extrusion_class == 2:
        # Return the first match for other cases
        return valid_files[0][0] 


def modify_gcode(current_filename, folder, output_folder, u_value, layer_height_class, extrusion_class):
    # Get all filenames in the folder
    filenames = [f for f in os.listdir(folder) if re.match(r'LH\d+\.\d+_E\d+\.\d+', f)]
    
    # Determine the input filename based on the given classes
    input_filename = choose_input_filename(filenames, current_filename, layer_height_class, extrusion_class)
    
    if input_filename is None:
        return
    
    # Full path to the input file
    input_filepath = os.path.join(folder, input_filename)
    
    # Define the output filename as the same as input filename but in the new output folder
    output_filename = os.path.join(output_folder, input_filename)
    
    # Read the original G-code file
    with open(input_filepath, 'r') as file:
        gcode_lines = file.readlines()

    # Define the pattern to search for the Y value with the dynamic u factor
    pattern = r'(Y-110\+20\*u)'

    # Prepare an empty list to store the modified lines
    modified_lines = []

    # Loop through each line in the original G-code
    for line in gcode_lines:
        # Search for the pattern Y-110+20*u in the current line
        match = re.search(pattern, line)
        if match:
            # Calculate the new Y value based on the provided u value
            y_value = -110 + 20 * u_value
            # Replace the pattern with the actual calculated Y value
            new_line = re.sub(pattern, f'Y{y_value}', line)
            modified_lines.append(new_line)
        else:
            # If the pattern is not found, keep the original line
            modified_lines.append(line)

    # Write the modified G-code to a new file
    with open(output_filename, 'w') as file:
        file.writelines(modified_lines)

    print(f"Modified G-code has been saved to {output_filename}.")


################### call function from taking images ##################

# Set OctoPrint API details
octoprint_url = 'http://192.168.0.102/api/' #
api_key = 'E9FBFC206F274E6A8927EAD651D06753' #
gcode_folder = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\initial_gcode"
next_gcode_folder = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\next_gcode"
download_dir = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\test_print_photo"
csv_folder = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\test_print_photo\final_csv_for_slicing"

# SSH details for the Raspberry Pi
raspberry_pi_ip = "192.168.0.120" #
raspberry_pi_user = "user" #
raspberry_pi_password = "toi'sLAMA" #
timelapse_script = "/home/user/camera_project/take_timelapse.py" 
raspberry_pi_image_dir = "/home/user/Image_detection"

# Global variables
ssh = None
scp = None

# GUI setup
root = tk.Tk()
root.title("Select G-code File")
gcode_files = [f for f in os.listdir(gcode_folder) if f.endswith('.gcode')]
gcode_var = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=gcode_var, values=gcode_files)
dropdown.pack(pady=10)
dropdown.set("Select a G-code file")
select_button = tk.Button(root, text="Confirm", command=select_gcode)
select_button.pack(pady=10)

root.mainloop()



###### call function from preprocessing data ##############
def monitor_and_process():
    input_folder = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\test_print_photo\Image_detection"
    output_folder = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\test_print_photo\Image_for_preprocess"
    folder = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Dataset\G-code\test print\NEW\append testing"
    output_filename = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\next_gcode"  # Output folder

    DATA_DIR = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Test_print\test_print_photo"
    BATCH_SIZE = 8 #8
    DATASET_NAME = "dataset_full"
    DATA_CSV = os.path.join(DATA_DIR, "test_print.csv")
    DATASET_MEAN = [0.2915257, 0.27048784, 0.14393276]
    DATASET_STD = [0.066747, 0.06885352, 0.07679665]

    # Initial G-code filename
    current_filename = 'LH1.2_E0.5.gcode'
    u_value = 2

    model = ParametersClassifier.load_from_checkpoint(
        checkpoint_path=r"D:\MUDTRACKER3D\MudTracker3D\4_Machine_Learning\checkpoints\21102024\1234\MHResAttNet-dataset_full-21102024-epoch=48-val_loss=0.08-val_acc=0.98.ckpt",
        num_classes=3,
        gpus=1,
    )
    model.eval()

    
  


    while True:
        # Step 1: Monitor and delete images if over 12 exist
        while True:
            image_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
            if len(image_files) >= 12:  #12
                image_files.sort(key=lambda x: int(os.path.splitext(x)[0]))
                for img in image_files[:2] + image_files[-2:]:
                    os.remove(os.path.join(input_folder, img))
                    print(f"Deleted: {img}")
                break

        # Step 2: Crop and resize images
        process_images_when_ready(input_folder, output_folder, target_resolution=(1280, 720), center_point=(1166, 720))

        # PREPROCESS IMAGE


        DATE = datetime.now().strftime("%d%m%Y")
        print(f"DATA_DIR: {DATA_DIR}")


        # Initialize the data module
        data_module = ParametersDataModule(
            batch_size=BATCH_SIZE,
            data_dir=DATA_DIR,
            csv_file=DATA_CSV,
            dataset_name=DATASET_NAME,
            mean=DATASET_MEAN,
            std=DATASET_STD,
            load_saved=False,
            transform=True
        )


        # Load the CSV file and check paths
        df = pd.read_csv(DATA_CSV)

        # Define the output directory for saving the visualizations
        OUTPUT_DIR = os.path.join(DATA_DIR, f"image_for_prediction_{DATE}")
        make_dirs(OUTPUT_DIR)


        data_module.setup(stage="test", save=False, test_all=True)
        
        test_dataloader = data_module.test_dataloader()

        # Process each batch in the data loader to ensure all images are processed
        for batch_idx, batch in enumerate(test_dataloader):
            print(f"Processing batch {batch_idx + 1}")
            visualize_batch(batch, df, OUTPUT_DIR, DATASET_STD, DATASET_MEAN)

        print("All images processed.")

        img_paths = [
            os.path.join(OUTPUT_DIR, img)
            for img in os.listdir(OUTPUT_DIR)
            if os.path.splitext(img)[1] == ".jpg"
        ]

        # Step 3: Preprocess and predict labels
        print("********* MudTracker3D sample predictions *********")
        print("Layer_height | Extrusion")
        print("*********************************************")
        layer_height_preds = []
        extrusion_preds = []
       

        for img_path in img_paths:
            pil_img = Image.open(img_path)
            x = preprocess(pil_img).unsqueeze(0)
            y_hats = model(x)
            y_hat0, y_hat1 = y_hats

            _, preds0 = torch.max(y_hat0, 1)
            _, preds1 = torch.max(y_hat1, 1)
            preds = torch.stack((preds0, preds1)).squeeze()

    
            preds_str = str(preds.numpy())
            img_basename = os.path.basename(img_path)
            print("Input:", img_basename, "->", "Prediction:", preds_str)
         # Collect predictions
            layer_height_preds.extend(preds0.numpy())
            extrusion_preds.extend(preds1.numpy())

        final_layer_height_label = stats.mode(layer_height_preds)[0][0]
        final_extrusion_label = stats.mode(extrusion_preds)[0][0]

        print(f"Layer Height: {final_layer_height_label}, Extrusion: {final_extrusion_label}")

        # Call the function to delete files
        delete_files_in_folder(output_folder)

        # Step 4: Modify G-code
        modify_gcode(current_filename, folder, output_filename, u_value, layer_height_class=final_layer_height_label, extrusion_class=final_extrusion_label)
        u_value = u_value + 2 

       
        # Update current_filename to be the output G-code for the next loop iteration
        file_names = os.listdir(output_filename)
        current_filename = str(file_names)
        print(str(file_names))
        delete_files_in_folder(input_folder)

        print("********* next round *********")

        
        # Step 5: Break if condition (1, 1) is met
        if final_layer_height_label == 1 and final_extrusion_label == 1:
            print("Terminating loop as G-code state reached (1, 1)")
            break

         # Run monitor function in a separate thread
        monitor_thread = threading.Thread(target=execute_gcode, daemon=True)
        monitor_thread.start()



if __name__ == "__main__":
    monitor_and_process()


