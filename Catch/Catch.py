from tkinter import *
from typing import Tuple
from AiPlayer import *
from Ball import *
import time
from tkinter.tix import WINDOW
from random import *

window = Tk()




WIDTH = 500
HEIGHT = 500
UPDATE = 0.01

canvas = Canvas(window, width=WIDTH, height=HEIGHT)
canvas.pack()

fall_ball = Ball(canvas, randrange(WIDTH),0,25)
fall_ball.change_velocity(0,4)

user_ball = Ball(canvas, randrange(WIDTH), HEIGHT, 25)

def keydown(e):
    if e.char == "a":
        user_ball.change_velocity(-5,0)
    if e.char == "d":
        user_ball.change_velocity(5,0)
def keyup(e):
    user_ball.change_velocity(0,0)

ai = AiPlayer(user_ball)

score = 0
canvas.create_text(WIDTH*0.70, 25, text="Score: ", fill="red", font=('Helvetica 15 bold'))
my_score = canvas.create_text(WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
ai.train(1000)

# Main Loop
while True:

    window.bind("<KeyPress>", keydown)
    window.bind("<KeyRelease>", keyup)
    fall_ball.move()


#ai make move
    actions = ai.get_available_moves()
    tuple_state = tuple((int(fall_ball.center[0]),int(fall_ball.center[1]), int(ai.ball.center[0]),int(ai.ball.center[1])))
    action = ai.guess_best_move(tuple_state)
    
    ai.make_move(action)
    ai.ball.move()


    
    if(fall_ball.center[1]>(HEIGHT)):
            
        if (fall_ball.center[0] >= ai.ball.coordinates[0] and fall_ball.center[0] <= ai.ball.coordinates[2]):

            score += 1
            canvas.delete(my_score)
            my_score = canvas.create_text(WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

        else:
            score -= 1
            canvas.delete(my_score)
            my_score = canvas.create_text(WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

        fall_ball.canvas.move(fall_ball.image,randrange(fall_ball.canvas.winfo_width())-fall_ball.center[0],(fall_ball.yVelocity-fall_ball.canvas.winfo_height()))

    if(user_ball.center[0]>500):
        ai.ball.canvas.move(ai.ball.image, -WIDTH, ai.ball.yVelocity)

    if(user_ball.center[0]<0):
        ai.ball.canvas.move(ai.ball.image, WIDTH, ai.ball.yVelocity)
                
    window.update()
    time.sleep(UPDATE)
    
window.mainloop()

