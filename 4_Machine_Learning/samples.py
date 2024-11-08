import os
from model.network_module import ParametersClassifier
from PIL import Image
from train_config import *
import time

sample_data = r"C:\Users\xdin9\OneDrive - Delft University of Technology\MSc3_CORE_Group 6\Dataset\Prototype V2\cropped_testprint_lines_1_copy\outputs_03112024"
model = ParametersClassifier.load_from_checkpoint(
    checkpoint_path=r"D:\MUDTRACKER3D\MudTracker3D\4_Machine_Learning\checkpoints\01112024\1234\MHResAttNet-final_dataset_full_filteredA1&B1-01112024-epoch=27-val_loss=0.04-val_acc=0.99.ckpt",
    num_classes=3,
    gpus=1,
)
model.eval()
img_paths = [
    os.path.join(sample_data, img)
    for img in os.listdir(sample_data)
    if os.path.splitext(img)[1] == ".jpg"
]

print("********* MudTracker3D sample predictions *********")
print("Layer_height | Extrusion")
print("*********************************************")

t1 = time.time()

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

t2 = time.time()
print(f"Completed {len(img_paths)} predictions in {t2 - t1:.2f}s")
