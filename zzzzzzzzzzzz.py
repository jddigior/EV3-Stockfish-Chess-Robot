
import boardDetection
import pieceDetection
import numpy as np
import cv2 as cv


img = cv.imread("pointsInit.png",0)
copy = cv.imread("pointsInit.png")
copy2 = cv.imread("pointsInit.png")



img = boardDetection.resize(img, 1.5)
copy = boardDetection.resize(copy, 1.5)
copy2 = boardDetection.resize(copy2, 1.5)

points = boardDetection.Vmain(img,copy,copy2)


img = cv.imread("pieceInit.png",0)
img = boardDetection.resize(img,1.5)

boardDetection.display(img)
cThresh, eThresh = pieceDetection.init(img, points)

newState = pieceDetection.main(img, points, cThresh,eThresh)
print(newState)
