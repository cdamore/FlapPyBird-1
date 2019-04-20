import pygame, random, sys
from pygame.locals import *
from itertools import cycle
from utils import getHitmask
from globals import *
from utils import *
from flappy import *
import net
import random

class Bird:
    def __init__(self, y, playerIndexGen):
        self.x = int(SCREENWIDTH * 0.2) # bird stays in same x position
        self.y = y
        self.net = net.Net()
        self.score = 0
        self.id = random.randint(1,1001)
        self.playerIndex = 0
        self.playerIndexGen = playerIndexGen
        self.x_dist = 0
        self.y_dist = 0
        self.loopIter = 0
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        self.images = [pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
                       pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
                       pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha()]
        self.hitmasks = [getHitmask(self.images[0]),
                         getHitmask(self.images[1]),
                         getHitmask(self.images[2])]
        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY =  10   # max vel along Y, max descend speed
        self.playerMinVelY =  -8   # min vel along Y, max ascend speed
        self.playerAccY    =   1   # players downward accleration
        self.playerRot     =  45   # player's rotation
        self.playerVelRot  =   3   # angular speed
        self.playerRotThr  =  20   # rotation threshold
        self.playerFlapAcc =  -9   # players speed on flapping
        self.playerFlapped = False # True when player flaps
        self.atStart = True
        self.max_y = 0
        self.min_y = 0

        self.randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        self.PLAYER_IMAGES = {}
        self.PLAYER_IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[self.randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[self.randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[self.randPlayer][2]).convert_alpha(),
        )


    def set_postion(self, x, y):
        x = self.x
        y = self.y

    def get_postion(self):
        return (self.x, self.y)

    def update(self, upperPipes, lowerPipes, basex):
        # print('upperPipes: ' + str(upperPipes[0]['y']))
        # print('lowerPipes: ' + str(lowerPipes[0]['y']))
        # print('basex: ' + str(basex))
        #print('upperPipe: ' + str(upperPipes[0]['y']))

        if (upperPipes[0]['x'] > 0):
            self.x_dist = upperPipes[0]['x']
            self.y_dist = self.y - (lowerPipes[0]['y'] - 60)
        else:
            self.x_dist = upperPipes[1]['x']
            self.y_dist = self.y - (lowerPipes[1]['y'] - 60)

        if self.x_dist > 170:
            self.atStart = True
        else:
            self.atStart = False

        if self.x_dist > 160:
            self.x_dist = 160

        self.x_dist = (float(self.x_dist) / float(160))
        self.y_dist = (float(self.y_dist) / float(720)) + 0.8

        # print('y_dist: ' + str(self.y_dist))
        # print('x_dist: ' + str(self.x_dist))

        if self.y_dist > self.max_y:
            self.max_y = self.y_dist
        if self.y_dist < self.min_y:
            self.min_y = self.y_dist

        # print('y_min: ' + str(self.min_y))
        # print('x_max: ' + str(self.max_y))


        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
        # if dist too far (start of game), flap
        if self.x_dist == 1 and self.atStart:
            if self.y > 200:
                self.playerVelY = self.playerFlapAcc
                self.playerFlapped = True
                SOUNDS['wing'].play()
        else:
            if (self.net.eval(self.x_dist, self.y_dist) > 0.8):
                if self.y > -2 * IMAGES['player'][0].get_height():
                    self.playerVelY = self.playerFlapAcc
                    self.playerFlapped = True
                    SOUNDS['wing'].play()



        # check for crash here
        crashTest = checkCrash({'x': self.x, 'y': self.y, 'index': self.playerIndex},
                               upperPipes, lowerPipes)

        # if bird crashed
        if crashTest[0]:
            return True

        # check for score
        playerMidPos = self.x + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1
                SOUNDS['point'].play()

        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(self.playerIndexGen)
        self.loopIter = (self.loopIter + 1) % 30

        # rotate the player
        if self.playerRot > -90:
            self.playerRot -= self.playerVelRot

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            self.playerRot = 45

        playerHeight = IMAGES['player'][self.playerIndex].get_height()
        self.y += min(self.playerVelY, BASEY - self.y - playerHeight)

        # print score so player overlaps the score
        showScore(self.score)

        # Player rotation has a threshold
        visibleRot = self.playerRotThr
        if self.playerRot <= self.playerRotThr:
            visibleRot = self.playerRot

        playerSurface = pygame.transform.rotate(self.PLAYER_IMAGES['player'][self.playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (self.x, self.y))

        return False
