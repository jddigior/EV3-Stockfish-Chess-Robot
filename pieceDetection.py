import numpy as np
import cv2 as cv

import boardDetection

def init(img, points):
    """
    Input starting image and points array \n
    Finds average pixel weight and edge amounts  \n
    Returns thresholds for colours and nonzeros to be used in main   
    """
    img = boardDetection.gBlur(img,7)
    edges = boardDetection.gBlur(img,5)
    edges = cv.Canny(img,40,70)

    Cblack = np.zeros((8,2),dtype = np.int32)
    Cwhite = np.zeros((8,2),dtype = np.int32)
    minEdges = 60
    maxEmpt = 10

    for i in range(8):
        for j in range(8):
            x1 = points[i][j][0] +10
            x2 = points[i+1][j+1][0] -10 
            y1 = points[i][j][1] +10
            y2 = points[i+1][j+1][1] -10
            
            square = edges[y1:y2,x1:x2]
            sqaure = img[y1+5:y2-5,x1+5:x2-5]

            if j < 2 :
                Cwhite[i][j] = np.average(sqaure)
                if len(np.nonzero(square)[0]) < minEdges :
                    minEdges = len(np.nonzero(square)[0])
            elif j > 5 :
                Cblack[i][j-6] = np.average(sqaure)
                if len(np.nonzero(square)[0]) < minEdges :
                        minEdges = len(np.nonzero(square)[0])
                
            else :
                if len(np.nonzero(square)[0]) > maxEmpt :
                    maxEmpt = len(np.nonzero(square)[0])


    whiteAvg = np.average(Cwhite)
    blackAvg = np.average(Cblack)

    cThreshold = int(0.5*(whiteAvg+blackAvg))
    eThreshold = int(0.5*(maxEmpt + minEdges))

    return cThreshold, eThreshold


def main(img,points,cThresh,eThresh):
    """
    Input full grayscale image of board, points array, colour thresh, and edge thresh \n
    Blurs, edge detects, and loops through each square to find non-empties \n
    Checks colours of non-empty squares by in unaltered grayscale image \n
    Returns a board state array
    """
    newState = np.zeros((8,8), dtype = np.byte)

    img = boardDetection.gBlur(img,7)
    #edges = boardDetection.mBlur(img,3)
    edges = boardDetection.gBlur(img,5)
    edges = cv.Canny(img,40,70)


    for i in range(8):
        for j in range(8):
            x1 = points[i][j][0] +10
            x2 = points[i+1][j+1][0] -10 
            y1 = points[i][j][1] +10
            y2 = points[i+1][j+1][1] -10 
            
            square = edges[y1:y2,x1:x2]
            sqaure = img[y1+5:y2-5,x1+5:x2-5]
            
            if len(np.nonzero(square)[0]) > eThresh:
                if np.average(sqaure) > cThresh :
                    newState[i][j] = 1
                else :
                    newState[i][j] = -1
    
    return newState

