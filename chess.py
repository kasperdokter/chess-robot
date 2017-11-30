import numpy as np
import subprocess

class Game:
    
    # Start the stockfish engine 
    stockfish = subprocess.Popen(["/usr/games/stockfish"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    # ./stockfish_8_x64.exe    

    # Skill level (0,...,20)
    skill_level = 3
    
    # Time that the computer can think.
    move_time = 1

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
        x1,y1 = self.a2c(m[:2])
        x2,y2 = self.a2c(m[2:])
        return x1,y1,x2,y2,self.need_lift(m),self.is_capture(m)
        
    def need_lift(self,m):
        """
            Determines whether the grabber must be lifted, such that the robot does not knock over other pieces.
            
            :param string m: Simplified algebraic notation of the move (such as g1f3 for Ng1-f3 and e1g1 for 0-0).
        """
        x1,y1 = self.a2c(m[:2])
        x2,y2 = self.a2c(m[2:])
        if x1 == x2:
            for t in range(1,y2-y1):
                if self.position.has_key(self.c2a(x1,y1+t)):
                    return True
            return False
                    
        if y1 == y2:
            for t in range(1,x2-x1):
                if self.position.has_key(self.c2a(x1+t,y1)):
                    return True
            return False
            
        #if np.abs(x2-x1) == np.abs(y2-y1):
        #    for t in range(1,np.abs(x2-x1)):
        #        print (self.c2a(x1+np.sign(x2-x1)*t,y1+np.sign(y2-y1)*t))
        #        if self.position.has_key(self.c2a(x1+np.sign(x2-x1)*t,y1+np.sign(y2-y1)*t)):
        #            return True
        #    return False

        return True
        
    def is_capture(self,m):
        """
            Checks if this move captures a piece.
            
            :param string m: Simplified algebraic notation of the move (such as g1f3 for Ng1-f3 and e1g1 for 0-0).
        """
        return self.position.has_key(m[2:])
        
    def move(self,m):
        """
            Executes a move.
            
            :param string m: Simplified algebraic notation of the move (such as g1f3 for Ng1-f3 and e1g1 for 0-0).
        """
        s0 = m[:2]
        s1 = m[2:]
        if self.position.has_key(s0):
            self.position[s1] = self.position[s0]
            del self.position[s0]
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
                
    def find_move(squares):
        """
            Find the move from a list of squares that changed.
        """
        for (x,y) in squares:
            if G.position.has_key(G.c2a(x,y)):
                s1 = G.c2a(x,y)
            else:
                s2 = G.c2a(x,y)
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
