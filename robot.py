#!/usr/bin/env python
#
# This code is testing the the chess robot.
# 
# Hardware: Connect EV3 or NXT motor to the BrickPi3 motor port B. Make sure that the BrickPi3 is running on a 9v power supply.
#
# Results:  When you run this program, motor B position will be controlled by up and down arrows.

from __future__ import print_function # use python 3 syntax but make it compatible with python 2
from __future__ import division       #                           ''

import time     # import the time library for the sleep function
import brickpi3 # import the BrickPi3 drivers

BP = brickpi3.BrickPi3() # Create an instance of the BrickPi3 class. BP will be the BrickPi3 object.

P = BP.PORT_B

try:
#    try:
#        BP.offset_motor_encoder(P, BP.get_motor_encoder(P)) # reset encoder B
#    except IOError as error:
#        print(error)

    if BP.get_voltage_battery() < 7:
        print("Battery voltage is too low (" + str(BP.get_voltage_battery())  + "V). Exiting.") )
        SafeExit()

    deg = 0
    BP.set_motor_limits(P, 50, 360)

    while True:
       
        d = int(raw_input("afstand (graden):"))
        deg = deg + d
        print("graden = " + str(deg))
#        try:
#            print("encoder = " + str(BP.get_motor_encoder(P)))
#            print("status = " + str(BP.get_motor_status(P)))
#        except IOError as error:
#            print(error)
        BP.set_motor_position(P, deg)
        
        time.sleep(0.02)  # delay for 0.02 seconds (20ms) to reduce the Raspberry Pi CPU load.

except KeyboardInterrupt: # except the program gets interrupted by Ctrl+C on the keyboard.
    BP.reset_all()        # Unconfigure the sensors, disable the motors, and restore the LED to the control of the BrickPi3 firmware.
