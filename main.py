import sys
import chess
import robot
import camera

G = chess.Game()
R = robot.Robot()
C = camera.Camera()          

try:
    print("Press enter to complete your move, or enter q to quit.")
    
    C.picture()
    
    while True:
    
        # Improve: detect when the user completed a move.
        c = raw_input(">")
        if c == "q":
            break
        
        # Take a picture
        C.picture()
        
        # Get all squares that changed since the previous move.
        squares = C.changes()
        
        # Use the current position to determine what move is played.
        m1 = G.find_move(squares)
        
        # Execute the move on the internal board.
        G.move(m1)
        
        # Let the engine calculate the best move.
        m2 = G.best_move()
        
        # Perform the move at the chess board.
        R.move(G.get_move(m))
        
        # Update the internal board.
        G.move(m2)
        
        # Take a picture.
        C.picture()

except KeyboardInterrupt:
    R.stop()