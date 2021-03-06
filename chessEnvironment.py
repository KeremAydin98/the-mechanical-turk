import pygame, sys, math
import numpy as np

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255,255,255)
RED = pygame.Color(255,0,0)
BLUE = pygame.Color(0,0,255)
L_GREEN = pygame.Color(204, 255, 229)
D_GREEN = pygame.Color(0, 204, 102)


class ChessEnv:

    def __init__(self, frame_size):

        self.frame_size_x = frame_size
        self.frame_size_y = frame_size
        self.block_size = frame_size // 8
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))

        self.sides = ["white","black"]

        self.black_pieces = {"rook": [[0, 0], [7, 0]],
                                        "knight": [[1, 0], [6, 0]],
                                        "bishop": [[2, 0], [5, 0]],
                                        "king": [[3, 0]],
                                        "queen": [[4, 0]],
                                        "pawn": [[pos, 1] for pos in range(0, 8)]}

        self.white_pieces = {"rook": [[0, 7], [7, 7]],
                                        "knight": [[1, 7], [6, 7]],
                                        "bishop": [[2, 7], [5, 7]],
                                        "king": [[3, 7]],
                                        "queen": [[4, 7]],
                                        "pawn": [[pos, 6] for pos in range(0, 8)]}

        self.all_positions = {"white":self.white_pieces, "black":self.black_pieces}

        # To check whether the pawn can move two squares in one turn or not
        self.first_pawn_moves = {"white":[True]*8,"black":[True]*8}

        self.white_possible_moves = self.update_possible_moves(side="white")
        self.black_possible_moves = self.update_possible_moves(side="black")

        self.white_rockable = {"short":True,"long":True}
        self.black_rockable = {"short": True, "long": True}

        self.reset()

    def reset(self):

        # Draws the board
        self.draw_board()
        # Put the pieces on the board
        self.put_pieces()

        self.white_possible_moves = self.update_possible_moves(side="white")
        self.black_possible_moves = self.update_possible_moves(side="black")

        pygame.display.flip()

    def draw_board(self):

        self.game_window.fill(D_GREEN)

        for y in range(8):
            for x in range(8):
                rect_1 = pygame.Rect(2 * x * self.block_size,2*y*self.block_size, self.block_size, self.block_size)
                rect_2 = pygame.Rect((2 * x - 1) * self.block_size, (2 * y - 1) * self.block_size, self.block_size, self.block_size)
                pygame.draw.rect(self.game_window, L_GREEN, rect_1)
                pygame.draw.rect(self.game_window, L_GREEN, rect_2)

    def put_pieces(self):

        all_sides = {"white":self.white_pieces, "black":self.black_pieces}

        for side, pieces in all_sides.items():

            for name, position in pieces.items():

                one_piece = pygame.image.load("pieces/" + side[0] + "_" + name + ".png")
                one_piece = pygame.transform.scale(one_piece, (self.block_size, self.block_size))

                for pos in position:

                    pos = [element * self.block_size for element in pos]
                    pygame.draw.rect(self.game_window, BLUE, pos + [5] + [5])
                    self.game_window.blit(one_piece, pos)

    def rockin_roll(self, side):

        if side == "white":

            rocks = []

            if self.white_rockable["short"]:

                rock_move = [1,7]
                king_moves =[[1,7],[2,7]]

                for king_move in king_moves:
                    for piece, black_moves in self.black_possible_moves.items():
                        for moves in black_moves.values():
                            for move in moves:
                                if king_move in move:
                                    rock_move = False

                if rock_move:
                    rocks.append(rock_move)

            if self.white_rockable["long"]:

                rock_move = [5,7]
                king_moves = [[4,7],[5,7]]

                for king_move in king_moves:
                    for piece, black_moves in self.black_possible_moves.items():
                        for moves in black_moves.values():
                            for move in moves:
                                if king_move in move:
                                    rock_move = False

                if rock_move:
                    rocks.append(rock_move)

            return rocks

        else:

            rocks = []

            if self.black_rockable["short"]:

                rock_move = [1,0]
                king_moves = [[1,0],[2,0]]

                for king_move in king_moves:
                    for piece, white_moves in self.white_possible_moves.items():
                        for moves in white_moves.values():
                            for move in moves:
                                if king_move in move:
                                    rock_move = False

                if rock_move:
                    rocks.append(rock_move)

            if self.black_rockable["long"]:

                rock_move = [5, 0]
                king_moves = [[5,0],[4,0]]

                for king_move in king_moves:
                    for piece, white_moves in self.white_possible_moves.items():
                        for moves in white_moves.values():
                            for move in moves:
                                if king_move in move:
                                    rock_move = False

                if rock_move:
                    rocks.append(rock_move)

            return rocks

    # looks if there is a check
    def check_for_check(self, side):

        if side == "white":
            for piece, white_moves in self.white_possible_moves.items():
                for moves in white_moves.values():
                    for move in moves:
                        if self.black_pieces["king"][0] in move:

                            return True

        else:

            for piece, black_moves in self.black_possible_moves.items():
                for moves in black_moves.values():
                    for move in moves:
                        if self.white_pieces["king"][0] in move:

                            return True

        return False

    def get_rid_of_checks(self, side, possible_moves, which_piece, check_piece):

        check_crasher_moves = []

        if side == "white":

            for direction in possible_moves:

                for move in direction:

                    if move == self.black_pieces[check_piece[0]][check_piece[1]]:

                        old_white_pos = self.white_pieces[which_piece[0]][which_piece[1]]
                        self.eat_piece(side=side, which_piece=which_piece, move=move)

                        if not self.check_for_check(side="black"):
                            check_crasher_moves.append(move)

                        self.white_pieces[which_piece[0]][which_piece[1]] = old_white_pos
                        self.black_pieces[check_piece[0]][check_piece[1]] = move

                    else:

                        old_white_pos = self.white_pieces[which_piece[0]][which_piece[1]]
                        self.white_pieces[which_piece[0]][which_piece[1]] = move

                        if not self.check_for_check(side="black"):
                            check_crasher_moves.append(move)

                        self.white_pieces[which_piece[0]][which_piece[1]] = old_white_pos

        else:

            for direction in possible_moves:

                for move in direction:

                    if move == self.white_pieces[check_piece[0]][check_piece[1]]:

                        old_black_pos = self.black_pieces[which_piece[0]][which_piece[1]]
                        self.eat_piece(side=side, which_piece=which_piece, move=move)

                        if not self.check_for_check(side="white"):
                            check_crasher_moves.append(move)

                        self.black_pieces[which_piece[0]][which_piece[1]] = old_black_pos
                        self.white_pieces[check_piece[0]][check_piece[1]] = move

                    else:

                        old_black_pos = self.black_pieces[which_piece[0]][which_piece[1]]
                        self.black_pieces[which_piece[0]][which_piece[1]] = move

                        if not self.check_for_check(side="white"):
                            check_crasher_moves.append(move)

                        self.black_pieces[which_piece[0]][which_piece[1]] = old_black_pos

        if check_crasher_moves:
            for real_dot in check_crasher_moves:
                # Change the location of the red dot to the center of the square
                draw_dot = [element * self.block_size + self.block_size / 2 for element in real_dot]
                # Draw circle on the possible moves
                pygame.draw.circle(self.game_window, RED, draw_dot, 10)

        return check_crasher_moves

    def move_piece(self, side, which_piece, position):

        en_passant = False

        if side == "white":

            old_pos = self.white_pieces[which_piece[0]][which_piece[1]]

            self.white_pieces[which_piece[0]][which_piece[1]] = position

            if which_piece[0] == "pawn":

                self.first_pawn_moves[side][which_piece[1]] = False

                if np.abs((np.subtract(old_pos, position))).tolist() == [0,2]:

                    en_passant = which_piece[1]

            elif which_piece[0] == "rook" and which_piece[1] == 0:

                self.white_rockable["short"] = False

            elif which_piece[0] == "rook" and which_piece[1] == 1:

                self.white_rockable["long"] = False

            elif which_piece[0] == "king":

                self.white_rockable["short"] = False
                self.white_rockable["long"] = False

            if which_piece[0] == "king" and old_pos == [3,7] and position == [1,7]:

                self.white_pieces["rook"][0] = [2,7]

            elif which_piece[0] == "king" and old_pos == [3,7] and position == [5,7]:

                self.white_pieces["rook"][1] = [4,7]

            self.white_possible_moves = self.update_possible_moves(side="white")
            self.black_possible_moves = self.update_possible_moves(side="black")

        else:

            old_pos = self.black_pieces[which_piece[0]][which_piece[1]]

            self.black_pieces[which_piece[0]][which_piece[1]] = position

            if which_piece[0] == "pawn":

                self.first_pawn_moves[side][which_piece[1]] = False

                if np.abs((np.subtract(old_pos, position))).tolist() == [0, 2]:
                    en_passant = which_piece[1]

            elif which_piece[0] == "rook" and which_piece[1] == 0:

                self.black_rockable["short"] = False

            elif which_piece[0] == "rook" and which_piece[1] == 1:

                self.black_rockable["long"] = False

            elif which_piece[0] == "king":

                self.black_rockable["short"] = False
                self.black_rockable["long"] = False

            if which_piece[0] == "king" and old_pos == [3,0] and position == [1,0]:

                self.black_pieces["rook"][0] = [2,0]

            elif which_piece[0] == "king" and old_pos == [3,0] and position == [5,0]:

                self.black_pieces["rook"][1] = [4,0]

            self.white_possible_moves = self.update_possible_moves(side="white")
            self.black_possible_moves = self.update_possible_moves(side="black")

        return en_passant

    def eat_piece(self, side, which_piece, move):

        if side == "white":

            for name, positions in self.black_pieces.items():

                for i, position in enumerate(positions):

                    if move == position and which_piece[0] != "king":

                        self.black_pieces[name][i] = [8,8]
                        self.white_possible_moves = self.update_possible_moves(side="white")
                        self.black_possible_moves = self.update_possible_moves(side="black")

                    elif which_piece[0] == "pawn" and abs(which_piece[1]-i) == 1 and np.abs(np.subtract(self.black_pieces[name][i],move)).tolist() == [0,1]:

                        self.black_pieces[name][i] = [8,8]
                        self.white_possible_moves = self.update_possible_moves(side="white")
                        self.black_possible_moves = self.update_possible_moves(side="black")

        else:

            for name, positions in self.white_pieces.items():

                for i, position in enumerate(positions):

                    if move == position and which_piece[0] != "king":

                        self.white_pieces[name][i] = [8,8]
                        self.white_possible_moves = self.update_possible_moves(side="white")
                        self.black_possible_moves = self.update_possible_moves(side="black")

                    elif which_piece[0] == "pawn" and abs(which_piece[1]-i) == 1 and np.abs(np.subtract(self.white_pieces[name][i], move)).tolist() == [0, 1]:

                        self.white_pieces[name][i] = [8, 8]
                        self.white_possible_moves = self.update_possible_moves(side="white")
                        self.black_possible_moves = self.update_possible_moves(side="black")

    def available_moves(self, side, event, mouse_pos=None, check=False, en_passant=False):

        which_piece = None

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        moving_positions = []
        final_moves = []

        if mouse_pos and side == "white":

            for piece_name, values in self.white_pieces.items():

                for i, value in enumerate(values):

                    if math.dist(value, mouse_pos) < 0.5:

                        all_directions = self.white_possible_moves[piece_name][i]
                        if all_directions:
                            for directions in all_directions:
                                moving_positions.append(directions)

                        which_piece = [piece_name, i]

                        if which_piece[0] == "king":

                            if self.rockin_roll(side=side):

                                moving_positions.append(self.rockin_roll(side=side))

                        if which_piece[0] == "pawn" and en_passant:

                            white_pawns = [self.white_pieces["pawn"][en_passant+1], self.white_pieces["pawn"][en_passant-1]]
                            black_pawn = self.black_pieces["pawn"][en_passant]

                            if np.abs(np.subtract(white_pawns[0],black_pawn)).tolist() == [1,0] or np.abs(np.subtract(white_pawns[1],black_pawn)).tolist() == [1,0]:

                                moving_positions.append([np.subtract(black_pawn,[0,1]).tolist()])

                if not check:
                    for direction in moving_positions:
                        direction = self.dont_get_pass(side, direction, which_piece, en_passant=en_passant)
                        for real_dot in direction:

                            do_it = True

                            if which_piece[0] == "king":
                                do_it = self.dont_move_king(side, moving_position=real_dot)

                            if do_it:
                                final_moves.append(real_dot)
                                # Change the location of the red dot to the center of the square
                                draw_dot = [element * self.block_size + self.block_size / 2 for element in real_dot]
                                # Draw circle on the possible moves
                                pygame.draw.circle(self.game_window, RED, draw_dot, 10)

        elif mouse_pos and side == "black":

            for piece_name, values in self.black_pieces.items():

                for i, value in enumerate(values):

                    if math.dist(value, mouse_pos) < 0.5:

                        all_directions = self.black_possible_moves[piece_name][i]

                        if all_directions:
                            for directions in all_directions:
                                moving_positions.append(directions)

                        which_piece = [piece_name, i]

                        if which_piece[0] == "pawn" and en_passant:

                            black_pawns = [self.black_pieces["pawn"][en_passant+1], self.black_pieces["pawn"][en_passant-1]]
                            white_pawn = self.white_pieces["pawn"][en_passant]

                            if np.abs(np.subtract(black_pawns[0],white_pawn)).tolist() == [1,0] or np.abs(np.subtract(black_pawns[1],white_pawn)).tolist() == [1,0]:

                                moving_positions.append([np.add(white_pawn,[0,1]).tolist()])

                        if which_piece[0] == "king":

                            if self.rockin_roll(side=side):

                                moving_positions.append(self.rockin_roll(side=side))

                if not check:
                    for direction in moving_positions:
                        direction = self.dont_get_pass(side, direction, which_piece, en_passant=en_passant)
                        for real_dot in direction:

                            do_it = True

                            if which_piece[0] == "king":

                                do_it = self.dont_move_king(side, moving_position=real_dot)

                            if do_it:
                                final_moves.append(real_dot)
                                # Change the location of the red dot to the center of the square
                                draw_dot = [element * self.block_size + self.block_size / 2 for element in real_dot]
                                # Draw circle on the possible moves
                                pygame.draw.circle(self.game_window, RED, draw_dot, 10)

        return final_moves, which_piece

    def dont_move_king(self, side, moving_position):

        if side == "white":

            for piece, black_moves in self.black_possible_moves.items():
                for moves in black_moves.values():
                    for move in moves:
                        if moving_position in move:
                            return False

            return True

        else:

            for piece, white_moves in self.white_possible_moves.items():
                for moves in white_moves.values():
                    for move in moves:
                        if moving_position in move:
                            return False

            return True

    # Possible moves are restricted by other pieces
    def dont_get_pass(self, side, direction, which_piece, en_passant=False):

        same_side = []
        opp_side = []

        for positions in self.white_pieces.values():
            for position in positions:
                if side == "white":
                    same_side.append(position)
                else:
                    opp_side.append(position)

        for positions in self.black_pieces.values():
            for position in positions:
                if side == "black":
                    same_side.append(position)
                else:
                    opp_side.append(position)

        all_sides = same_side + opp_side

        ok_red_dots = []

        for dot in direction:

            next_dot = False

            for piece in all_sides:

                if math.dist(dot, piece) < 0.5 and piece in same_side and (which_piece[0] != "knight" and which_piece[0] != "king"):

                    return ok_red_dots

                elif math.dist(dot, piece) < 0.5 and piece in opp_side and (which_piece[0] != "knight" and which_piece[0] != "king"):

                    if which_piece[0] == "pawn" and self.all_positions[side][which_piece[0]][which_piece[1]][0] == dot[0]:

                        return ok_red_dots

                    ok_red_dots.append(dot)

                    return ok_red_dots

                elif math.dist(dot, piece) < 0.5 and piece in same_side and (which_piece[0] == "knight" or which_piece[0] == "king"):

                    next_dot = True

            if which_piece[0] == "pawn" and self.all_positions[side][which_piece[0]][which_piece[1]][0] != dot[0] and not en_passant:

                return ok_red_dots

            if not next_dot:

                ok_red_dots.append(dot)

        return ok_red_dots

    def update_possible_moves(self, side):

        possible_moves = {"rook": {0:[],1:[]},
                          "knight": {0:[],1:[]},
                          "bishop": {0:[],1:[]},
                          "king": {0:[]},
                          "queen": {0:[]},
                          "pawn": {0:[],1:[],2:[],3:[],4:[],5:[],6:[],7:[]}}

        for i,piece_position in enumerate(self.all_positions[side]["pawn"]):

            if side == "black" and self.first_pawn_moves[side][i]:

                move = np.add(piece_position,[[0,1],[0,2]]).tolist()

                eat_l = np.add(piece_position,[-1,1]).tolist()
                eat_r = np.add(piece_position, [1, 1]).tolist()

                all_directions = [move] + [[eat_l]] + [[eat_r]]
                which_piece = ["pawn", i]

                for direction in all_directions:
                    possible_move = self.dont_get_pass(side, direction, which_piece)
                    possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                    if len(possible_move) != 0:
                        possible_moves["pawn"][i].append(possible_move)

            elif side == "black" and not self.first_pawn_moves[side][i]:

                move = np.add(piece_position, [0, 1]).tolist()

                eat_l = np.add(piece_position, [-1, 1]).tolist()
                eat_r = np.add(piece_position, [1, 1]).tolist()

                all_directions = [[move]] + [[eat_l]] + [[eat_r]]
                which_piece = ["pawn", i]

                for direction in all_directions:
                    possible_move = self.dont_get_pass(side, direction, which_piece)
                    possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                    if len(possible_move) != 0:
                        possible_moves["pawn"][i].append(possible_move)

            elif side == "white" and self.first_pawn_moves[side][i]:

                move = np.add(piece_position, [[0, -1], [0, -2]]).tolist()

                eat_l = np.add(piece_position, [-1, -1]).tolist()
                eat_r = np.add(piece_position, [1, -1]).tolist()

                all_directions = [move] + [[eat_l]] + [[eat_r]]
                which_piece = ["pawn", i]

                for direction in all_directions:
                    possible_move = self.dont_get_pass(side, direction, which_piece)
                    possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                    if len(possible_move) != 0:
                        possible_moves["pawn"][i].append(possible_move)

            else:

                move = np.add(piece_position, [0, -1]).tolist()

                eat_l = np.add(piece_position, [-1, -1]).tolist()
                eat_r = np.add(piece_position, [1, -1]).tolist()

                all_directions = [[move]] + [[eat_l]] + [[eat_r]]
                which_piece = ["pawn", i]

                for direction in all_directions:
                    possible_move = self.dont_get_pass(side, direction, which_piece)
                    possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                    if len(possible_move) != 0:
                        possible_moves["pawn"][i].append(possible_move)

        for i,piece_position in enumerate(self.all_positions[side]["rook"]):

            right = np.add(piece_position,[[pos, 0] for pos in range(1,8)]).tolist()
            left = np.add(piece_position,[[-pos, 0] for pos in range(1,8)]).tolist()
            up = np.add(piece_position,[[0, pos] for pos in range(1,8)]).tolist()
            down = np.add(piece_position, [[0, -pos] for pos in range(1, 8)]).tolist()

            all_directions = [up] + [right] + [down] + [left]
            which_piece = ["rook",i]

            for direction in all_directions:
                possible_move = self.dont_get_pass(side, direction, which_piece)
                possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                if len(possible_move) != 0:
                    possible_moves["rook"][i].append(possible_move)

        for i,piece_position in enumerate(self.all_positions[side]["bishop"]):

            top_r = np.add(piece_position, [[pos, pos] for pos in range(1,8)]).tolist()
            top_l = np.add(piece_position, [[-pos, -pos] for pos in range(1,8)]).tolist()
            down_r = np.add(piece_position, [[pos, -pos] for pos in range(1,8)]).tolist()
            down_l = np.add(piece_position, [[-pos, pos] for pos in range(1,8)]).tolist()

            all_directions = [top_r] + [top_l] + [down_r] + [down_l]
            which_piece = ["bishop",i]

            for direction in all_directions:
                possible_move = self.dont_get_pass(side, direction, which_piece)
                possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                if len(possible_move) != 0:
                    possible_moves["bishop"][i].append(possible_move)

        for i,piece_position in enumerate(self.all_positions[side]["knight"]):

            moves = [[-2,-1],[-2,1],[2,-1],[2,1],[-1,-2],[-1,2],[1,-2],[1,2]]

            all_directions = [np.add(piece_position,[move for move in moves]).tolist()]
            which_piece = ["knight",i]

            for direction in all_directions:
                possible_move = self.dont_get_pass(side, direction, which_piece)
                possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                if len(possible_move) != 0:
                    possible_moves["knight"][i].append(possible_move)

        for i,piece_position in enumerate(self.all_positions[side]["king"]):

            right = np.add(piece_position, [1,0]).tolist()
            left = np.add(piece_position, [-1,0]).tolist()
            up = np.add(piece_position, [0,-1]).tolist()
            down = np.add(piece_position, [0, 1]).tolist()

            top_r = np.add(piece_position, [1,-1]).tolist()
            top_l = np.add(piece_position, [-1,-1]).tolist()
            down_r = np.add(piece_position, [1,1]).tolist()
            down_l = np.add(piece_position, [-1,1]).tolist()

            all_directions = [[right]] + [[left]] + [[up]] + [[down]] + [[top_r]] + [[top_l]] + [[down_r]] + [[down_l]]
            which_piece = ["king", i]

            for direction in all_directions:
                possible_move = self.dont_get_pass(side, direction, which_piece)
                possible_move = list(filter(lambda x: 0 <= x[0] <= 7 and 0 <= x[1] <= 7, possible_move))
                if len(possible_move) != 0:
                    possible_moves["king"][i].append(possible_move)

        for i,piece_position in enumerate(self.all_positions[side]["queen"]):

            right = np.add(piece_position, [[pos, 0] for pos in range(1, 8)]).tolist()
            left = np.add(piece_position, [[-pos, 0] for pos in range(1, 8)]).tolist()
            up = np.add(piece_position, [[0, pos] for pos in range(1, 8)]).tolist()
            down = np.add(piece_position, [[0, -pos] for pos in range(1, 8)]).tolist()

            top_r = np.add(piece_position, [[pos, pos] for pos in range(1, 8)]).tolist()
            top_l = np.add(piece_position, [[-pos, -pos] for pos in range(1, 8)]).tolist()
            down_r = np.add(piece_position, [[pos, -pos] for pos in range(1, 8)]).tolist()
            down_l = np.add(piece_position, [[-pos, pos] for pos in range(1, 8)]).tolist()

            all_directions = [right] + [left] + [up] + [down] + [top_r] + [top_l] + [down_r] + [down_l]
            which_piece = ["queen", i]

            for direction in all_directions:
                possible_move = self.dont_get_pass(side, direction, which_piece)
                possible_move = list(filter(lambda x: 0<=x[0]<=7 and 0<=x[1]<=7, possible_move))
                if len(possible_move) != 0:
                    possible_moves["queen"][i].append(possible_move)

        return possible_moves