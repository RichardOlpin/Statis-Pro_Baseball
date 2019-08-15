import pygame
import sys

pygame.init()
pygame.mixer.init()

board = pygame.image.load("images/game_board_orig.jpg")

windowSize = (board.get_size())

screen = pygame.display.set_mode(windowSize)

pygame.mouse.set_visible(0)

x, y = 0, 0
directionX, directionY = 1, 1
clock = pygame.time.Clock()

while 1:

    clock.tick(40)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    screen.fill((0, 0, 0))

    screen.blit(board, (x, y))

    pygame.display.update()
