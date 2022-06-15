import pygame, sys, math
from pygame.surfarray import array3d
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

        self.all_positions = {"white": {"rook": [[0, 0], [7, 0]],
                                        "knight": [[1, 0], [6, 0]],
                                        "bishop": [[2, 0], [5, 0]],
                                        "king": [[3, 0]],
                                        "queen": [[4, 0]],
                                        "pawn": [[pos, 1] for pos in range(8)]},
                              "black": {"rook": [[0, 7], [7, 7]],
                                        "knight": [[1, 7], [6, 7]],
                                        "bishop": [[2, 7], [5, 7]],
                                        "king": [[3, 7]],
                                        "queen": [[4, 7]],
                                        "pawn": [[pos, 6] for pos in range(8)]}}

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

        sides = ["white","black"]

        for side in sides:

            for name, position in self.all_positions[side].items():

                one_piece = pygame.image.load("pieces/" + side[0] + "_" + name + ".png")
                one_piece = pygame.transform.scale(one_piece, (self.block_size, self.block_size))

                for pos in position:

                    pos = [element * self.block_size for element in pos]
                    pygame.draw.rect(self.game_window, BLUE, pos + [5] + [5])
                    self.game_window.blit(one_piece, pos)

    def move_piece(self, side, which_piece, position):

        self.all_positions[side][which_piece[0]][which_piece[1]] = position

    def available_moves(self, side, event, mouse_pos=None):

        ok_red_dots = None
        which_piece = None

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if mouse_pos:

            red_dots, which_piece = self.show_possible_moves(side, mouse_pos)

            if not np.array_equal(red_dots, [[0,0]]):
                for direction in red_dots:

                    print("direction",direction, which_piece)
                    ok_red_dots = self.dont_get_pass(side, direction, which_piece)

                    print("red dots", ok_red_dots, which_piece)

                    if not ok_red_dots:
                        break

                    for real_dot in ok_red_dots:
                        draw_dot = [element * self.block_size + self.block_size / 2 for element in real_dot]
                        pygame.draw.circle(self.game_window, RED, draw_dot, 10)

                    return ok_red_dots, which_piece

        return ok_red_dots, which_piece

    # red dots should stop after being close to an allied piece
    def dont_get_pass(self, side, direction, which_piece):

        all_positions = []

        for positions in self.all_positions[side].values():

            for position in positions:
                all_positions.append(position)

        ok_red_dots = []

        if side == "black":

            direction.reverse()

        for dot in direction:

            dont = True

            for pos in all_positions:

                if math.dist(pos, dot) < 1 and which_piece[0] != "knight":

                    return ok_red_dots

                elif which_piece[0] == "knight" and math.dist(pos, dot) < 1:

                    dont = False

            if dont:
                ok_red_dots.append(dot)

        return ok_red_dots

    def show_possible_moves(self, side, mouse_pos):

        for i,piece_position in enumerate(self.all_positions[side]["pawn"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                if side == "white":

                    return [[np.add(piece_position,[0,1]).tolist()]],["pawn",i]

                else:

                    return [[np.add(piece_position,[0, -1]).tolist()]], ["pawn",i]

        for i,piece_position in enumerate(self.all_positions[side]["rook"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                right = np.add(piece_position,[[pos, 0] for pos in range(1,8)]).tolist()
                left = np.add(piece_position,[[pos, 0] for pos in range(-1,-8,-1)]).tolist()
                up = np.add(piece_position,[[0, pos] for pos in range(1,8)]).tolist()
                down = np.add(piece_position, [[0, pos] for pos in range(-1, -8,-1)]).tolist()

                return [up] + [right] + [down] + [left], ["rook",i]

        for i,piece_position in enumerate(self.all_positions[side]["bishop"]):
            if math.dist(mouse_pos, piece_position) < 0.5:
                top_r = np.add(piece_position, [[pos, pos] for pos in range(1,8)]).tolist()
                top_l = np.add(piece_position, [[-pos, pos] for pos in range(1,8)]).tolist()
                down_r = np.add(piece_position, [[pos, -pos] for pos in range(1,8)]).tolist()
                down_l = np.add(piece_position, [[-pos, pos] for pos in range(1,8)]).tolist()

                return [top_r] + [top_l] + [down_r] + [down_l], ["bishop",i]

        for i,piece_position in enumerate(self.all_positions[side]["knight"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                moves = [[-2,-1],[-2,1],[2,-1],[2,1],[-1,-2],[-1,2],[1,-2],[1,2]]

                return [np.add(piece_position,[move for move in moves]).tolist()], ["knight",i]

        for i,piece_position in enumerate(self.all_positions[side]["king"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                moves = [[-1,-1],[-1,1],[-1,0],[0,-1],[0,1],[1,-1],[1,1],[1,0]]

                return [np.add(piece_position, [move for move in moves]).tolist()], ["king",i]

        for i,piece_position in enumerate(self.all_positions[side]["queen"]):
            if math.dist(mouse_pos, piece_position) < 0.5:

                right = np.add(piece_position, [[pos, 0] for pos in range(1, 8)]).tolist()
                left = np.add(piece_position, [[pos, 0] for pos in range(-1, -8, -1)]).tolist()
                up = np.add(piece_position, [[0, pos] for pos in range(1, 8)]).tolist()
                down = np.add(piece_position, [[0, pos] for pos in range(-1, -8, -1)]).tolist()

                top_r = np.add(piece_position, [[pos, pos] for pos in range(1, 8)]).tolist()
                top_l = np.add(piece_position, [[-pos, pos] for pos in range(1, 8)]).tolist()
                down_r = np.add(piece_position, [[pos, -pos] for pos in range(1, 8)]).tolist()
                down_l = np.add(piece_position, [[-pos, pos] for pos in range(1, 8)]).tolist()

                return [right] + [left] + [up] + [down] + [top_r] + [top_l] + [down_r] + [down_l], ["queen",i]

        return [[0,0]], False


pygame.init()

chess_env = ChessEnv(800)
pygame.display.set_caption("Chess Game")
side_n = 1

while True:

    if side_n % 2 == 1:
        side = "white"
    else:
        side = "black"

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            pos = [element/chess_env.block_size for element in pos]

            possible_moves, which_piece = chess_env.available_moves(side, event, pos)

            print(possible_moves, which_piece)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = pygame.mouse.get_pos()
            pos = [element / chess_env.block_size for element in pos]

            if possible_moves:
                for move in possible_moves:
                    if math.dist(move, pos) < 0.5:
                        chess_env.move_piece(side, which_piece, move)
                        possible_moves = None
                        side_n += 1
                        print("all position",chess_env.all_positions)
            print("possible_move", possible_moves)
            chess_env.reset()

    pygame.display.update()
    img = array3d(chess_env.game_window)

