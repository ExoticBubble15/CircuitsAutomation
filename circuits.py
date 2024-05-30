import cv2
from PIL import ImageGrab
import numpy as np
import pytesseract

#for correcting ocr readings
VALID = "1234567890qwertyuiopasdfghjklzxcvbnm"
def correct(str):
    str = str.lower()
    ret = ""
    for i in range(len(str)):
        if VALID.find(str[i]) != -1:
            ret += str[i]
    return ret

#node class for representing cells
class Node:
    def __init__(self, text):
        self.text = text
        self.top, self.bot, self.left, self.right = None, None, None, None

    def setTop(self, top):
            self.top = top

    def setBot(self, bot):
            self.bot = bot

    def setLeft(self, left):
            self.left = left

    def setRight(self, right):
            self.right = right

wordGraph = [["","","",""], ["","","",""], ["","","",""], ["","","",""]]    #creates virtual game board: '~' denotes user inputted space, [y][x] for accessing
def display(prefix, arr):
    print(f'\n{prefix}')
    for i in range(len(arr)):
        print(arr[i])

BOXCOORDS = [1920/2-315, 1080/2-15, 1920/2+315, 1080/2+325]
YADJ = 20   #adjusting cell view area so ocr works
XSEGMENT, YSEGMENT = (BOXCOORDS[2]-BOXCOORDS[0])/4, (BOXCOORDS[3]-BOXCOORDS[1])/4
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#first iteration to create cells
for yCount in range(4):
    for xCount in range(4):
        img = ImageGrab.grab(bbox=(BOXCOORDS[0]+xCount*XSEGMENT, BOXCOORDS[1]+yCount*YSEGMENT+YADJ, BOXCOORDS[0]+(xCount+1)*XSEGMENT, BOXCOORDS[1]+(yCount+1)*YSEGMENT-YADJ))
        img = np.array(img)
        word = correct(pytesseract.image_to_string(img))
        if len(np.where(img==[0])[0]) != 0: #detecting if area has any black and thus is nonempty
            if word == "":
                word = "~"
            wordGraph[yCount][xCount] = word#Node(word)
        print(f'{xCount}, {yCount}: {word}')
        # cv2.imshow("", img)
        # cv2.waitKey(250)

display("word graph", wordGraph)
# print(wordGraph[0][1].text)

#second iteration to create edges
for yCount in range(4):
    for xCount in range(4):