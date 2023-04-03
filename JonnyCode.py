# pip install stockfish
from stockfish import Stockfish

# pip install chess
import chess

# pip install chess-board
from chessboard import display

# pip install pyautogui
import pyautogui

# pip install time
import time

## PUT THE PATH TO INSTRUCTIONS FILE HERE
#instructionsPath = "C:/Users/Jonathan DiGiorgio/OneDrive - University of Waterloo/Python/ChessEngine/robotInstructions.txt"
#instructionsPath = r"C:\Users\joedi\OneDrive - University of Waterloo\Chess Robot\Code\MoveInstructions.txt"
#instructionsPath = r"C:\Users\Jonathan DiGiorgio\OneDrive - University of Waterloo\Chess Robot\Code\MoveInstructions.txt"


#settings
#thinkTime = 1000            #stockfish think time in ms
#PlayerVsStockfish = True    #True for player vs stockfish, False for stockfish vs stockfish
#uploadFileTime = 0.25       #time between clicks for file upload in s



"""
## ENTER YOUR STOCKFISH PATH
stockfish = Stockfish(path="C:\Program Files\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe", 
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

board = chess.Board()
"""



#valid_fen = stockfish.get_fen_position()

#endGame = False
#board.legal_moves


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

def makeMove(nextMove):
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


################################################################################
#                                 MAIN CODE                                    #
################################################################################

#instructionsPath = r"C:\Users\Jonathan DiGiorgio\OneDrive - University of Waterloo\Chess Robot\Code\MoveInstructions.txt"


def init():
    """
    Initializes all variables for the script and chess engines \n
    Returns xPos, yPos, game_board
    """

    position = findButtonPos()
    xPos = position[0]
    yPos = position[1]

    game_board = display.start()

    return xPos, yPos, game_board


def main(fMove, xPos, yPos, path):
    """
    Input fish move and cursor x and y \n
    Writes and sends all necessary information on file \n
    Updates chess boards    
    """
    writeRobotMoveInstruction(fMove,path)    
    makeMove(fMove)
    writeRobotGameState(path)
    #uploadFileToEV3(xPos, yPos, path)
    print("done")