import chess
import chess.svg
import random
import time
import numpy as np
from sklearn.linear_model import LinearRegression
from chessPlay import train, play



board = chess.Board()
state_dict = {
    "r": 1,
    "n": 2,
    "b": 3,
    "q": 4,
    "k": 5,
    "p": 6,
    "R": 7,
    "N": 8,
    "B": 9,
    "Q": 10,
    "K": 11,
    "P": 12
}
print(board)
print(board.board_fen())
rows = board.board_fen().split('/')
print(rows)
state = []



for row in rows:
    #print(row)
    for letter in row:
        
        if letter in state_dict.keys():
            state.append(state_dict[letter])
        else:
            for i in range(int(letter)):
                state.append(0)

'''print(state)
print(len(state))
'''





num_actions = 0



ai = train(500)
play(ai)

