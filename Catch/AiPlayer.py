from zoneinfo import available_timezones

from pkg_resources import get_distribution
from Ball import *
from random import *
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
import math
import Constants

class AiPlayer:
    def __init__(self, ball):
        self.ball = ball
        self.alpha = 1
        self.buffer = {}
        self.reg = SGDRegressor()
        self.epsilon = 0.9
        self.discount = 0.1

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
        
        qval = old_q + self.alpha*(reward + (self.discount*((future_reward)-old_q)))
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
            except:
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
        return [(-Constants.USER_SPEED,0),(0,0),(Constants.USER_SPEED,0)]
    
    def make_move(self, move):
        self.ball.change_velocity(move[0],move[1])
        
    def create_feature_vector(self, state, action):
        # Accepts a state tuple that can have n fall balls, one user ball and an action Tuple.
        # We want to take the state that may have multiple balls and get the distance for each ball and return a feature vector 
        # of only the closest ball to the player
        # going to make a feature that is the distance of the fall ball and user ball to represent the state and 
        # maybe minus the distance of the fall ball and user ball
        # assuming that the particular action was taken.


        fall_balls_amount = (len(state)-2)/2
        user_ball_tuple = (state[len(state)-2], state[len(state)-1])
        fall_states = []
        states_to_check = []
        for i in range(int(fall_balls_amount*2)):
            if i != 0 and i % 2 != 0:
                fall_states.append(state[i])
                fall_states.append(user_ball_tuple[0])
                fall_states.append(user_ball_tuple[1])
                states_to_check.append((fall_states[0],fall_states[1],fall_states[2],fall_states[3]))
                fall_states = []
            else:
                fall_states.append(state[i])

        distances = {}
        for s in states_to_check:
            distances.update({s: self.get_distance(s)})

        distance = min(distances.values())
        closest_state = [key for key, value in distances.items() if value == min(distances.values())]
        
        new_state = (closest_state[0][0],closest_state[0][1]+Constants.FALL_SPEED,closest_state[0][2]+action[0],closest_state[0][3])
        new_distance = self.get_distance(new_state)
        state_feature = distance - new_distance

        if action == (-Constants.USER_SPEED,0):
            feature_vector = [state_feature, 0 ,0 ,1]
        elif action == (0,0):
            feature_vector = [0, state_feature, 0 ,1]
        else:
            feature_vector = [0, 0, state_feature, 1]
        return feature_vector

    def get_distance(self, state):
        # Since the player can move from one side of the screen to the other by moving past the edge of either side, this method
        # will return the closest distance based on that fact. This will require pretending the that the user ball exists at it's current position, + the canvas width on the x axis, and 
        # also - the canvas width on the x value.  This will return the closest distance.
        
        distance_vectors = []
        distances = []

        distance_vectors.append([abs(state[0]-state[2]),abs(state[1]-state[3])])
        distance_vectors.append([abs(state[0]-(state[2]+Constants.WIDTH)),abs(state[1]-state[3])])
        distance_vectors.append([abs(state[0]-(state[2]-Constants.WIDTH)),abs(state[1]-state[3])])

        for distance_vector in distance_vectors:
            distances.append(math.sqrt((distance_vector[0] * distance_vector[0]) + (distance_vector[1] * distance_vector[1])))

        distance = min(distances)
        return distance

    def train(self, n):

        catch_count = 0
        count = 0
        #Play game n times
        
        count+=1
        fall_balls = []
        fall_ball = (randrange(Constants.WIDTH),0)
        fall_balls.append(fall_ball)
        
        f1 = fall_ball[0]
        f2 = fall_ball[1]
        u1 = randrange(Constants.WIDTH)
        u2 = Constants.HEIGHT
    
        state = (f1, f2, u1, u2)
        last = {
            "state":None,"action":None
        }
        normalize_ball_drop = 0
        
        # Game loop
        while True:
            #updates decreases epsilon and increases the discount factor based on the number of n
            if self.epsilon > 0.01:
                self.epsilon -= (1/(n*25))
            if self.discount < 0.99:
                self.discount += (1/(n*25))
            state_list = []
            
            action = self.guess_best_move(state)

            # Keep track of last state and action
            last["state"] = state
            last["action"] = action
            
            # create a new training fall ball at a certain rate
            normalize_ball_drop += 1
            if randrange(30) < (Constants.FALL_BALL_RATE * 100):
                if normalize_ball_drop >= 30:
                    state_list.append(randrange(Constants.WIDTH))
                    state_list.append(0)
                    normalize_ball_drop = 0
            
            
            #drop all of the fall balls in the current state and append them to the state list
            for k in range(len(state)-2):
                if k % 2 != 0:
                    state_list.append(state[k]+Constants.FALL_SPEED)    
                else:
                    state_list.append(state[k])
                
            # Apply the actions to the end of the state list
            state_list.append(state[len(state)-2]+action[0])
            state_list.append(state[len(state)-1]+action[1])
            
            # assingn the state as a tuple of the state list
            state = tuple(state_list)
            
            #correct for going to far left or right.
            if state[len(state)-2] > Constants.WIDTH:
                
                state_list.pop()
                x = state_list.pop()
                new_x = x - Constants.WIDTH
                state_list.append(new_x)
                state_list.append(Constants.HEIGHT)
                state = tuple(state_list)

            if state[len(state)-2] < 0:
                state_list.pop()
                x = state_list.pop()
                new_x = x + Constants.WIDTH
                state_list.append(new_x)
                state_list.append(Constants.HEIGHT)
                state = 0
                state = tuple(state_list)
            
            
            for b in range(len(state)-2):
                if b % 2 != 0:
                    # if ball completes fall, get the proper reward
                    if state[b] >= Constants.HEIGHT:
                        
                        count += 1

                        #if player catches the ball
                        if ((state[b-1] >= (state[len(state)-2] - (Constants.USER_SIZE/2))) and (state[b-1] <= (state[len(state)-2] + (Constants.USER_SIZE/2)))):
                            self.update_model(
                                last["state"],
                                last["action"],
                                state,
                                1
                            )
                            catch_count+=1
                            print("catch")
                            edit_list = list(state)
                            edit_list.pop(b)
                            edit_list.pop(b-1)
                            state = tuple(edit_list)

                        # if player doesn't catch the ball
                        elif ((state[b-1] <= (state[len(state)-2] - (Constants.USER_SIZE/2))) or (state[b-1] >= (state[len(state)-2] + (Constants.USER_SIZE/2)))):
                            self.update_model(
                                last["state"],
                                last["action"],
                                state,
                                0
                            )
                            print("no Catch")
                            edit_list = list(state)
                            edit_list.pop(b)
                            edit_list.pop(b-1)
                            state = tuple(edit_list)
                    else:
                        if ((state[b-1] >= (state[len(state)-2] - (Constants.USER_SIZE/2))) and (state[b-1] <= (state[len(state)-2] + (Constants.USER_SIZE/2)))):
                            self.update_model(
                                last["state"],
                                last["action"],
                                state,
                                0
                            )  
            
            if count >= n:
                break