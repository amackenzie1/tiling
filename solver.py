from game_interface import Answer, GameMessage, TotemAnswer, Question, TotemQuestion
import random
from collections import Counter 
import math
import time
import os 
from integer import integer, get_sets 
import pickle 

class Solver:
    def __init__(self):
        """
        This method should be use to initialize some variables you will need throughout the challenge.
        """
        I = [(0, 0), (1, 0), (2, 0), (3, 0)]
        L = [(0, 0), (1, 0), (2, 0), (2, 1)]
        T = [(0, 0), (1, 0), (2, 0), (1, 1)]
        J = [(0, 0), (1, 0), (2, 0), (0, 1)]
        S = [(0, 0), (1, 0), (1, 1), (2, 1)]
        Z = [(0, 0), (0, 1), (1, 1), (1, 2)]
        O = [(0, 0), (1, 0), (0, 1), (1, 1)]

        self.coords = {"I": I, "L": L, "T": T, "J": J, "S": S, "Z": Z, "O": O}
        badness = {"I": 0, "T": 0, "O": 2, "J": 3, "L": 3, "Z": 5, "S": 5}
        self.badness = sorted(badness.items(), key=lambda x: x[1], reverse=True)
        self.badness = [i[0] for i in self.badness]
        self.mappings = pickle.load(open("mappings.p", "rb"))

    def rotate(self, piece):
        """
        Rotates a piece 90 degrees clockwise
        """
        return [(y, -x) for x, y in piece]

    def rotations(self, piece):
        if piece == "O":
            return [self.coords[piece]]
        elif piece == "I":
            i = self.coords[piece]
            return [i, self.rotate(i)]
        else:
            i = self.coords[piece]
            return [i, self.rotate(i), self.rotate(self.rotate(i)), self.rotate(self.rotate(self.rotate(i)))]

    def show(self, board, size=(4, 8)):
        for x in range(0, size[0]):
            for y in range(0, size[1]):
                if (x, y) in board:
                    print("X", end="")
                else:
                    print(".", end="")
            print()

    def shift(self, piece, direction):
        if isinstance(piece, TotemAnswer):
            return TotemAnswer(shape=piece.shape, coordinates=self.shift(piece.coordinates, direction))
        return [(x + direction[0], y+direction[1]) for x, y in piece]


    def get_badness(self, board):
        """measure of non-convexity"""
        badness = 0
        for i, j in board:
            if i - 1 >= 0 and (i-1, j) not in board:
                badness += 1
            if j - 1 >= 0 and (i, j-1) not in board:
                badness += 1
        return badness  

    def solve_128(self, pieces):
        totems = []
        O = TotemAnswer(shape="O", coordinates=self.coords["O"])
        I_normal = TotemAnswer(shape="I", coordinates=self.coords["I"])
        I_rotated = TotemAnswer(shape="I", coordinates=[(0, 0), (0, 1), (0, 2), (0, 3)])
        X_box = [TotemAnswer(shape="J", coordinates=[(0, 1), (0, 0), (1, 0), (2, 0)]), TotemAnswer(shape="J", coordinates=[(1, 1), (2, 1), (3, 1), (3, 0)])]
        Y_box = [TotemAnswer(shape="L", coordinates=[(0, 2), (0, 1), (0, 0), (1, 0)]), TotemAnswer(shape="L", coordinates=[(0, 3), (1, 3), (1, 2), (1, 1)])]
        for i in range(7):
            shifted = self.shift(O, (0, i*2))
            totems.append(shifted)
            pieces.remove("O")

        for j in range(1, 7):
            shifted = self.shift(O, (j*2, 0))
            totems.append(shifted)
            pieces.remove("O")
        
        for i in range(2):
            shifted = [self.shift(j, (14+4*i, 0)) for j in X_box]
            totems += shifted 
            pieces.remove("J")
            pieces.remove("J")

        for i in range(2):
            shifted = [self.shift(j, (0, 14+4*i)) for j in Y_box]
            totems += shifted 
            pieces.remove("L")
            pieces.remove("L")

        for i in range(5):
            shifted = self.shift(I_normal, (i*4 +2, 2)) 
            totems.append(shifted)
            pieces.remove("I")
        
        for j in range(5):
            shifted = self.shift(I_rotated, (2, j*4 + 3))
            totems.append(shifted)
            pieces.remove("I")

        inner = self.big_stack(pieces)
        inner = [self.shift(i, (3, 3)) for i in inner]
        totems += inner
        return totems

        

    def solve_512(self, pieces):
        totems = []
        O = TotemAnswer(shape="O", coordinates=self.coords["O"])
        for i in range(23):
            shifted = self.shift(O, (0, i*2))
            totems.append(shifted)
            pieces.remove("O")
        for j in range(1, 23):
            shifted = self.shift(O, (j*2, 0))
            totems.append(shifted)
            pieces.remove("O")
        
        inner = self.big_stack(pieces)
        inner = [self.shift(i, (2, 2)) for i in inner]
        totems += inner
        return totems
        

    def variations(self, piece, board, size=(4, 8)):
        """finds the possible valid placements for a 
        piece on the board"""

        variations = set()
        for j in self.rotations(piece):
            for x in range(-5, size[0]+5):
                for y in range(-5, size[1] +5):
                    shifted = self.shift(j, (x, y))
                    bad = False 
                    for k in shifted:
                        if k in board:
                            bad = True 
                            break
                        if k[0] < 0 or k[0] >= size[0] or k[1] < 0 or k[1] >= size[1]:
                            bad = True
                            break 
                    if not bad and tuple(shifted) not in variations:
                        variations.add(tuple(shifted))

        good = [] 
        for i in variations:
            if len(board) == 0:
                if (0, 0) in i:
                    good.append(i)
                continue 

            for x, y in i:
                big_break = False
                for k in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
                    if k in board:
                        big_break = True 
                        good.append(i)
                        break 
                if big_break:
                    break
        return good

    def stack(self, pieces, size=(4, 8), beam_size=8):
        """beam search for stacking small boards,
        was also used for finding the tilings of the
        4x4 and 4x8 squares we use"""

        beam = []
        board = set()
        totems = []
        for i in set(pieces):
            pieces2 = pieces.copy()
            pieces2.remove(i)
            v = self.variations(i, board, size)
            variations = []
            for j in v:
                board2 = board.copy()
                board2.update(j)
                badness2 = self.get_badness(board2)
                totems2 = totems.copy()
                totems2.append(TotemAnswer(shape=i, coordinates=j))
                variations.append((board2, badness2, pieces2, totems2))            
            variations = sorted(variations, key= lambda x: x[1])[:beam_size]
            beam += variations 
        
        beam = sorted(beam, key=lambda x: x[1])
        beam = beam[:beam_size]

        for i in range(len(pieces)-1):
            newbeam = []
            for board, badness, pieces, totems in beam:
                for i in set(pieces):
                    pieces2 = pieces.copy()
                    pieces2.remove(i)
                    v = self.variations(i, board, size)
                    variations = []
                    for j in v:
                        board2 = board.copy()
                        board2.update(j)
                        badness2 = self.get_badness(board2)
                        totems2 = totems.copy()
                        totems2.append(TotemAnswer(shape=i, coordinates=j))
                        variations.append((board2, badness2, pieces2, totems2))            

                    variations = sorted(variations, key= lambda x: x[1])[:beam_size]
                    newbeam += variations 

            beam = sorted(newbeam, key=lambda x: x[1])[:beam_size]
            print(len(beam))

        if len(beam) == 0:
            return None

        result = beam[0]
        self.show(result[0], size=(4,8))
        return result[-1]
    
    def size(self, num_pieces):
        """side length of the board"""
        root = math.sqrt(num_pieces*4)
        if (int(root) - root)**2 < 1e-6:
            return root 
        else:
            return 4 * (int(root)//4 + 1)

    def big_stack(self, pieces, squares=None):
        """stacking boxes of shapes 4x4 and 4x8"""

        side_length = self.size(len(pieces))
        if squares == None:
            squares = integer(pieces)

        for box, num in squares:
            for i in range(int(num)):
                for j in box:
                    pieces.remove(j)

        squares_totems = []

        for box, num in squares:
            for j in range(int(num)):
                squares_totems.append(self.mappings[tuple(box)])

        eights = [i for i in squares_totems if len(i) == 8]
        fours = [i for i in squares_totems if len(i) == 4]

        if len(pieces) != 0:
            if len(pieces) <= 3:
                leftover = self.stack(pieces, size=(4, 4), beam_size=8)
                fours.append(leftover)
            else:
                leftover = self.stack(pieces, size=(4, 8), beam_size=8)
                eights.append(leftover)
        answer = []
        x = 0
        y = 0
        for i in eights:
            shifted = [self.shift(j, (x, y)) for j in i]
            answer += shifted
            if x == side_length-4:
                x = 0
                y += 8
            else:
                x += 4

        parity = 0 
        for i in fours:
            if parity == 0:
                shifted = [self.shift(j, (x, y)) for j in i]
                answer += shifted
                parity = 1 

            elif parity == 1:
                shifted = [self.shift(j, (x, y+4)) for j in i]
                answer += shifted
                if x == side_length-4:
                    x = 0
                    y += 8
                    parity = -1
                else:
                    x += 4
                    parity = 0
            else:
                shifted = [self.shift(j, (x, y)) for j in i]
                answer += shifted
                if x == side_length-4:
                    x = 0
                    y += 4
                else:
                    x += 4
    
        return answer 
        

    def get_answer(self, game_message: GameMessage) -> Answer:
        """
        Here is where the magic happens, for now the answer is a single 'I'. I bet you can do better ;)
        """
        question = game_message.payload
        print("Time :", time.time())
        print("Received Question:", question)
 
        pieces = [] 

        for i in question.totems: 
            pieces.append(i.shape)
        
        board_size =  int(math.sqrt(4*len(pieces)))
        if board_size >= 44:
            totems = self.solve_512(pieces)
        elif board_size == 22:
            totems = self.solve_128(pieces)
        elif board_size <= 10:
            totems = self.stack(pieces, size=(board_size, board_size), beam_size=2)
            while totems == None:
                print(board_size)
                board_size += 1
                totems = self.stack(pieces, size=(board_size, board_size), beam_size=2)
        else:
            totems = self.big_stack(pieces)

        answer = Answer(totems)
        print("Sending Answer:", answer)
        return answer

if __name__ == "__main__":
    s = Solver()
    question = Question(totems=[TotemQuestion(shape='O'), TotemQuestion(shape='J'), TotemQuestion(shape='O'), TotemQuestion(shape='I'), TotemQuestion(shape='J'), TotemQuestion(shape='L'), TotemQuestion(shape='S'), TotemQuestion(shape='J'), TotemQuestion(shape='L'), TotemQuestion(shape='J'), TotemQuestion(shape='Z'), TotemQuestion(shape='O'), TotemQuestion(shape='S'), TotemQuestion(shape='Z'), TotemQuestion(shape='J'), TotemQuestion(shape='O'), TotemQuestion(shape='J'), TotemQuestion(shape='I'), TotemQuestion(shape='S'), TotemQuestion(shape='I'), TotemQuestion(shape='Z'), TotemQuestion(shape='L'), TotemQuestion(shape='Z'), TotemQuestion(shape='L'), TotemQuestion(shape='I'), TotemQuestion(shape='I'), TotemQuestion(shape='Z'), TotemQuestion(shape='L'), TotemQuestion(shape='T'), TotemQuestion(shape='S'), TotemQuestion(shape='J'), TotemQuestion(shape='S'), TotemQuestion(shape='S'), TotemQuestion(shape='I'), TotemQuestion(shape='I'), TotemQuestion(shape='J'), TotemQuestion(shape='O'), TotemQuestion(shape='I'), TotemQuestion(shape='L'), TotemQuestion(shape='J'), TotemQuestion(shape='L'), TotemQuestion(shape='O'), TotemQuestion(shape='O'), TotemQuestion(shape='I'), TotemQuestion(shape='O'), TotemQuestion(shape='Z'), TotemQuestion(shape='S'), TotemQuestion(shape='J'), TotemQuestion(shape='T'), TotemQuestion(shape='I'), TotemQuestion(shape='Z'), TotemQuestion(shape='I'), TotemQuestion(shape='L'), TotemQuestion(shape='L'), TotemQuestion(shape='S'), TotemQuestion(shape='Z'), TotemQuestion(shape='S'), TotemQuestion(shape='J'), TotemQuestion(shape='S'), TotemQuestion(shape='T'), TotemQuestion(shape='S'), TotemQuestion(shape='J'), TotemQuestion(shape='I'), TotemQuestion(shape='L')])
    message = GameMessage(tick=1, payload=question)
    t1 = time.time()
    #s.get_answer(message)
    print(time.time() - t1)
    pieces = """T, I, I, Z, J, J, O, J, Z, S, T, J, L, I, O, L"""
    pieces = pieces.split(", ")
    print(s.stack(pieces, size=(8,8), beam_size=256))