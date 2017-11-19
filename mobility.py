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

#from __future__ import print_function # use python 3 syntax but make it compatible with python 2
#from __future__ import division       #                           ''

import time
import brickpi3

BP = brickpi3.BrickPi3()

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

########################################################################################

def A(d):
    try:
        BP.set_motor_position(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A) + d)
    except IOError as error:
        print(error)
    return

def B(d):
    try:
        BP.set_motor_position(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B) + d)
    except IOError as error:
        print(error)
    return

def C(d):
    try:
        BP.set_motor_position(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C) + d)
    except IOError as error:
        print(error)
    return

########################################################################################

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

########################################################################################
	
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


 
