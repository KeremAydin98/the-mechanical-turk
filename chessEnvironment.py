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
                                        "pawn": [[pos, 1] for pos in range(8)]}

        self.white_pieces = {"rook": [[0, 7], [7, 7]],
                                        "knight": [[1, 7], [6, 7]],
                                        "bishop": [[2, 7], [5, 7]],
                                        "king": [[3, 7]],
                                        "queen": [[4, 7]],
                                        "pawn": [[pos, 6] for pos in range(8)]}

        self.all_positions = {"white":self.white_pieces, "black":self.black_pieces}

        # To check whether the pawn can move two squares in one turn or not
        self.first_pawn_moves = {"white":[True]*8,"black":[True]*8}

        self.reset()

    def reset(self):

        # Draws the board
        self.draw_board()
        # Put the pieces on the board
        self.put_pieces()

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

    def move_piece(self, side, which_piece, position):

        if side == "white":

            self.white_pieces[which_piece[0]][which_piece[1]] = position

            if which_piece[0] == "pawn":

                self.first_pawn_moves[side][which_piece[1]] = False

        else:

            self.black_pieces[which_piece[0]][which_piece[1]] = position

            if which_piece[0] == "pawn":
                self.first_pawn_moves[side][which_piece[1]] = False

    def eat_piece(self, side, which_piece, move):

        if side == "white":

            for name, positions in self.black_pieces.items():

                    for i, position in enumerate(positions):

                        if move == position and which_piece[0] != "king":

                            self.black_pieces[name][i] = [8,8]

        else:

            for name, positions in self.white_pieces.items():

                    for i, position in enumerate(positions):

                        if move == position and which_piece[0] != "king":

                            self.white_pieces[name][i] = [8,8]

    def available_moves(self, side, event, mouse_pos=None):

        which_piece = None

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if mouse_pos:

            red_dots, which_piece= self.show_possible_moves(side, mouse_pos)
            moving_positions = []

            if not np.array_equal(red_dots, [[0,0]]):
                for direction in red_dots:

                    ok_red_dots = self.dont_get_pass(side, direction, which_piece)

                    if not ok_red_dots:
                        continue

                    for real_dot in ok_red_dots:
                        # Change the location of the red dot to the center of the square
                        draw_dot = [element * self.block_size + self.block_size / 2 for element in real_dot]
                        # Draw circle on the possible moves
                        pygame.draw.circle(self.game_window, RED, draw_dot, 10)
                        # Add the real_dot to moving positions
                        moving_positions.append(real_dot)

        return moving_positions, which_piece

    # Possible moves are restricted by other pieces
    def dont_get_pass(self, side, direction, which_piece):

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

                if math.dist(dot, piece) < 0.5 and piece in same_side and which_piece[0] != "knight":

                    return ok_red_dots

                elif math.dist(dot, piece) < 0.5 and piece in opp_side and which_piece[0] != "knight":

                    if which_piece[0] == "pawn" and self.all_positions[side][which_piece[0]][which_piece[1]][0] == dot[0]:

                        return ok_red_dots

                    ok_red_dots.append(dot)

                    return ok_red_dots

                elif math.dist(dot, piece) < 0.5 and piece in same_side and which_piece[0] == "knight":

                    next_dot = True

            if which_piece[0] == "pawn" and self.all_positions[side][which_piece[0]][which_piece[1]][0] != dot[0]:

                return ok_red_dots

            if not next_dot:

                ok_red_dots.append(dot)

        return ok_red_dots

    def show_possible_moves(self, side, mouse_pos):

        for i,piece_position in enumerate(self.all_positions[side]["pawn"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                if side == "black" and self.first_pawn_moves[side][i]:

                    move = np.add(piece_position,[[0,1],[0,2]]).tolist()

                    eat_l = np.add(piece_position,[-1,1]).tolist()
                    eat_r = np.add(piece_position, [1, 1]).tolist()

                    return [move] + [[eat_l]] + [[eat_r]], ["pawn",i]

                elif side == "black" and not self.first_pawn_moves[side][i]:

                    move = np.add(piece_position, [0, 1]).tolist()

                    eat_l = np.add(piece_position, [-1, 1]).tolist()
                    eat_r = np.add(piece_position, [1, 1]).tolist()

                    return [[move]] + [[eat_l]] + [[eat_r]], ["pawn", i]

                elif side == "white" and self.first_pawn_moves[side][i]:

                    move = np.add(piece_position, [[0, -1], [0, -2]]).tolist()

                    eat_l = np.add(piece_position, [-1, -1]).tolist()
                    eat_r = np.add(piece_position, [1, -1]).tolist()

                    return [move] + [[eat_l]] + [[eat_r]], ["pawn", i]

                else:

                    move = np.add(piece_position, [0, -1]).tolist()

                    eat_l = np.add(piece_position, [-1, -1]).tolist()
                    eat_r = np.add(piece_position, [1, -1]).tolist()

                    return [[move]] + [[eat_l]] + [[eat_r]], ["pawn", i]

        for i,piece_position in enumerate(self.all_positions[side]["rook"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                right = np.add(piece_position,[[pos, 0] for pos in range(1,8)]).tolist()
                left = np.add(piece_position,[[-pos, 0] for pos in range(1,8)]).tolist()
                up = np.add(piece_position,[[0, pos] for pos in range(1,8)]).tolist()
                down = np.add(piece_position, [[0, -pos] for pos in range(1, 8)]).tolist()

                return [up] + [right] + [down] + [left], ["rook",i]

        for i,piece_position in enumerate(self.all_positions[side]["bishop"]):
            if math.dist(mouse_pos, piece_position) < 0.5:
                top_r = np.add(piece_position, [[pos, pos] for pos in range(1,8)]).tolist()
                top_l = np.add(piece_position, [[-pos, -pos] for pos in range(1,8)]).tolist()
                down_r = np.add(piece_position, [[pos, -pos] for pos in range(1,8)]).tolist()
                down_l = np.add(piece_position, [[-pos, pos] for pos in range(1,8)]).tolist()

                return [top_r] + [top_l] + [down_r] + [down_l], ["bishop",i]

        for i,piece_position in enumerate(self.all_positions[side]["knight"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                moves = [[-2,-1],[-2,1],[2,-1],[2,1],[-1,-2],[-1,2],[1,-2],[1,2]]

                return [np.add(piece_position,[move for move in moves]).tolist()], ["knight",i]

        for i,piece_position in enumerate(self.all_positions[side]["king"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                right = np.add(piece_position, [1,0]).tolist()
                left = np.add(piece_position, [-1,0]).tolist()
                up = np.add(piece_position, [0,-1]).tolist()
                down = np.add(piece_position, [0, 1]).tolist()

                top_r = np.add(piece_position, [1,-1]).tolist()
                top_l = np.add(piece_position, [-1,-1]).tolist()
                down_r = np.add(piece_position, [1,1]).tolist()
                down_l = np.add(piece_position, [-1,1]).tolist()

                return [[right]] + [[left]] + [[up]] + [[down]] + [[top_r]] + [[top_l]] + [[down_r]] + [[down_l]], ["king",i]

        for i,piece_position in enumerate(self.all_positions[side]["queen"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                right = np.add(piece_position, [[pos, 0] for pos in range(1, 8)]).tolist()
                left = np.add(piece_position, [[-pos, 0] for pos in range(1, 8)]).tolist()
                up = np.add(piece_position, [[0, pos] for pos in range(1, 8)]).tolist()
                down = np.add(piece_position, [[0, -pos] for pos in range(1, 8)]).tolist()

                top_r = np.add(piece_position, [[pos, pos] for pos in range(1, 8)]).tolist()
                top_l = np.add(piece_position, [[-pos, -pos] for pos in range(1, 8)]).tolist()
                down_r = np.add(piece_position, [[pos, -pos] for pos in range(1, 8)]).tolist()
                down_l = np.add(piece_position, [[-pos, pos] for pos in range(1, 8)]).tolist()

                return [right] + [left] + [up] + [down] + [top_r] + [top_l] + [down_r] + [down_l], ["queen",i]

        return [[0,0]], False