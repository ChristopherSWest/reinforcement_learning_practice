from tkinter import *
from AiPlayer import *
from Player import *
from Ball import *
import time
from random import *
import Constants


class CatchGame:

    def __init__(self, window):
        self.window = window
        self.canvas = Canvas(self.window, width=Constants.WIDTH, height=Constants.HEIGHT)        
        self.fall_balls = []
        self.fall_ball = Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)
        self.fall_ball.draw_ball(self.canvas)
        self.user_ball = Player(randrange(Constants.WIDTH), Constants.HEIGHT, Constants.USER_SIZE)
        self.user_ball.draw_ball(self.canvas)
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
        self.canvas.pack()
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
                    new_ball = Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)
                    new_ball.draw_ball(self.canvas)
                    self.fall_balls.append(new_ball)
                    normalize_ball_drop = 0
            self.window.bind("<KeyPress>", self.keydown)
            self.window.bind("<KeyRelease>", self.keyup)
            state_list = []
            for ball in self.fall_balls:
                ball.move()
                state_list.append(int(ball.x))
                state_list.append(int(ball.y))
            state_list.append(int(self.ai.ball.x))
            state_list.append(int(self.ai.ball.y))            

            state = {
                'falling_objects': [],
                'player': Player(self.user_ball.x, self.user_ball.y, Constants.USER_SIZE)
            }
            # Need to create a state dict that doesn't use tkinter objects.  
            for ball in self.fall_balls:
                state["falling_objects"].append(Ball(ball.x,ball.y, Constants.FALL_BALL_SIZE))
            '''state = {
                "falling_objects": self.fall_balls,
                "player": self.user_ball
            }'''

        #ai make move
            actions = self.ai.get_available_moves()
            
            tuple_state = tuple((int(self.fall_ball.x),int(self.fall_ball.y), int(self.ai.ball.x),int(self.ai.ball.y)))
            action = self.ai.guess_best_move(state)
            #print(state)
            self.ai.make_move(action)
            self.ai.ball.move()


            for ball in self.fall_balls:
                if(ball.y>(Constants.HEIGHT)):
                        
                    if (ball.x >= self.ai.ball.coordinates[0] and ball.x <= self.ai.ball.coordinates[2]):

                        score += 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

                    else:
                        score -= 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))


                    ball.delete_ball()
                    remove_ball = self.fall_balls.pop(self.fall_balls.index(ball))

            if(self.ai.ball.x>Constants.WIDTH):
                self.ai.ball.canvas.move(self.ai.ball.image, -Constants.WIDTH, self.ai.ball.yVelocity)

            if(self.ai.ball.x<0):
                self.ai.ball.canvas.move(self.ai.ball.image, Constants.WIDTH, self.ai.ball.yVelocity)

                        
            self.window.update()
            time.sleep(Constants.UPDATE)
            

    def run_user_game(self):
        self.canvas.pack()
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
                    new_ball = Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)
                    new_ball.draw_ball(self.canvas)
                    self.fall_balls.append(new_ball)
                    normalize_ball_drop = 0
            self.window.bind("<KeyPress>", self.keydown)
            self.window.bind("<KeyRelease>", self.keyup)
            state_list = []
            for ball in self.fall_balls:
                ball.move()
                state_list.append(int(ball.x))
                state_list.append(int(ball.y))
            state_list.append(int(self.user_ball.x))
            state_list.append(int(self.user_ball.y))
            self.user_ball.move()
            
            for ball in self.fall_balls:
                if(ball.y>(Constants.HEIGHT)):
                    
                    if (ball.x >= self.user_ball.coordinates[0] and ball.x <= self.user_ball.coordinates[2]):

                        score += 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))
                        
                    else:
                        score -= 1
                        self.canvas.delete(my_score)
                        my_score = self.canvas.create_text(Constants.WIDTH*0.80, 25, text=score, fill="red", font=('Helvetica 15 bold'))

                    ball.delete_ball()
                    remove_ball = self.fall_balls.pop(self.fall_balls.index(ball))
                    

            if(self.user_ball.x>Constants.WIDTH):
                self.user_ball.canvas.move(self.user_ball.image, -Constants.WIDTH, self.user_ball.yVelocity)

            if(self.user_ball.x<0):
                self.user_ball.canvas.move(self.user_ball.image, Constants.WIDTH, self.user_ball.yVelocity)
                        
            self.window.update()
            time.sleep(Constants.UPDATE)

