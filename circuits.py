#https://circuitsgame.com/
import cv2
from PIL import ImageGrab
import numpy as np
import pytesseract
import pyautogui
from openai import OpenAI
import os
import time

#for correcting ocr readings
#keeps only alphanumerics
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
    def __init__(self, text, row, col):
        self.text = text
        self.pos = (row, col)
        self.top, self.bot, self.left, self.right = None, None, None, None
    
    def getRow(self):
        return self.pos[0]
    
    def getCol(self):
        return self.pos[1]

    def __str__(self):
        return self.displayNode()

    def displayNode(self):
        ret = (f'node text: {self.text} | ')
        if self.top != None:
            ret += f'top: {self.top.text}, '
        if self.bot != None:
            ret += f'bot: {self.bot.text}, '
        if self.left != None:
            ret += f'left: {self.left.text}, '
        if self.right != None:
            ret += f'right: {self.right.text}'
        return ret

    def getNumNeighbors(self):
        if self.text != '~':
            raise ValueError("node value is not '~'")

        count = 0
        for i in [self.top, self.bot, self.left, self.right]:
            if i != None and i.text != '~':
                count += 1
        return count
    
    def getConnections(self):
        if self.text != '~':
            raise ValueError("node value is not '~'")

        phrases = []
        for i in [self.top, self.left]: 
            if i != None and i.text != '~':
                phrases.append(f'{i.text} []')
        for i in [self.bot, self.right]: 
            if i != None and i.text != '~':
                phrases.append(f'[] {i.text}')
        # return phrases
        return ", ".join(phrases)

#virtual game board: '~' = user inputted space, [y][x] (from top left) for accessing
wordGraph = [[None, None, None, None],
             [None, None, None, None],
             [None, None, None, None],
             [None, None, None, None]]
#chatGPT api
client = OpenAI(api_key = os.environ.get("API_KEY"))

#white = contains = within range
#black = outside of range
def colorFilter(img, rgb, tolerance):
    r, g, b = rgb[0], rgb[1], rgb[2]
    lowerBound = np.array([r-tolerance, g-tolerance, b-tolerance])
    upperBound = np.array([r+tolerance, g+tolerance, b+tolerance])
    return cv2.inRange(img, lowerBound, upperBound)

def addHorizEdge(xCount, yCount):
    leftNode = wordGraph[yCount][xCount]
    rightNode = wordGraph[yCount][xCount+1]
    leftNode.right = rightNode
    rightNode.left = leftNode

def addVertEdge(xCount, yCount):
    topNode = wordGraph[yCount][xCount]
    botNode = wordGraph[yCount+1][xCount]
    topNode.bot = botNode
    botNode.top = topNode

def fillIn(node):
    initialPrompt = node.getConnections()
    boxXCoords = (BOXCOORDS[0]+node.getRow()*XSEGMENT, BOXCOORDS[0]+(node.getRow()+1)*XSEGMENT)
    boxYCoords = (BOXCOORDS[1]+node.getCol()*YSEGMENT+YADJ, BOXCOORDS[1]+(node.getCol()+1)*YSEGMENT-YADJ)
    cellSelect = (sum(boxXCoords)/2, sum(boxYCoords)/2)

    def getCompletePrompt(initial, avoidWords, beginsWith):
        prompt = initial
        if len(avoidWords) > 0:
            prompt += (f'. avoid {", ".join(f"'{word}'" for word in avoidWords)}')
        if len(beginsWith) > 0:
            prompt += (f". begins with '{beginsWith}'")
        print(f'prompt: {prompt}')
        return prompt

    def getWordList(prompt):
        completion = client.chat.completions.create(
            # model="gpt-4o-mini",
            model = "gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a puzzle-solving bot. Your task is to solve word puzzles by filling blanks with a single word that creates valid, commonly recognized phrases or compound words. Respond with a list of 10 possible 1-word answers, ordered from most to least likely, using only necessary alphanumerics."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response = completion.choices[0].message.content
        response = response.split()
        validWords = []
        for i in response:
            try:
                float(i)
            except:
                corrected = correct(i)
                if correct != '':
                    validWords.append(corrected)
        print(f'word list: {validWords}')
        return validWords

    def moveToClick(pos):
        pyautogui.moveTo(pos)
        pyautogui.click()

    def useBolt():
        raise KeyError("bolt used!")
        moveToClick(useBoltButton)
        updatedCell = ImageGrab.grab(bbox=(boxXCoords[0], boxYCoords[0], boxXCoords[1], boxYCoords[1]))
        updatedCell = np.array(updatedCell)
        starting = (correct(pytesseract.image_to_string(updatedCell)))
        print(f'bolt used: {starting}')
        return starting

    def solveAttempt(wordList):
        for word in wordList:
            moveToClick(cellSelect)
            pyautogui.write(word)
            pyautogui.press('enter')
            time.sleep(0.1)

            img = ImageGrab.grab(bbox=(boxXCoords[0], boxYCoords[0], boxXCoords[1], boxYCoords[1]))
            img = np.array(img)
            img = colorFilter(img, [226,212,4], 10)
            if len(np.where(img==[255])[0]) != 0:
                print(f'SUCCESS with {word}')
                node.text = word
                return
            else:
                print(f'FAIL with {word}')
        moveToClick(cellSelect)
        solveAttempt(getWordList(getCompletePrompt(initialPrompt, wordList, useBolt())))

    solveAttempt(getWordList(getCompletePrompt(initialPrompt, [], "")))

BOXCOORDS = [1920/2-315, 1080/2-15, 1920/2+315, 1080/2+325]
YADJ = 20   #adjusting cell view area so ocr works
XSEGMENT, YSEGMENT = (BOXCOORDS[2]-BOXCOORDS[0])/4, (BOXCOORDS[3]-BOXCOORDS[1])/4
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
numInputs = 0
useBoltButton = (776, 457)

#reading and creating cells
print("READING AND CREATING CELLS")
for yCount in range(4):
    for xCount in range(4):
        img = ImageGrab.grab(bbox=(BOXCOORDS[0]+xCount*XSEGMENT, BOXCOORDS[1]+yCount*YSEGMENT+YADJ, BOXCOORDS[0]+(xCount+1)*XSEGMENT, BOXCOORDS[1]+(yCount+1)*YSEGMENT-YADJ))
        img = np.array(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #need to convert to grayscale so that correct answers dont mess up ocr reading
        word = correct(pytesseract.image_to_string(img))
        if len(np.where(img==[0])[0]) != 0: #detecting if area has any black and thus is nonempty/a valid cell
            if word == "":
                word = "~"
                numInputs += 1
            wordGraph[yCount][xCount] = Node(word, xCount, yCount) 
        print(f'xCount:{xCount}, yCount:{yCount}: {word}')
        # cv2.imshow("", img)
        # cv2.waitKey(0)

#creating edges
connectSize = 3
#traverses horizontal edges, left to right then top to bot
print("\nCREATING HORIZONTAL EDGES")
for yCount in range(4):
    for xCount in range(3):
        img = ImageGrab.grab(bbox=(BOXCOORDS[0]+(xCount+1)*XSEGMENT-connectSize, BOXCOORDS[1]+yCount*YSEGMENT, BOXCOORDS[0]+(xCount+1)*XSEGMENT+connectSize, BOXCOORDS[1]+(yCount+1)*YSEGMENT))
        img = np.array(img)
        img = colorFilter(img, [0,0,0], 50)
        # cv2.imshow("", img)
        if len(np.where(img==[255])[0]) != 0:
            print(f'horizontal edge at xCount:{xCount}, yCount:{yCount}')
            addHorizEdge(xCount, yCount)
        else:
            print(f'nothing at xCount:{xCount}, yCount:{yCount}')
        # cv2.waitKey(0)

#traverses vertical edges, top to bot then left to right
print("\nCREATING VERTICAL EDGES")
for xCount in range(4):
    for yCount in range(3):
        img = ImageGrab.grab(bbox=(BOXCOORDS[0]+xCount*XSEGMENT, BOXCOORDS[1]+(yCount+1)*YSEGMENT-connectSize, BOXCOORDS[0]+(xCount+1)*XSEGMENT, BOXCOORDS[1]+(yCount+1)*YSEGMENT+connectSize))
        img = np.array(img)
        img = colorFilter(img, [0,0,0], 50)
        # cv2.imshow("", img)
        if len(np.where(img==[255])[0]) != 0:
            print(f'vertical edge at xCount:{xCount}, yCount:{yCount}')
            addVertEdge(xCount, yCount)
        else:
            print(f'nothing at xCount:{xCount}, yCount:{yCount}')
        # cv2.waitKey(0)

print("\nSOLVING PUZZLE")
while (numInputs > 0):
    nextTarget = Node("~", None, None) #dummy comparison node
    for row in range(len(wordGraph)):
        for col in range(len(wordGraph[row])):
            node = wordGraph[row][col]
            try:
                if node.text == '~' and node.getNumNeighbors() > nextTarget.getNumNeighbors():
                    nextTarget = node
            except:
                continue
    #api shit
    print(f'\ntarget: {nextTarget}')
    fillIn(nextTarget)
    numInputs -= 1