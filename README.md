# MudTracker3D
Accompanying code to CORE 2024 project: "MudTracket3d- Clay 3d printing extrusion monitoring and auto-calibration using Machine Learning"
Aim: To develop an auto calibration system for adjusting Layer height and Extrusion amount for WASP clay 3D printing using Machine Learning.
### Project process workflow:
![Hardware Setup]([https://github.com/Nova7397/MudTracker3D/blob/main/media/Main_Flowchart.png](https://github.com/Nova7397/MudTracker3D/blob/main/media/Main%20Workflow.png))

This github repository reflects the workflow diagram shown above categorizing the overall scripts into four sub-folders. Each folder consists of more information of process workflows within README jupyter notebooks. Each folder has requirement dependencies and installation guidelines that are required for running the scripts. 
*PLEASE NOTE THAT THE MACHINE LEARNING MODEL AND AUTO CALIBRATION LOOP IS IMPLEMENTED USING PYTHON v3.6.8*

We have also provided sample images from the dataset and processed result samples in each folder for reference. 

### Overall calibration flowchart:
Following flowchart shows our main flowchart for our current final auto-calibration tool present : 4_Machine_Learning/Auto_correction_workflow_testlines.py
![Hardware Setup](https://github.com/Nova7397/MudTracker3D/blob/main/media/Main_Flowchart.png)

### Folders: 
## 1. Data collection 
This folder contains the codes to connect the system setup with raspberry pi and the WASP printer in order to create our dataset. Following illustration shows our setup for dataset collection:

![Hardware Setup](https://github.com/Nova7397/MudTracker3D/blob/main/media/Hardware%20Setup.png)

## 1. Data collection
Data Visualization folder contains all the codes used to visualize the data into graphs for presentation
Data folder has class definitions to transform and prepare splitted dataset for machine learning
Model folder contains the Machine learning network

Files:
train_config.py contains the training settings- hyperparameters for training the model
train.py is the code to run for training the model
samples.py is to be used to predict the parameter values for a given image(testing). This uses a checkpoint saved after the model is trained.
test.py sets the seed for training and calls the classes.

Reference readmes contain the library requirements and the lisence data from 'https://github.com/cam-cambridge/caxton' - to be modified at the end based on our project.
