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
    X = BP.PORT_B
    Y = BP.PORT_A
    Z = BP.PORT_C
    H = BP.PORT_D

    px = 100   # power limit for columns
    sx = 500   # speed limit for columns (degree/second)
    dx = -710  # degrees to move 1 column right

    py = 100   # power for rows
    sy = 500   # speed for rows (degree/second)
    dy = 710   # degrees to move 1 row up

    pz = 100   # power limit for lifting
    sz = 500   # speed limit for lifting (degree/second)
    dz = -750  # angle to lift the piece (degrees)
    tz = np.abs(dz/sz)

    pu = 50    # power for closing the grabber
    tu = 0.17  # time to close the grabber

    # initial position
    x0, y0 = (2, 7)

    # current position
    xc, yc = (x0, y0)
    
    def __init__(self):
        """
            Initializes the robot.
        """
        if self.BP.get_voltage_battery() < 7:
            print("Battery voltage is too low (" + str(self.BP.get_voltage_battery())  + "V). Exiting.")
            self.BP.reset_all()
            sys.exit()

        # resets the encoder of the motors and sets the motor limits.
        self.BP.set_motor_limits(self.X, self.px, self.sx)
        self.BP.set_motor_limits(self.Y, self.py, self.sy)
        self.BP.set_motor_limits(self.Z, self.pz, self.sz)
        try:
            self.BP.offset_motor_encoder(self.X, self.BP.get_motor_encoder(self.X)-self.xc*self.dx)
            self.BP.offset_motor_encoder(self.Y, self.BP.get_motor_encoder(self.Y)-self.yc*self.dy)
            self.BP.offset_motor_encoder(self.Z, self.BP.get_motor_encoder(self.Z))
        except IOError as error:
            print(error)
        return
    
    def exit(self):
        """
            Terminates the robot.
        """
        self.BP.reset_all()
        return
    
    def move(self,x1,y1,x2,y2,up,cap):
        """
            Performs a move on the chess board.
        """
        
        # todo rochade
        
        # In case of a capture, first take the captured piece and put it on the side of the board.
        if cap == True:
            self.goto(x2,y2)
            self.down()
            self.close()
            self.up()
            self.goto(8,y2)
            self.open()
            
        self.goto(x1,y1)
        self.down()
        self.close()
        if up == True:
            self.up()
        self.goto(x2,y2)
        if up == True:
            self.down()
        self.open()
        self.up()
        self.goto(x0,y0)
        return
    
    def goto(self,x,y):
        """
            Moves the robot
        """

        # calculate the duration of the move
        t = 1.2 * np.max([np.abs(x-self.xc),np.abs(y-self.yc)])
        
        if t > 0:
            # calculate the speed of each coordinate
            vx = np.abs((x-self.xc)*self.dx/t)
            vy = np.abs((y-self.yc)*self.dy/t)
            
            # set the speed of each motor
            self.BP.set_motor_limits(self.X, self.px, vx)
            self.BP.set_motor_limits(self.Y, self.py, vy)

            # move with correct speed to target position
            self.BP.set_motor_position(self.X, x * self.dx)
            self.BP.set_motor_position(self.Y, y * self.dy)

            # wait until the move is completed
            time.sleep(t)

            # update the current position
            self.xc, self.yc = (x, y)
        return

    def up(self):
        """
            Lift the grabber.
        """
        self.BP.set_motor_position(self.Z, 0)
        time.sleep(self.tz)
        return
        
    def down(self):
        """
            Lower the grabber.
        """
        self.BP.set_motor_position(self.Z, self.dz)
        time.sleep(self.tz)
        return
        
    def close(self):
        """
            Close the grabber.
        """
        self.BP.set_motor_power(self.H, -self.pu)
        time.sleep(self.tu)
        self.BP.set_motor_power(self.H, 0)
        return

    def open(self):
        """
            Open the grabber.
        """
        self.BP.set_motor_power(self.H, self.pu)
        time.sleep(self.tu)
        self.BP.set_motor_power(self.H, 0)
        return
        
    def h(self,t,p):
        self.BP.set_motor_power(self.H, p)
        time.sleep(t)
        self.BP.set_motor_power(self.H, 0)
        return

