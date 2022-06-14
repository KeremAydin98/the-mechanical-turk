import pygame, time, sys, math
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

    def available_moves(self, side, event,mouse_pos=None):

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if mouse_pos:

            red_dots = self.show_possible_moves(side, mouse_pos)

            if not np.array_equal(red_dots, [[0,0]]):
                for dot in red_dots:
                    dot = [element * self.block_size + self.block_size/2 for element in dot]
                    pygame.draw.circle(self.game_window, RED, dot, 10)

            return red_dots

    def show_possible_moves(self, side, mouse_pos):

        for i, pawn_position in enumerate(self.all_positions[side]["pawn"]):
            if math.dist(mouse_pos, pawn_position) < 0.5:

                if side == "white":

                    return [np.add(self.all_positions[side]["pawn"][i],[0,1])]

                else:

                    return [np.add(self.all_positions[side]["pawn"][i],[0, -1])]

        for i, pawn_position in enumerate(self.all_positions[side]["rook"]):
            if math.dist(mouse_pos, pawn_position) < 0.5:

                available_x = np.add(self.all_positions[side]["rook"][i],[[pos, 0] for pos in range(-7,8)])
                available_y = np.add(self.all_positions[side]["rook"][i],[[0, pos] for pos in range(-7,8)])

                return available_x.tolist() + available_y.tolist()

        for i, pawn_position in enumerate(self.all_positions[side]["bishop"]):
            if math.dist(mouse_pos, pawn_position) < 0.5:
                reverse_slash = np.add(self.all_positions[side]["bishop"][i], [[pos, pos] for pos in range(-7,8)])
                slash = np.add(self.all_positions[side]["bishop"][i], [[-pos, pos] for pos in range(-7,8)])

                return reverse_slash.tolist() + slash.tolist()

        for i, pawn_position in enumerate(self.all_positions[side]["knight"]):
            if math.dist(mouse_pos, pawn_position) < 0.5:

                moves = [[-2,-1],[-2,1],[2,-1],[2,1],[-1,-2],[-1,2],[1,-2],[1,2]]

                return np.add(self.all_positions[side]["knight"][i],[move for move in moves])

        for i, pawn_position in enumerate(self.all_positions[side]["king"]):
            if math.dist(mouse_pos, pawn_position) < 0.5:

                moves = [[-1,-1],[-1,1],[-1,0],[0,-1],[0,1],[1,-1],[1,1],[1,0]]

                return np.add(self.all_positions[side]["king"][i], [move for move in moves])

        for i, pawn_position in enumerate(self.all_positions[side]["queen"]):
            if math.dist(mouse_pos, pawn_position) < 0.5:

                x_moves = [[0,move] for move in range(-7,8)]
                y_moves = [[move,0] for move in range(-7,8)]

                reverse_slash_moves = [[move,move] for move in range(-7,8)]
                slash_moves = [[-move, move] for move in range(-7, 8)]

                all_moves = x_moves + y_moves + reverse_slash_moves + slash_moves

                return np.add(self.all_positions[side]["queen"][i], [move for move in all_moves]).tolist()

        return [[0,0]]


pygame.init()

chess_env = ChessEnv(800)
pygame.display.set_caption("Chess Game")

while True:

    for event in pygame.event.get():
        pos = None
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            pos = [element/chess_env.block_size for element in pos]

        possible_moves = chess_env.available_moves("white",event, pos)

    pygame.display.update()
    img = array3d(chess_env.game_window)

