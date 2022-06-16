import pygame, math
from chessEnvironment import chess_env
from pygame.surfarray import array3d

pygame.init()

Chess = chess_env(800)
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
            pos = [element/Chess.block_size for element in pos]

            possible_moves, which_piece = Chess.available_moves(side, event, pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = pygame.mouse.get_pos()
            pos = [element / Chess.block_size for element in pos]

            # Move the piece
            if possible_moves:
                for move in possible_moves:
                    if math.dist(move, pos) < 0.5:
                        Chess.move_piece(side, which_piece, move)
                        side_n += 1
                        possible_moves = None

                        Chess.eat_piece(side, which_piece, move)

                        break

            Chess.reset()

    pygame.display.update()
    img = array3d(chess_env.game_window)