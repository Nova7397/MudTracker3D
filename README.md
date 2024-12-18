# MudTracker3D
[[ProjectVideo](https://youtu.be/TLkMxpruhxE)]

Accompanying code to CORE 2024 project: "MudTracket3d- Clay 3d printing extrusion monitoring and auto-calibration using Machine Learning"

Aim: To develop an auto calibration system for adjusting Layer height and Extrusion amount for WASP clay 3D printing using Machine Learning.
### Project process workflow:
![Main_Workflow](https://github.com/Nova7397/MudTracker3D/blob/main/media/Main%20Workflow.png)

This github repository reflects the workflow diagram shown above categorizing the overall scripts into five main sub-folders. Each folder consists of more information of process workflows within README jupyter notebooks. Each folder has requirement dependencies and installation guidelines that are required for running the scripts. 
*PLEASE NOTE THAT THE MACHINE LEARNING MODEL AND AUTO CALIBRATION LOOP IS IMPLEMENTED USING PYTHON v3.6.8*

We have also provided sample images from the dataset and processed result samples in each folder for reference. 

### Overall calibration flowchart:
Following flowchart shows our main flowchart for our current final auto-calibration tool present at: 4_Machine_Learning/Auto_correction_workflow_testlines.py

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

(Source: Brion. D., &amp, Pattinson, S. (2022) Generalisable 3D printing error detection and correction via multihead neural networks). We used the ‘Attention-56 network’ published by Wang et. Al (2017) in a multi head network as is used for a similar objective of classifying images into parameter qualities for FDM printing using plastics in Brion et. Al, 2022. We derive our machine learning process and aim to modify the parameters based on our clay printing parameters. 

3x ATTENTION MODULES: 
Enable the model to focus on the most relevant features within an image, enhancing its ability to capture critical details.
6x RESIDUAL BLOCKS: 
Introduce shortcuts that facilitate more efficient learning by allowing information to bypass certain layers, thereby improving model performance and convergence.
*We have not provided trained model checkpoints in the repository due to space constraints*

### Results from samples in repo:

The results for the models in this work were trained on a workstation using an Intel Core i7-13700H CPU (14 cores and 20 threads), an Nvidia GeForce RTX 4060 Laptop GPU, and 16GB of RAM on an MSI Pulse 15 B13VFK laptop.

In the top level `data` directory inside Machine learning, there are 4 cropped and full sample images of different parameter combinations for a range of prints. These are labelled `image [A B].jpg` where each of A and  B are numbers 0, 1, and 2 corresponding to low, good, and high levels respectively. Each letter is for the four different parameters: A - Layer height, B - Extrusion amount

You can test these samples with the provided script and should receive an output similar to the one below. On our system iterating through each sample individually takes around 0.07s per sample. Naturally if the batch size is increased the rate per sample can be greatly increased.

```bash 
python src/samples.py

********* CAXTON sample predictions *********
       Layer Height | Extrusion amount
*********************************************
Input: A1m_368.jpg_label_[1 1].jpg -> Prediction: [1 1]
Input: B7a_279.jpg_label_[1 2].jpg -> Prediction: [1 2]
Input: C2a_034.jpg_label_[2 1].jpg -> Prediction: [2 1]
Input: D5a_044.jpg_label_[2 2].jpg -> Prediction: [2 2]
Completed 8 predictions in 0.56s
```

## Custom slicing(Grasshopper)
Our final folder consists of grasshopper script of our custom slicer developed to slice a geometry for 3D printing clay using WASP printer.

## Media
Media folder consists of necessary documentation images.
