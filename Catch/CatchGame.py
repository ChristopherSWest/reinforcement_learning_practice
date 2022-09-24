from tkinter import *
from typing import Tuple
from AiPlayer import *
from Ball import *
import time
from tkinter.tix import WINDOW
from random import *
import Constants


class CatchGame:

    def __init__(self, window):
        self.window = window
        self.canvas = Canvas(self.window, width=Constants.WIDTH, height=Constants.HEIGHT)
        self.canvas.pack()
        self.fall_balls = []
        self.fall_ball = Ball(self.canvas, randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)
        self.user_ball = Ball(self.canvas, randrange(Constants.WIDTH), Constants.HEIGHT, Constants.USER_SIZE)
        self.ai = AiPlayer(self.user_ball)
        self.fall_balls.append(self.fall_ball)

    def keydown(self, e):
        if e.char == "a":
            self.user_ball.change_velocity(-Constants.USER_SPEED,0)
        if e.char == "d":
            self.user_ball.change_velocity(Constants.USER_SPEED,0)
    def keyup(self, e):
        self.user_ball.change_velocity(0,0)

    def run_ai_game(self, train_n):
        
        score = 0
        self.canvas.create_text(Constants.WIDTH*0.70, 25, text="Score: ", fill="red", font=('Helvetica 15 bold'))
        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
        self.ai.train(train_n)
        normalize_ball_drop = 0
        
        # Main Loop
        while True:
            normalize_ball_drop += 1
            for ball in self.fall_balls:
                ball.change_velocity(0,Constants.FALL_SPEED)
            if randrange(40) < (Constants.FALL_BALL_RATE * 100):
                if normalize_ball_drop >= 30:
                    self.fall_balls.append(Ball(self.canvas, randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE))
                    normalize_ball_drop = 0
            self.window.bind("<KeyPress>", self.keydown)
            self.window.bind("<KeyRelease>", self.keyup)
            state_list = []
            for ball in self.fall_balls:
                ball.move()
                state_list.append(int(ball.center[0]))
                state_list.append(int(ball.center[1]))
            state_list.append(int(self.ai.ball.center[0]))
            state_list.append(int(self.ai.ball.center[1]))
            
        #TODO: Need to change below to be methods so that I can choose between running the game with a controllable user or an AI user

        #ai make move
            actions = self.ai.get_available_moves()
            
            tuple_state = tuple((int(self.fall_ball.center[0]),int(self.fall_ball.center[1]), int(self.ai.ball.center[0]),int(self.ai.ball.center[1])))
            action = self.ai.guess_best_move((state_list))
            
            self.ai.make_move(action)
            self.ai.ball.move()


            for ball in self.fall_balls:
                if(ball.center[1]>(Constants.HEIGHT)):
                        
                    if (ball.center[0] >= self.ai.ball.coordinates[0] and ball.center[0] <= self.ai.ball.coordinates[2]):

                        score += 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

                    else:
                        score -= 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

                    #ball.canvas.move(ball.image,randrange(ball.canvas.winfo_width())-ball.center[0],(ball.yVelocity-ball.canvas.winfo_height()))

                    #removes the ball from the game
                    ball.delete_ball()
                    remove_ball = self.fall_balls.pop(self.fall_balls.index(ball))

            if(self.ai.ball.center[0]>Constants.WIDTH):
                self.ai.ball.canvas.move(self.ai.ball.image, -Constants.WIDTH, self.ai.ball.yVelocity)

            if(self.ai.ball.center[0]<0):
                self.ai.ball.canvas.move(self.ai.ball.image, Constants.WIDTH, self.ai.ball.yVelocity)

                        
            self.window.update()
            time.sleep(Constants.UPDATE)
            

    def run_user_game(self):
        
        score = 0
        self.canvas.create_text(Constants.WIDTH*0.70, 25, text="Score: ", fill="red", font=('Helvetica 15 bold'))
        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
        normalize_ball_drop = 0
        
        # Main Loop
        while True:
            normalize_ball_drop += 1
            for ball in self.fall_balls:
                ball.change_velocity(0,Constants.FALL_SPEED)
            if randrange(40) < (Constants.FALL_BALL_RATE * 100):
                if normalize_ball_drop >= 30:
                    self.fall_balls.append(Ball(self.canvas, randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE))
                    normalize_ball_drop = 0
            self.window.bind("<KeyPress>", self.keydown)
            self.window.bind("<KeyRelease>", self.keyup)
            state_list = []
            for ball in self.fall_balls:
                ball.move()
                state_list.append(int(ball.center[0]))
                state_list.append(int(ball.center[1]))
            state_list.append(int(self.user_ball.center[0]))
            state_list.append(int(self.user_ball.center[1]))
            self.user_ball.move()
            
            for ball in self.fall_balls:
                if(ball.center[1]>(Constants.HEIGHT)):
                    
                    if (ball.center[0] >= self.user_ball.coordinates[0] and ball.center[0] <= self.user_ball.coordinates[2]):

                        score += 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
                        
                    else:
                        score -= 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

                    # resets the ball at the top
                    #ball.canvas.move(ball.image,randrange(ball.canvas.winfo_width())-ball.center[0],(ball.yVelocity-ball.canvas.winfo_height()))

                    # removes the ball from the game
                    ball.delete_ball()
                    remove_ball = self.fall_balls.pop(self.fall_balls.index(ball))
                    

            if(self.user_ball.center[0]>Constants.WIDTH):
                self.user_ball.canvas.move(self.user_ball.image, -Constants.WIDTH, self.user_ball.yVelocity)

            if(self.user_ball.center[0]<0):
                self.user_ball.canvas.move(self.user_ball.image, Constants.WIDTH, self.user_ball.yVelocity)
                        
            self.window.update()
            time.sleep(Constants.UPDATE)

