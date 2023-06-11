"""

This file runs the game controlled by computer agent that learns through Q-Learning. There is functions used for running the game, and functions for the user to choose relating to the q-learning process.

"""

import datetime
import pandas as pd
import pygame
import random
import numpy as np
import warnings
import math
import time
import game_funcs as funcs
import game_configs as config


def generate_inputs(block_size, x, y, food_x, food_y):
    # this generates the inputs needed for the q-table lookup.
    inputs = [1, 1, 1, 1, 0, 0, 0, 0]  # up, right, down, left, food_left, food_right, food_up, food_down.
    next_moves = [[0, -block_size], [block_size, 0], [0, block_size], [-block_size, 0]]  # in the order up, right, down, left.
    for i in range(4):  # cycles through each move.
        
        x_step_test, y_step_test = next_moves[i]  # separates move into x and y components.
        snake_x_test, snake_y_test = funcs.snake_step(x, y, x_step_test, y_step_test)  # moving the snake pieces in sequence according to the test direction.
        if snake_x_test[0] + x_step_test >= config.dis_width or snake_x_test[0] + x_step_test < 0 or snake_y_test[0] + y_step_test >= config.dis_height or snake_y_test[0] + y_step_test < 0:  # detecting hitting the edge of the board.
            inputs[i] = 0  # marks this move invalid.
        else:
            check_self_collide = funcs.snake_self_collision(snake_x_test, snake_y_test)  # detecting the snake hitting itself.
            if check_self_collide == True:  # snake self collision has been detected.
                inputs[i] = 0  # marks this move invalid.

    if food_x < x[0]:  # detecting food to the left of snake head.
        inputs[4] = 1
    elif food_x > x[0]:  # detecting food to the right.
        inputs[5] = 1

    if food_y < y[0]:  # detecting food above.
        inputs[6] = 1
    elif food_y > y[0]:  # detecting food below.
        inputs[7] = 1

    return np.array(inputs)


def search_qtable(q_table, state):
    # this searches the q-table for the current state and returns the row. If this is a new state, it adds it to the q-table.
    table_row = q_table.loc[q_table['state'] == str(state)]  # searching q-table.

    if table_row.empty:  # this is a new state.
        new_row = {'state': str(state), 'up': 0, 'right': 0, 'down': 0, 'left': 0}  # initiates new row.
        q_table = pd.DataFrame.append(q_table, new_row, ignore_index=True)  # adds new row to q-table.
        table_row = q_table.loc[q_table['state'] == str(state)]  # extracts row.

    return table_row, q_table


def make_decision(table_row, epsilon, body_direction):
    # this makes a decision based on the input information.
    extracted = table_row.iloc[0]  # formatting the row.
    list_form = [extracted[1], extracted[2],  extracted[3], extracted[4]]

    if random.randint(0, 100) < epsilon*100:  # random decision is made.
        decision = random.randint(0, 3)
        while decision == body_direction:  # keeps going until random decision is not a 180 turn into the snake body.
            decision = random.randint(0, 3)
    else:
        decision = np.argsort(list_form)[-1]  # selects best decision.
        if decision == body_direction:  # decision is a 180 turn into the snake body.
            decision = np.argsort(list_form)[-2]  # selects second best decision.

    return decision


def process_decision(decision, snake_block_size):
    # turns the decision into the steps in each direction, and modifies the body directions.
    # 0 = up, 1 = right, 2 = down, 3 = left.
    if decision == 0:
        snake_x_step = 0
        snake_y_step = -snake_block_size
        body_direction = 2
    elif decision == 1:
        snake_x_step = snake_block_size
        snake_y_step = 0
        body_direction = 3
    elif decision == 2:
        snake_x_step = 0
        snake_y_step = snake_block_size
        body_direction = 0
    elif decision == 3:
        snake_x_step = -snake_block_size
        snake_y_step = 0
        body_direction = 1

    return snake_x_step, snake_y_step, body_direction


def decision_analysis(q_table, state, decision, gameover, fruit_eaten, fruit_closer):
    # analyses the decision to score it, and inputs this score into table.
    string_stor = ['up', 'right', 'down', 'left']
    table_row = q_table.loc[q_table['state'] == str(state)]  # extracts table row based on state.
    prev = table_row[string_stor[decision]]  # extracts
    new = prev  # initially has the old value.

    if gameover == True:  # decision causes the game to end.
        new = prev - 0.01  # decreases score.
    elif fruit_eaten == True:  # decision causes a piece of fruit to be eaten.
        new = prev + 0.01  # increases score.
    elif fruit_closer == True:  # decision causes the fruit to become closer.
        new = prev + 0.001  # slightly increases score.

    idx = q_table[q_table['state'] == str(state)].index.values[0]
    q_table.iloc[idx, decision + 1] = new  # inserts new score into q-table.

    return q_table  # returns the modified q-table.


def modified_food_collision(snake_x, snake_y, food_x, food_y, score):
    # this modifies the 'food_collision' function to also provide an indicator variable, 'eaten'.
    prev_score = score
    snake_x, snake_y, food_x, food_y, score = funcs.food_collision(snake_x, snake_y, food_x, food_y, score)  # runs original 'food_collision' function.
    if prev_score != score:  # checks if score has increased.
        eaten = True
    else:
        eaten = False

    return snake_x, snake_y, food_x, food_y, score, eaten


def run_agent(q_table, epsilon, analyse_decisions):
    # this is the main running loop for the game training an agent using Q-Learning. If 'analyse_decisions' == True, then the Q-table is updated with each decision.
    game_over = False  # indicates whether the game has finished.
    running = True  # indicates whether the window needs to close.

    snake_x, snake_y, snake_x_step, snake_y_step, score, food_x, food_y = funcs.game_init()  # initialise variables.

    timeout = 0  # timeout counter.
    body_direction = 3  # initial body direction is left.
    game_over_check = 0
    old_fruit_dist = 0

    while running:

        if timeout == 200:  # 200 moves have been made.
            game_over = True
        
        if game_over == True:
            return score, q_table


        # MAKING DECISION
        state = generate_inputs(config.snake_block_size, snake_x, snake_y, food_x, food_y)  # formatting the inputs for the agent.
        q_row, q_table = search_qtable(q_table, state)  # extracting row from the q-table, or initialising a new row.
        decision = make_decision(q_row, epsilon, body_direction)  # making a decision.
        snake_x_step, snake_y_step, body_direction = process_decision(decision, config.snake_block_size)  # extracting changes from decision.


        # PROCESSING GAME STATE
        if snake_x[0] >= config.dis_width or snake_x[0] < 0 or snake_y[0] >= config.dis_height or snake_y[0] < 0:  # detecting hitting the edge of the board.
            game_over = True
        
        check_self_collide = funcs.snake_self_collision(snake_x, snake_y)  # detecting the snake hitting itself.
        if check_self_collide == True:  # snake self collision has been detected.
            game_over = True

        snake_x, snake_y = funcs.snake_step(snake_x, snake_y, snake_x_step, snake_y_step)  # moving the snake pieces in sequence.
        
        snake_x, snake_y, food_x, food_y, score, fruit_eaten = modified_food_collision(snake_x, snake_y, food_x, food_y, score)  # detecting food collision.

        new_fruit_dist = math.sqrt((food_x - snake_x[0])**2 + (food_y - snake_y[0])**2)  # calculating new distance to food.
        if new_fruit_dist < old_fruit_dist:
            fruit_closer = True  # fruit is now closer to snake head.
        else:
            fruit_closer = False  # fruit is not closer to snake head.
        old_fruit_dist = new_fruit_dist  # prepping 'old_fruit_dist' for next move.


        # UPDATING Q_TABLE
        if analyse_decisions == True:  # if this is given as False, then the Q-table won't be updated as it is used.
            q_table = decision_analysis(q_table, state, decision, game_over, fruit_eaten, fruit_closer)


        # UPDATING FRAME
        funcs.frame_update(snake_x, snake_y, food_x, food_y, score)

        pygame.display.update()  # refreshing the game display each frame.
        config.clock.tick(1000)  # moving onto the next frame.
        timeout += 1  # incrementing timeout counter.


def save_table(q_table):
    # saves the Q-table in csv format, labelled with the date and time.
    ts = datetime.datetime.today()
    f_name = 'q_table-' + str(ts.year) + str(ts.month) + str(ts.day) + '-' + str(ts.hour) + str(ts.minute)  # filename string.
    q_table.to_csv(f_name, index=False)


def load_table(filename):
    # loads a pre-existing Q-table, according to the string 'filename'.
    table = pd.read_csv(filename)
    return table


def new_table():
    # initiates a new Q-table as a pd.DataFrame.
    qt_init = {'state': [0], 'up': [0], 'right': [0], 'down': [0], 'left': [0]}
    q_table = pd.DataFrame(qt_init)
    return q_table


def train_agent(filename, num_games, epsilon):
    # trains an agent started with a table indicated by 'filename'. Saves trained table into a new csv file.
    q_table = load_table(filename)  # loads the Q-table.

    time1 = time.time()  # taken initial time.
    for i in range(num_games):
        score, q_table = run_agent(q_table, epsilon, analyse_decisions=True)

    time2 = time.time()  # take end time.
    save_table(q_table)  # saves the trained table.
    print('Training Complete. Time taken for ' + str(num_games) + ' games: ' + str(time2 - time1) + ' seconds.') 


def assess_agent(filename):
    # this tests an agent by running it 100 times using the Q-table indicated by 'filename' without altering the Q-table, and printing the average score achieved.
    q_table = load_table(filename)  # loads the Q-table.
    scores_cache = []  # initiates score storing.
    for i in range(100):  # runs for 100 games.
        score, q_table = run_agent(q_table, epsilon=0, analyse_decisions=False)  # epsilon = 0 for no random decisions to be made (no exploration).
        scores_cache.append(score)  # add score into storage.
    print('Assessment Complete. Average Score: ' + str(sum(scores_cache) / len(scores_cache)))  # printing the average score achieved.


warnings.simplefilter('ignore', lineno=53)  # prevents warning from flooding the console.

"""

EXAMPLE USING FUNCTIONS.

table = new_table()  # creates new table.
save_table(table)  # saves the table.

filename = 'q_table-empty'  # empty table.
filename = 'q_table-202365-1338'  # table trained over 10,000 games, epsilon = 0.3.
# train_agent(filename, 5000, 0.3)
assess_agent(filename)

"""
