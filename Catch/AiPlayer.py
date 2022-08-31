from zoneinfo import available_timezones

from pkg_resources import get_distribution
from Ball import *
from random import *
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
import math
# state is a tuple f = fall_ball, u = user_ball.  state = (f1, f2, u1, u2)
#

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
                #print(best)
                
                return best
            else:

                return best_moves[0]

    def get_available_moves(self):
        return [(-5,0),(0,0),(5,0)]
    
    def make_move(self, move):
        self.ball.change_velocity(move[0],move[1])
        
    def create_feature_vector(self, state, action):
        # going to make a feature that is the distance of the fall ball and user ball to represent the state and 
        # maybe minus the distance of the fall ball and user ball
        # assuming that the particular action was taken.
        distance = self.get_distance(state)
        new_state = (state[0],state[1]+4,state[2]+action[0],state[3])
        new_distance = self.get_distance(new_state)
        state_feature = distance - new_distance

        if action == (-5,0):
            feature_vector = [state_feature, 0 ,0 ,1]
        elif action == (0,0):
            feature_vector = [0, state_feature, 0 ,1]
        else:
            feature_vector = [0, 0, state_feature, 1]
        return feature_vector

    def get_distance(self, state):
        distance_vector = [abs(state[0]-state[2]),abs(state[1]-state[3])]
        distance = math.sqrt((distance_vector[0] * distance_vector[0]) + (distance_vector[1] * distance_vector[1]))
        return distance

    def train(self, n):
        catch_count = 0
        count = 0
        #Play game n times
        for i in range(n):
            count+=1
            
            #updates decreases epsilon and increases the discount factor based on the number of n
            if self.epsilon > 0.01:
                self.epsilon -= (1/n)
            if self.discount < 0.99:
                self.discount += (1/n)
            print(f"Playing training game {i + 1}")
            f1 = randrange(500)
            f2 = 0
            u1 = state[2] if i > 0 else randrange(500)
            u2 = 500
            #state = (f1, f2, u1, u2)
            state = (f1, f2, u1, u2)
            last = {
                "state":None,"action":None
            }
            
            # Game loop
            while True:

                
                
                action = self.guess_best_move(state)
                 # Keep track of last state and action

                last["state"] = state
                last["action"] = action
                
                #print(state, action)
                state = (state[0], state[1]+4, state[2]+action[0], state[3]+action[1])
                
                
                #correct for going to far left or right.
                if state[2] > 500:
                    state = (state[0],state[1],state[2]-500,state[3])
                if state[2] < 0:
                    state = (state[0],state[1],state[2]+500,state[3])

                
                # if game is over get the proper reward
                
            
                if state[1] >= 500:
                    #if player catches the ball
                    if ((state[0] >= (state[2] - 12.5)) and (state[0] <= (state[2] + 12.5))):
                        self.update_model(
                            last["state"],
                            last["action"],
                            state,
                            1
                        )
                        catch_count+=1
                        print("catch")
                        break
                    # if player doesn't catch the ball
                    elif ((state[0] <= (state[2] - 12.5)) or (state[0] >= (state[2] + 12.5))):
                        self.update_model(
                            last["state"],
                            last["action"],
                            state,
                            -1
                        )
                        print("no Catch")
                        break       
                # if the game is not over, continue
                else:
                    if ((state[0] >= (state[2] - 12.5)) and (state[0] <= (state[2] + 12.5))):
                        self.update_model(
                            last["state"],
                            last["action"],
                            state,
                            0
                        )
                    
                    '''self.update_model(
                        last["state"],
                        last["action"],
                        state,
                        0
                    )'''
                    #print(state)
        print(f"Catch Count: {catch_count}")
        print(f"Not Catch Count: {count - catch_count}")
        print(f"percentage caugh: {(catch_count/count)*100}")
        #print(self.q.values())
                

            



    