import sys
import chess
import robot
import camera

G = chess.Game()
R = robot.Robot()
C = camera.Camera()          

try:
    print("De Schaakturk")
    G.skill_level = int(raw_input("Welk niveau wil je spelen [0..20]? "))
    G.new_game()
    
    while True:
    
        # Take a picture.
        C.picture()
    
        # Improve: detect when the user completed a move.
        m1 = raw_input("> ")
        
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
        p1,x1,y1,p2,x2,y2,lift,castle,ep = G.get_move(m2)
        print("< " + m2)
        R.move(p1,x1,y1,p2,x2,y2,lift,castle,ep)
        #raw_input("please execute " + m2 + " : " + str(G.get_move(m2)))        

        # Update the internal board.
        G.move(m2)

        G.show()

except KeyboardInterrupt:
    R.exit()
    C.save("p")
