from __future__ import print_function 
from __future__ import division

import sys
import time
import brickpi3
import numpy as np

class Robot:

    # Create a BrickPi3 object.
    BP = brickpi3.BrickPi3() 
    
    # Ports of motors.
    X = BP.PORT_A
    Y = BP.PORT_C
    Z = BP.PORT_B
    H = BP.PORT_D

    px = 100   # power limit for columns
    sx = 500   # speed limit for columns (degree/second)
    dx = 710   # degrees to move 1 column right

    py = 100   # power for rows
    sy = 500   # speed for rows (degree/second)
    dy = -710  # degrees to move 1 row up

    pz = 100   # power limit for lifting
    sz = 500   # speed limit for lifting (degree/second)
    dz = -900  # angle to lift the piece (degrees)
    tz = np.abs(dz/sz)

    pu = 100   # power for closing the grabber
    tu = 0.17  # time to close the grabber

    # initial position
    x0, y0 = (4, 7)

    # current position
    xc, yc = (x0, y0)
    
    def __init__(self):
        """
            Initializes the robot.
        """
        if BP.get_voltage_battery() < 7:
            print("Battery voltage is too low (" + str(BP.get_voltage_battery())  + "V). Exiting.")
            BP.reset_all()
            sys.exit()

        # resets the encoder of the motors and sets the motor limits.
        BP.set_motor_limits(X, px, sx)
        BP.set_motor_limits(Y, py, sy)
        BP.set_motor_limits(Z, pz, sz)
        try:
            BP.offset_motor_encoder(X, BP.get_motor_encoder(X)-xc*dx)
            BP.offset_motor_encoder(Y, BP.get_motor_encoder(Y)-yc*dy)
            BP.offset_motor_encoder(Z, BP.get_motor_encoder(Z))
        except IOError as error:
            print(error)
        return
    
    def exit(self):
        """
            Terminates the robot.
        """
        BP.reset_all()
        return
    
    def move(self,x1,y1,x2,y2,up,cap):
        """
            Performs a move on the chess board.
        """
        
        # todo rochade
        
        # In case of a capture, first take the captured piece and put it on the side of the board.
        if cap == True:
            self.moveto(x2,y2)
            down()
            close()
            up()
            self.moveto()
            
        self.moveto(x1,y1)
        self.down()
        self.close()
        if up == True:
            self.up()
        moveto(x2,y2)
        if up == True:
            self.down()
        open()
        up()
        moveto(x0,y0)
        return
    
    def moveto(self,x,y):
        """
            Moves the robot to square (x,y) in {0,...,7}^2 = {a,...,h}x{1,...,8}
        """      
        # calculate the duration of the move
        t = 1.2 * np.max([np.abs(x-self.xc),np.abs(y-self.yc)])
        
        if t > 0:
            # calculate the speed of each coordinate
            vx = np.abs((x-self.xc)*self.dx/t)
            vy = np.abs((y-self.yc)*self.dy/t)
            
            # set the speed of each motor
            BP.set_motor_limits(self.X, self.px, vx)
            BP.set_motor_limits(self.Y, self.py, vy)

            # move with correct speed to target position
            BP.set_motor_position(self.X, x * self.dx)
            BP.set_motor_position(self.Y, y * self.dy)

            # wait until the move is completed
            time.sleep(t)

            # update the current position
            self.xc, self.yc = (x, y)
        return

    def up(self):
        """
            Lift the grabber.
        """
        BP.set_motor_position(self.Z, 0)
        time.sleep(self.tz)
        return
        
    def down(self):
        """
            Lower the grabber.
        """
        BP.set_motor_position(self.Z, self.dz)
        time.sleep(self.tz)
        return
        
    def close(self):
        """
            Close the grabber.
        """
        BP.set_motor_power(self.H, -self.pu)
        time.sleep(self.tu)
        BP.set_motor_power(self.H, 0)
        return

    def open(self):
        """
            Open the grabber.
        """
        BP.set_motor_power(self.H, self.pu)
        time.sleep(self.tu)
        BP.set_motor_power(self.H, 0)
        return
        

