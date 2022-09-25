from ast import Lambda
from tkinter import *
import tkinter
from turtle import width
import Constants
from CatchGame import CatchGame


def start_ai_game(main_window, start):
    for item in start:
        start[item].destroy()
    game = CatchGame(main_window)
    game.run_ai_game(Constants.TRAIN_N)

def start_person_game(main_window, start):
    for item in start:
        start[item].destroy()
    game = CatchGame(main_window)
    game.run_user_game()

# Main
main = Tk()
main.geometry(f'{Constants.WIDTH}x{Constants.HEIGHT}')

start_page = {}
start_page.update({"AiGameButton": Button(main, text="AI Game", height= int(Constants.GAME_BUTTON_HEIGHT), width= int(Constants.GAME_BUTTON_WIDTH),command=lambda: start_ai_game(main, start_page))})
start_page.update({"PersonGameButton": Button(main, text="Person Game", height= int(Constants.GAME_BUTTON_HEIGHT), width= int(Constants.GAME_BUTTON_WIDTH),command=lambda: start_person_game(main, start_page))})
start_page.update({"Title": Label(main, text="Catch!", font= Constants.TITLE_FONT)})
#b = Button(main, text="click", command=lambda: start_ai_game(main, b))
for item in start_page:
    if item == "PersonGameButton":
        start_page[item].place(x = Constants.PERSON_BUTTON_X, y = Constants.PERSON_BUTTON_Y)
    elif item == "AiGameButton":
        start_page[item].place(x = Constants.AI_GAME_BUTTON_X, y = Constants.AI_GAME_BUTTON_Y)
    elif item == "Title":
        start_page[item].place(x = Constants.TITLE_X, y = Constants.TITLE_Y)   
    else:
        start_page[item].pack()
main.mainloop()

