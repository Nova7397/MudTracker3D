import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import os

## This script applies to: \Rating pics\Raw_file ##

def callback(input):
    pass

def cannyEdge():
    root = os.getcwd()
    imgPath = os.path.join(root,r'\Rating pics\Raw_file\A1.4\A1.4_overhang.jpg') ### change location 
    img = cv.imread(imgPath)
    img = cv.cvtColor(img,cv.COLOR_BGR2RGB)

    height,width,_ = img.shape
    scale = 1/5
    heightscale = int(height*scale)
    widthscale = int(width*scale)
    img = cv.resize(img,(widthscale,heightscale),interpolation=cv.INTER_LINEAR)

    winname = 'canny'
    cv.namedWindow(winname)
    cv.createTrackbar('minThres',winname,0,255,callback)
    cv.createTrackbar('maxThres',winname,0,255,callback)

    while True:  

        minThres = cv.getTrackbarPos('minThres',winname)
        maxThres = cv.getTrackbarPos('maxThres',winname)
        
        edges = cv.Canny(img, minThres, maxThres)
        
        cv.imshow(winname, edges)

        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            save_path = os.path.join(rrot, 'canny_edge_output.jpg')
            cv.imwrite(save_path, edges)
            print(f"Image saved as: {save_path}")


    cv.destroyAllWindows()


if __name__ == '__main__':
    cannyEdge()