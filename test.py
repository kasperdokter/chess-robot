import chess
import robot
import camera

G = chess.Game()
C = camera.Camera()
R = robot.Robot()   

try:
    
    c = str(raw_input("> "))
    try:
        print(eval(c))
    except Exception as err:
        print(err)
    
except KeyboardInterrupt:
    R.stop()