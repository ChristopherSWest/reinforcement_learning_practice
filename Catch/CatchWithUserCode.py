from tkinter import *
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

while True:

    window.bind("<KeyPress>", keydown)
    window.bind("<KeyRelease>", keyup)
    fall_ball.move()
#    user_ball.move()

#ai make move
    ai.make_move(randrange(3))
    ai.ball.move()
    if(fall_ball.center[1]>(HEIGHT)):
            
            #print("true")
 #           if (fall_ball.center[0] >= user_ball.coordinates[0] and fall_ball.center[0] <= user_ball.coordinates[2]):
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
    #if(ai.ball.center[0]>500):
        #user_ball.canvas.move(user_ball.image, -WIDTH, user_ball.yVelocity)
        ai.ball.canvas.move(ai.ball.image, -WIDTH, ai.ball.yVelocity)

    if(user_ball.center[0]<0):
    #if(ai.ball.center[0]>500):
        #user_ball.canvas.move(user_ball.image, WIDTH, user_ball.yVelocity)
        ai.ball.canvas.move(ai.ball.image, WIDTH, ai.ball.yVelocity)
                
    window.update()
    time.sleep(UPDATE)
    
window.mainloop()

