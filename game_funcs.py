'''

This file contains functions used while running the snake game. Note that these functions do not handle running the game instance itself, but are flexible for use with different player input forms.

'''

import pygame
import random
import numpy as np
import game_configs as config


def display_message(msg, color):
    # display a message given as string 'msg' in the centre of the screen, shown in the RGB colour referenced from 'game_configs.py'.
    msg_text = config.text_font.render(msg, True, color)
    config.dis.blit(msg_text, [(config.dis_width / 2) - 200, config.dis_height / 2])


def game_init():
    # initialise variables used throughout running the game.
    snake_x = np.array([8 * config.snake_block_size, 7 * config.snake_block_size, 6 * config.snake_block_size])  # snake x position as an np.array. The head is at position [0].
    snake_y = np.array([3 * config.snake_block_size, 3 * config.snake_block_size, 3 * config.snake_block_size])  # snake y position as an np.array. The head is at position [0].
    snake_x_step = 0
    snake_y_step = 0
    score = 0
    food_x = round(random.randrange(0, config.dis_width - config.snake_block_size) / config.snake_block_size) * config.snake_block_size  # food x position.
    food_y = round(random.randrange(0, config.dis_height - config.snake_block_size) / config.snake_block_size) * config.snake_block_size  # food y position.

    return snake_x, snake_y, snake_x_step, snake_y_step, score, food_x, food_y


def game_over_screen(score):
    # displays the game over screen.
    config.dis.fill(config.white)
    display_message('Score: ' + str(score) + '. Press Q-Quit or P-Play Again', config.black)
    pygame.display.update()


def snake_self_collision(x, y):
    # detects a self collision of the snake head with the body.
    x = x-x[0]  # subtracts head position from all body pieces.
    y = y-y[0]
    combined = np.vstack((x, y)).T  # combined into array of coord pairs, one for each body part.
    combined = combined[1:]  # removes head piece from array.
    for body in combined:
        check = np.all(body==0)  # if both elements are zero, then the body is in the same position as the head.
        if check == True:
            return True  # triggers when a collision is found.
    
    return False


def food_collision(snake_x, snake_y, food_x, food_y, score):
    # detecting when the snake head hits the food, and spawning a new food.
    if snake_x[0] == food_x and snake_y[0] == food_y:  # detecting hitting the food.
        score += 1
        snake_x = np.append(snake_x, snake_x[-1])  # append arrays with snake body piece.
        snake_y = np.append(snake_y, snake_y[-1])
        food_x = round(random.randrange(0, config.dis_width - config.snake_block_size) / config.snake_block_size) * config.snake_block_size  # randomly generate new fruit coords.
        food_y = round(random.randrange(0, config.dis_height - config.snake_block_size) / config.snake_block_size) * config.snake_block_size
    
    return snake_x, snake_y, food_x, food_y, score


def snake_step(x, y, x_step, y_step):
    # iterates the snake coord arrays one step.
    x_new = np.copy(x)  # this avoids the original x and y getting overwritten.
    y_new = np.copy(y)
    if x_step == 0 and y_step == 0:
        pass
    else:
        for i in range(len(x_new) - 1, 0, -1):  # starts from the last entry, and ignores the first entry.
            x_new[i] = x_new[i - 1]  # each entry takes on the coords of the piece ahead of it.
            y_new[i] = y_new[i - 1]
        x_new[0] += x_step  # add step onto the head of the snake.
        y_new[0] += y_step
    
    return x_new, y_new


def frame_update(snake_x, snake_y, food_x, food_y, score):
    # draws the frame.
    config.dis.fill(config.white)  # covering the whole frame in white first.
    score_text = config.score_font.render('Score: ' + str(score), True, config.black)  # rendering 'score'.
    config.dis.blit(score_text, [0, 0])  # drawing score onto frame.
    controls_text = config.score_font.render('WASD', True, config.black)  # rendering controls.
    config.dis.blit(controls_text, [0, config.dis_height - 25])  # drawing controls onto frame.

    for i in range(0, len(snake_x)):  # drawing the snake.
        if i == 0:  # draws the head.
            pygame.draw.rect(config.dis, config.blue, [snake_x[i], snake_y[i], config.snake_block_size, config.snake_block_size])
        else:  # draws all the body pieces.
            pygame.draw.rect(config.dis, config.black, [snake_x[i], snake_y[i], config.snake_block_size, config.snake_block_size])

    pygame.draw.rect(config.dis, config.red, [food_x, food_y, config.snake_block_size, config.snake_block_size])  # drawing the food.
