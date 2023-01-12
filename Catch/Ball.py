from random import *
from GameObject import GameObject

class Ball(GameObject):
    def __init__(self, x, y, diameter):
        super().__init__(x, y, diameter)
        
        
    
    def move(self):
        self.coordinates = self.canvas.coords(self.image)
        self.x = (self.coordinates[2]+self.coordinates[0])/2 + self.xVelocity
        self.y = (self.coordinates[3]+self.coordinates[1])/2 + self.yVelocity
        self.center = ((self.coordinates[2]+self.coordinates[0])/2,(self.coordinates[3]+self.coordinates[1])/2)
        self.canvas.move(self.image,self.xVelocity,self.yVelocity)
    
    def change_velocity(self, xVelocity, yVelocity):
        self.xVelocity = xVelocity
        self.yVelocity = yVelocity    

    def delete_ball(self):
        self.canvas.delete(self.image)

    def draw_ball(self, canvas):
        self.canvas = canvas
        self.image = canvas.create_oval(self.x-(self.diameter/2),self.y-(self.diameter/2),self.x+(self.diameter/2),self.y+(self.diameter/2), fill="white")
        self.coordinates = self.canvas.coords(self.image)
        self.x = (self.coordinates[2]+self.coordinates[0])/2
        self.y = (self.coordinates[3]+self.coordinates[1])/2
        self.center = ((self.coordinates[2]+self.coordinates[0])/2,(self.coordinates[3]+self.coordinates[1])/2)
        