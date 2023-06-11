# snakeAI
Collection of scripts in my project to build the game Snake and then apply Q-Learning and a generational algorithm (GA) to train an agent. I compared this to an agent playing using a hardcoded algorithm. 
The Q-table was trained over 10,000 games with an epsilon value of 0.3.
The GA was used to train 100 generations containing 30 agents each.
All agents have a maximum moves limit of 200.

Average scores listed below are over 100 games:
Hardcoded: 16.29
Q-Learning: 9.63
GA: 9.03

So in the case of a snake game, the rules are simple enough that a hardcoded agent can perform very well. The GA model is far more time and memory consuming than Q-learning, however fails to produce better results. Both the Q-Learning and GA can benefit from further running, however they are still unlikely to converge near the hardcoded score anytime soon.

The file 'gamebuild' is the user-interactive game.
The file 'hardcoded' is the hardcoded algorithm to play the game, to use as a benchmark for the AI.
The file 'QL' is the AI training using Q-learning. At the end of the file is some example code of running the functions to train and assess a Q-table.
The file 'GA' is the training of a DNN model using a GA. At the end of the file is some example code of running the functions to train and assess a model.
