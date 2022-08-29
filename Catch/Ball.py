from random import *

class Ball:
    def __init__(self, canvas, x, y, diameter):
        self.canvas = canvas
        self.diameter = diameter
        self.image = canvas.create_oval(x-(self.diameter/2),y-(self.diameter/2),x+(self.diameter/2),y+(self.diameter/2), fill="white")
        self.coordinates = self.canvas.coords(self.image)
        self.center = ((self.coordinates[2]+self.coordinates[0])/2,(self.coordinates[3]+self.coordinates[1])/2)
        self.xVelocity = 0
        self.yVelocity = 0
    
    def move(self):
        self.coordinates = self.canvas.coords(self.image)
        self.center = ((self.coordinates[2]+self.coordinates[0])/2,(self.coordinates[3]+self.coordinates[1])/2)
        #print(self.coordinates, self.center)
        self.canvas.move(self.image,self.xVelocity,self.yVelocity)
        #print(self.canvas.winfo_width())
        


        


    def change_velocity(self, xVelocity, yVelocity):
        self.xVelocity = xVelocity
        self.yVelocity = yVelocity
        
        