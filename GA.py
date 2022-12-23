import datetime
import time
import pygame
import random
import numpy as np
import pygad.kerasga
from keras import Sequential
from keras.layers import Dense

# SETTINGS
dis_width = 100
dis_height = 100
white = (255, 255, 255)  # RGB colour system.
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)


def generate_inputs(block_size, screen_width, screen_height, x_coords, y_coords, foodx, foody):
    inputs = [1, 1, 1, 1, foodx-x_coords[0], foody-y_coords[0]]  # v1.1

    next_moves = [[0, -block_size], [block_size, 0], [0, block_size], [-block_size, 0]]  # in the order up, right, down, left.
    for i in range(4):
        x_test, y_test = next_moves[i]
        if x_coords[0] + x_test > screen_width or x_coords[0] + x_test < 0 or y_coords[0] + y_test > screen_height or y_coords[0] + y_test < 0:
            inputs[i] = 0
        else:
            for ii in range(1, len(x_coords)):
                if x_coords[0] + x_test == x_coords[ii] and y_coords[0] + y_test == y_coords[ii]:
                    inputs[i] = 0
    for i in range(4, 6):
        check = inputs[i]
        if check > 0:
            inputs[i] = 1
        elif check < 0:
            inputs[i] = -1
    return np.array(inputs)


def game_initialise():
    pygame.init()
    dis = pygame.display.set_mode((dis_width, dis_height))
    pygame.display.set_caption('Snake Game')

    clock = pygame.time.Clock()

    font_style = pygame.font.SysFont(None, 30)
    score_font = pygame.font.SysFont('verdana', 20)

    return dis, clock, font_style, score_font


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


def run_snake(model):
    dis, clock, font_style, score_font = game_initialise()
    snake_block_size = 10
    game_over = False
    start_pos = 50
    x1 = [start_pos, start_pos - 10, start_pos - 20, start_pos - 30]
    y1 = [start_pos, start_pos, start_pos, start_pos]
    body_direction = 3
    fruit_score = 3
    foodx = round(random.randrange(0, dis_width - snake_block_size) / snake_block_size) * snake_block_size
    foody = round(random.randrange(0, dis_height - snake_block_size) / snake_block_size) * snake_block_size

    timeout = 0
    while not game_over:
        if timeout == 200:
            game_over = True
        # NETWORK DECISION
        inputs = generate_inputs(snake_block_size, dis_width, dis_height, x1, y1, foodx, foody)
        inputs = inputs.reshape(1, 6)
        output = model.predict(inputs)
        decision = np.argsort(output[0])[-1]  # selecting index of largest output.
        if decision != body_direction:
            x1_change, y1_change, body_direction = process_decision(decision, snake_block_size)
        else:
            decision = np.argsort(output[0])[-2]  # selecting index of second largest output.
            x1_change, y1_change, body_direction = process_decision(decision, snake_block_size)

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
        text = score_font.render("Score: " + str(fruit_score - 3), True, black)
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

    print()
    pygame.quit()
    return fruit_score - 3


# GENETIC ALGORITHM
def fitness_func(solution, sol_idx):
    global model
    model_weights_matrix = pygad.kerasga.model_weights_as_matrix(model=model, weights_vector=solution)
    model.set_weights(weights=model_weights_matrix)

    scores_cache = []
    for i in range(3):
        scores_cache.append(run_snake(model))
    solution_fitness = np.average(scores_cache)
    print('Average: ' + str(solution_fitness))
    print()
    return solution_fitness


def on_generation(ga):
    print()
    print("--- Generation " + str(ga.generations_completed) + " Completed ---")
    print()


def initialise_model():
    model = Sequential()
    model.add(Dense(64, input_dim=6, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(4, activation='softmax'))

    model.build(input_shape=(1, 6))
    return model


def create_new_GA(model, num_gen, pop_size, num_par_mating):
    keras_ga = pygad.kerasga.KerasGA(model=model, num_solutions=pop_size)
    initial_population = keras_ga.population_weights
    ga_instance = pygad.GA(num_generations=num_gen,
                           num_parents_mating=num_par_mating,
                           initial_population=initial_population,
                           fitness_func=fitness_func,
                           save_best_solutions=False,
                           on_generation=on_generation,
                           keep_elitism=5,
                           stop_criteria=['reach_30', 'saturate_99999'])
    return ga_instance


def load_GA(f_name):
    ga_instance = pygad.load(f_name)
    return ga_instance


def run_GA(ga_instance, version):
    t_start = time.time()
    ga_instance.run()
    t_end = time.time()
    print('Time taken for ' + str(num_generations) + ' generations of ' + str(population_size) + ': ' + str(t_end-t_start))
    ts = datetime.datetime.today()
    f_name = version+'-'+str(ts.year)+str(ts.month)+str(ts.day)+'-'+str(ts.hour)+str(ts.minute)
    ga_instance.save(filename=f_name)
    return ga_instance, f_name


def split_sol(sol):
    output = []
    output.append(np.reshape(sol[:384], (6, 64)))  # layer 1 weights.
    output.append(sol[384:448])  # layer 1 biases.
    output.append(np.reshape(sol[448:2496], (64, 32)))  # layer 2 weights.
    output.append(sol[2496:2528])  # layer 2 biases, etc.
    output.append(np.reshape(sol[2528:3040], (32, 16)))
    output.append(sol[3040:3056])
    output.append(np.reshape(sol[3056:3120], (16, 4)))
    output.append(sol[3120:3124])
    return output


def new_model(version, num_generations, population_size, num_parents_mating):
    ga_instance = create_new_GA(model, num_gen=num_generations, pop_size=population_size, num_par_mating=num_parents_mating)
    time1 = time.time()
    ga_instance, f_name = run_GA(ga_instance, version=version)
    time2 = time.time()
    print('Time Taken: ' + str(time2 - time1))


def train_model(version, filename, num_generations):
    ga_instance = load_GA(f_name=filename)
    ga_instance.num_generations = num_generations
    time1 = time.time()
    ga_instance, f_name = run_GA(ga_instance, version=version)
    time2 = time.time()
    print('Time Taken: ' + str(time2 - time1))
    ga_instance.plot_fitness()


def assess_best(filename, num_games):
    ga_instance = load_GA(f_name=filename)
    best_sol, sol_fit, sol_idx = ga_instance.best_solution()
    model.set_weights(weights=split_sol(best_sol))
    scores_cache = []
    for i in range(num_games):
        print(i)
        scores_cache.append(run_snake(model))
    print('Average of ' + str(num_games) + ' games: ' + str(np.average(scores_cache)))


num_generations = 10
population_size = 30
num_parents_mating = 15
model = initialise_model()
version = 'v1.4.0'
f_name = 'v1.4.0-20221221-2219'
assess_best(f_name, 10)
