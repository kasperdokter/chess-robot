import sys
import chess
import robot
import camera

G = chess.Game()
R = robot.Robot()
C = camera.Camera()          

try:
    print("Press enter to complete your move.")
    
    G.new_game()
    C.picture()
    
    while True:
    
        # Improve: detect when the user completed a move.
        m1 = raw_input(">")
        
        if m1 == "":
            # Take a picture
            C.picture()
        
            # Get all squares that changed since the previous move.
            #squares = C.changes()
        
            # Use the current position to determine what move is played.
            #print(G.find_move(squares))
        
        # Execute the move on the internal board.
        G.move(m1)

        # Let the engine calculate the best move.
        m2 = G.best_move()
               
        # Perform the move at the chess board.
        x1,y1,x2,y2,lift,cap = G.get_move(m2)
        print("reply " + m2 + " : " + str(G.get_move(m2)))
        R.move(x1,y1,x2,y2,lift,cap)
        #raw_input("please execute " + m2 + " : " + str(G.get_move(m2)))        

        # Update the internal board.
        G.move(m2)

        G.show()

        # Take a picture.
        C.picture()

except KeyboardInterrupt:
    R.exit()
    C.save("p")
