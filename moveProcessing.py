#Gets board state arrays
#Obtains move through matrix subtraction
#Sends to stockfish
#Updates board state
#Updates movelist
from stockfish import Stockfish
import numpy as np
import cv2 as cv
import chess

#Jonny Libraries
import pyautogui
import time
from chessboard import display

#Board states will be sent from computer vision code in this format
#White is 1, black is -1, empty is 0
#Multiply board states by -1 if human is black

startBoard = np.array([[ 1, 1, 1, 1, 1, 1, 1, 1],
                       [ 1, 1, 1, 1, 1, 1, 1, 1],
                       [ 0, 0, 0, 0, 0, 0, 0, 0],
                       [ 0, 0, 0, 0, 0, 0, 0, 0],
                       [ 0, 0, 0, 0, 0, 0, 0, 0],
                       [ 0, 0, 0, 0, 0, 0, 0, 0],
                       [-1,-1,-1,-1,-1,-1,-1,-1],
                       [-1,-1,-1,-1,-1,-1,-1,-1]], dtype=np.byte)

columns =  ["a","b","c","d","e","f","g","h"]


#Fix filepath
def chessInit():
    """
    Initializes Stockfish and chess libraries \n
    Sets up all settings/variables \n
    Sets boards to starting position
    """
    global board
    board = chess.Board()
    #"C:\\Program Files\\stockfish_15.1_win_x64_avx2\\stockfish-windows-2022-x86-64-avx2.exe"
    global stockfish
    stockfish = Stockfish(path=r"C:\Users\joedi\OneDrive\Desktop\Chessbot3\Chessbot3\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe", 
    depth=18, parameters= {
        "Debug Log File": "",
        "Contempt": 0, # Higher means stockfish will play drawing moves less
        "Min Split Depth": 0,
        "Threads": 8, # More threads will make the engine stronger, but should be kept at less than the number of logical processors on your computer.
        "Ponder": "false",
        "Hash": 2048, # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2. E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
        "MultiPV": 1,
        "Skill Level": 20, #20 max
        "Move Overhead": 10,
        "Minimum Thinking Time": 1,
        "Slow Mover": 100,
        "UCI_Chess960": "false",
        "UCI_LimitStrength": "false", # turn this true to change ELO rating
        "UCI_Elo": 2850 #2850 max 1350 min
    })



def humanMove(oldState, newState, clr):
    """
    Input two board arrays from CV and 1 or -1 for player colour \n
    Outputs a 2x2 array with start and end coords for move
    """
    dBoard = newState - oldState
    dBoard *= clr
    coords = np.nonzero(dBoard)
    
    for i in range(len(coords[0])):
        row = coords[0][i]
        col = coords[1][i]
        
        if dBoard[row][col] == -1 :
            if len(coords[0]) == 4 and col == 4: #For castling
                start = str(columns[col]) + str(row+1)
            elif len(coords[0]) != 4 : 
                start = str(columns[col]) + str(row+1)

        elif dBoard[row][col] == 1 :
            if len(coords[0]) == 4:
                if col == 2 or col == 6 :  #For castling
                    end = str(columns[col]) + str(row+1)
            elif oldState[row][col] != -1 :  #For en passent
                end = str(columns[col]) + str(row+1)
            
        elif dBoard[row][col] == 2 :
            end = str(columns[col]) + str(row+1)

    return start + end

def fishMove(hMove):
    """
    Take human move, and set stockfish game position \n
    Get new move from stockfish and find move type \n
    Returns the move type, and stockfish move
    """
    if hMove != None :
        #board.push(chess.Move.from_uci(hMove))
        board.push_san(hMove)
        
        if stockfish.is_move_correct(hMove) :
            stockfish.make_moves_from_current_position([hMove])
        else :
            print("Error: invalid move")

    fMove = stockfish.get_best_move_time(3000)

    moveType = caseCheck(fMove)

    return moveType, fMove

def caseCheck(fMove):  
    """
    Checks if a move given by stockfish is a capture, en passent, or castle \n 
    Returns the moveType variable (0:normal, 1:capture, 2:EP, 3:castle)
    """
    moveType = 0
    
    if board.is_capture(chess.Move.from_uci(fMove)) == True :
        moveType = 1

    elif board.is_en_passant(chess.Move.from_uci(fMove)) == True :
        moveType = 2
    
    elif board.is_castling(chess.Move.from_uci(fMove)) == True :
        moveType = 3

    return moveType

def isGameOver():
    """
    Checks if the game has ended \n
    Returns boolean    
    """
    return board.is_game_over()

def updateBoards(oldState, newState, moveType, fmove):
    """
    Input both boardStates, moveType, and Stockfish move \n
    Applies Stockfish move to the most recent CV board state \n
    Sets that state to be the old state before human move \n
    Returns oldState
    """
    scol = int(columns.index(fmove[0]))
    srow = int(fmove[1])-1
    ecol = int(columns.index(fmove[2]))
    erow = int(fmove[3])-1
    
    #En passent
    if moveType == 2:
        newState[srow][ecol] = 0
    
    #Castle
    if moveType == 3:
        if ecol == 6:
            newState[erow][7] = 0
            newState[erow][5] = oldState[srow][7]
        elif ecol == 2:
            newState[erow][0] = 0
            newState[erow][3] = oldState[srow][0]

    newState[erow][ecol] = newState[srow][scol]
    newState[srow][scol] = 0
    oldState = newState
    return oldState

def main(hMove, oldState, newState):
    """
    Input human move, oldState, newState \n
    Get fish move and move type, and update boards \n
    Update board states \n
    Returns updated oldState and fish move
    """
    
    #Get move type and fish move
    moveType, fMove = fishMove(hMove)

    #Update board states
    oldState = updateBoards(oldState,newState, moveType, fMove)

    return oldState, fMove











##JonnyCode




def findButtonPos():
    """
    Initializes and returns cursor position for script
    """
    print("PLACE CURSOR OVER DOWNLOAD BUTTON IN ROBOTC > ROBOT > FILE UTILITY > RCDATA")

    print("Saving Coordinates in 5... ")
    time.sleep(2)
    print("3... ")
    time.sleep(1)
    print("2... ")
    time.sleep(1)
    print("1... ")
    time.sleep(1)
    print("Saved!")

    return pyautogui.position()

def writeRobotMoveInstruction(nextMove, path):
    """
    Input the stockfish move \n
    Gets and writes all necessary info to file for robot
    """
    f = open(path, "w")
    f.write(nextMove + ' ')
    
    if board.is_capture(chess.Move.from_uci(nextMove)):
        if board.is_en_passant(chess.Move.from_uci(nextMove)):
            f.write('2 ')
            if nextMove[3] == '6':
                f.write(nextMove[2] + '500 ')
            else:
                f.write(nextMove[2] + '400 ')
        else:
            f.write('1 ')
    elif board.is_castling(chess.Move.from_uci(nextMove)):
            f.write('3 ')
            if board.is_kingside_castling(chess.Move.from_uci(nextMove)):
                f.write('h' + nextMove[1] + 'f' + nextMove[1] +' ')
            else:
                f.write('a' + nextMove[1] + 'c' + nextMove[1]+' ')
    else:
        f.write('0 ')

    f.close()

def writeRobotGameState(path):
    """
    Input path, no output \n
    If the game has ended, writes the reason onto file for robot
    """
    f = open(path, "a")

    if board.is_checkmate():
        f.write('1')
    elif board.is_stalemate():
        f.write('2')
    elif board.is_insufficient_material():
        f.write('3')
    elif board.is_seventyfive_moves():
        f.write('4')
    elif board.is_fivefold_repetition():
        f.write('5')
    else:
        f.write('0')
    
    f.close()

def makeMove(nextMove, game_board):
    """
    Input stockfish move \n
    Updates chess boards and gui
    """
    stockfish.make_moves_from_current_position([nextMove])
    board.push_san(nextMove)
    display.update(stockfish.get_fen_position(), game_board)

def moveInputErrorHandling():
    """
    Console input move function \n
    Replace with human move input from other code if seen
    """
    nextMove = input('Next Move: ') 
    if len(nextMove) != 4 and len(nextMove) != 5:
        nextMove = '0000'
    while not(chess.Move.from_uci(nextMove) in board.legal_moves):
        nextMove = input('Illegal move. Enter a move: ')  
        if len(nextMove) != 4 and len(nextMove) != 5:
            nextMove = '0000'
    return nextMove

def uploadFileToEV3(xPos, yPos, path):
    """
    Input x and y position of cursor fro findButtonPos() \n
    Downloads file to robot
    """
    initPos = pyautogui.position()

    pyautogui.leftClick(xPos,yPos)
    time.sleep(0.25/3.0)

    pyautogui.write(path)
    #pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25/3.0)

    pyautogui.keyDown('enter') 

    time.sleep(0.25/3.0)
    pyautogui.leftClick(initPos)

def gameIsOver():
    """ 
    Checks if the game had ended \n
    Returns a boolean
    """
    return (board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material() 
            or board.is_seventyfive_moves() or board.is_fivefold_repetition())


def JonnyInit():
    """
    Initializes all variables for the script and chess engines \n
    Returns xPos, yPos, game_board
    """
    position = findButtonPos()
    xPos = position[0]
    yPos = position[1]

    game_board = display.start()

    return xPos, yPos, game_board
    

def JonnyMain(fMove, xPos, yPos, game_board, path):
    """
    Input fish move and cursor x and y \n
    Writes and sends all necessary information on file \n
    Updates chess boards    
    """
    writeRobotMoveInstruction(fMove,path)    
    makeMove(fMove, game_board)
    writeRobotGameState(path)
    uploadFileToEV3(xPos, yPos, path)

