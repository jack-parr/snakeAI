"""

This file runs the game controlled by computer agent that learns through a generational algorithm.

"""

import datetime
import time
import pygame
import numpy as np
import pygad.kerasga
from keras import Sequential
from keras.layers import Dense
import game_configs as config
import game_funcs as funcs
import QL as ql_funcs


def generate_inputs(block_size, snake_x, snake_y, food_x, food_y):
    # this generates the inputs needed for the model.
    inputs = [1, 1, 1, 1, 0, 0]  # up, right, down, left, food x direction, food y direction.

    next_moves = [[0, -block_size], [block_size, 0], [0, block_size], [-block_size, 0]]  # in the order up, right, down, left.
    for i in range(4):  # cycles through each move.
        
        x_step_test, y_step_test = next_moves[i]  # separates move into x and y components.
        snake_x_test, snake_y_test = funcs.snake_step(snake_x, snake_y, x_step_test, y_step_test)  # moving the snake pieces in sequence according to the test direction.
        if snake_x_test[0] + x_step_test >= config.dis_width or snake_x_test[0] + x_step_test < 0 or snake_y_test[0] + y_step_test >= config.dis_height or snake_y_test[0] + y_step_test < 0:  # detecting hitting the edge of the board.
            inputs[i] = 0  # marks this move invalid.
        else:
            check_self_collide = funcs.snake_self_collision(snake_x_test, snake_y_test)  # detecting the snake hitting itself.
            if check_self_collide == True:  # snake self collision has been detected.
                inputs[i] = 0  # marks this move invalid.

    if food_x - snake_x[0] > 0:  # food is to the right of head.
        inputs[4] = 1
    elif food_x - snake_x[0] < 0:  # food is to the left of head.
        inputs[4] = -1
    
    if food_y - snake_y[0] < 0:  # food is above the head.
        inputs[5] = 1
    elif food_y - snake_y[0] > 0:  # food is below the head.
        inputs[5] = -1

    return np.array(inputs)


def run_agent(model):
    # this is the main running loop for the game controlled by a model trained using generational algorithm.
    game_over = False  # indicates whether the game has finished.
    running = True  # indicates whether the window needs to close.

    snake_x, snake_y, snake_x_step, snake_y_step, score, food_x, food_y = funcs.game_init()  # initialise variables.

    timeout = 0  # timeout counter.
    body_direction = 3  # initial body direction is left.

    while running:

        if timeout == 200:
            game_over = True
        
        if game_over == True:
            return score


        # NETWORK DECISION
        inputs = generate_inputs(config.snake_block_size, snake_x, snake_y, food_x, food_y)  # generate inputs based on current game state.
        inputs = inputs.reshape(1, 6)  # reformat inputs for model.
        output = model.predict(inputs, verbose=0)  # get output from model. Verbose=0 supresses the progress bar output.
        decision = np.argsort(output[0])[-1]  # selecting index of largest output.

        if decision == body_direction:  # if decision is invalid, selecting index of second largest output.
            decision = np.argsort(output[0])[-2]
        
        snake_x_step, snake_y_step, body_direction = ql_funcs.process_decision(decision, config.snake_block_size)  # extracting changes from decision.
            

        # PROCESSING GAME STATE
        if snake_x[0] >= config.dis_width or snake_x[0] < 0 or snake_y[0] >= config.dis_height or snake_y[0] < 0:  # detecting hitting the edge of the board.
            game_over = True
        
        check_self_collide = funcs.snake_self_collision(snake_x, snake_y)  # detecting the snake hitting itself.
        if check_self_collide == True:  # snake self collision has been detected.
            game_over = True

        snake_x, snake_y = funcs.snake_step(snake_x, snake_y, snake_x_step, snake_y_step)  # moving the snake pieces in sequence.

        snake_x, snake_y, food_x, food_y, score = funcs.food_collision(snake_x, snake_y, food_x, food_y, score)  # detecting food collision.

        
        # UPDATING FRAME
        funcs.frame_update(snake_x, snake_y, food_x, food_y, score)

        pygame.display.update()  # refreshing the game display each frame.
        config.clock.tick(1000)  # moving onto the next frame.
        timeout += 1  # incrementing timeout counter.


# GENETIC ALGORITHM FUNCTIONS
def fitness_func(ga_instance, solution, sol_idx):
    # this is the fitness function, which returns averages the score of 3 games of snake played by a model.
    global model
    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=model, weights_vector=solution)
    model.set_weights(weights=model_weights_matrix)

    scores_cache = []  # initiates score storage.
    for i in range(3):  # plays 3 games.
        scores_cache.append(run_agent(model))  # runs the game and adds the score into the storage.

    solution_fitness = np.average(scores_cache)  # averages the scores.
    print('Average of Model: ' + str(solution_fitness))  # prints the average.

    return solution_fitness  # returns the average as the fitness score for that model.


def on_generation(ga):
    # this runs when a new generation starts to inform the user of the progress.
    print()
    print("--- Generation " + str(ga.generations_completed) + " Completed ---")
    print()


def initialise_model():
    # this initiates a new DNN model, with dimensions and activation functions specified.
    model = Sequential()
    model.add(Dense(64, input_dim=6, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(4, activation='softmax'))

    model.build(input_shape=(1, 6))  # builds the model object with the necessary input shape.
    return model


def create_new_GA(model, num_generations, population_size, num_parents_mating):
    # this initiates a GA instance according to the inputs.
    keras_ga = pygad.kerasga.KerasGA(model=model, num_solutions=population_size)
    initial_population = keras_ga.population_weights

    ga_instance = pygad.GA(num_generations=num_generations,
                           num_parents_mating=num_parents_mating,
                           initial_population=initial_population,
                           fitness_func=fitness_func,
                           save_best_solutions=False,
                           on_generation=on_generation,
                           keep_elitism=5,
                           stop_criteria=['reach_30', 'saturate_99999'])  # stops when it reaches 30 generations.
    
    return ga_instance


def load_GA(filename):
    # this loads a GA instance specified by the string 'filename'.
    ga_instance = pygad.load(filename)
    return ga_instance


def run_GA(ga_instance, version):
    # this function runs the GA instance and trains the model.
    time_start = time.time()  # takes a start time reading.
    ga_instance.run()  # runs the training.
    time_end = time.time()  # takes an end time reading.
    print('Time taken for ' + str(num_generations) + ' generations of ' + str(population_size) + ': ' + str(time_end - time_start))

    ts = datetime.datetime.today()  # current date and time.
    f_name = version+'-'+str(ts.year)+str(ts.month)+str(ts.day)+'-'+str(ts.hour)+str(ts.minute)  # creates the filename string.
    ga_instance.save(filename=f_name)  # saves the GA instance.

    return ga_instance, f_name


def split_sol(sol):
    # this splits the weights and biases of the model down, so that they can be correctly put into a model for assessment.
    output = []
    output.append(np.reshape(sol[:384], (6, 64)))  # layer 1 weights.
    output.append(sol[384:448])  # layer 1 biases.
    output.append(np.reshape(sol[448:2496], (64, 32)))  # layer 2 weights.
    output.append(sol[2496:2528])  # layer 2 biases
    output.append(np.reshape(sol[2528:3040], (32, 16)))  # layer 3 weights.
    output.append(sol[3040:3056])  # layer 3 biases.
    output.append(np.reshape(sol[3056:3120], (16, 4)))  # layer 4 weights.
    output.append(sol[3120:3124])  # ;ayer 4 biases.

    return output


def new_model(version, num_generations, population_size, num_parents_mating):
    # initiates a new model.
    ga_instance = create_new_GA(model, num_generations=num_generations, population_size=population_size, num_parents_mating=num_parents_mating)
    time_start = time.time()  # takes start time reading.
    ga_instance, f_name = run_GA(ga_instance, version=version)  # runs the training.
    time_end = time.time()  # takes end time reading.
    print('Time Taken: ' + str(time_end - time_start))


def train_model(version, filename, num_generations):
    # trains the model using a pre-existing GA instance specified by the 'filename' string using a specified number of generations. Saves using the 'version' string.
    ga_instance = load_GA(filename=filename)  # loads the GA instance.
    ga_instance.num_generations = num_generations  # sets the number of generations.
    time_start = time.time()  # take a start time reading.
    ga_instance, f_name = run_GA(ga_instance, version=version)  # runs the training.
    time_end = time.time()  # takes an end time reading.
    print('Time Taken: ' + str(time_end - time_start))
    ga_instance.plot_fitness()  # plots the fitness of the model throughout the training.


def assess_best(filename, num_games):
    # assesses the best model from the GA instance specified by the 'filename' string, over a specified number of games.
    ga_instance = load_GA(filename=filename)  # loads the GA instance.
    best_sol, sol_fit, sol_idx = ga_instance.best_solution()  # extracts best solution.
    model.set_weights(weights=split_sol(best_sol))  # sets weights of best solution.

    scores_cache = []  # initiates score storage.
    for i in range(num_games):  # runs the number of games specified.
        scores_cache.append(run_agent(model))  # runs the model and stores the score.

    print('Average of ' + str(num_games) + ' games: ' + str(np.average(scores_cache)))


"""
EXAMPLE USING FUNCTIONS.
"""

model = initialise_model()  # initiates the model object.
version = 'v1.4.0'  # specifies version number.

num_generations = 10  # parameters training.
population_size = 30
num_parents_mating = 15

# new_model(version, num_generations, population_size, num_parents_mating)  # trains a new model.

filename = 'v1.4.0-100_generations'
# train_model(version, filename, 10)

assess_best(filename, 100)  # assesses best model from specified saved GA instance.
