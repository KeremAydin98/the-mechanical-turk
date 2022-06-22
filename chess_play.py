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
done = False
en_passant = False

while True:

    if done:
        break

    if side_n % 2 == 1:
        side = "white"
    else:
        side = "black"

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            pos = [element/Chess.block_size for element in pos]

            if check:

                possible_moves, which_piece = Chess.available_moves(side, event, pos, check=True, en_passant=en_passant)
                possible_moves = Chess.get_rid_of_checks(side=side, possible_moves=possible_moves, which_piece=which_piece, check_piece=check_piece)
                en_passant = False

                if len(possible_moves) == 0:

                    print("CHECKMATE")
                    done = True
                    break

            else:

                possible_moves, which_piece = Chess.available_moves(side, event, pos, en_passant=en_passant)
                en_passant = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = pygame.mouse.get_pos()
            pos = [element / Chess.block_size for element in pos]

            if check and possible_moves:
                for move in possible_moves:
                    if math.dist(move, pos) < 0.5:

                        en_passant = Chess.move_piece(side, which_piece, move)
                        side_n += 1
                        possible_moves = None

                        check = False

                        Chess.eat_piece(side, which_piece, move)

                        check = Chess.check_for_check(side=side)

                        if check:
                            print("CHECK")
                            check_piece = which_piece

                        break

            # Move the piece
            elif possible_moves and not check:
                for move in possible_moves:
                        if math.dist(move, pos) < 0.5:

                            en_passant = Chess.move_piece(side, which_piece, move)
                            side_n += 1
                            possible_moves = None

                            check = False

                            Chess.eat_piece(side, which_piece, move)

                            check = Chess.check_for_check(side=side)

                            if check:

                                print("CHECK")
                                check_piece = which_piece

                            break

            Chess.reset()

    pygame.display.update()
    img = array3d(Chess.game_window)