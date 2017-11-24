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
import sys
import time
import brickpi3
import picamera
import cv2
import numpy as np
import subprocess

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

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

def move(m):
    if len(m) == 4:
        x1,y1 = A2C(m[:2])
        x2,y2 = A2C(m[-2:])
        moveto(x1,y1)
        grab()
        moveto(x2,y2)
        drop()
        moveto(x0,y0)
    return

def init():
    # resets the encoder of the motors and sets the motor limits.
    BP.set_motor_limits(X, px, sx)
    BP.set_motor_limits(Y, py, sy)
    BP.set_motor_limits(Z, pz, sz)
    global xc,yc
    try:
        BP.offset_motor_encoder(X, BP.get_motor_encoder(X)-xc*dx)
        BP.offset_motor_encoder(Y, BP.get_motor_encoder(Y)-yc*dy)
        BP.offset_motor_encoder(Z, BP.get_motor_encoder(Z))
    except IOError as error:
        print(error)
    return
	
def moveto(x,y):
    # moves the robot to square (x,y) in {0,...,7}^2 = {a,...,h}x{1,...,8}
    
    # calculate the duration of the move
    global xc,yc
    t = 1.2 * np.max([np.abs(x-xc),np.abs(y-yc)])
    
    if t > 0:
        # calculate the speed of each coordinate
        vx = np.abs((x-xc)*dx/t)
        vy = np.abs((y-yc)*dy/t)
        print([t,vx,vy])
        # set the speed of each motor
        BP.set_motor_limits(X, px, vx)
        BP.set_motor_limits(Y, py, vy)

        # move with correct speed to target position
        BP.set_motor_position(X, x * dx)
        BP.set_motor_position(Y, y * dy)

        # wait until the move is completed
        time.sleep(t)

        # update the current position
        xc, yc = (x, y)
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

def A2C(s):
    # algebraic notation to cartesian coordinates
    x,y = (0,0)
    if len(s) == 2:
       x = np.max([np.min([ord(s[0])-97,7]),0])
       y = np.max([np.min([int(s[1])-1,7]),0])
    return (x,y)

#########################  Main program loop  #################################
	
try:

    if BP.get_voltage_battery() < 7:
        print("Battery voltage is too low (" + str(BP.get_voltage_battery())  + "V). Exiting.")
        BP.reset_all()
        sys.exit()

    init()
		
    while True:
        c = str(raw_input("> "))
        try:
            eval(c)
        except Exception as error:
            print(error)
        time.sleep(0.02) # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.       

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
