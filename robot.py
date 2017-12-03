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

    tsq = 1.1  # time to move over a single square (seconds)

    pz = 100   # power limit for lifting
    sz = 800   # speed limit for lifting (degree/second)
    dz = -900  # angle to lift the piece (degrees)
    hRNB = 50  # extra height of the grabber for rook, knight, and bishop
    hKQ = 100  # extra height of the grabber for king, and queen
    
    pu = 60    # power for closing the grabber
    tu = 0.2   # time to close the grabber
    du = 0.01  # less time to open grabber

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

        self.reset()
        return

    def reset(self):
        """
            Resets the robot to its initial configuration
        """
        self.BP.reset_all()

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
    
    def move(self,p1,x1,y1,p2,x2,y2,lift,castle,ep):
        """
            Performs a move on the chess board.
            p1 is the piece at source location
            x1,y1 is source location
            p2 is the piece at target location (empty string "" if no piece is there)
            x2,y2 is target location
            lift is true, if the piece must be lifted
            castle is true, if the rook must be moved
            ep is true, for en passant capture
        """
        
        # In case of a capture, first take the captured piece and put it on the side of the board.
        if p2 != "":
            self.remove(p2,x2,y2)
            
        # Move the piece from (x1,x2) to (y1,y2)
        self.transport(p1,x1,y1,x2,y2,lift)

        # If move is a castling move, move the rook.
        if castle == True:
            xr1 = 0
            xr2 = 3
            if x2 == 6:
                xr1 = 7
                xr2 = 5
            self.transport("r",xr1,y2,xr2,y2,True)
        
        # If move is en passant, capture the pawn.
        if ep == True:
            self.remove("p",x2,y1)

        # Go to initial position and reset the motors.
        self.goto(self.x0,self.y0)
        time.sleep(0.2)
        self.reset()
        return
        
    def transport(self,p,x1,y1,x2,y2,up):
        """
            Transports a piece p from (x1,y1) to (x2,y2) 
        """
        self.goto(x1,y1)
        self.down(p)
        self.close()
        if up == True:
            self.up(p)
        self.goto(x2,y2)
        if up == True:
            self.down(p)
        self.open()
        self.up(p)
        return
        
    def remove(p,x,y):
        """
            Removes a piece p from (x,y) to an edge of the board. 
        """
        xe = x
        ye = y
        
        # If we are closer to the side, move horizontally.
        if np.abs(y-3.5) <= np.abs(x-3.5):
            if (x <= 3):
                xe = -1
            else: 
                xe = 8
        else:
            if (y <= 3):
                ye = -1
            else:
                ye = 8
                
        # Move the captured piece to the side.
        self.transport(p,x,y,xe,ye,True)
        
        return
        
    def goto(self,x,y):
        """
            Moves the robot
        """

        # calculate the duration of the move
        t = self.tsq * np.max([np.abs(x-self.xc),np.abs(y-self.yc)])
        
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

    def up(self,p):
        """
            Lift the grabber.
        """
        h = 0
        if p.lower() in ["r", "n", "b"]:
            h = self.hRNB
        if p.lower() in ["k", "q"]:
            h = self.hKQ
        self.BP.set_motor_position(self.Z, 0)
        time.sleep(np.abs((self.dz+h)/self.sz))
        return
        
    def down(self,p):
        """
            Lower the grabber.
        """
        h = 0
        if p.lower() in ["r", "n", "b"]:
            h = self.hRNB
        if p.lower() in ["k", "q"]:
            h = self.hKQ
        self.BP.set_motor_position(self.Z, self.dz + h)
        time.sleep(np.abs((self.dz+h)/self.sz))
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
        time.sleep(self.tu-self.du)
        self.BP.set_motor_power(self.H, 0)
        return
        
    def h(self,t,p):
        self.BP.set_motor_power(self.H, p)
        time.sleep(t)
        self.BP.set_motor_power(self.H, 0)
        return

