import pygame, math
from chessEnvironment import ChessEnv
from pygame.surfarray import array3d
import numpy as np

# To turn of the filter warnings of numpy
np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

pygame.init()

Chess = ChessEnv(800)
pygame.display.set_caption("Chess Game")
side_n = 1
check = False

while True:

    if side_n % 2 == 1:
        side = "white"
    else:
        side = "black"

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            pos = [element/Chess.block_size for element in pos]

            if check:

                possible_moves, which_piece = Chess.available_moves(side, event, pos, check=True)
                possible_moves = Chess.get_rid_of_checks(side=side, possible_moves=possible_moves, which_piece=which_piece)
                check = False

            else:

                possible_moves, which_piece = Chess.available_moves(side, event, pos)


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = pygame.mouse.get_pos()
            pos = [element / Chess.block_size for element in pos]

            # Move the piece
            if possible_moves:
                for direction in possible_moves:
                    for move in direction:
                        if math.dist(move, pos) < 0.5:

                            Chess.move_piece(side, which_piece, move)
                            side_n += 1
                            possible_moves = None

                            Chess.eat_piece(side, which_piece, move)

                            check = Chess.check_for_check(side=side)

                            if check:

                                print("CHECK")

                            break

            Chess.reset()

    pygame.display.update()
    img = array3d(Chess.game_window)