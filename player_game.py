"""

This file runs the user-interactive game.

"""

import pygame
import game_configs as config
import game_funcs as funcs


def game_loop():
    # this is the main running loop for a player controlled game.
    game_over = False  # indicates whether the game has finished.
    running = True  # indicates whether the window needs to close.

    snake_x, snake_y, snake_x_step, snake_y_step, score, food_x, food_y = funcs.game_init()  # initialise variables.

    while running:

        while game_over:  # switching to the game over screen.
            funcs.game_over_screen(score)

            for event in pygame.event.get():  # handling user input during game over screen.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:  # 'q' key to quit window.
                        quit()
                    if event.key == pygame.K_p:  # 'p' key to play again.
                        game_loop()  # reruns the game loop.


        # USER INPUT
        for event in pygame.event.get():  # handling user input during the game.
            if event.type == pygame.QUIT:  # user quits the game.
                quit()

            if event.type == pygame.KEYDOWN:  # keyboard is used to change snake direction.
                if event.key == pygame.K_a and snake_x_step != config.snake_block_size:  # 'a' key to move left.
                    snake_x_step = -config.snake_block_size
                    snake_y_step = 0
                elif event.key == pygame.K_d and snake_x_step != -config.snake_block_size:  # 'd' key to move right.
                    snake_x_step = config.snake_block_size
                    snake_y_step = 0
                elif event.key == pygame.K_w and snake_y_step != config.snake_block_size:  # 'w' key to move up.
                    snake_x_step = 0
                    snake_y_step = -config.snake_block_size
                elif event.key == pygame.K_s and snake_y_step != -config.snake_block_size:  # 's' key to move down.
                    snake_x_step = 0
                    snake_y_step = config.snake_block_size


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
        config.clock.tick(config.snake_speed)  # moving onto the next frame.

    pygame.quit()  # quits the pygame instance.
    quit()  # quits this running instance.


game_loop()  # running the game loop.
