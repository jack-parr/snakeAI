"""

This file runs the game controlled by a hardcoded computer agent.

"""

import pygame
import math
import numpy as np
import game_configs as config
import game_funcs as funcs


def sim_score(collision, current_fruit_dis, new_fruit_dis):
    # this calculates the score of a move based on the input information.
    score = 1000 - (new_fruit_dis - current_fruit_dis) - (collision * 1000)
    return score


def sim_collision(x, y, snake_x_step_test, snake_y_step_test):
    # this detects any kind of gameover via collision, based on the test direction.
    snake_x_test, snake_y_test = funcs.snake_step(x, y, snake_x_step_test, snake_y_step_test)  # moving the snake pieces in sequence according to the test direction.

    if snake_x_test[0] >= config.dis_width or snake_x_test[0] < 0 or snake_y_test[0] >= config.dis_height or snake_y_test[0] < 0:  # detecting hitting the edge of the board.
        return True  # returns if snake leaves board.
    
    check_self_collide = funcs.snake_self_collision(snake_x_test, snake_y_test)  # detecting the snake hitting itself.
    if check_self_collide == True:  # snake self collision has been detected.
        return True  # returns if snake collides with itself.
    
    return False  # returns if snake survives.


def list_loop(idx):
    # this checks if the reference has spilled out of the dimensions, and loops it to the other end of the list.
    if idx == -1:
        return 3
    elif idx == 4:
        return 0
    else:
        return idx


def calc_new_food_dis(snake_x, snake_y, snake_x_step_test, snake_y_step_test, food_x, food_y):
    # calculates new distance to food based on current snake arrays and the test snake steps.
    return math.sqrt((snake_x[0] + snake_x_step_test - food_x) ** 2 + (snake_y[0] + snake_y_step_test - food_y) ** 2)


def run_agent():
    # this is the running loop for a game controlled by the hardcoded agent.
    game_over = False  # indicates whether the game has finished.
    running = True  # indicates whether the window needs to close.

    snake_x, snake_y, snake_x_step, snake_y_step, score, food_x, food_y = funcs.game_init()  # initialise variables.

    orientation_idx = 0  # 0 = right, 1 = down, 2 = left, 3 = up.
    ori_x_lookup = [config.snake_block_size, 0, -config.snake_block_size, 0]  # lookup in x-direction based on 'orientation_idx'.
    ori_y_lookup = [0, config.snake_block_size, 0, -config.snake_block_size]  # lookup in y-direction based on 'orientation_idx'.
    decision_lookup = [0, -1, 1]  # straight, left, right.

    timeout = 0  # initialising timeout counter.
    while running:

        if timeout == 200:  # 200 moves have been made.
            game_over = True
        
        if game_over == True:  # game is over, either by collision or by timeout.
            return score  # returns the score.
        
        current_food_dis = math.sqrt((snake_x[0] - food_x) ** 2 + (snake_y[0] - food_y) ** 2)  # calculates the current distance to the food.
        

        # SIMULATIONS
        # STRAIGHT
        test_orientation_idx = orientation_idx  # keeps the orientation the same.
        snake_x_step_test = ori_x_lookup[test_orientation_idx]  # extracts snake step values in each direction.
        snake_y_step_test = ori_y_lookup[test_orientation_idx]
        new_food_dis = calc_new_food_dis(snake_x, snake_y, snake_x_step_test, snake_y_step_test, food_x, food_y)  # calculates what would be the new distance to the food.
        collision_check = sim_collision(snake_x, snake_y, snake_x_step_test, snake_y_step_test)  # checks for any collisions.
        score_straight = sim_score(collision_check, current_food_dis, new_food_dis)  # scores based on input information.
        
        # TURN LEFT
        test_orientation_idx = list_loop(orientation_idx - 1)  # turns orientation to the left.
        snake_x_step_test = ori_x_lookup[test_orientation_idx]  # extracts snake step values in each direction.
        snake_y_step_test = ori_y_lookup[test_orientation_idx]
        new_food_dis = calc_new_food_dis(snake_x, snake_y, snake_x_step_test, snake_y_step_test, food_x, food_y)  # calculates what would be the new distance to the food.
        collision_check = sim_collision(snake_x, snake_y, snake_x_step_test, snake_y_step_test)  # checks for any collisions.
        score_left = sim_score(collision_check, current_food_dis, new_food_dis)  # scores based on input information.
        
        # TURN RIGHT
        test_orientation_idx = list_loop(orientation_idx + 1)  # turns orientation to the left.
        snake_x_step_test = ori_x_lookup[test_orientation_idx]  # extracts snake step values in each direction.
        snake_y_step_test = ori_y_lookup[test_orientation_idx]
        new_food_dis = calc_new_food_dis(snake_x, snake_y, snake_x_step_test, snake_y_step_test, food_x, food_y)  # calculates what would be the new distance to the food.
        collision_check = sim_collision(snake_x, snake_y, snake_x_step_test, snake_y_step_test)  # checks for any collisions.
        score_right = sim_score(collision_check, current_food_dis, new_food_dis)  # scores based on input information.


        # MAKING DECISION
        decision_idx = np.argmax(np.array([score_straight, score_left, score_right]))  # finds highest scoring direction.
        decision = decision_lookup[decision_idx]  # extracts the decision.
        orientation_idx = list_loop(orientation_idx + decision)  # modifies the orientation.

        snake_x_step = ori_x_lookup[orientation_idx]  # finds step values in each direction based on decision.
        snake_y_step = ori_y_lookup[orientation_idx]


        # PROCESSING GAME STATE
        if snake_x[0] >= config.dis_width or snake_x[0] < 0 or snake_y[0] >= config.dis_height or snake_y[0] < 0:  # detecting hitting the edge of the board.
            game_over = True
            continue  # jumps to start of while loop. Avoids extra animation after collision.
        
        check_self_collide = funcs.snake_self_collision(snake_x, snake_y)  # detecting the snake hitting itself.
        if check_self_collide == True:  # snake self collision has been detected.
            game_over = True
            continue  # jumps to start of while loop. Avoids extra animation after collision.

        snake_x, snake_y = funcs.snake_step(snake_x, snake_y, snake_x_step, snake_y_step)  # moving the snake pieces in sequence.
        
        snake_x, snake_y, food_x, food_y, score = funcs.food_collision(snake_x, snake_y, food_x, food_y, score)  # detecting food collision.


        # UPDATING FRAME
        funcs.frame_update(snake_x, snake_y, food_x, food_y, score)

        pygame.display.update()  # refreshing the game display each frame.
        config.clock.tick(1000)  # moving onto the next frame.
        timeout += 1  # incrementing timeout counter.



def run_batch(num_agents):
    # runs a specified number of agents in a row.
    scores_cache = []
    for i in range(num_agents):
        agent_score = run_agent()
        scores_cache.append(agent_score)
    print('Average Score: ' + str(sum(scores_cache)/len(scores_cache)))


run_batch(100)
