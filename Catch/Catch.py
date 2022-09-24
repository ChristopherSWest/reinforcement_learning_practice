from tkinter import *
from typing import Tuple
from AiPlayer import *
from Ball import *
import time
from tkinter.tix import WINDOW
from random import *
import Constants

window = Tk()


canvas = Canvas(window, width=Constants.WIDTH, height=Constants.HEIGHT)
canvas.pack()
fall_balls = []
fall_ball = Ball(canvas, randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)

fall_balls.append(fall_ball)

for ball in fall_balls:
    ball.change_velocity(0,Constants.FALL_SPEED) 

user_ball = Ball(canvas, randrange(Constants.WIDTH), Constants.HEIGHT, Constants.USER_SIZE)

def keydown(e):
    if e.char == "a":
        user_ball.change_velocity(-Constants.USER_SPEED,0)
    if e.char == "d":
        user_ball.change_velocity(Constants.USER_SPEED,0)
def keyup(e):
    user_ball.change_velocity(0,0)

ai = AiPlayer(user_ball)

score = 0
canvas.create_text(Constants.WIDTH*0.70, 25, text="Score: ", fill="red", font=('Helvetica 15 bold'))
my_score = canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
ai.train(500)
normalize_ball_drop = 0
# Main Loop
while True:
    normalize_ball_drop += 1
    for ball in fall_balls:
        ball.change_velocity(0,Constants.FALL_SPEED)
    if randrange(40) < (Constants.FALL_BALL_RATE * 100):
        if normalize_ball_drop >= 30:
            fall_balls.append(Ball(canvas, randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE))
            normalize_ball_drop = 0
    window.bind("<KeyPress>", keydown)
    window.bind("<KeyRelease>", keyup)
    state_list = []
    for ball in fall_balls:
        ball.move()
        state_list.append(int(ball.center[0]))
        state_list.append(int(ball.center[1]))
    state_list.append(int(ai.ball.center[0]))
    state_list.append(int(ai.ball.center[1]))
    
    #user_ball.move()
    #fall_ball.move()

#TODO: Need to change below to be methods so that I can choose between running the game with a controllable user or an AI user

#ai make move
    actions = ai.get_available_moves()
    
    tuple_state = tuple((int(fall_ball.center[0]),int(fall_ball.center[1]), int(ai.ball.center[0]),int(ai.ball.center[1])))
    action = ai.guess_best_move((state_list))
    
    ai.make_move(action)
    ai.ball.move()


    for ball in fall_balls:
        if(ball.center[1]>(Constants.HEIGHT)):
                
            if (ball.center[0] >= ai.ball.coordinates[0] and ball.center[0] <= ai.ball.coordinates[2]):

                score += 1
                canvas.delete(my_score)
                my_score = canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

            else:
                score -= 1
                canvas.delete(my_score)
                my_score = canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

            #ball.canvas.move(ball.image,randrange(ball.canvas.winfo_width())-ball.center[0],(ball.yVelocity-ball.canvas.winfo_height()))

            #removes the ball from the game
            ball.delete_ball()
            remove_ball = fall_balls.pop(fall_balls.index(ball))

    if(ai.ball.center[0]>Constants.WIDTH):
        ai.ball.canvas.move(ai.ball.image, -Constants.WIDTH, ai.ball.yVelocity)

    if(ai.ball.center[0]<0):
        ai.ball.canvas.move(ai.ball.image, Constants.WIDTH, ai.ball.yVelocity)



    '''for ball in fall_balls:
        if(ball.center[1]>(Constants.HEIGHT)):
            
            if (ball.center[0] >= user_ball.coordinates[0] and ball.center[0] <= user_ball.coordinates[2]):

                score += 1
                canvas.delete(my_score)
                my_score = canvas.create_text(WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
                
            else:
                score -= 1
                canvas.delete(my_score)
                my_score = canvas.create_text(WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

            # resets the ball at the top
            #ball.canvas.move(ball.image,randrange(ball.canvas.winfo_width())-ball.center[0],(ball.yVelocity-ball.canvas.winfo_height()))

            # removes the ball from the game
            ball.delete_ball()
            remove_ball = fall_balls.pop(fall_balls.index(ball))
            

    if(user_ball.center[0]>Constants.WIDTH):
        user_ball.canvas.move(user_ball.image, -Constants.WIDTH, user_ball.yVelocity)

    if(user_ball.center[0]<0):
        user_ball.canvas.move(user_ball.image, Constants.WIDTH, user_ball.yVelocity)'''
                
    window.update()
    time.sleep(Constants.UPDATE)
    
window.mainloop()

