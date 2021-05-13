import gym
import retro
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.optimizers import SGD
from keras.models import load_model
from keras import optimizers
import random

env = retro.make(game='1943-Nes')

# 生成虚拟数据
x_train = np.random.random((1000, 20))
y_train = np.random.randint(1, size=(1000, 1))
x_test = np.random.random((100, 20))
y_test = np.random.randint(1, size=(100, 1))

model = Sequential()

model.add(Dense(9))
model.add(Dense(3))
model.add(Dense(1))

sgd = optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mean_squared_error',
              optimizer='sgd',
              metrics=['accuracy'])

model.fit(x_train, y_train,
          epochs=10,
          batch_size=256)
score = model.evaluate(x_test, y_test, batch_size=256)

model.summary()


def generate_data_one_episode():
    x, y, score = [], [], 0
    state = env.reset()
    while True:
        action = random.randrange(0, 8)
        x.append(state)
        y.append([1, 0] if action == 0 else [0, 1])  
        state, reward, done, _ = env.step(action) 
        score += reward
        if done:
            break
    return x, y, score


def generate_training_data(expected_score=100):
    data_X, data_Y, scores = [], [], []
    for i in range(20000):
        x, y, score = generate_data_one_episode()
        if score > expected_score:
            data_X += x
            data_Y += y
            scores.append(score)
    print('dataset size: {}, max score: {}'.format(len(data_X), max(scores)))
    return np.array(data_X), np.array(data_Y)


model.save('1943-Nes.h5')

del model

model = load_model('1943-Nes.h5')
ep = 10000
ep += ep
for i in range(ep):
    state = env.reset()
    score = 100
    while True:
        time.sleep(0.01)
        env.render()  
        action = env.action_space.sample() 
        state, reward, done, info = env.step(action)  
        score += reward  
        if done: 
            print('using nn, score: ', score) 
            break
env.close()
