from random import random
from collections import deque
from this import d
import numpy as np
import chess
import chess.svg
from random import *
import time
import math
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import SGDRegressor
from copy import deepcopy
import joblib



class ChessAI():

    def __init__(self, alpha=0.1, epsilon=1):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - `action` is a tuple `(i, j)` for an action
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon
        self.reg = SGDRegressor()
        self.reg2 = SGDRegressor()
        self.flip = 0
        self.discount = 1

    def get_state(self, board):
        """
        Converts the fen chessboard format to a 8x8 array that represents the state 
        of the game board
        """
        '''state_dict = {
            "r": -1,
            "n": -1,
            "b": -1,
            "q": -1,
            "k": -1,
            "p": -1,
            "R": 1,
            "N": 1,
            "B": 1,
            "Q": 1,
            "K": 1,
            "P": 1,
        }'''
        state_dict = {
            "r": -0.5,
            "n": -0.3,
            "b": -0.3,
            "q": -0.9,
            "k": -1,
            "p": -0.1,
            "R": 0.5,
            "N": 0.3,
            "B": 0.3,
            "Q": 0.9,
            "K": 1,
            "P": 0.1,
        }
        '''state_dict = {
            "r": 0.5,
            "n": 0.3,
            "b": 0.3,
            "q": 0.9,
            "k": 1,
            "p": 0.1,
            "R": 0.5,
            "N": 0.3,
            "B": 0.3,
            "Q": 0.9,
            "K": 1,
            "P": 0.1,
        }'''
        
        

        rows = board.board_fen().split('/')
        
        state = []

        for row in rows:
            #print(row)
            for letter in row:
                if letter in state_dict.keys():
                    state.append(state_dict[letter])
                else:
                    for i in range(int(letter)):
                        state.append(0)
        array = np.array(state)
        array.reshape(8,8)
        return state
    
    def save_model(self):
        joblib.dump(self.reg, "dubQ1.pkl")
        joblib.dump(self.reg2, "dubQ2.pkl")

    def load_model(self):
        self.reg = joblib.load("dubQ1.pkl")
        self.reg2 = joblib.load("dubQ2.pkl")

    def get_action(self, action):
        action_dict = {
            "a": 0,
            "b": 1,
            "c": 2,
            "d": 3,
            "e": 4,
            "f": 5,
            "g": 6,
            "h": 7,
            "r": 1,
            "n": 2,
            "b": 3,
            "q": 4,
            "k": 5,
            "p": 6,
            "R": 7,
            "N": 8,
            "B": 9,
            "Q": 10,
            "K": 11,
            "P": 12,
        }
        action_int = []
        
        for letter in action:
            if letter in action_dict.keys():
                action_int.append(int(action_dict[letter]))
            else:
                action_int.append(int(letter))
        if len(action_int) == 4:
            action_int.append(0)
        return list(action_int)

   
    def update_model(self, old_state, action, new_state, reward):
        #Try to predict the value of old q.  If the model isn't initialized yet, set old to 0
        
        try:
            if self.flip == 0:
                old = self.reg.predict([self.create_feature_vector(old_state, action)])
            else:
                old = self.reg2.predict([self.create_feature_vector(old_state, action)])
        except:
            old = 0
        best_future = self.best_future_reward(new_state)
        
        self.update_q_model(old_state, action, old, reward, best_future)

    
    
  

    def update_q_model(self, state, action, old_q, reward, future_reward):
        # get a new value estimate using the regression model
        #self.alpha = 1 - (1/len(list(state.legal_moves)))
        qval = old_q + self.alpha * (reward + (self.discount *future_reward) - old_q)
        array_x = self.create_feature_vector(state,action)
        array_y = [qval]
        
        X = np.array(array_x)
        X = X.reshape(1, -1)
        
        Y = np.array(array_y)
        
        
        # Try a partial fit.  if the model hasn't been fitted yet, use the fit method instead
        if self.flip == 0:
            try:
                self.reg.partial_fit(X,Y.ravel())
            except:
                self.reg.fit(X,Y.ravel())
        else:
            try:
                self.reg2.partial_fit(X,Y.ravel())
            except:
                self.reg2.fit(X,Y.ravel())


    def best_future_reward(self, state):
        """
        Given a state `state`, consider all possible `(state, action)`
        pairs available in that state and return the maximum of all
        of their Q-values.

        Use 0 as the Q-value if a `(state, action)` pair has no
        Q-value in `self.q`. If there are no available actions in
        `state`, return 0.
        """
        #gonna assume the next player makes the best move else return 0
        #check if terminal state if it is return 0 else opponent makes move
        
        r = 0

        #flip  a coin 
        self.flip = randrange(2)

        best_new_turn = deepcopy(state)
        
        if bool(best_new_turn.legal_moves) == False:
            return 0
        else:
            #oposite player makes best move based on policy
            copy_state = deepcopy(best_new_turn)
            best_new_turn.push(self.guess_best_move(best_new_turn, custom_epsilon=0, bothQ=True))
            
            move = self.guess_best_move(best_new_turn, custom_epsilon=0)
            try:
                if self.flip == 0:
                    best_reward = self.reg2.predict([self.create_feature_vector(best_new_turn, move)])
                else:
                    best_reward = self.reg.predict([self.create_feature_vector(best_new_turn, move)])
            except:
                best_reward = 0
            return best_reward
            
            
        
            #if terminal after opponent move return 0 else make estimate
            if bool(best_new_turn.legal_moves) == False:
                if best_new_turn.is_checkmate() == True:
                    return 0
                else:
                    return 0
                
            else:
                move = self.guess_best_move(copy_state, custom_epsilon=0)
                try:
                    if self.flip == 0:
                        best_reward = self.reg2.predict([self.create_feature_vector(copy_state, move)])
                    else:
                        best_reward = self.reg.predict([self.create_feature_vector(copy_state, move)])
                except:
                    best_reward = 0
                r += best_reward# * -1
                
                move = self.guess_best_move(best_new_turn, custom_epsilon=0)
                try:
                    if self.flip == 0:
                        best_reward = self.reg2.predict([self.create_feature_vector(best_new_turn, move)])
                    else:
                        best_reward = self.reg.predict([self.create_feature_vector(best_new_turn, move)])
                except:
                    best_reward = 0
                r += best_reward
                return r
                move = self.guess_best_move(copy_state, custom_epsilon=0)
                try:
                    best_opponent_reward = self.reg.predict([self.create_feature_vector(copy_state, move)])
                except:
                    best_reward = 0
                return best_opponent_reward * -1
                if best_new_turn.is_checkmate() == True:
                    return -1
                else:
                    return 0
            #else make best policy move
            
                
                copy_state = deepcopy(best_new_turn)
                best_new_turn.push(self.guess_best_move(best_new_turn,custom_epsilon=0))

                
                # if terminal now, return actual reward value
                
                if bool(best_new_turn.legal_moves) == False:
                    if best_new_turn.is_checkmate() == True:
                        return 1
                    else:
                        return 0
                
                else:
                    # return q estimate
                    move = self.guess_best_move(copy_state, custom_epsilon=0)
                    try:
                        best_reward = self.reg.predict([self.create_feature_vector(best_new_turn, move)])
                    except:
                        best_reward = 0
                    return best_reward


                    '''copy_state = deepcopy(best_new_turn)
                    best_new_turn.push(self.guess_best_move(best_new_turn,custom_epsilon=0))
                    
                    #if terminal after opponent best guess move return negative reward
                    if bool(best_new_turn.legal_moves) == False:
                        move = self.guess_best_move(copy_state, custom_epsilon=0)
                        try:
                            best_opponent_reward = self.reg.predict([self.create_feature_vector(copy_state, move)])
                        except:
                            best_reward = 0
                        return best_opponent_reward * -1
                    #else not terminal after opponent move, return best future reward
                    
                    move = self.guess_best_move(best_new_turn, custom_epsilon=0)
                    try:
                        best_reward = self.reg.predict([self.create_feature_vector(best_new_turn, move)])
                    except:
                        best_reward = 0
            
                
            return best_reward'''
        #raise NotImplementedError

    def get_piece_ave(self, state):
        b_ave = 0
        b_total = 0
        b_count = 0
        w_ave = 0
        w_total = 0
        w_count = 0
        for piece in self.get_state(state):
            if piece < 0:
                b_total += piece
                b_count += 1
            if piece > 0:
                w_total += piece
                w_count += 1
        b_ave = (b_total/b_count) * - 1
        w_ave = (w_total/w_count)

        return b_ave, b_total, b_count, w_ave, w_total, w_count

    def create_feature_vector(self, state, move):
        #self.get_state(state)
        
        #print(move.to_square)
        copy_state = deepcopy(state)
        copy_state.push(move)
        #feature_vector = self.get_state(copy_state)
        feature_vector = [1]
        '''if copy_state.is_checkmate() == True:
            feature_vector.append(1)
        else:
            feature_vector.append(0)'''
        #print(state)
        '''try:
            copy_state.push(move)
        except:
            copy_state.pop()
            copy_state.push(move)'''

        state_vector = []
        copy_vector = []
        state_vector = self.get_state(state)
        copy_vector = self.get_state(copy_state)

        if state.turn == True:
            feature_vector.append(1)
            feature_vector.append(0)
        else:
            feature_vector.append(0)
            feature_vector.append(1)

        if state.is_checkmate() == True:
            feature_vector.append(1)
        else:
            feature_vector.append(0)

        if copy_state.is_checkmate() == True:
            feature_vector.append(1)
        else:
            feature_vector.append(0)

        #feature_vector.append(len(state.attacks(move.from_square))/64)
        #feature_vector.append(len(copy_state.attacks(move.to_square))/64)
        

        if state.is_attacked_by(copy_state.turn, move.from_square) == True:
            feature_vector.append(1)
        else:
            feature_vector.append(0)
        if state.is_attacked_by(state.turn, move.to_square) == True:
            feature_vector.append(1)
        else:
            feature_vector.append(0)

        '''if state.is_pinned(copy_state.turn, move.to_square) == True:
            feature_vector.append(1)
        else:
            feature_vector.append(0)'''
        
        

        '''b_ave, b_total, b_count, w_ave, w_total, w_count = self.get_piece_ave(state)
        copy_b_ave, copy_b_total, copy_b_count, copy_w_ave, copy_w_total, copy_w_count = self.get_piece_ave(copy_state)

        feature_vector.append(w_count/64)
        feature_vector.append(copy_w_count/64)
        
        feature_vector.append(b_count/64)
        feature_vector.append(copy_b_count/64)

        feature_vector.append(w_ave)
        feature_vector.append(copy_w_ave)
        feature_vector.append(b_ave)
        feature_vector.append(copy_b_ave)
        #feature_vector.append(1-(1/state.legal_moves.count()))
        #feature_vector.append(1-(1/copy_state.legal_moves.count()))
        
        #print(feature_vector)
        #print(self.get_action(str(move)))
        #feature_vector.append(1)
        #print(feature_vector)'''
        return feature_vector



    def guess_best_move(self, state, custom_epsilon=None,bothQ=None):
        # Guess the best move to take based on the prediciting the value of the state/action pair.
        # Will select a random move with the probability of epsilon
        random_number = randrange(100)
        estimated_values = {}
        best_moves = []
        available_moves = list(state.legal_moves)
        for move in available_moves:
            try:
                q1 = self.reg.predict([self.create_feature_vector(state, move)])
                
            except Exception as e:
                #print(e)
                q1 = 0
            try:
                q2 = self.reg2.predict([self.create_feature_vector(state, move)])
                
            except Exception as e:
                #print(e)
                q2 = 0
            dq = (q1 + q2)/2    
            
            if bothQ==True:
                estimated_values.update({move: dq})
            elif self.flip == 0:
                estimated_values.update({move: q1})
            elif self.flip == 1:
                estimated_values.update({move: q2})    


        best_moves = [key for key, value in estimated_values.items() if value == max(estimated_values.values())]
        
        #print(estimated_values)
        if random_number <= self.epsilon * 100 and custom_epsilon is None:
            return sample(available_moves,1)[0]
        else:
            if len(best_moves) > 1:
                best = sample(best_moves,1)[0]#best_moves[randrange(len(best_moves))]
                '''print(state)
                print(best)'''
                
                return best
            else:
                #print(best_moves[0])

                return best_moves[0]


    def choose_action(self, board):
        """
        Given a state `state`, return an action `(i, j)` to take.

        If `epsilon` is `False`, then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).

        If `epsilon` is `True`, then with probability
        `self.epsilon` choose a random available action,
        otherwise choose the best action available.

        If multiple actions have the same Q-value, any of those
        options is an acceptable return value.
        """
        
        moves = list(board.legal_moves)
        
        action = sample(moves,1)[0]

            

        return(action)

        
        
        raise NotImplementedError




    
def train(n,reload=None):
    """
    Train an AI by playing `n` games against itself.
    """
    
    player = ChessAI()
    if n == 0:
        player.epsilon = 0.05
        player.load_model()
        return player
    elif reload == True:
        player.load_model()
    
    checkmate_count = 0
    count = 0
    # Play n games
    for i in range(n):

        if player.discount < 0.1:
            player.discount += 1/n
        count += 1
        print(f"Playing training game {i + 1}")
        piece_value = {
            1:1,
            2:3,
            3:3,
            4:5,
            5:9
        }
        
        game = chess.Board()
        '''if len(player.q) % 50 == 0 and len(player.q) > 0:
            states, actions, rewards, next_states = player.sample()
            print(f"state: {states}, actions{actions}, rewards: {rewards}, next_states: {next_states}")'''
            

        # Keep track of last move made by either player
        last = {
            False: {"state": None, "action": None},
            True: {"state": None, "action": None}
        }
        if player.epsilon > 0.09:
                player.epsilon -= (1/(n/4))
        # Game loop
        while game.is_game_over() == False:
            #print(player.epsilon)
            
            
            
            #player.alpha = 1 - (checkmate_count/count)    
            
            

            # Keep track of current state and action
            state = deepcopy(game)
            action = player.guess_best_move(game, bothQ=True)#player.choose_action(game, epsilon)
                        
            
            # Keep track of last state and action
            last[game.turn]["state"] = state
            last[game.turn]["action"] = action
            
            # Make move
            game.push(action)
            new_state = deepcopy(game)
            
            
            # When game is over, update Q values with rewards
            if game.is_checkmate() == True:
                
                
                #player.update_model(game_copy, action, game, -5)
                
                
                checkmate_count += 1   
                print(f"Checkmate ratio: {(checkmate_count/count*100)}")
                
                player.update_model(state, action, new_state, -1)
                #if game.turn == False:
                player.update_model(
                    last[game.turn]["state"],
                    last[game.turn]["action"],
                    new_state,
                    1
                )
                '''elif game.turn == True:
                    player.update_model(
                        game_copy,
                        action,
                        game,
                        -1
                    )'''
                break
            elif game.is_game_over() == True and game.is_checkmate() == False:
                player.update_model(state, action, new_state, 0)
                player.update_model(
                    last[game.turn]["state"],
                    last[game.turn]["action"],
                    new_state,
                    0
                )
                break
            
                
            # If game is continuing, no rewards yet
            
            elif game.is_game_over() == False:
                player.update_model(state, action, new_state, 0)
                try:
                    player.update_model(
                        last[game.turn]["state"],
                        last[game.turn]["action"],
                        new_state,
                        0
                        )
                except:
                    player.update_model(state, action, new_state, 0)

    print("Done training")

    # Return the trained AI
    player.save_model()
    return player

def play(ai, human_player=None):
    """
    Play human game against the AI.
    `human_player` can be set to 0 or 1 to specify whether
    human player moves first or second.
    """
    
    # If no player order set, choose human's order randomly
    if human_player is None:
        #human_player = randint(0, 1)
        human_player = False
    else:
        human_player = True
    # Create new game
    board = chess.Board()

    # Game loop
    while True:
        
        if board.result() != '*':
            decision = input("Would you like to play again on this model?  Y/E")
            if decision.capitalize() == 'Y':
                board.reset()
            else:    
                break
        # Print the boardgame
        
        moves = list(board.legal_moves)
        
        #time.sleep(1)
        if board.turn == chess.WHITE:
            print("White's turn")
            if bool(board.legal_moves):
                #board.push(ai.choose_action(board))
                board.push(ai.guess_best_move(board,custom_epsilon=0,bothQ=True))
                
                
            else: print(moves)
        else:
            print("Black's turn")
            if bool(board.legal_moves):

                #move = chess.Move.from_uci(str(ai.choose_action(board)))
                if human_player == False:
                    board.push(ai.choose_action(board))
                    #board.push(ai.guess_best_move(board,custom_epsilon=0,bothQ=True))

                human_move = ""
                while board.turn == chess.BLACK and human_player == True:
                    try:
                        human_move = input()
                        hmove = chess.Move.from_uci(human_move)
                        if hmove in moves:
                            board.push(hmove)
                        else:
                            raise Exception("illegal move")
                    except Exception as e:
                        print("not a move, dumb dumb")      
                        print(e)
                if human_move == "exit":
                    break
        
        print(board)
        if board.turn == chess.BLACK:
            print(f"White's move: {board.peek()}")
        else:
            print(f"Black's move: {board.peek()}")
        print("")
        print("")

        print(board.result())

        # Compute available actions
        

        # Let human make a move
        
        # Have AI make a move
        

        # Make move
        

        # Check for winner
        
