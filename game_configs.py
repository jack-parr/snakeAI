'''

This file contains configuration variables used in the 'gamefuncs.py' functions.

'''

import pygame


white = (255, 255, 255)  # RGB colour system.
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)


# INITIALISE DISPLAY WINDOW
pygame.init()
dis_width = 400
dis_height = 300
dis = pygame.display.set_mode((dis_width, dis_height))  # 'dis' is the pygame window object.
pygame.display.set_caption('Snake Game')  # title of the window.
clock = pygame.time.Clock()  # the clock is used to control FPS of game.


# TEXTS
text_font = pygame.font.SysFont(None, 30)
score_font = pygame.font.SysFont('verdana', 20)

# GAME VARIABLES
snake_block_size = 20
snake_speed = 10
