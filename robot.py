#!/usr/bin/env python
#
# This code is testing the the chess robot.
# 
# Hardware: Connect the following EV3 or NXT motors to the BrickPi3 motor ports: 
#   port A : motor for lifting pieces
#   port B : motor for vertical position (row 1,...,8)
#   port C : motor for horizontal position (column a,...,h)
#   port D : motor for grabbing pieces
# 
# Make sure that robot is positioned at square a1 with an open grabber fully lifted.
#
# Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  ...

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import numpy as np  # import the mathematical functions
import time         # import the time library for the sleep function
import brickpi3     # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

px = 50    # power limit for columns
sx = 360   # speed limit for columns (degree/second)
dx = -235  # degrees to move 1 column right

py = 50    # power for rows
sy = 360   # speed for rows (degree/second)
dy = -2200 # degrees to move 1 row up

pz = 50    # power limit for lifting
sz = 360   # speed limit for lifting (degree/second)
dz = 10    # angle to lift the piece (degrees)
tz = 2     # time to lift and lower the grabber (second)

pu = 30    # power for closing the grabber
tu = 0.9   # time to close the grabber

#########################  functions for easy finetuning  #################################

def set_px(a):
    global px
    px = a
    return
	
def set_sx(a):
    global sx
    sx = a
    return
	
def set_dx(a):
    global dx
    dx = a
    return
	
	
def set_py(a):
    global py
    py = a
    return
	
def set_sy(a):
    global sy
    sy = a
    return
	
def set_dy(a):
    global py
    dy = a
    return
	
	
def set_pz(a):
    global pz
    pz = a
    return
	
def set_sz(a):
    global sz
    sz = a
    return
	
def set_dz(a):
    global dz
    dz = a
    return
	
def set_tz(a):
    global tz
    tz = a
    return
	
	
def set_pu(a):
    global pu
    pu = a
    return
	
def set_tu(a):
    global tu
    tu = a
    return
	

#########################  Functions for robot movement  #################################


def initialize():
    # resets the encoder of the motors and sets the motor limits.
    BP.set_motor_limits(BP.PORT_A, pz, sz)
    BP.set_motor_limits(BP.PORT_B, py, sy)
    BP.set_motor_limits(BP.PORT_C, px, sx)
    try:
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_A))
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))
        BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C))
    except IOError as error:
        print(error)
    return
	
def moveto(x,y):
    # moves the robot to square (x,y) in {0,...,7}^2 = {a,...,h}x{1,...,8}
    BP.set_motor_position(BP.PORT_C, x * dx)
    BP.set_motor_position(BP.PORT_B, y * dy)
    return

def up():
    # lift the grabber
    BP.set_motor_position(BP.PORT_A, 0)
    time.sleep(tz)
    return
	
def down():
    # lower the grabber
    BP.set_motor_position(BP.PORT_A, dz)
    time.sleep(tz)
    return
	
def close():
    # close the grabber
    BP.set_motor_power(BP.PORT_D, pu)
    time.sleep(tu)
    BP.set_motor_power(BP.PORT_D, 0)
    return

def open():
    # open the grabber
    BP.set_motor_power(BP.PORT_D, -pu)
    time.sleep(tu)
    BP.set_motor_power(BP.PORT_D, 0)
    return
	
def grab():
    # picks up a piece at the current position
    down()
    close()
    up()
    return

def drop():
    # drops a piece at the current position
    down()
    open()
    up()
    return


#########################  Main program loop  #################################
	
try:

    if BP.get_voltage_battery() < 7:
        print("Battery voltage is too low (" + str(BP.get_voltage_battery())  + "V). Exiting.")
        SafeExit()
		
    while True:
        c = str(raw_input("> "))
        try:
            eval(c)
        except Exception as error:
            print(error)
        time.sleep(0.02) # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.       

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
