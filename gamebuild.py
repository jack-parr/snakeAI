"""

This is the user-interactive game build.

"""

import pygame
import time
import random

pygame.init()

white = (255, 255, 255)  # RGB colour system.
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)

dis_width = 400
dis_height = 300
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()

font_style = pygame.font.SysFont(None, 30)


def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [(dis_width / 2) - 200, dis_height / 2])


def gameLoop():
    game_over = False
    game_close = False

    snake_block_size = 20
    snake_speed = 10
    x1 = [3 * snake_block_size]
    y1 = [3 * snake_block_size]
    x1_change = 0
    y1_change = 0
    score = 0
    foodx = round(random.randrange(0, dis_width - snake_block_size) / snake_block_size) * snake_block_size
    foody = round(random.randrange(0, dis_height - snake_block_size) / snake_block_size) * snake_block_size

    while not game_over:

        while game_close:  # dealing with the game over screen.
            dis.fill(white)
            message("You Lost! Press Q-Quit or C-Play Again", red)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():  # dealing with the key presses during the game.
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    x1_change = -snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_RIGHT:
                    x1_change = snake_block_size
                    y1_change = 0
                elif event.key == pygame.K_UP:
                    y1_change = -snake_block_size
                    x1_change = 0
                elif event.key == pygame.K_DOWN:
                    y1_change = snake_block_size
                    x1_change = 0

        if x1[0] >= dis_width or x1[0] < 0 or y1[0] >= dis_height or y1[0] < 0:  # detecting hitting the edge.
            game_close = True
        for i in range(1, len(x1)):  # detecting hitting itself.
            if x1[0] == x1[i] and y1[0] == y1[i]:
                game_close = True

        if x1[0] == foodx and y1[0] == foody:  # detecting hitting the food.
            score += 1
            x1.append(x1[-1])
            y1.append(y1[-1])
            foodx = round(random.randrange(0, dis_width - snake_block_size) / snake_block_size) * snake_block_size
            foody = round(random.randrange(0, dis_height - snake_block_size) / snake_block_size) * snake_block_size

        if len(x1) > 1:  # moving the snake pieces in sequence.
            for i in range(len(x1) - 1, 0, -1):
                x1[i] = x1[i - 1]
                y1[i] = y1[i - 1]
        x1[0] += x1_change
        y1[0] += y1_change

        dis.fill(white)
        score_font = pygame.font.SysFont('verdana', 20)
        text = score_font.render("Score: " + str(score), True, black)
        dis.blit(text, [0, 0])
        for i in range(0, score + 1):  # drawing the new snake each frame.
            if i == 0:
                pygame.draw.rect(dis, blue, [x1[i], y1[i], snake_block_size, snake_block_size])
            else:
                pygame.draw.rect(dis, black, [x1[i], y1[i], snake_block_size, snake_block_size])

        pygame.draw.rect(dis, red, [foodx, foody, snake_block_size, snake_block_size])  # drawing the food each frame.

        pygame.display.update()
        clock.tick(snake_speed)

    pygame.quit()
    quit()


gameLoop()
