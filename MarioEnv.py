from pyboy import PyBoy
import gymnasium as gym
from gymnasium.spaces import Box, Discrete
from gymnasium.wrappers import FlattenObservation

from enum import Enum
import numpy as np

import math
import random
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import sys

# set up matplotlib
is_ipython = 'inline' in matplotlib.get_backend()
if is_ipython:
    from IPython import display

plt.ion()

device = torch.device(
    "cuda" if torch.cuda.is_available() else
    # "mps" if torch.backends.mps.is_available() else
    "cpu"
)

class Actions(Enum):
    NOOP = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    JUMP = 5
    FIRE = 6
    LEFT_PRESS = 7
    RIGHT_PRESS = 8
    JUMP_PRESS = 9
    LEFT_RUN = 10
    RIGHT_RUN = 11
    LEFT_JUMP = 12
    RIGHT_JUMP = 13
    
# class ARROW_Function(Enum):
#     NOOP = 0
#     LEFT = 1
#     RIGHT = 2
#     UP = 3
#     DOWN = 4
#     LEFT_PRESS = 5
#     RIGHT_PRESS = 6
    
# class A_FUNCTION(Enum):
#     NOOP = 0
#     BUTTON_A = 1  # Jump

# class B_FUNCTION(Enum):
#     NOOP = 0
#     BUTTON_B = 1  # RUN OR FIRE

# Create action groups for easier reference
# DIRECTION_ACTIONS = [ARROW_Function.NOOP, ARROW_Function.LEFT, ARROW_Function.RIGHT, ARROW_Function.UP, ARROW_Function.DOWN, ARROW_Function.LEFT_PRESS, ARROW_Function.RIGHT_PRESS]
# A_FUNCTION_ACTIONS = [A_FUNCTION.NOOP, A_FUNCTION.BUTTON_A]
# B_FUNCTION_ACTIONS = [B_FUNCTION.NOOP, B_FUNCTION.BUTTON_B]

class MarioEnv(gym.Env):
    def __init__(self, pyboy):
        # super().__init__(PyBoy)
        self.pyboy = pyboy
    
        # Define action space using the number of actions in each group
        # self.n_directions = len(DIRECTION_ACTIONS)
        # self.a_functions = len(A_FUNCTION_ACTIONS)
        # self.b_functions = len(B_FUNCTION_ACTIONS)
        # self.action_space = MultiDiscrete(np.array([self.n_directions, self.a_functions, self.b_functions]), seed=42)
        self.action_space = Discrete(len(Actions), seed=42)

        # Define observation space
        self.observation_space = Box(low=0, high=255, shape=(16, 20), dtype=np.int32) # 假設距離的值範圍是 0-255
        

    def step(self, action):
        assert self.action_space.contains(action), "%r (%s) invalid" % (action, type(action))
        
        # Move the agent
        if action == Actions.NOOP.value:
            pass
        elif action == Actions.LEFT_PRESS.value:
            self.pyboy.button_press("left")
        elif action == Actions.RIGHT_PRESS.value:
            self.pyboy.button_press("right")
        elif action == Actions.LEFT.value:
            self.pyboy.button("left")
        elif action == Actions.RIGHT.value:
            self.pyboy.button("right")
        elif action == Actions.UP.value:
            self.pyboy.button("up")
        # elif action == Actions.DOWN.value:
        #     self.pyboy.button("down")   
        elif action == Actions.JUMP_PRESS.value:
            self.pyboy.button_press("b")
            self.pyboy.button_press("a")
            self.pyboy.button_press("right")
        elif action == Actions.JUMP.value:
            self.pyboy.button("a")   
        elif action == Actions.FIRE.value:
            self.pyboy.button("b")
        elif action == Actions.LEFT_RUN.value:
            self.pyboy.button_press("b")
            self.pyboy.button_press("left")
        elif action == Actions.RIGHT_RUN.value:
            self.pyboy.button_press("b")
            self.pyboy.button_press("right")
        elif action == Actions.LEFT_JUMP.value:
            self.pyboy.button_press("a")
            self.pyboy.button_press("left")
        elif action == Actions.RIGHT_JUMP.value:
            self.pyboy.button_press("a")
            self.pyboy.button_press("right")

        # # Move the agent
        # if action == ARROW_Function[0].NOOP.value:
        #     pass
        # elif action == ARROW_Function.LEFT_PRESS.value:
        #     self.pyboy.button_press("left")
        # elif action == ARROW_Function.RIGHT_PRESS.value:
        #     self.pyboy.button_press("right")
        # elif action == ARROW_Function.LEFT.value:
        #     self.pyboy.button("left")
        # elif action == ARROW_Function.RIGHT.value:
        #     self.pyboy.button("right")
        # elif action == ARROW_Function.UP.value:
        #     self.pyboy.button("up")
        # elif action == ARROW_Function.DOWN.value:
        #     self.pyboy.button("down")
            
        # # A button actions for the agent    
        # if action == A_FUNCTION.NOOP.value:
        #     pass
        # elif action == A_FUNCTION.BUTTON_A.value:
        #     self.pyboy.button_press("a")
        
        # # B button actions for the agent    
        # if action == B_FUNCTION.NOOP.value:
        #     pass
        # elif action == B_FUNCTION.BUTTON_B.value:
        #     self.pyboy.button("b")
            
        self.pyboy.tick()
                
        terminated = self.pyboy.game_wrapper.level_progress > 2601
        
        
        reward=self.pyboy.game_wrapper.score

        state=self._get_obs()
        
        
        info = {}
        truncated = False

        return state, reward, terminated, truncated, info

    def reset(self, seed=42, options=None):
        super().reset(seed=seed)
        #self.pyboy.game_wrapper.reset_game()

        state=self._get_obs()
            
        info = {}
            
        return state, info

    def render(self):
        self.pyboy.tick()

    def close(self):
        self.pyboy.stop()

    def _get_obs(self):
        return self.pyboy.game_area()
        


# if GPU is to be used
device = torch.device(
    "cuda" if torch.cuda.is_available() else
    "mps" if torch.backends.mps.is_available() else
    "cpu"
)

    
pyboy = PyBoy("rom.gb", window="SDL2") 
env = MarioEnv(pyboy)

# flatten the array
env = FlattenObservation(env)

mario = pyboy.game_wrapper
mario.start_game()

state, info = env.reset()


state = torch.from_numpy(state).to(device)

print(state)
# tensor([339, 339, 339, 339, 339, 339, 339, 339, 339, 339, 339, 339, 339, 339,
#         339, 339, 339, 339, 339, 339, 320, 320, 320, 320, 320, 320, 320, 320,
#         320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 320, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 321, 322, 321, 322,
#         323, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
#         300, 324, 325, 326, 325, 326, 327, 300, 300, 300, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 310, 350, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 310,
#         300, 300, 350, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300,
#         300, 300, 300, 129, 310, 300, 300, 300, 300, 350, 300, 300, 300, 300,
#         300, 300, 300, 300, 300, 300, 300, 300, 300, 310, 300, 300, 300, 300,
#         300, 300, 350, 300, 300, 300, 300, 300, 300, 300, 300, 300, 310, 350,
#         310, 300, 300, 300, 300, 306, 307, 300, 300, 350, 300, 300, 300, 300,
#         300, 300, 300, 368, 369, 300,   0,   1, 300, 306, 307, 305, 300, 300,
#         300, 300, 350, 300, 300, 300, 300, 300, 310, 370, 371, 300,  16,  17,
#         300, 305, 300, 305, 300, 300, 300, 300, 300, 350, 300, 300, 300, 300,
#         352, 352, 352, 352, 352, 352, 352, 352, 352, 352, 352, 352, 352, 352,
#         352, 352, 352, 352, 352, 352, 353, 353, 353, 353, 353, 353, 353, 353,
#         353, 353, 353, 353, 353, 353, 353, 353, 353, 353, 353, 353],
#        device='cuda:0', dtype=torch.int32)



 # Get the total 320 number of elements in the tensor
print("flatten observation space :", torch.tensor(env.observation_space.shape)) #tensor([320])


print("action_space.sample" ,env.action_space.sample()) #1


Transition = namedtuple('Transition',
                        ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):

    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

class DQN(nn.Module):

    def __init__(self, n_observations, n_actions):
        super(DQN, self).__init__()
        self.layer1 = nn.Linear(n_observations, 512)
        self.layer2 = nn.Linear(512, 1024)
        self.layer3 = nn.Linear(1024, 1024)
        self.layer4 = nn.Linear(1024, 64)
        self.layer5 = nn.Linear(64, n_actions)

    # Called with either one element to determine next action, or a batch
    # during optimization. Returns tensor([[left0exp,right0exp]...]).
    def forward(self, x):
        x = F.relu(self.layer1(x))
        x = F.relu(self.layer2(x))
        x = F.relu(self.layer3(x))
        x = F.relu(self.layer4(x))
        return self.layer5(x)


BATCH_SIZE = 128
GAMMA = 0.99
EPS_START = 0.9
EPS_END = 0.05
EPS_DECAY = 1000
TAU = 0.005
LR = 1e-4

# Get number of actions from gym action space
n_actions = env.action_space.n
print("n_actions :", n_actions) #14

n_observations = env.observation_space.shape[0]
print("n_observations :", n_observations) #320

policy_net = DQN(n_observations, n_actions).to(device)
target_net = DQN(n_observations, n_actions).to(device)

print(f"Model structure: {policy_net}\n\n")

for name, param in policy_net.named_parameters():
    print(f"Layer: {name} | Size: {param.size()} | Values : {param[:2]} \n")

target_net.load_state_dict(policy_net.state_dict())

optimizer = optim.AdamW(policy_net.parameters(), lr=LR, amsgrad=True)
memory = ReplayMemory(10000)


print(policy_net)
print(target_net)

steps_done = 0


def select_action(observation):
    global steps_done
    sample = random.random()
    eps_threshold = EPS_END + (EPS_START - EPS_END) * \
        math.exp(-1. * steps_done / EPS_DECAY)
    steps_done += 1
    if sample > eps_threshold:
        with torch.no_grad():
            # t.max(1) will return the largest column value of each row.
            # second column on max result is index of where max element was
            # found, so we pick action with the larger expected reward.
            return policy_net(observation).max(1).indices.view(1, 1)
    else:
        return torch.tensor([[env.action_space.sample()]], device=device, dtype=torch.long)



episode_durations = []


def plot_durations(show_result=False):
    plt.figure(1)
    durations_t = torch.tensor(episode_durations, dtype=torch.float)
    if show_result:
        plt.title('Result')
    else:
        plt.clf()
        plt.title('Training...')
    plt.xlabel('Episode')
    plt.ylabel('Duration')
    plt.plot(durations_t.numpy())
    # Take 100 episode averages and plot them too
    if len(durations_t) >= 100:
        means = durations_t.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    plt.pause(0.001)  # pause a bit so that plots are updated
    if is_ipython:
        if not show_result:
            display.display(plt.gcf())
            display.clear_output(wait=True)
        else:
            display.display(plt.gcf())
            

def optimize_model():
    if len(memory) < BATCH_SIZE:
        return
    transitions = memory.sample(BATCH_SIZE)
    
    # Transpose the batch
    batch = Transition(*zip(*transitions))

    # Compute a mask of non-final states and concatenate the batch elements
    non_final_mask = torch.tensor(
        tuple(map(lambda s: s is not None, batch.next_state)),
        device=device,
        dtype=torch.bool
    )
    
    non_final_next_states = torch.cat(
        [s for s in batch.next_state if s is not None]
    )
    
    state_batch = torch.cat(batch.state).to(device)
    action_batch = torch.cat(batch.action).to(device).view(BATCH_SIZE, 1)

    # Convert rewards to tensor and add an extra dimension
    # Convert rewards to tensors, add an extra dimension, and concatenate
    # reward_batch = torch.cat([r.unsqueeze(0).clone().detach() for r in batch.reward]).to(device)

    reward_batch = torch.cat([torch.tensor(r).unsqueeze(0) for r in batch.reward]).to(device)

    # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
    # columns of actions taken. These are the actions which would've been taken
    # for each batch state according to policy_net
    state_action_values = policy_net(state_batch).gather(1, action_batch).squeeze()

    # Compute V(s_{t+1}) for all next states.
    # Expected values of actions for non_final_next_states are computed based
    # on the "older" target_net; selecting their best reward with max(1).values
    # This is merged based on the mask, such that we'll have either the expected
    # state value or 0 in case the state was final.
    next_state_values = torch.zeros(BATCH_SIZE, device=device)
    with torch.no_grad():
        next_state_values[non_final_mask] = target_net(non_final_next_states).max(1)[0]
    # Compute the expected Q values
    expected_state_action_values = (next_state_values * GAMMA) + reward_batch
    
    # Ensure expected_state_action_values has an extra dimension for compatibility with state_action_values
    # expected_state_action_values = expected_state_action_values.unsqueeze(1)

    # Compute Huber loss with matching shapes
    criterion = nn.SmoothL1Loss()
    loss = criterion(state_action_values, expected_state_action_values)

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    # In-place gradient clipping
    torch.nn.utils.clip_grad_value_(policy_net.parameters(), 100)
    optimizer.step()
    
    
if torch.cuda.is_available() or torch.backends.mps.is_available():
    num_episodes = 600
else:
    num_episodes = 50

mario_pos = pyboy.get_sprite_by_tile_identifier([0, 1, 16, 17])
Big_mario = pyboy.get_sprite_by_tile_identifier([33, 32, 49, 48])
flower = pyboy.get_sprite_by_tile_identifier([146, 147])
flying_1 = pyboy.get_sprite_by_tile_identifier([160, 161, 176, 177])
bee = pyboy.get_sprite_by_tile_identifier([192, 193, 208, 209])
turle = pyboy.get_sprite_by_tile_identifier([150, 151])
mushroom = pyboy.get_sprite_by_tile_identifier([131])

for i_episode in range(num_episodes):
    # Initialize the environment and get its state
    state, info = env.reset()
    
    mario.set_lives_left(10)
    
    mario_score = mario.score
    mario_coins = mario.coins
    mario_lives = mario.lives_left
    
    Goomba = pyboy.memory[0XD100] == 0
    flatten_Goomba = pyboy.memory[0XD100] == 1
    if Goomba is flatten_Goomba:
        mario_score = mario_score + 100
       
    Nokobon = pyboy.memory[0XD100] == 4
    Nokobon_bomb = pyboy.memory[0XD100] == 5
    if Nokobon is Nokobon_bomb:
        mario_score = mario_score + 100
            
    # Powerup Status  
    Powerup_Status = pyboy.memory[0xFF99]
    if Powerup_Status == 0:
        mario_score = mario_score + 0
    elif Powerup_Status == 1:
        mario_score = mario_score + 1000
        
    state = torch.tensor(state, dtype=torch.float32, device=device).unsqueeze(0)
    for t in count():
        action = select_action(state)
        observation, reward, terminated, truncated, _ = env.step(action.item())
        done = terminated or truncated
            
        if terminated == True:
            next_state = None
        else:
            next_state = torch.tensor(observation, dtype=torch.float32, device=device).unsqueeze(0)

        # Store the transition in memory
        # memory.push(state, action, next_state, reward)
        memory.push(state, action, next_state, reward)

        # Move to the next state
        state = next_state
        
        reward = mario.score
        reward = torch.tensor([reward], device=device)
        
        
        truncated = bool(mario.level_progress >= 2601)
        if truncated == True:
            mario_score = max(0, mario_score)
            print("level complete")
            sys.exit()

        # Perform one step of the optimization (on the policy network)
        optimize_model()

        # Soft update of the target network's weights
        # θ′ ← τ θ + (1 −τ )θ′
        target_net_state_dict = target_net.state_dict()
        policy_net_state_dict = policy_net.state_dict()
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key]*TAU + target_net_state_dict[key]*(1-TAU)
        target_net.load_state_dict(target_net_state_dict)

        if done:
            episode_durations.append(t + 1)
            plot_durations()
            break
        
        if mario.lives_left == 0:
            mario.reset_game()
            break

print('Complete')
plot_durations(show_result=True)
plt.ioff()
plt.show()
