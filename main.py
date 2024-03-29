import sys
import chess
import robot
import camera

G = chess.Game()
R = robot.Robot()
C = camera.Camera()          

try:
    G.skill_level = int(raw_input("Welk niveau wil je spelen [0..20]? "))
    G.new_game()
    
    while True:

        print("Even wachten aub...")

        # Take a picture.
        #C.picture()

        #Improve: detect when the user completed a move.
        raw_input("Speel een zet en geef enter.")
        
        # Take a picture
        #C.picture()
        
        # Get all squares that changed since the previous move.
        #squares = C.changes()
        
        # Use the current position to determine what move is played.
        #m1 = G.find_move(squares)
        m1 = "a2a3"
	a = raw_input("Heb je " + m1 +" gespeeld?")
        if a != "":
            m1 = a
        print("> " + m1)
                   
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

        C.s = False

except KeyboardInterrupt:
    R.exit()
    C.save("p")
