import chess
import robot
import camera

G = chess.Game()
C = camera.Camera()
R = robot.Robot()   

try:

    while True:
        c = str(raw_input("> "))
        if c == "q":
            break
        try:
            print(eval(c))
        except Exception as err:
            print(err)
    R.exit()    

except KeyboardInterrupt:
    R.exit()
