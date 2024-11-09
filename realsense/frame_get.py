import open3d as o3d
import cv2
import numpy as np
import pyrealsense2 as rs

#检查相机
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    
