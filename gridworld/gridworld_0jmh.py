#!/usr/bin/env python

#gridworld_0jmh.py
#
#by Joe Hahn
#jmh.datasciences@gmail.com
#31 January 2018
#
#this was adapted from http://outlace.com/rlpart3.html  
#to execute:    ./gridworld_0jmh.py

#imports
import numpy as np

#initialize state = dict containing x,y coordinates of all objects in the system
def initialize_state():
    state = {'agent':{'x':5, 'y':5}, 'goal':{'x':1, 'y':1}, 'pit':{'x':3, 'y':2}, 'wall':{'x':1, 'y':3}}
    return state

#initialize the environment = dict containing all other constants that describe the system
def initialize_environment(state, grid_size):
    actions = ['up', 'down', 'left', 'right']
    action_indexes = range(len(actions))
    objects = state.keys()
    max_moves = 5*grid_size
    environment = {'actions':actions, 'action_indexes':action_indexes, 'objects':objects,
        'grid_size':grid_size, 'max_moves':max_moves}
    return environment

#define agent's possible actions
def move_agent(state, action, environment):
    agent = state['agent'].copy()
    next_state = state.copy()
    grid_size = environment['grid_size']
    if (action == 'up'):
        if (agent['y'] < grid_size-1):
            agent['y'] += 1
    if (action == 'down'):
        if (agent['y'] > 0):
            agent['y'] -= 1
    if (action == 'right'):
        if (agent['x'] < grid_size-1):
            agent['x'] += 1
    if (action == 'left'):
        if (agent['x'] > 0):
            agent['x'] -= 1
    wall = state['wall']
    if (agent != wall):
        next_state['agent'] = agent
    return next_state

#get reward
def get_reward(current_state, previous_state):
    if (current_state['agent'] == current_state['goal']):
        #agent is at goal
        return 10
    if (current_state['agent'] == current_state['pit']):
        #agent is in pit
        return -10
    if (current_state == previous_state):
        #agent was blocked by a wall or boundary
        return -3
    return -1

#check if game is still on or over
def check_game_on(state, N_moves, environment):
    agent = state['agent']
    goal = state['goal']
    pit = state['pit']
    max_moves = environment['max_moves']
    game_on = True
    if (agent == goal):
        game_on = False
    if (agent == pit):
        game_on = False
    if (N_moves > max_moves):
        game_on = False
    return game_on

#generate 2D string array showing locations of all objects
def state_grid(state, environment):
    grid_size = environment['grid_size']
    grid = np.zeros((grid_size, grid_size), dtype='string')
    objects = environment['objects']
    for object in objects:
        xy = state[object]
        x = xy['x']
        y = xy['y']
        grid[y, x] = object[0].upper()
    return grid

#convert state into a numpy array of x,y coordinates
def state2vector(state, environment):
    vector = []
    for object in objects:
        xy = state[object]
        x = xy['x']
        y = xy['y']
        vector += [x, y]
    return np.array(vector).reshape(1, len(vector))

#check initial conditions
grid_size = 6
rn_seed = 15
state = initialize_state()
environment = initialize_environment(state, grid_size)
objects = environment['objects']
actions = environment['actions']
action_indexes = environment['action_indexes']
state_vector = state2vector(state, environment)
print 'objects = ', objects
print 'actions = ', actions
print 'action_indexes = ', action_indexes
print 'state = ', state
print 'state_vector = ', state_vector
print 'state_vector.shape = ', state_vector.shape
print state_grid(state, environment)
N_inputs = state_vector.shape[1]
N_outputs = len(actions)
grid_size = environment['grid_size']
max_moves = environment['max_moves']
print 'N_inputs = ', N_inputs
print 'N_outputs = ', N_outputs
print 'grid_size = ', grid_size
print 'max_moves = ', max_moves
print 'rn_seed = ', rn_seed

##build neural network
#from keras.models import Sequential
#from keras.layers.core import Dense, Dropout, Activation
#from keras.layers.advanced_activations import LeakyReLU, PReLU
#from keras.optimizers import RMSprop
#model = Sequential()
#model.add(Dense(16*N_inputs, input_shape=(N_inputs,)))
#model.add(LeakyReLU(alpha=0.01))
#model.add(Dense(12*N_inputs))
#model.add(LeakyReLU(alpha=0.01))
#model.add(Dense(N_outputs))
#model.add(Activation('linear'))
#rms = RMSprop()
#model.compile(loss='mse', optimizer=rms)
#print model.summary()

#build neural network
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
model = Sequential()
model.add(Dense(164, kernel_initializer='lecun_uniform', input_shape=(N_inputs,)))
model.add(Activation('relu'))
model.add(Dense(150, kernel_initializer='lecun_uniform'))
model.add(Activation('relu'))
model.add(Dense(N_outputs, kernel_initializer='lecun_uniform'))
model.add(Activation('linear'))
rms = RMSprop()
model.compile(loss='mse', optimizer=rms)
print model.summary()

#train
N_training_games = 2000
gamma = 0.9
epsilon = 1.0
np.random.seed(rn_seed)
action_indexes = environment['action_indexes']
for N_games in range(N_training_games):
    state = initialize_state()
    game_over = False
    N_moves = 0
    if (N_games > 20):
        #slowly ramp epsilon down to 0.1
        if (epsilon > 0.1):
            epsilon -= 1.0/(N_training_games/2)
    game_on = check_game_on(state, N_moves, environment)
    while (game_on):
        state_vector = state2vector(state, environment)
        #Let's run our Q function on S to get Q values for all possible actions
        Q = model.predict(state_vector, batch_size=1)
        if (np.random.random() < epsilon):
            #choose a random action_index
            action_index = np.random.choice(action_indexes)
        else:
            #choose best action_index from Q(s,a) values
            action_index = np.argmax(Q)
        action = actions[action_index]
        next_state = move_agent(state, action, environment)
        next_state_vector = state2vector(next_state, environment)
        next_Q = model.predict(next_state_vector, batch_size=1)
        max_Q = np.max(next_Q)
        reward = get_reward(next_state, state)
        game_on = check_game_on(next_state, N_moves, environment)
        if (game_on):
            revised_Q = reward + gamma*max_Q
        else:
            revised_Q = reward
            print("game number: %s" % N_games)
            print("move number: %s" % N_moves)
            print("action: %s" % action)
            print("reward: %s" % reward)
            print("epsilon: %s" % epsilon)
            if (N_moves > environment['max_moves']):
                print("too many turns")
            else:
                print("game over")            
        Q[0][action_index] = revised_Q
        model.fit(state_vector, Q, batch_size=1, epochs=1, verbose=0)
        state = next_state
        N_moves += 1

#test
def test(environment):
    state = initialize_state()
    grid = state_grid(state, environment)
    print('initial state:')
    print np.rot90(grid.T)
    print ("=======================")
    N_moves = 0
    game_over = False
    while (game_over == False):
        state_vector = state2vector(state, environment)
        Q = model.predict(state_vector, batch_size=1)
        action_index = np.argmax(Q)
        action = actions[action_index]
        next_state = move_agent(state, action, environment)
        N_moves += 1
        print("move: %s    action: %s" %(N_moves, action))
        grid = state_grid(next_state, environment)
        print np.rot90(grid.T)
        reward = get_reward(next_state, state)
        state = next_state
        print("reward: %s" % reward)
        if (reward > -5) and (reward < 5):
            #non-terminal state
            pass
        else:
            #terminal state
            game_over = True
            print("game completed")
        if (N_moves > environment['max_moves']):
            print("game lost, too many moves")
            game_over = True

test(environment)