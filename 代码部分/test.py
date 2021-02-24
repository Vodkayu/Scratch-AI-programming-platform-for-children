import cv2
from urllib.request import urlretrieve
import requests
import numpy as np

frame=np.ones((400,400),np.uint8)

bbox = cv2.selectROI('out', frame)

