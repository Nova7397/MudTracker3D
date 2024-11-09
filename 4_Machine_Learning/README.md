# MudTracker3D
Clay 3d printing extrusion monitoring and auto-calibration using Machine Learning

## Setup

This repository allows you to easily train a multi-head residual attention neural network to classify the state of the four most important printing parameters: flow rate, lateral speed, Z offset, and hotend temperature from a single input image.
First create a Python 3 virtual environment and install the requirements - this should only take a couple of minutes. We used PyTorch (v1.7.1), Torchvision (v0.8.2), and CUDA (v11.3) in this work. See the complete list of requirements in `requirements.txt`.

```
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

Inside the `src` directory are two sub-directories for our `data` and `model`. We use Pytorch-Lightning (v1.1.4) as a wrapper for both the dataset and datamodule classes and for our model.
Various settings can be configured inside the `src/train_config.py` file such as the number of epochs, learning rate, number of GPUs, batch size etc. Also in this file are the pixel channel means and standard deviations used to normalise the image data during training. 
To train the network use the follow line:

```
python src/train.py
```

The command line arguments `-e` for number of epochs and `-s` for the seed can be easily added to the above command.

After training the network is able to simulatneously predict the classification of the two parameters from a single input image with an average accuracy of 98%.

**Heatmaps for parameter predictions on test samples:**
[Heatmaps](https://github.com/Nova7397/MudTracker3D/blob/main/4_Machine_Learning/diagram/prediction%20result%20for%20model%206.png)

**Preprocessed samples:**
[cropped](https://github.com/Nova7397/MudTracker3D/blob/main/4_Machine_Learning/diagram/cropped%20images%20after%20preprocessing.png)

**Visualizing attention masks of a single channel within the network:**
[masks](https://github.com/Nova7397/MudTracker3D/blob/main/4_Machine_Learning/diagram/attention%20mask%20visualization_channel%200.png)


## Calibration loop
Run the calibration loop- Auto_correction_workflow_testlines.py file after establishing required the hardware setup with the WASP clay 3D printer as shown in 'Data collection'. A pop-up will appear for selecting the initial gcode settings- then the calibration loop starts with ML label predictions until a 'good' parameter combination is reached-> the parameter settings are then saved as a csv file in a specific location. The custom slicing grasshopper script can then be run to slice the opject with the setting in the csv file and save a gcode which is then sent sent to the printer.

