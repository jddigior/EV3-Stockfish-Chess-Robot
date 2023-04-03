import numpy as np
import cv2 as cv
from stockfish import Stockfish
import chess

import boardDetection
import pieceDetection
import moveProcessing



#Initialize Script
xPos, yPos, game_board = moveProcessing.JonnyInit()
instructionsPath = r"C:\Users\joedi\OneDrive - University of Waterloo\Chess Robot\Code\MoveInstructions.txt"

#Initialize chess boards
moveProcessing.chessInit()

#Initialize board states
oldState = moveProcessing.startBoard
newState = moveProcessing.startBoard

#Board detect
cam = cv.VideoCapture(0)
while True:
    ret, frame = cam.read()
    cv.imshow("frame",frame)
    key = cv.waitKey(1)
    if key%256 == 27 : #escape hit
            break
    elif key%256 == 32 : #space hit
        imgName = "pointsInit.png"
        frame = boardDetection.resize(frame,1.5)
        cv.imwrite(imgName, frame)
        img = cv.imread(imgName, 0)
        boardDetection.display(img)
        break
copy = cv.imread(imgName)  
copy2 = cv.imread(imgName)
points = boardDetection.Vmain(img,copy,copy2)

#Get colour of human player
clr = 1
colour = input('What color are you (b/w): ')
if colour == "b":
     clr = -1

while True:
    ret, frame = cam.read()
    cv.imshow("frame",frame)
    key = cv.waitKey(1)
    if key%256 == 27 : #escape hit
            break
    elif key%256 == 32 : #space hit
        imgName = "pieceInit.png"
        frame = boardDetection.resize(frame,1.5)
        cv.imwrite(imgName, frame)
        img = cv.imread(imgName, 0)
        cThresh, eThresh = pieceDetection.init(img,points)
        break
print("Game starting")
eThresh *= 0.85
imgCounter = 1
firstMove = True

while True:
    
   #When signaled to take new picture, do so
   while True :
        if firstMove == True and clr == -1: #break if stockfish is making first move
             break
        ret, frame = cam.read()
        cv.imshow("frame",frame)
        key = cv.waitKey(1)
        if key%256 == 27 : #escape hit
            break
        elif key%256 == 32 : #space hit
            imgName = "img{}.png".format(imgCounter)
            imgCounter += 1
            frame = boardDetection.resize(frame,1.5)
            cv.imwrite(imgName, frame)
            img = cv.imread(imgName, 0)
            boardDetection.display(img)
            break
   if firstMove == True and clr == -1 :
        hMove = None
        firstMove = False
        
        
   else :
        #Get board state from img   
        newState = pieceDetection.main(img,points,cThresh,eThresh)
        newState = np.transpose(newState)
        print(newState)

        #Get human move from board states   
        hMove = moveProcessing.humanMove(oldState, newState, clr)
        print("Human move: " + hMove)

   #Get fish move and move type, update board states
   oldState, fMove = moveProcessing.main(hMove, oldState, newState)
   print("Stockfish move: " + fMove)

   #Jonny code: Get human move, send file, push moves
   moveProcessing.JonnyMain(fMove, xPos, yPos, game_board, instructionsPath)
     #Uncomment download script later
     
   #Check if game ends
   if moveProcessing.isGameOver() :
        break