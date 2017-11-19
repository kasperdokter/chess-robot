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

import mobility
import vision
	
try:

    if BP.get_voltage_battery() < 7:
        print("Battery voltage is too low (" + str(BP.get_voltage_battery())  + "V). Exiting.")
        BP.reset_all()
        sys.exit()
		
    while True:
        c = str(raw_input("> "))
        try:
            eval(c)
        except Exception as error:
            print(error)

except KeyboardInterrupt:
    BP.reset_all()


 
