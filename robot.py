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

import io
import time
import brickpi3
#import picamera
#import cv2
import numpy as np

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

X = BP.PORT_A
Y = BP.PORT_C
Z = BP.PORT_B
H = BP.PORT_D

px = 100   # power limit for columns
sx = 500   # speed limit for columns (degree/second)
dx = -733  # degrees to move 1 column right

py = 100   # power for rows
sy = 500   # speed for rows (degree/second)
dy = 733   # degrees to move 1 row up

pz = 100   # power limit for lifting
sz = 500   # speed limit for lifting (degree/second)
dz = -900  # angle to lift the piece (degrees)
tz = 2     # time to lift and lower the grabber (second)

pu = 100   # power for closing the grabber
tu = 0.1   # time to close the grabber

def x(d):
    try:
        BP.set_motor_position(X, BP.get_motor_encoder(X) + d)
    except IOError as error:
        print(error)
    return

def y(d):
    try:
        BP.set_motor_position(Y, BP.get_motor_encoder(Y) + d)
    except IOError as error:
        print(error)
    return

def z(d):
    try:
        BP.set_motor_position(Z, BP.get_motor_encoder(Z) + d)
    except IOError as error:
        print(error)
    return

def h(t, p):
    BP.set_motor_power(H, p)
    time.sleep(t)
    BP.set_motor_power(H, 0)
    return

#def pic():
#    stream = io.BytesIO()
#    with picamera.PiCamera() as camera:
#        camera.start_preview()
#        time.sleep(2)
#        camera.capture(stream, format='jpeg')
#    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
#    img = cv2.imdecode(data, 1)
#    cv2.imshow('image', img)
#    cv2.waitkey(0)
#    cv2.destroyAllWindows()
#    return

#########################  Functions for robot movement  #################################


def initialize():
    # resets the encoder of the motors and sets the motor limits.
    BP.set_motor_limits(Z, pz, sz)
    BP.set_motor_limits(Y, py, sy)
    BP.set_motor_limits(X, px, sx)
    try:
        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))
        BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C))
    except IOError as error:
        print(error)
    return
	
def mv(x,y):
    # moves the robot to square (x,y) in {0,...,7}^2 = {a,...,h}x{1,...,8}
    BP.set_motor_position(X, x * dx)
    BP.set_motor_position(Y, y * dy)
    return

def up():
    # lift the grabber
    BP.set_motor_position(Z, 0)
    time.sleep(tz)
    return
	
def down():
    # lower the grabber
    BP.set_motor_position(Z, dz)
    time.sleep(tz)
    return
	
def close():
    # close the grabber
    BP.set_motor_power(H, -pu)
    time.sleep(tu)
    BP.set_motor_power(H, 0)
    return

def open():
    # open the grabber
    BP.set_motor_power(H, pu)
    time.sleep(tu)
    BP.set_motor_power(H, 0)
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

    initialize()
		
    while True:
        c = str(raw_input("> "))
        try:
            eval(c)
        except Exception as error:
            print(error)
        time.sleep(0.02) # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.       

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
