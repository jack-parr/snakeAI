import datetime
import pandas as pd
import pygame
import random
import numpy as np
import warnings
import math
import time

# SETTINGS
dis_width = 100
dis_height = 100
white = (255, 255, 255)  # RGB colour system.
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)


def generate_inputs(block_size, screen_width, screen_height, x_coords, y_coords, foodx, foody):
    inputs = [1, 1, 1, 1, 0, 0, 0, 0]  # up, right, down, left, foodxleft, foodxright, foodyup, foodydown.
    next_moves = [[0, -block_size], [block_size, 0], [0, block_size], [-block_size, 0]]  # in the order up, right, down, left.
    for i in range(4):
        x_test, y_test = next_moves[i]
        if x_coords[0] + x_test > screen_width or x_coords[0] + x_test < 0 or y_coords[0] + y_test > screen_height or y_coords[0] + y_test < 0:
            inputs[i] = 0
        else:
            for ii in range(1, len(x_coords)):
                if x_coords[0] + x_test == x_coords[ii] and y_coords[0] + y_test == y_coords[ii]:
                    inputs[i] = 0
    if foodx < x_coords[0]:
        inputs[4] = 1
    elif foodx > x_coords[0]:
        inputs[5] = 1
    if foody < y_coords[0]:
        inputs[6] = 1
    elif foody > y_coords[0]:
        inputs[7] = 1

    return np.array(inputs)


def game_initialise():
    pygame.init()
    dis = pygame.display.set_mode((dis_width, dis_height))
    pygame.display.set_caption('Snake Game')

    clock = pygame.time.Clock()

    font_style = pygame.font.SysFont(None, 30)
    score_font = pygame.font.SysFont('verdana', 20)

    return dis, clock, font_style, score_font


def search_qtable(q_table, state):
    table_row = q_table.loc[q_table['state'] == str(state)]
    if table_row.empty:
        new_row = {'state': str(state), 'up': 0, 'right': 0, 'down': 0, 'left': 0}
        q_table = pd.DataFrame.append(q_table, new_row, ignore_index=True)
        table_row = q_table.loc[q_table['state'] == str(state)]
    return table_row, q_table


def make_decision(table_row, epsilon, body_direction):
    extracted = table_row.iloc[0]
    list_form = [extracted[1], extracted[2],  extracted[3], extracted[4]]
    if random.randint(0, 100) < epsilon*100:
        decision = random.randint(0, 3)
        while decision == body_direction:
            decision = random.randint(0, 3)
    else:
        decision = np.argsort(list_form)[-1]
        if decision == body_direction:
            decision = np.argsort(list_form)[-2]
    return decision


def process_decision(decision, snake_block_size):
    # 0=up, 1=right, 2=down, 3=left.
    if decision == 0:
        x1_change = 0
        y1_change = -snake_block_size
        body_direction = 2
    elif decision == 1:
        x1_change = snake_block_size
        y1_change = 0
        body_direction = 3
    elif decision == 2:
        x1_change = 0
        y1_change = snake_block_size
        body_direction = 0
    elif decision == 3:
        x1_change = -snake_block_size
        y1_change = 0
        body_direction = 1

    return x1_change, y1_change, body_direction


def decision_analysis(q_table, state, decision, gameover, fruit_eaten, fruit_closer):
    string_stor = ['up', 'right', 'down', 'left']
    table_row = q_table.loc[q_table['state'] == str(state)]
    prev = table_row[string_stor[decision]]
    new = prev
    if gameover == 1:
        new = prev - 0.01
    elif fruit_eaten == 1:
        new = prev + 0.01
    elif fruit_closer == 1:
        new = prev + 0.001
    idx = q_table[q_table['state'] == str(state)].index.values[0]
    q_table.iloc[idx, decision + 1] = new
    return q_table


def run_snake(q_table, epsilon, analyse_decisions):
    dis, clock, font_style, score_font = game_initialise()
    snake_block_size = 10
    game_over = False
    start_pos = 50
    x1 = [start_pos, start_pos - 10, start_pos - 20, start_pos - 30]
    y1 = [start_pos, start_pos, start_pos, start_pos]
    body_direction = 3
    fruit_score = 3
    tot_score = fruit_score - 3
    foodx = round(random.randrange(0, dis_width - snake_block_size) / snake_block_size) * snake_block_size
    foody = round(random.randrange(0, dis_height - snake_block_size) / snake_block_size) * snake_block_size

    timeout = 0
    game_over_check = 0
    old_fruit_dist = 0
    while not game_over:
        if timeout == 200:
            break
        elif game_over_check == 1:
            break

        # NETWORK DECISION
        state = generate_inputs(snake_block_size, dis_width, dis_height, x1, y1, foodx, foody)
        q_row, q_table = search_qtable(q_table, state)
        decision = make_decision(q_row, epsilon, body_direction)
        x1_change, y1_change, body_direction = process_decision(decision, snake_block_size)

        # PROCESSING DECISION IN GAME
        if len(x1) > 1:  # moving the snake pieces in sequence.
            for i in range(len(x1) - 1, 0, -1):
                x1[i] = x1[i - 1]
                y1[i] = y1[i - 1]
        x1[0] += x1_change
        y1[0] += y1_change

        if x1[0] > dis_width or x1[0] < 0 or y1[0] > dis_height or y1[0] < 0:  # detecting hitting the edge.
            game_over_check = 1
        for i in range(1, len(x1)):  # detecting hitting itself.
            if x1[0] == x1[i] and y1[0] == y1[i]:
                game_over_check = 1

        fruit_closer = 0
        new_fruit_dist = math.sqrt((foodx - x1[0])**2 + (foody - y1[0])**2)
        if new_fruit_dist < old_fruit_dist:
            fruit_closer = 1
        old_fruit_dist = new_fruit_dist

        fruit_eaten = 0
        if x1[0] == foodx and y1[0] == foody:  # detecting hitting the food.
            fruit_eaten = 1
            fruit_score += 1
            tot_score = fruit_score - 3
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

        # UPDATING Q_TABLE
        if analyse_decisions:
            q_table = decision_analysis(q_table, state, decision, game_over_check, fruit_eaten, fruit_closer)

        # DRAWING GAME FRAME UPDATE
        dis.fill(white)
        text = score_font.render("Score: " + str(tot_score), True, black)
        dis.blit(text, [0, 0])
        for i in range(0, fruit_score + 1):  # drawing the new snake each frame.
            if i == 0:
                pygame.draw.rect(dis, blue, [x1[i], y1[i], snake_block_size, snake_block_size])
            else:
                pygame.draw.rect(dis, black, [x1[i], y1[i], snake_block_size, snake_block_size])

        pygame.draw.rect(dis, red, [foodx, foody, snake_block_size, snake_block_size])  # drawing the food each frame.
        pygame.display.update()

        timeout += 1
        clock.tick(1000)

    pygame.quit()
    return tot_score, q_table


def save_table(q_table):
    ts = datetime.datetime.today()
    f_name = 'q_table-' + str(ts.year) + str(ts.month) + str(ts.day) + '-' + str(ts.hour) + str(ts.minute)
    q_table.to_csv(f_name, index=False)


def load_table(filename):
    table = pd.read_csv(filename)
    return table


def new_table():
    qt_init = {'state': [0], 'up': [0], 'right': [0], 'down': [0], 'left': [0]}
    q_table = pd.DataFrame(qt_init)
    return q_table


def train_agent(filename, time_seconds, increment):
    q_table = load_table(filename)
    epsilon = 1
    loop = True
    time1 = time.time()
    num_games = 0
    while loop:
        time2 = time.time()
        if time2 - time1 > time_seconds:
            loop = False

        score, q_table = run_snake(q_table, epsilon, analyse_decisions=True)
        num_games += 1
        if epsilon > 0.1:
            epsilon = epsilon - increment
    save_table(q_table)
    print('Training Complete. Games Played: ' + str(num_games))


def assess_agent(filename):
    q_table = load_table(filename)
    scores_cache = []
    for i in range(100):
        print(i)
        score, q_table = run_snake(q_table, epsilon=0, analyse_decisions=False)
        scores_cache.append(score)
    print(sum(scores_cache) / len(scores_cache))


warnings.simplefilter('ignore', lineno=63)
filename = 'q_table-20221222-1326'
train_agent(filename, 3600, 1/5000)
