import cv2
import numpy as np

## This script applies to: \Rating pics\Overhang_deviaton & \Rating pics\Zigzag_straightness to calculate the maked area ##

def calculate_white_area(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Create a mask for white color (255, 255, 255)
    # This will be true where the pixel value is exactly (255, 255, 255)
    mask = cv2.inRange(image, (255, 255, 255), (255, 255, 255))

    # Calculate the area of the white regions
    area = cv2.countNonZero(mask)
    
    # Calculate the total area of the image
    total_area = image.shape[0] * image.shape[1]
    
    # Calculate the percentage area
    percentage_area = (area / total_area) * 100 if total_area > 0 else 0
    
    # Return the area in pixels and the percentage
    return area, percentage_area


# Example Usage
if __name__ == "__main__":
    image_path = "C:\\Users\\dinki\\Delft University of Technology\\Wei Wei - MSc3_CORE_Group 6\\Dataset\\Prototype V2\\Rating pics\\Area Deviation\\B2-l_raw.png"  ### Replace path ###

    # Calculate area for the specified white color
    area, percentage = calculate_white_area(image_path)
    
    print(f"Area of pure white color: {area} pixels")
    print(f"Percentage of pure white color: {percentage:.2f}%")