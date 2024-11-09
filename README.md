# MudTracker3D
Accompanying code to CORE 2024 project: "MudTracket3d- Clay 3d printing extrusion monitoring and auto-calibration using Machine Learning"
Aim: To develop an auto calibration system for adjusting Layer height and Extrusion amount for WASP clay 3D printing using Machine Learning.
### Project process workflow:
![Main_Workflow](https://github.com/Nova7397/MudTracker3D/blob/main/media/Main%20Workflow.png)

This github repository reflects the workflow diagram shown above categorizing the overall scripts into four sub-folders. Each folder consists of more information of process workflows within README jupyter notebooks. Each folder has requirement dependencies and installation guidelines that are required for running the scripts. 
*PLEASE NOTE THAT THE MACHINE LEARNING MODEL AND AUTO CALIBRATION LOOP IS IMPLEMENTED USING PYTHON v3.6.8*

We have also provided sample images from the dataset and processed result samples in each folder for reference. 

### Overall calibration flowchart:
Following flowchart shows our main flowchart for our current final auto-calibration tool present : 4_Machine_Learning/Auto_correction_workflow_testlines.py

![Main Flowchart](https://github.com/Nova7397/MudTracker3D/blob/main/media/Main_Flowchart.png)

### Folders: 
## 1. Data collection 
This folder contains the codes to connect the system setup with raspberry pi and the WASP printer in order to create our dataset. Following illustration shows our setup for dataset collection:

![Hardware Setup](https://github.com/Nova7397/MudTracker3D/blob/main/media/Hardware%20Setup.png)

## 2. Data Rating
This folder contains all the scripts used for objective assessment using elevation images of printed specimens. Sample images and description is provided within the folder. This Rating collectively for each specimen is used to identify parameter labels for our Final dataset. Visualization of rating parameters can also be found in this folder.

## 3. Data Preparation
This folder contains a jupyter notebook with a set of code blocks that are in order and with descriptions to be followed to modify the raw dataset(s) into a single labelled final filtered dataset. Some sample raw images, processed images and csv files have been provided in the folder for reference. 
The distribution of dataset labels visualization can be found in the folder.
The final dataset csv used for the ML model is also provided here.

## 4. Machine Learning
This folder for scripts using which we trained our Machine Learning model, and our main auto-calibration loop python file. 
We use Attention 56 Network model for multi head classification task for our clay 3D printing parameter adjustments of layer height and extrusion amount. We implement a similar workflow from 'https://github.com/cam-cambridge/caxton' for FDM Printing using Plastic. All scripts in this folder have been implemented using Python v3.6.8. Kindly follow the readme instructions carefully for executing the scripts.

### Attention 56 Network model:
![MLmodel](https://github.com/Nova7397/MudTracker3D/blob/main/media/ML%20model.png)

## Custom slicing(Grasshopper)
Our final folder consists of grasshopper script of our custom slicer developed to slice a geometry for 3D printing clay using WASP printer.

## Media
Media folder consists of necessary documentation images/videos.
