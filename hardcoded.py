import pandas as pd
import pygame
import random
import numpy as np
import math
import matplotlib.pyplot as plt
import netfuncs
import time


# Settings.
dis_width = 100
dis_height = 100
white = (255, 255, 255)  # RGB colour system.
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)


# Setting Up Game.
pygame.init()
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Snake Game')

clock = pygame.time.Clock()

font_style = pygame.font.SysFont(None, 30)
score_font = pygame.font.SysFont('verdana', 20)


def sim_score(collision, old_fruit_dis, new_fruit_dis):
    value = 1000 - (new_fruit_dis - old_fruit_dis) - (collision * 1000)
    return value


def sim_collision(x1, y1, x_test, y_test):
    check = 0
    if x_test > dis_width or x_test < 0 or y_test > dis_height or y_test < 0:  # detecting hitting the edge.
        check = 1
    for i in range(1, len(x1)):  # detecting hitting itself.
        if x_test == x1[i] and y_test == y1[i]:
            check = 1
    return check


def list_loop(idx):
    if idx == -1:
        return 3
    elif idx == 4:
        return 0
    else:
        return idx


# Running Generation.
def run_generation():
    snake_block_size = 10
    game_over = False
    start_pos = 50
    x1 = [start_pos, start_pos - 10, start_pos - 20, start_pos - 30]
    y1 = [start_pos, start_pos, start_pos, start_pos]
    orientation_idx = 0  # 0 = right, 1 = down, 2 = left, 3 = up.
    ori_x_lookup = [snake_block_size, 0, -snake_block_size, 0]
    ori_y_lookup = [0, snake_block_size, 0, -snake_block_size]
    fruit_score = 3
    foodx = round(random.randrange(0, dis_width - snake_block_size) / snake_block_size) * snake_block_size
    foody = round(random.randrange(0, dis_height - snake_block_size) / snake_block_size) * snake_block_size
    bias_s = 0
    bias_l = 0
    bias_r = 0

    timeout = 0
    while not game_over:
        if timeout == 200:
            game_over = True
        old_food_dis = math.sqrt((x1[0] - foodx) ** 2 + (y1[0] - foody) ** 2)

        # SIMULATIONS
        # STRAIGHT
        test_orientation_idx = orientation_idx
        test_orientation_idx = list_loop(test_orientation_idx)
        x_test = x1[0] + ori_x_lookup[test_orientation_idx]
        y_test = y1[0] + ori_y_lookup[test_orientation_idx]
        new_food_dis = math.sqrt((x_test - foodx) ** 2 + (y_test - foody) ** 2)
        collision_check = sim_collision(x1, y1, x_test, y_test)
        value_S = sim_score(collision_check, old_food_dis, new_food_dis) + bias_s
        decision = "S"

        # LEFT
        test_orientation_idx = orientation_idx - 1
        test_orientation_idx = list_loop(test_orientation_idx)
        x_test = x1[0] + ori_x_lookup[test_orientation_idx]
        y_test = y1[0] + ori_y_lookup[test_orientation_idx]
        new_food_dis = math.sqrt((x_test - foodx) ** 2 + (y_test - foody) ** 2)
        collision_check = sim_collision(x1, y1, x_test, y_test)
        value_L = sim_score(collision_check, old_food_dis, new_food_dis) + bias_l
        if value_L > value_S:
            decision = "L"

        # RIGHT
        test_orientation_idx = orientation_idx + 1
        test_orientation_idx = list_loop(test_orientation_idx)
        x_test = x1[0] + ori_x_lookup[test_orientation_idx]
        y_test = y1[0] + ori_y_lookup[test_orientation_idx]
        new_food_dis = math.sqrt((x_test - foodx) ** 2 + (y_test - foody) ** 2)
        collision_check = sim_collision(x1, y1, x_test, y_test)
        value_R = sim_score(collision_check, old_food_dis, new_food_dis) + bias_r
        if value_R > value_L and value_R > value_S:
            decision = "R"

        if decision == "S":  # keep going straight.
            pass
        elif decision == "L":  # turn left.
            orientation_idx -= 1
        elif decision == "R":  # turn right.
            orientation_idx += 1
        orientation_idx = list_loop(orientation_idx)

        x1_change = ori_x_lookup[orientation_idx]
        y1_change = ori_y_lookup[orientation_idx]

        # PROCESSING DECISION IN GAME
        if len(x1) > 1:  # moving the snake pieces in sequence.
            for i in range(len(x1) - 1, 0, -1):
                x1[i] = x1[i - 1]
                y1[i] = y1[i - 1]
        x1[0] += x1_change
        y1[0] += y1_change

        if x1[0] > dis_width or x1[0] < 0 or y1[0] > dis_height or y1[0] < 0:  # detecting hitting the edge.
            game_over = True
        for i in range(1, len(x1)):  # detecting hitting itself.
            if x1[0] == x1[i] and y1[0] == y1[i]:
                game_over = True

        if x1[0] == foodx and y1[0] == foody:  # detecting hitting the food.
            fruit_score += 1
            x1.append(x1[-1])
            y1.append(y1[-1])
            check_fruit_spawn = True
            while check_fruit_spawn:
                foodx = round(random.randrange(0, dis_width - snake_block_size) / snake_block_size) * snake_block_size
                foody = round(random.randrange(0, dis_height - snake_block_size) / snake_block_size) * snake_block_size
                spawn_new_fruit = False
                for i in range(len(x1)):
                    x_check = x1[i]
                    y_check = y1[i]
                    if foodx == x_check and foody == y_check:
                        spawn_new_fruit = True
                        break
                if not spawn_new_fruit:
                    check_fruit_spawn = False

        # DRAWING GAME FRAME UPDATE
        dis.fill(white)
        text = score_font.render("Score: " + str(fruit_score - 2), True, black)
        dis.blit(text, [0, 0])
        for i in range(0, fruit_score + 1):  # drawing the new snake each frame.
            if i == 0:
                pygame.draw.rect(dis, blue, [x1[i], y1[i], snake_block_size, snake_block_size])
            else:
                pygame.draw.rect(dis, black, [x1[i], y1[i], snake_block_size, snake_block_size])

        pygame.draw.rect(dis, red, [foodx, foody, snake_block_size, snake_block_size])  # drawing the food each frame.
        pygame.display.update()

        timeout += 1
        clock.tick(300)

    print("Score: " + str(fruit_score - 3))
    return fruit_score - 3


def run_agent(num_games):
    scores_cache = []
    for i in range(num_games):
        print(i)
        sim = run_generation()
        scores_cache.append(sim)
    print(sum(scores_cache)/len(scores_cache))


run_agent(100)
