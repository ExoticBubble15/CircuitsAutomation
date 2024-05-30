import cv2
from PIL import ImageGrab, Image
import numpy as np
import pytesseract
import time

# xlength, ylength = 1920, 1080
# xoffset, yoffsettop, yoffsetbot = 315, 15, 325
BOXCOORDS = [1920/2-315, 1080/2-15, 1920/2+315, 1080/2+325]
XSEGMENT, YSEGMENT = (BOXCOORDS[2]-BOXCOORDS[0])/4, (BOXCOORDS[3]-BOXCOORDS[1])/4
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

for ycount in range(4):
    for xcount in range(4):
    # img = ImageGrab.grab(bbox=(xlength/2-xoffset, ylength/2-yoffsettop, xlength/2+xoffset, ylength/2+yoffsetbot))
    # img = ImageGrab.grab(bbox=(BOXCOORDS[0], BOXCOORDS[1], BOXCOORDS[2], BOXCOORDS[3]))
        img = ImageGrab.grab(bbox=(BOXCOORDS[0]+xcount*XSEGMENT, BOXCOORDS[1]+ycount*YSEGMENT, BOXCOORDS[0]+(xcount+1)*XSEGMENT, BOXCOORDS[1]+(ycount+1)*YSEGMENT))
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow("", img)
        cv2.waitKey(0)
