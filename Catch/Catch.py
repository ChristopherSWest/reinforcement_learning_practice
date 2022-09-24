from tkinter import *
import Constants
from CatchGame import CatchGame

window = Tk()
game = CatchGame(window)
#game.run_ai_game(Constants.TRAIN_N)
game.run_user_game()
