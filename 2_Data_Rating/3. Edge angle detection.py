import cv2
import numpy as np
import math
import os

## This script applies to: \Rating pics\Overhang_angle ##

# Path to the image
image_path = r"C:\Users\dinki\Desktop\TU BK BT\2Y-1Q\CORE\MudTracker3D\Rating pics\B1.1\B1.1_overhang_modified.jpg" ###change location

# Check if the file exists
if not os.path.isfile(image_path):
    print(f"Error: Unable to load image at path: {image_path}")
else:
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if image is None:
        print("Error: Image could not be loaded. Check the file format and path.")
    else:
        # Display the original image for verification
        cv2.imshow("Original Image", image)
        cv2.waitKey(0)

        # Resize the input image to reduce size before processing
        input_scale_factor = 1.0  # Adjust this value as needed
        image_resized = cv2.resize(image, (0, 0), fx=input_scale_factor, fy=input_scale_factor)

        # Ensure the image is binary (white line on black background)
        # Since the line is white on a black background, we do not need to invert.
        binary_image = image_resized  # Use directly as binary image

        # Show the binary image for debugging
        cv2.imshow("Binary Image", binary_image)
        cv2.waitKey(0)

        # Use a copy of the binary image to draw detected lines
        output_image = cv2.cvtColor(binary_image, cv2.COLOR_GRAY2BGR)

        # Detect lines using the Hough Line Transform
        distance_resolution = 1  # Pixel resolution for the accumulator (1 pixel)
        angle_resolution = np.pi / 180  # Angle resolution in radians (1 degree)
        threshold = 40  # Minimum votes to detect a line; adjust as needed

        lines = cv2.HoughLines(binary_image, distance_resolution, angle_resolution, threshold)

        # Check how many lines were detected
        if lines is not None:
            print(f"Detected lines: {len(lines)}")
        else:
            print("No lines detected.")

        # Function to filter out redundant lines based on angle tolerance
        def filter_lines(lines, angle_tolerance=5.0):
            filtered_lines = []
            angles = []

            if lines is not None:
                for rho, theta in lines[:, 0]:
                    angle = math.degrees(theta)
                    if angle > 90:
                        angle = angle - 180  # Normalize angles to range -90 to +90

                    # Check if this line's angle is close to any already added line's angle
                    if not any(abs(angle - existing_angle) < angle_tolerance for existing_angle in angles):
                        filtered_lines.append((rho, theta, angle))
                        angles.append(angle)

            return filtered_lines

        # Filter lines to reduce multiple angle readings
        filtered_lines = filter_lines(lines)

        # Draw the filtered lines and display their angles
        for rho, theta, angle in filtered_lines:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))

            # Draw the line in red on the output image
            cv2.line(output_image, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # Display the angle of the line in green text with + or - sign
            angle_text = f"{angle:+.2f}°"

            # Determine the midpoint for the angle text and apply boundary checks
            text_x = max(10, min(int((x1 + x2) / 2), output_image.shape[1] - 50))
            text_y = max(20, min(int((y1 + y2) / 2), output_image.shape[0] - 10))

            # Add angle text near the line
            cv2.putText(output_image, angle_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Display the image with detected lines
        cv2.imshow("Detected Lines with Angles", output_image)
        cv2.waitKey(0)  # Wait for a key press to close the window
        cv2.destroyAllWindows()