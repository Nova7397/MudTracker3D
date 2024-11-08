import re
import os
import csv

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

    if layer_height_class == 2 and extrusion_class == 2:
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
        csv_output_path = os.path.join(folder_csv, csv_filename)
    
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

    else:
        # Return an error if no valid file is found
        print("Error: No valid input filename found based on the given criteria.")
        return None

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


# Example usage:
current_filename = 'LH0.9_E0.5.gcode'  # Current G-code
folder = r'C:\Users\Swornava\Delft University of Technology\Wei Wei - MSc3_CORE_Group 2\Dataset\G-code\test print\NEW\append testing'  # Folder containing G-code files
folder_csv = r'C:\Users\Swornava\Delft University of Technology\Wei Wei - MSc3_CORE_Group 2\Test_print\test_print_photo\final_csv_for_slicing' 
output_folder = r'C:\Users\Swornava\Delft University of Technology\Wei Wei - MSc3_CORE_Group 2\Test_print\next_gcode'  # Output folder
u_value = 1  # Value for Y calculation
layer_height_class = 2  # Specify layer height class
extrusion_class = 2  # Specify extrusion class

modify_gcode(current_filename, folder, output_folder, u_value, layer_height_class, extrusion_class)