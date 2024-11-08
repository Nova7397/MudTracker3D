import os
import time
from PIL import Image, ImageEnhance

# Function to crop and resize images using the center point as the crop center
def crop_and_resize_images(input_folder, output_folder, target_resolution=(1280, 720), center_point=(2291, 1039)):
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
                # BRIGHTNESS (if you want to enhance brightness)
                # brightness_factor = 1.7
                # enhancer = ImageEnhance.Brightness(img)
                # img = enhancer.enhance(brightness_factor)

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
                resized_img = cropped_img.resize(target_resolution, Image.Resampling.LANCZOS)

                # Save the processed image to the output folder
                resized_img.save(output_file_path)

                print(f"Processed and saved: {filename}")

# Function to continuously monitor the folder and process images every 20 seconds
def process_images_periodically(input_folder, output_folder, target_resolution=(1280, 720), center_point=(2291, 1039)):
    while True:
        # Check how many images are in the input folder
        image_count = len([f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))])
        
        if image_count >= 15:
            # Process the images if there are at least 15 in the folder
            crop_and_resize_images(input_folder, output_folder, target_resolution, center_point)
        
        # Wait for 20 seconds before checking the folder again
        time.sleep(20)

# Define input and output folder paths and the center point
input_folder = r'C:\Users\Swornava\Delft University of Technology\Wei Wei - MSc3_CORE_Group 2\Test_print\test_print_photo\Image_detection' #Input folder path
output_folder = r'C:\Users\Swornava\Delft University of Technology\Wei Wei - MSc3_CORE_Group 2\Test_print\test_print_photo\Image_for_preprocess'  # Output folder path
center_point = (1136, 739)  # x, y center point in pixels

# Start the periodic processing of images
process_images_periodically(input_folder, output_folder, target_resolution=(1280, 720), center_point=center_point)
