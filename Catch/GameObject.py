from random import *

class GameObject:
    def __init__(self, x, y, diameter):
        self.diameter = diameter
        self.x = x
        self.y = y
        self.xVelocity = 0
        self.yVelocity = 0
    
   
    
    def change_velocity(self, xVelocity, yVelocity):
        self.xVelocity = xVelocity
        self.yVelocity = yVelocity    

    