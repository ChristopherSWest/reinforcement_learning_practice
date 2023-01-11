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
        
        qval = old_q + self.alpha*(reward + self.discount*future_reward-old_q)
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
                #print(state)
            except Exception as e:
                #print('failed to estimate')
                print(e)
                #print(state)
                estimated_values.update({move: 0})
            
        best_moves = [key for key, value in estimated_values.items() if value == max(estimated_values.values())]
        '''for v in estimated_values:
            print(f'{v}: {estimated_values[v]}')'''
        
        #print(estimated_values.values())
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
        # assuming that the particular action was taken. feature value = f(S,A)


        '''fall_balls_amount = len(state["falling_objects"])#(len(state)-2)/2
        user_ball_tuple = (state["player"].x,state["player"].y) #(state[len(state)-2], state[len(state)-1])
        fall_states = []
        states_to_check = []'''
        
        '''for i in range(int(fall_balls_amount*2)):
            if i != 0 and i % 2 != 0:
                fall_states.append(state[i])
                fall_states.append(user_ball_tuple[0])
                fall_states.append(user_ball_tuple[1])
                states_to_check.append((fall_states[0],fall_states[1],fall_states[2],fall_states[3]))
                fall_states = []
            else:
                fall_states.append(state[i])'''

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
                closest_object = [key for key, value in distances.items() if value == min(distances.values())]
                #print(closest_object[0])
                distance = self.get_distance(closest_object[0],state['player'])
                object_copy = deepcopy(closest_object[0])
                #print(f"closest Object: ({closest_object[0].x}, {closest_object[0].y})")
                #print(f"orignial_player: ({state['player'].x}, {state['player'].y})")
                object_copy.change_velocity(0, Constants.FALL_SPEED)
                object_copy.x = object_copy.x + object_copy.xVelocity
                object_copy.y = object_copy.y + object_copy.yVelocity
                new_player_position = deepcopy((state["player"]))
                new_player_position.change_velocity(action[0],action[1])
                new_player_position.x = new_player_position.x + new_player_position.xVelocity
                new_player_position.y = new_player_position.y + new_player_position.yVelocity
                #(closest_state[0][0],closest_state[0][1]+Constants.FALL_SPEED,closest_state[0][2]+action[0],closest_state[0][3])
                new_distance = self.get_distance(object_copy,new_player_position)
                #print(distance)
                #print(f'Action: {action}')
                #print(f"NEW closest Object: ({object_copy.x}, {object_copy.y})")
                #print(f"NEW orignial_player: ({new_player_position.x}, {new_player_position.y})")
                #print(f'new: {new_distance}')
                state_feature = distance - new_distance
                
                #print(f"State_Feature: {state_feature}")
                #print("")
            except Exception as e:
                print(e)
            if action == (-Constants.USER_SPEED,0):
                feature_vector = [state_feature, 0 ,0 ,1]
            elif action == (0,0):
                feature_vector = [0, state_feature, 0 ,1]
            else:
                feature_vector = [0, 0, state_feature, 1]
        finally:
            return feature_vector

    def get_distance(self, falling_object, player):
        # Since the player can move from one side of the screen to the other by moving past the edge of either side, this method
        # will return the closest distance based on that fact. This will require pretending the that the user ball exists at it's current position, + the canvas width on the x axis, and 
        # also - the canvas width on the x value.  This will return the closest distance.
        
        distance_vectors = []
        distances = []

        

        distance_vectors.append([falling_object.x-player.x,falling_object.y-player.y])
        distance_vectors.append([abs(falling_object.x-(player.x+Constants.WIDTH)),abs(falling_object.y-player.y)])
        distance_vectors.append([abs(falling_object.x-(player.x-Constants.WIDTH)),abs(falling_object.y-player.y)])

        
        for distance_vector in distance_vectors:
            #print(math.sqrt((distance_vector[0] * distance_vector[0]) + (distance_vector[1] * distance_vector[1])))
            distances.append(math.sqrt((distance_vector[0] * distance_vector[0]) + (distance_vector[1] * distance_vector[1])))

        distance = min(distances)
        #print(f"Distance: {distance}")
        return distance

    def train(self, n):

        catch_count = 0
        count = 0
        #Play game n times
        
        count+=1
        fall_balls = []
        fall_ball = Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE)
        fall_ball.change_velocity(0, Constants.FALL_SPEED)
        fall_balls.append(fall_ball)
        
        '''f1 = fall_ball[0]
        f2 = fall_ball[1]
        u1 = randrange(Constants.WIDTH)
        u2 = Constants.HEIGHT'''


        #state = (f1, f2, u1, u2)
        #state = [fall_ball,Player(randrange(Constants.WIDTH), Constants.HEIGHT, Constants.USER_SIZE)]
        state = {
            "falling_objects":[fall_ball],
            "player":Player(randrange(Constants.WIDTH), Constants.HEIGHT, Constants.USER_SIZE) 
        }
        
        
        last = {
            "state":None,"action":None
        }
        normalize_ball_drop = 0
        
        # Game loop
        while True:
            #updates decreases epsilon and increases the discount factor based on the number of n
            if self.epsilon > 0.01:
                self.epsilon -= (1/(n*20))
            if self.discount < 0.99:
                self.discount += (1/(n*20))
            state_list = []
            
            action = self.guess_best_move(state)
            
            # Keep track of last state and action
            last["state"] = state
            last["action"] = action
            
            # create a new training fall ball at a certain rate
            normalize_ball_drop += 1
            if randrange(40) < (Constants.FALL_BALL_RATE * 100):
                if normalize_ball_drop >= 30:
                    #state_list.append(Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE))
                    state["falling_objects"].append(Ball(randrange(Constants.WIDTH),0,Constants.FALL_BALL_SIZE))
                    
                    normalize_ball_drop = 0
            
            
            '''#drop all of the fall balls in the current state and append them to the state list
            for k in range(len(state)-2):
                if k % 2 != 0:
                    state_list.append(state[k]+Constants.FALL_SPEED)    
                else:
                    state_list.append(state[k])'''

            # for each falling ball, update x and y
            for k in state["falling_objects"]:
                if isinstance(k, Ball):
                    k.change_velocity(0,Constants.FALL_SPEED)
                    k.x += k.xVelocity
                    k.y += k.yVelocity
            # For Player Apply change velocity based on action and update x and y
            state["player"].change_velocity(action[0],action[1])
            state["player"].x += state["player"].xVelocity
            state["player"].y += state["player"].yVelocity

            #print(f'Player position: {(state["player"].x, state["player"].y)} ')
                    
                    
                    
            
            '''state_list.append(state[len(state)-2]+action[0])
            state_list.append(state[len(state)-1]+action[1])'''

            
            '''# assingn the state as a tuple of the state list
            state = tuple(state_list)'''
            
            #correct for going too far left or right.
            # Too far right
            if state["player"].x > Constants.WIDTH:
                state["player"].x = state['player'].x - Constants.WIDTH
                
            # Too far left
            if state["player"].x < Constants.WIDTH - Constants.WIDTH:
                state["player"].x = (Constants.WIDTH - Constants.WIDTH) + Constants.USER_SIZE#Constants.WIDTH
                
            #print(f'Count: {count},  Epsilon: {self.epsilon}')
            #print(f'ball coords: {state["player"].x}, {state["player"].y}')
            #print(len(state["falling_objects"]))
            for idx, b in enumerate(state["falling_objects"]):
                #print(f"Ball {idx}: ({b.x},{b.y})")
                
            # if ball completes fall, get the proper reward
            
#                if b % 2 != 0:
                if b.y >= Constants.HEIGHT:
                    count += 1

                    #if player catches the ball
                    if ((b.x >= (state["player"].x - (Constants.USER_SIZE/2))) and (b.x <= (state["player"].x + (Constants.USER_SIZE/2)))):
                        self.update_model(
                            last["state"],
                            last["action"],
                            state,
                            -1
                        )
                        catch_count+=1
                        
                        print("catch")
                        print(f"Ball: ({b.x},{b.y})")
                        print(f"Player: ({state['player'].x}, {state['player'].y})")
                        state["falling_objects"].pop(idx)
                        

                    # if player doesn't catch the ball
                    elif ((b.x < (state["player"].x - (Constants.USER_SIZE/2))) or (b.x > (state["player"].x + (Constants.USER_SIZE/2)))):
                        self.update_model(
                            last["state"],
                            last["action"],
                            state,
                            0
                        )
                        print("no Catch")
                        
                        state["falling_objects"].pop(idx)

                '''else:
                    self.update_model(
                        last["state"],
                        last["action"],
                        state,
                        0
                    )'''
            
            if count >= n:
                break