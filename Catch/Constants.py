# Here's a list of constants to make it easier to update aspects of the game.

# Main Window constants
WIDTH = 700
HEIGHT = 600

# Main Menu Constants
GAME_BUTTON_WIDTH = int((WIDTH*0.2)/10)
GAME_BUTTON_HEIGHT = int((HEIGHT*0.05)/10)
AI_GAME_BUTTON_X = int(WIDTH*0.75) - (GAME_BUTTON_WIDTH*10)
AI_GAME_BUTTON_Y = int(HEIGHT*0.75)
PERSON_BUTTON_X = int(WIDTH*0.25)
PERSON_BUTTON_Y = int(HEIGHT*0.75)
TITLE_WIDTH = int(WIDTH * 0.75)
TITLE_HEIGHT = int(HEIGHT * 0.25)
TITLE_FONT_SIZE = 50
TITLE_FONT = ("Helvetica", TITLE_FONT_SIZE)
TITLE_X = int(WIDTH*0.5) - int(TITLE_FONT_SIZE * 1.38)
TITLE_Y = int(HEIGHT*0.2)

# Game Constants
FALL_BALL_RATE = 0.016 # This is hopefully the aprox rate for 1 ball to fall for every half screen drop 
UPDATE = 0.01

# Ball Constants

# User Ball
USER_SIZE = 25
USER_SPEED = WIDTH/100

# Fall Ball
FALL_BALL_SIZE = 15
FALL_SPEED = HEIGHT/125

# AI Constants
TRAIN_N = 1000

