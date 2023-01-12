from zoneinfo import available_timezones
from Player import *
from pkg_resources import get_distribution
from Ball import *
from random import *
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
import math
import Constants
from copy import deepcopy

class AiPlayer:
    def __init__(self, ball):
        self.ball = ball
        self.alpha = .7
        self.buffer = {}
        self.reg = SGDRegressor()
        self.epsilon = 0.5
        self.discount = 0.6

    def update_model(self, old_state, action, new_state, reward):
        #Try to predict the value of old q.  If the model isn't initialized yet, set old to 0
        try:
            old = self.reg.predict([self.create_feature_vector(old_state, action)])
        except:
            old = 0
        best_future = self.best_future_reward_model(new_state)
        
        self.update_q_model(old_state, action, old, reward, best_future)

  
    def update_q_model(self, state, action, old_q, reward, future_reward):
        # get a new value estimate using the regression model
        
        qval = old_q + self.alpha * (reward + self.discount * future_reward - old_q)
        array_x = self.create_feature_vector(state,action)
        array_y = [qval]

        X = np.array(array_x)
        X = X.reshape(1, -1)
        
        Y = np.array(array_y)
        
        
        # Try a partial fit.  if the model hasn't been fitted yet, use the fit method instead
        try:
            self.reg.partial_fit(X,Y.ravel())
        except:
            self.reg.fit(X,Y.ravel())
    

    def best_future_reward_model(self, state):
        rewards = []
        available_moves = self.get_available_moves()
        for move in available_moves:
            try:
                rewards.append(self.reg.predict([self.create_feature_vector(state, move)]))
            except:
                rewards.append(0)
        
        best_reward = max(rewards)
        return best_reward

    def guess_best_move(self, state):
        # Guess the best move to take based on the prediciting the value of the state/action pair.
        # Will select a random move with the probability of epsilon
        random_number = randrange(100)
        estimated_values = {}
        best_moves = []
        available_moves = self.get_available_moves()
        
        for move in available_moves:
            try:
                estimated_values.update({move: self.reg.predict([self.create_feature_vector(state, move)])})
            except Exception as e:
                print(e)
                estimated_values.update({move: 0})
            
        best_moves = [key for key, value in estimated_values.items() if value == max(estimated_values.values())]
        
  
        if random_number <= self.epsilon * 100:
            return sample(available_moves,1)[0]
        else:
            if len(best_moves) > 1:
                best = best_moves[randrange(len(best_moves))]
                
                return best
            else:

                return best_moves[0]

    def get_available_moves(self):
        return [(-Constants.USER_SPEED,0),(0,0),(Constants.USER_SPEED,0),(-Constants.USER_HIGH_SPEED,0),(Constants.USER_HIGH_SPEED,0)]
    
    def make_move(self, move):
        self.ball.change_velocity(move[0],move[1])
        
    def create_feature_vector(self, state, action):
        # Accepts a state tuple that can have n fall balls, one user ball and an action Tuple.
        # We want to take the state that may have multiple balls and get the distance for each ball and return a feature vector 
        # of only the closest ball to the player
        # going to make a feature that is the distance of the fall ball and user ball to represent the state and 
        # maybe minus the distance of the fall ball and user ball
        # assuming that the particular action was taken. feature value = f(S,A)


        try:
            distances = {}
            for s in state["falling_objects"]:
                distances.update({s: self.get_distance(s,state["player"])})

            distance = min(distances.values())
        except ValueError as e:
            print(e)
            feature_vector = [0, 0, 0, 1]
        else:
            try:
                x_total = 0
                y_total = 0
                x_avg = 0
                y_avg = 0
                for obj in state['falling_objects']:
                    x_total += obj.x
                    y_total += obj.y

                x_avg = (x_total/ len(state["falling_objects"]))
                y_avg = (y_total/ len(state["falling_objects"]))
                avg_ball = Ball(x_avg,y_avg,Constants.FALL_BALL_SIZE)
                avg_distance = self.get_distance(avg_ball, state['player'])

                closest_object = [key for key, value in distances.items() if value == min(distances.values())]
                
                distance = self.get_distance(closest_object[0],state['player'])
                object_copy = deepcopy(closest_object[0])
                
                object_copy.change_velocity(0, Constants.FALL_SPEED)
                object_copy.x = object_copy.x + object_copy.xVelocity
                object_copy.y = object_copy.y + object_copy.yVelocity
                new_player_position = deepcopy((state["player"]))
                new_player_position.change_velocity(action[0],action[1])
                new_player_position.x = new_player_position.x + new_player_position.xVelocity
                new_player_position.y = new_player_position.y + new_player_position.yVelocity
                
                new_distance = self.get_distance(object_copy,new_player_position)
                state_feature = distance - new_distance
                
            except Exception as e:
                print(e)
            feature_vector = [state_feature, x_avg - (state["player"].x), y_avg - (state["player"].y), avg_distance,state['player'].x, state['player'].y, object_copy.xVelocity - (state["player"].xVelocity), object_copy.yVelocity - (state["player"].yVelocity), 1]
            
        finally:
            return feature_vector

    def get_distance(self, falling_object, player):
        # Since the player can move from one side of the screen to the other by moving past the edge of either side, this method
        # will return the closest distance based on that fact. This will require pretending the that the user ball exists at it's current position, + the canvas width on the x axis, and 
        # also - the canvas width on the x value.  This will return the closest distance.
        
        distance_vectors = []
        distances = []

        

        distance_vectors.append([abs(falling_object.x - player.x),abs(falling_object.y - player.y)])
        distance_vectors.append([abs(falling_object.x - (player.x + Constants.WIDTH)),abs(falling_object.y - player.y)])
        distance_vectors.append([abs(falling_object.x - (player.x - Constants.WIDTH)),abs(falling_object.y - player.y)])

        
        for distance_vector in distance_vectors:
            #print(math.sqrt((distance_vector[0] * distance_vector[0]) + (distance_vector[1] * distance_vector[1])))
            distances.append(math.sqrt((distance_vector[0] * distance_vector[0]) + (distance_vector[1] * distance_vector[1])))

        distance = min(distances)
        return distance

    def train(self, n):
        buff = 10
        catch_count = 0
        count = 0
        #Play game n times
        
        count+=1
        fall_balls = []
        fall_ball = Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)
        fall_ball.change_velocity((randrange(-100,100)/100), Constants.FALL_SPEED)
        fall_balls.append(fall_ball)
        
        


        state = {
            "falling_objects":[fall_ball],
            "player":Player(randrange(Constants.WIDTH), Constants.HEIGHT, Constants.USER_SIZE) 
        }
        
        
        last = {
            "state":None,"action":None
        }
        normalize_ball_drop = 0
        catch_combo = 0
        last_list = []
        # Game loop
        while True:
            #updates decreases epsilon and increases the discount factor based on the number of n
            if n > buff:
                if self.epsilon > 0.05:
                    self.epsilon -= (1/(n))
            

                '''if self.discount < 0.8:
                    self.discount += (1/(n*30))
            print(self.discount)'''

            '''if self.alpha > 0.05:
                self.alpha -= (1/(n))'''
            #print(self.epsilon)
            action = self.guess_best_move(state)
            
            # Keep track of last state and action
            last["state"] = state
            last["action"] = action
            
            

            # create a new training fall ball at a certain rate
            normalize_ball_drop += 1
            if randrange(40) < (Constants.FALL_BALL_RATE * 100):
                if normalize_ball_drop >= 5:
                    state["falling_objects"].append(Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE))
                    
                    normalize_ball_drop = 0
        

            # for each falling ball, update x and y
            for k in state["falling_objects"]:
                if isinstance(k, Ball):
                    if k.yVelocity == 0:
                        k.change_velocity((randrange(-200,200)/100),Constants.FALL_SPEED)
                    
                    if k.x <= 0 + Constants.FALL_BALL_SIZE/2 or k.x >= Constants.WIDTH - Constants.FALL_BALL_SIZE/2:
                        k.change_velocity((k.xVelocity * -1), k.yVelocity)  
                    else:
                        k.change_velocity((randrange(-50,50)/100) + k.xVelocity, k.yVelocity)
                    k.x += k.xVelocity
                    k.y += k.yVelocity
            # For Player Apply change velocity based on action and update x and y
            state["player"].change_velocity(action[0],action[1])
            state["player"].x += state["player"].xVelocity
            state["player"].y += state["player"].yVelocity

            
            #correct for going too far left or right.
            # Too far right
            if state["player"].x > Constants.WIDTH:
                state["player"].x = state['player'].x - Constants.WIDTH
                
            # Too far left
            if state["player"].x < Constants.WIDTH - Constants.WIDTH:
                state["player"].x = (Constants.WIDTH - Constants.WIDTH) + Constants.WIDTH
            
            for idx, b in enumerate(state["falling_objects"]):
                
            # if ball completes fall, get the proper reward
            
#                if b % 2 != 0:
                if b.y >= Constants.HEIGHT:
                    count += 1

                    #if player catches the ball
                    if ((b.x >= (state["player"].x - (Constants.USER_SIZE/1.5))) and (b.x <= (state["player"].x + (Constants.USER_SIZE/1.5)))):
                        if n < buff:
                            last_copy = deepcopy(last)
                            last_copy.update({"value": 1})
                            last_list.append(last_copy)
                        else:
                            self.update_model(
                                last["state"],
                                last["action"],
                                state,
                                (1)
                            )
                        catch_count+=1
                        
                        print("catch")
                        state["falling_objects"].pop(idx)
                        

                    # if player doesn't catch the ball
                    elif ((b.x < (state["player"].x - (Constants.USER_SIZE/1.5))) or (b.x > (state["player"].x + (Constants.USER_SIZE/1.5)))):
                        catch_combo = 0
                        if n < buff:
                            last_copy = deepcopy(last)
                            last_copy.update({"value": -1})
                            last_list.append(last_copy)
                        else:
                            self.update_model(
                                last["state"],
                                last["action"],
                                state,
                                -1
                            )
                        print("no Catch")
                        
                        state["falling_objects"].pop(idx)

                else:
                    # add buffer dictionary to initialize.
                    if n < buff:
                        last_copy = deepcopy(last)
                        last_copy.update({"value": 0})
                        last_list.append(last_copy)
                    elif n == buff:
                        array_y = []
                        
                        for q in last_list:
                            array_x = self.create_feature_vector(q["state"],q["action"])
                            array_y.append[q["value"]]
                            
                            

                        X = np.array(array_x)
                        #X = X.reshape(1, -1)
                        
                        Y = np.array(array_y)
                        
                        
                        # Try a partial fit.  if the model hasn't been fitted yet, use the fit method instead
                        try:
                            self.reg.partial_fit(X,Y.ravel())
                        except:
                            self.reg.fit(X,Y.ravel())


            if count >= n:
                print(f"Catch percentage:  %{catch_count/count}")
                break