#!/usr/bin/env python
#
# This code controls a chess robot.
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

from __future__ import print_function 
from __future__ import division

import io
import sys
import cv2
import time
import brickpi3
import picamera
import numpy as np
import subprocess

# Create a BrickPi3 object.
BP = brickpi3.BrickPi3() 

# Start the stockfish engine.
stockfish = subprocess.Popen(["/usr/games/stockfish"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

############################  Parameters  #############################

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

###########################  Moving pieces  ###########################

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
    
#############################  Utilities  #############################

def A2C(s):
    # algebraic notation to cartesian coordinates
    x,y = (0,0)
    if len(s) == 2:
       x = np.max([np.min([ord(s[0])-97,7]),0])
       y = np.max([np.min([int(s[1])-1,7]),0])
    return (x,y)
    
    
#############################  Stockfish  #############################

def get_best_move(moves_list, move_time, skill_level):
	"""
	>>> get_best_move([], '500', '20')
	(u'e2e4', '')
	"""
	moves_as_str = ' '.join(moves_list)
	stockfish.stdin.write(('setoption name Threads value 1\n').encode('utf-8'))
	stockfish.stdin.flush()
	stockfish.stdin.write(('setoption name Hash value 512\n').encode('utf-8'))
	stockfish.stdin.flush()
	stockfish.stdin.write(('setoption name OwnBook value true\n').encode('utf-8'))
	stockfish.stdin.flush()
	stockfish.stdin.write(('setoption name Skill Level value ' + skill_level + '\n').encode('utf-8'))
	stockfish.stdin.flush()
	stockfish.stdin.write(('position startpos moves ' + moves_as_str + '\n').encode('utf-8'))
	stockfish.stdin.flush()
	stockfish.stdin.write(('go wtime ' + move_time + ' btime ' + move_time + '\n').encode('utf-8'))
	stockfish.stdin.flush()

	bestmove = "";
	analysis = "";

	while True:
		line = stockfish.stdout.readline().decode().rstrip()
		if "score cp" in line or "score mate" in line:
			analysis = line.split('multipv')[0]
		if "bestmove" in line:
			bestmove = line
			break
	
	return bestmove.split()[1], analysis

print(get_best_move(["e2e4"], '2000', '20'))

##############################  Vision  ###############################

def pic():
    stream = io.BytesIO()
    with picamera.PiCamera() as camera:
        camera.start_preview()
        time.sleep(2)
        camera.capture(stream, format='jpeg')
    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
    img = cv2.imdecode(data, 1)
    cv2.imshow('image', img)
    cv2.waitkey(0)
    cv2.destroyAllWindows()
    return
   
def detectMove(img1, img2):
    """Detects a move by comparing two images. The first image captures 
    the initial position and the second image captures the position after
    the move.

    Args:
        img1 (numpy.ndarray): The first image.
        img2 (numpy.ndarray): The second image.

    Returns:
        string: textual representation of the move.
    """
    
    # Convert to gray scale
    img1_gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    
    # Initiate STAR detector
    orb = cv2.ORB_create()

    # Find the keypoints and descriptors with ORB
    kp1, des1 = orb.detectAndCompute(img2_gray,None)
    kp2, des2 = orb.detectAndCompute(img1_gray,None)

    # Create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1,des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key = lambda x:x.distance)
    
    # Find the best matches.
    good = matches[:10]

    # Reformat the source and target points.
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

    # Compute the 3x3 transformation matrix.
    M, mask = cv2.findHomography(src_pts,dst_pts,cv2.RANSAC,5.0)

    # Get the size of the second image
    rows,cols = img2_gray.shape
    
    # Align the second image.
    img3_gray = cv2.warpPerspective(img2_gray, M, (cols, rows))
    
    # Blur the second image and the aligned version of the second image
    blur_img1 = cv2.blur(img1_gray,(45,45))
    blur_img3 = cv2.blur(img3_gray,(45,45))
    
    # Take the absolute difference of the these images
    diff = cv2.absdiff(blur_img1,blur_img3)
    
    # Transform the gray scale difference to black and white via threshholding
    ret,thresh = cv2.threshold(diff,27,255,cv2.THRESH_BINARY)
    
    squares = []
    for x in range(8):
       for y in range(8):
          mask = np.zeros(thresh.shape, np.uint8)
          mask = cv2.circle(mask, (900+1850*x/7-20*y/7,400+1840*y/7), 100, 255, -1) #TODO
          m = cv2.mean(thresh, mask)
          if (m[0] > 50):
              squares.append((x,y))   
              
    print(squares)
    
    return

############################  Fine-tuning  ############################

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
    
#########################  Main program loop  #########################
	
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

except KeyboardInterrupt:
    BP.reset_all()