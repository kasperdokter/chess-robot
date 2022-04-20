import numpy as np
import subprocess

class Game:
    
    # Start the stockfish engine 
    stockfish = subprocess.Popen(["/usr/games/stockfish"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # ./stockfish_8_x64.exe    

    # Skill level (0,...,20)
    skill_level = 6
    
    # Time that the computer can think.
    move_time = 2

    # Moves of the game
    moves = []

    # Current position at the board
    position = {}
    
    def new_game(self):
        """
            Set up the initial position and clears the move list.
        """
        self.moves = []
        self.position = { 
            "a1" : "r", "b1" : "n", "c1" : "b", "d1" : "q", "e1" : "k", "f1" : "b", "g1" : "n", "h1" : "r", 
            "a2" : "p", "b2" : "p", "c2" : "p", "d2" : "p", "e2" : "p", "f2" : "p", "g2" : "p", "h2" : "p", 
            "a7" : "P", "b7" : "P", "c7" : "P", "d7" : "P", "e7" : "P", "f7" : "P", "g7" : "P", "h7" : "P", 
            "a8" : "R", "b8" : "N", "c8" : "B", "d8" : "Q", "e8" : "K", "f8" : "B", "g8" : "N", "h8" : "R" 
        }
        
    def get_move(self,m):
        """
            Transform the move into a format understandable for the robot.
        """
        s1 = m[:2]
        s2 = m[2:4]
        
        p1 = self.position[s1]
        x1,y1 = self.a2c(s1)
        
        p2 = ""
        if self.position.has_key(s2):
            p2 = self.position[s2]
        x2,y2 = self.a2c(s2)
        
        lift = self.need_lift(m)
        castle = self.is_castle(m)
        ep = self.is_enpassant(m)
        
        return p1,x1,y1,p2,x2,y2,lift,castle,ep

    def is_castle(self,m):
        """
            Checks if the move is a castling move.
        """
        s1 = m[:2]
        s2 = m[2:4]
        if s1 == "e1" and self.position.has_key("e1"):
            if self.position["e1"] == "k" and (s2 == "c1" or s2 == "g1"):
                return True  
        
        if s1 == "e8" and self.position.has_key("e8"):
            if self.position["e8"] == "K" and (s2 == "c8" or s2 == "g8"):
                return True

        return False

    def is_enpassant(self,m):
        """
            Checks if the move is an en passant capture
        """
        s1 = m[:2]
        s2 = m[2:4]
        if self.position.has_key(s1) and not self.position.has_key(s2):
            if self.position[s1].lower() == "p" and m[0] != m[2]:
                return True
        return False
        
    def need_lift(self,m):
        """
            Determines whether the grabber must be lifted, such that the robot does not knock over other pieces.
            
            :param string m: Simplified algebraic notation of the move (such as g1f3 for Ng1-f3 and e1g1 for 0-0).
        """

        # Never lift a pawn
        if self.position[m[:2]] == "p" or self.position[m[:2]] == "P":
            return False

        x1,y1 = self.a2c(m[:2])
        x2,y2 = self.a2c(m[2:4])

        # If the move is vertical, check for obstacles.
        if x1 == x2:
            for t in range(1,y2-y1):
                if self.position.has_key(self.c2a(x1,y1+t)):
                    return True
            return False

        # If the move is horizontal, check for obstacles.
        if y1 == y2:
            for t in range(1,x2-x1):
                if self.position.has_key(self.c2a(x1+t,y1)):
                    return True
            return False

        # If the move is diagonal, check for obstacles below, above, and on the diagonal.
        if np.abs(x2-x1) == np.abs(y2-y1):
            if self.position.has_key(self.c2a(x1+np.sign(x2-x1),y1)):
                return True
            if self.position.has_key(self.c2a(x1,y1+np.sign(y2-y1))):
                return True
            for t in range(1,np.abs(x2-x1)):
                if self.position.has_key(self.c2a(x1+np.sign(x2-x1)*(t+1),y1+np.sign(y2-y1)*t)):
                    return True
                if self.position.has_key(self.c2a(x1+np.sign(x2-x1)*t,y1+np.sign(y2-y1)*(t+1))):
                    return True
                if self.position.has_key(self.c2a(x1+np.sign(x2-x1)*t,y1+np.sign(y2-y1)*t)):
                    return True
            return False

        # By default, the piece must be lifted.
        return True
        
    def move(self,m):
        """
            Executes a move.
            
            :param string m: Simplified algebraic notation of the move (such as g1f3, e1g1 (0-0), d7d8q (promotion)).
        """
        s0 = m[:2]
        s1 = m[2:4]

        castle = self.is_castle(m)
        enpass = self.is_enpassant(m)

        if self.position.has_key(s0):

            # Get the piece
            p = self.position[s0]
            
            # Update, if case of promotion
            if len(m) == 5:
                p = m[4]
            
            # Drop the piece
            self.position[s1] = p
            del self.position[s0]
            
            # For castling, move the rook
            if castle:
                if s1[0] == "c":
                    self.position["d" + m[1]] = "r"
                    del self.position["a" + m[1]]
                else:
                    self.position["f" + m[1]] = "r"
                    del self.position["h" + m[1]]
            
            # En passant capture
            if enpass:
                del self.position[m[2]+m[1]]
            
        self.moves.append(m)
        return
        
    def show(self):
        """
            Prints the current position and all moves to the console
        """
        print("moves " + ' '.join(self.moves))
        for y in range(8):
            line = ""
            for x in range(8):
                s = self.c2a(x,7-y)
                if self.position.has_key(s):
                    line += self.position[s]
                else:
                    line += "-"
            print(line)
        return
        
    def best_move(self):
        """
            Invokes Stockfish to calculate the best move in the current position.
            
            :param int move_time: Time that the engine is allowed to think in seconds.
        """
        move_string = ' '.join(self.moves)
        
        self.stockfish.stdin.write(('setoption name Skill Level value ' + str(self.skill_level) + '\n').encode('utf-8'))
        self.stockfish.stdin.flush()
        self.stockfish.stdin.write(('position startpos moves ' + move_string + '\n').encode('utf-8'))
        self.stockfish.stdin.flush()
        self.stockfish.stdin.write(('go movetime ' + str(1000 * self.move_time) + '\n').encode('utf-8'))
        self.stockfish.stdin.flush()

        while True:
            line = self.stockfish.stdout.readline().decode().rstrip()
            if "bestmove" in line:
                return line.split()[1]
        
        return
                
    def find_move(self,squares):
        """
            Find the move from a list of squares that changed.
        """
        sqrs = [self.c2a(x,y) for (x,y) in squares]
        if set(sqrs) == set(["e1","f1","g1","h1"]):
            return "e1g1"
        if set(sqrs) == set(["a1","c1","d1","e1"]):
            return "e1c1"
        if set(sqrs) == set(["e8","f8","g8","h8"]):
            return "e8g8"
        if set(sqrs) == set(["a8","c8","d8","e8"]):
            return "e8c8"

        s1 = "a1"
        s2 = "a1"
        for (x,y) in squares:
            s = self.c2a(x,y)
            if self.position.has_key(s):
                if (len(self.moves) % 2 == 0) == self.position[s].islower():
                    s1 = s
                else:
                    s2 = s
            else:
                s2 = s
        return s1 + s2
                
    def a2c(self,s):
        """
            From algebraic notation to cartesian coordinates.
            If the string is invalid, it returns (0,0).
            
            :param string S: square (such as a1, h8). 
        """
        x,y = (0,0)
        if len(s) == 2:
            x = np.max([np.min([ord(s[0])-97,7]),0])
            y = np.max([np.min([int(s[1])-1,7]),0])
        return (x,y)
    
    def c2a(self,x,y):
        """
            From cartesian coordinates to algebraic notation.
            
            :param int x: Column 0=a, 7=h.
            :param int y: Row 0=1, 7=8.
        """
        return chr(x + 97) + str(y+1)
