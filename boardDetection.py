import numpy as np
import cv2 as cv



#Track outers, record them as approximations
#Track inners, do normal things but only with inner 7
#add outers to the lines, sort, get points

def display(imageName):
    """
    Input image \n
    Displays it and waits for a key to be pressed to close window
    """
    cv.imshow("display",imageName)
    cv.waitKey(0)
    cv.destroyAllWindows

def resize(image,scaleFact):
    """
    Input image and scale factor (>0) \n
    Get resized image
    """

    width=int(image.shape[1]*scaleFact)
    height=int(image.shape[0]*scaleFact)
    newDim=(width,height)
    return cv.resize(src=image,dsize=newDim)

def getOuters(image):
    """
    Gets user to click four outer corners of the board \n
    Turns the click coordinates into the four outermost lines \n
    Returns horz1,horz2,vert1,vert2
    """
    def click_event(event, x, y, flags, params):
        """
        Defines what to do with mouseCallback input 
        """
        if event == cv.EVENT_LBUTTONDOWN:
            clicks.append((x,y))

    clicks = []
    cv.imshow("getClicks", image)
    cv.setMouseCallback('getClicks', click_event)
    cv.waitKey(0)
    cv.destroyAllWindows()
    
    coord1 = clicks[0]
    coord2 = clicks[1]
    coord3 = clicks[2]
    coord4 = clicks[3]

    vert1 = int(0.5*(coord1[0]+coord3[0]))
    vert2 = int(0.5*(coord2[0]+coord4[0]))
    horz1 = int(0.5*(coord1[1]+coord2[1]))
    horz2 = int(0.5*(coord3[1]+coord4[1]))

    return horz1,horz2,vert1,vert2



def gBlur(image,kSize):
    """
    Input image and kernel size to apply Gaussian blur \n
    Standard deviation parameters are set to 0
    """
    return cv.GaussianBlur(image, (kSize,kSize), 0, 0)

def mBlur(image,kSize):
    """
    Input image and kernel size to apply median blur
    """
    return cv.medianBlur(image,kSize)

def biFilt(image,diameter):
    """
    Input image and pixel group diameter to apply bilateral filter \n
    Colour and space standard deviations are hard-coded
    """
    return cv.bilateralFilter(image,diameter,25,25)

def cEdge(image):
    """
    Applies canny edge detector to blurred image \n
    Thresholds are set to 150 and 200 \n
    Only input is img (CHANGE AFTER)
    """
    return cv.Canny(image, 150, 200)

def houghP(image):
    """
    Applies probabalistic hough transform to image \n
    All parameters are currently hard-coded in \n
    Returns an array of lines segments where each row is x1,y1,x2,y2
    """
    #image, rho, theta, accumulator threshold, lines maxGap, minLength
    #Default: 0.65,0.25*pi/18-,80,40,500
    lines = cv.HoughLinesP(image, 0.65, 0.25*np.pi/180, threshold=50, minLineLength=40,maxLineGap=500)
    
    return lines

def lineOri(lines, epsilon) :
    """
    Takes lines from houghP and an epsilon value \n
    Epsilon is the maximum change in x or y for verticle/horizontal lines \n
    Returns two arrays (Xlines,Ylines) for all verticle and horizontal lines (x1,x2,y1,y2) for each line
    """
    vertIndex = []
    horzIndex = []

    #Get indices of verticle and horizontal lines in lines
    for i in range(len(lines)):
        for x1,y1,x2,y2 in lines[i]:
            if abs(x2-x1) <= epsilon:
                vertIndex.append(i)
            elif abs(y2-y1) <= epsilon:
                horzIndex.append(i)
    
    vertLines = np.empty((len(vertIndex),4), dtype = np.int32)
    for i in range(len(vertIndex)):
        vertLines[i] = lines[vertIndex[i]]

    horzLines = np.empty((len(horzIndex),4), dtype = np.int32)
    for i in range(len(horzIndex)):
        horzLines[i] = lines[horzIndex[i]]

    return horzLines, vertLines

def lineApprox(horz,vert):
    """
    Vectorized approximation of horizontal and vertical line arrays \n
    Describes each verticle/horizontal line using an average x/y value \n
    Returns a single column array that gives a single value to describe each line
    """
    Hget = np.array([[0],
                    [0.5],
                    [0],
                    [0.5]], dtype = np.float32)
    Vget = np.array([[0.5],
                     [0],
                     [0.5],
                     [0]], dtype = np.float32)
    Yvals = np.matmul(horz,Hget).astype(np.float32)
    Xvals = np.matmul(vert,Vget).astype(np.float32)

    return(Xvals,Yvals)

def removeOuter(lines, bounds):
    """
    Removes any lines outside of getOuters bounds\n
    Use with approximated line and boundsinput \n
    Returns the same array of approximated lines but without the outer edges
    """
    max = bounds[1]
    min = bounds[0]
    delIndex = []
    for i in range(len(lines)):
        if ((min+10)>lines[i]) or ((max-10)<lines[i]):
             delIndex.append(i)
    for i in reversed(delIndex):
        lines = np.delete(lines,i,0)
    return lines

def groupLines(lines):
    """
    Kmeans clustering of the approximated lines \n
    Takes one of the output arrays from lineApprox and condenses them into 9 lines \n
    Changes to 7 lines after implementation of getOuters() function
    """
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    flags = cv.KMEANS_RANDOM_CENTERS

    compactness, labels, centres = cv.kmeans(lines, 7, None, criteria, 40, flags)

    return centres

def fixGroups(lines, klines):
    """
    Input Xlines or Ylines (one before and one after k-means) \n
    If there are overlapping lines in the klustered array, remove some from original \n
    Returns True if a change was made, False if everything is fine \n
    Also returns the modified original array
    """
    isModified = False
    for i in range(len(klines)) :
        delIndex = []
        kline1 = klines[i]
        for j in range(len(klines)):
            if (j!= i) and (abs(kline1-klines[j])<20):
                isModified = True
                editCount = 0
                for k in range(len(lines)):
                    if (abs(kline1-lines[k])<20):
                        editCount += 1
                        if editCount%2 == 0:
                            delIndex.append(k)

        if isModified == True :
            for d in reversed(delIndex):
                lines = np.delete(lines,d,0)
            break
    
    return isModified, lines

def recInters(horz, vert):
     """
     Takes approximated and clustered horizontal and vertical lines (Ylines,Xlines) \n
     Sorts them and stores into a 9x9x2 array of x,y values for each corner
     """
     horz.sort(0)
     vert.sort(0)

     points = np.zeros((9,9,2), dtype = np.int32)

     for i in range(len(horz)):
         for j in range(len(vert)):
             points[i][j][0] = vert[j]
             points[i][j][1] = horz[i]

     return points 

def main(img):
    """
    Entire board detection \n
    Input grayscale, resized image \n
    Outputs 9x9 points array for piece detection
    """
    img = mBlur(img,5)
    img = biFilt(img,20)
    img = cv.Canny(img, 150, 200)

    lines = houghP(img)
    horzLines, vertLines = lineOri(lines,50)
    
    Xlines, Ylines = lineApprox(horzLines,vertLines)
    Xlines = removeOuter(Xlines)
    Ylines = removeOuter(Ylines)

    Xlines = groupLines(Xlines).astype(np.int32)
    Ylines = groupLines(Ylines).astype(np.int32)

    points = recInters(Ylines,Xlines)

    return points

def Vmain(img,copy,copy2):
    """
    Same functionality as main, but with additional input of two coloured, resized images \n
    Returns 9x9 points array for piece detection, while displaying all steps
    """
    horz1,horz2,vert1,vert2 = getOuters(img)
    vertOuters = np.array([[vert1], [vert2]])
    horzOuters = np.array([[horz1], [horz2]])

    img = mBlur(img,3)
    img = biFilt(img,10)
    display(img)
    img = cv.Canny(img, 120, 160)
    display(img)

    lines = houghP(img)
    horzLines, vertLines = lineOri(lines,50)

    
    for i in range(len(horzLines)):
        cv.line(copy,(horzLines[i][0],horzLines[i][1]),(horzLines[i][2],horzLines[i][3]),(100,200,0),2)
    for i in range(len(vertLines)):
        cv.line(copy,(vertLines[i][0],vertLines[i][1]),(vertLines[i][2],vertLines[i][3]),(100,200,0),2)
    display(copy)
    

    Xlines, Ylines = lineApprox(horzLines,vertLines)

    Xlines = removeOuter(Xlines,vertOuters)    
    Ylines = removeOuter(Ylines,horzOuters)

    
    bigY = img.shape[0] -1
    bigX = img.shape[1] -1
    """
    for X in Xlines:                                         
            cv.line(copy,(int(X),1),(int(X),bigY),(100,200,0),2)
    for Y in Ylines:
            cv.line(copy,(1,int(Y)),(bigX,int(Y)),(100,200,0),2)
    display(copy)
    """

    XlinesCopy = Xlines
    YlinesCopy = Ylines

    Xlines = groupLines(Xlines).astype(np.int32)
    Ylines = groupLines(Ylines).astype(np.int32)

    while True:
        badKlustX, XlinesCopy = fixGroups(XlinesCopy, Xlines)
        badKlustY, YlinesCopy = fixGroups(YlinesCopy, Ylines)

        if badKlustX == False and badKlustY == False:
            break
        if badKlustX == True:
            Xlines = groupLines(XlinesCopy).astype(np.int32)
        if badKlustY == True:
            Ylines = groupLines(YlinesCopy).astype(np.int32)

    Xlines = np.append(Xlines, vertOuters, axis=0)
    Ylines = np.append(Ylines, horzOuters, axis=0)

    bigY = img.shape[0] -1
    bigX = img.shape[1] -1
    for X in Xlines:                                         
        cv.line(copy2,(int(X),1),(int(X),bigY),(100,200,0),2)
    for Y in Ylines:
            cv.line(copy2,(1,int(Y)),(bigX,int(Y)),(100,200,0),2)
    display(copy2)
    for X in Xlines:
        for Y in Ylines:
            cv.circle(copy2, (int(X),int(Y)),4,(200,100,0),thickness=-1)
    display(copy2)

    points = recInters(Ylines,Xlines)

    return points



""""
img = cv.imread("pointsInit.png",0)

copy = cv.imread("pointsInit.png")
copy2 = cv.imread("pointsInit.png")

img = resize(img, 1.2)
copy = resize(copy, 1.2)
copy2 = resize(copy2, 1.2)


points = Vmain(img,copy,copy2)
"""


