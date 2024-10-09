# MudTracker3D
Error detection and real-time tracking of additive manufacturing process using clay
test changes

Folders: 
Data collection folder contains the codes to connect the system setup with raspberry pi and the WASP printer in order to create our dataset
Data Visualization folder contains all the codes used to visualize the data into graphs for presentation
Data folder has class definitions to transform and prepare splitted dataset for machine learning
Model folder contains the Machine learning network

Files:
train_config.py contains the training settings- hyperparameters for training the model
train.py is the code to run for training the model
samples.py is to be used to predict the parameter values for a given image(testing). This uses a checkpoint saved after the model is trained.
test.py sets the seed for training and calls the classes.
