from itertools import cycle
import random, sys, pygame
from pygame.locals import *
from globals import *
from load_data import *
from utils import *
import numpy as np
import bird
import random
import net

def main():
    pygame.init()
    pygame.display.set_caption('Flappy Bird')
    load_static_data()
    init = True

    while True:
        set_new_background()
        set_new_pipes()
        movementInfo = showWelcomeAnimation()

        # if first iteration
        if init:
            birds = [bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen']),
                    bird.Bird(movementInfo['playery'],movementInfo['playerIndexGen'])]
            init = False
        else:
            for i in range(len(birds)):
                birds[i].y = movementInfo['playery']
                birds[i].playerIndexGen = movementInfo['playerIndexGen']
                birds[i].score = 0

        # start round
        mainGame(movementInfo, birds)

        # breed birds (crossover and mutate)
        breed(birds)


def showWelcomeAnimation():

    """Shows welcome screen animation of flappy bird"""
    # select random player sprites
    randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
    IMAGES['player'] = (
        pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
        pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
        pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
    )
    # index of player to blit on screen
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    # iterator used to change playerIndex after every 5th iteration
    loopIter = 0

    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)

    basex = 0
    # amount by which base can maximum shift to left
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # player shm for up-down motion on welcome screen
    playerShmVals = {'val': 0, 'dir': 1}


    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                # make first flap sound and return values for mainGame
                SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'],
                    'basex': basex,
                    'playerIndexGen': playerIndexGen,
                }
        if generation > 0:
            return {
                'playery': playery + playerShmVals['val'],
                'basex': basex,
                'playerIndexGen': playerIndexGen,
            }


        # adjust playery, playerIndex, basex
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))
        SCREEN.blit(IMAGES['player'][playerIndex],
                    (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def mainGame(movementInfo, birds):
    global upperPipes, lowerPipes, basex, baseShift, generation

    # xpos of base
    basex = movementInfo['basex']
    # amount to shift base
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

    # get 2 new pipes to add to upperPipes lowerPipes list
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # list of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]

    # list of lowerpipe
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    crashes = [False] * 10
    scores = [0] * 10

    while True:
        # update environment (eg: pipes, base)
        update_environment()
        # update bird
        for i in range(len(birds)):
            if not crashes[i]:
                crashes[i] = birds[i].update(upperPipes, lowerPipes, basex)

        # if all birds crashed
        if all(crashes):
            # for i in range(len(birds)):
            #     scores[i] = birds[i].score
            generation += 1
            #return scores
            return

        showGeneration(generation)
        # update screen
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def update_environment():
    global basex

    basex = -((-basex + 100) % baseShift)

    # move pipes to left
    for uPipe, lPipe in zip(upperPipes, lowerPipes):
        uPipe['x'] += pipeVelX
        lPipe['x'] += pipeVelX

    # add new pipe when first pipe is about to touch left of screen
    if 0 < upperPipes[0]['x'] < 5:
        newPipe = getRandomPipe()
        upperPipes.append(newPipe[0])
        lowerPipes.append(newPipe[1])

    # remove first pipe if its out of the screen
    if upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
        upperPipes.pop(0)
        lowerPipes.pop(0)

    # draw sprites
    SCREEN.blit(IMAGES['background'], (0,0))

    for uPipe, lPipe in zip(upperPipes, lowerPipes):
        SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
        SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

    SCREEN.blit(IMAGES['base'], (basex, BASEY))

def breed(birds):

    set_best_birds(birds)
    print("best bird id: " +  str(birds[0].id))
    birds[0].net.display()
    for i in range(2, len(birds)):
        crossover_and_mutate(birds[0].net, birds[0].net, birds[i].net)

def set_best_birds(birds):
    # get best (top 2) birds from round
    global score_1, score_2, x_pose_1, x_pose_2
    top = 0
    for i in range(len(birds)):
        if (score_1 < birds[i].score) or ((score_1 == birds[i].score) and (x_pose_1 > birds[i].x_dist)):
            top = i
            score_1 = birds[i].score
            x_pose_1 = birds[i].x_dist
            print('NEW BEST')
    temp = birds[0]
    birds[0] = birds[top]
    birds[top] = temp
    top = 1
    for i in range(1, len(birds)):
        if (score_2 < birds[i].score) or ((score_2 == birds[i].score) and (x_pose_2 > birds[i].x_dist)):
            top = i
            score_2 = birds[i].score
            x_pose_2 = birds[i].x_dist
    temp = birds[1]
    birds[1] = birds[top]
    birds[top] = temp

    # reset birds if max score = 0
    if (score_1 == 0):
        reset_birds(birds)

def crossover_and_mutate(net1, net2, new_net):

    # set crossover and mutation rate
    crossover_rate = 0.9
    mutation_rate = 0.05

    # for each weight in layer 1
    for x in xrange(new_net.weights1.shape[0]):
        for y in xrange(new_net.weights1.shape[1]):
            if random.random() > 0.5:
                if random.random() < crossover_rate:
                    new_net.weights1[x][y] = net1.weights1[x][y]
            else:
                if random.random() < crossover_rate:
                    new_net.weights1[x][y] = net2.weights1[x][y]
            if random.random() < mutation_rate:
                new_net.weights1[x][y] = random.uniform(-1.0, 1.0)
    # for each weight in layer 2
    for x in xrange(new_net.weights2.shape[0]):
        for y in xrange(new_net.weights2.shape[1]):
            if random.random() > 0.5:
                if random.random() < crossover_rate:
                    new_net.weights2[x][y] = net1.weights2[x][y]
            else:
                if random.random() < crossover_rate:
                    new_net.weights2[x][y] = net2.weights2[x][y]
            if random.random() < mutation_rate:
                new_net.weights2[x][y] = random.uniform(-1.0, 1.0)

def reset_birds(birds):
    # reset neural net for each bird (except best one)
    print('resetting')
    for i in range(1, len(birds)):
        birds[i].net.reset()

if __name__ == '__main__':
    main()
