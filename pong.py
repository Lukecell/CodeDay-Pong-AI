#!/usr/bin/env python
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.

import pygame
from math import atan2, degrees, pi, sqrt
from pygame.locals import *
from sys import exit
import random
import pongNet
import numpy as np

#Change this to manipulate speed of simulation
GLOBAL_WIDTH = 640
GLOBAL_HEIGHT = 480
#GLOBAL_SPEED = 10000
GLOBAL_SPEED = 100
GLOBAL_OFFSET = GLOBAL_HEIGHT / 200

#some misc stuff
INPUT_VECTOR_SIZE = 3

#generates random number for variance in direction
def getRandomNum():
    return (random.randrange(9, 10) * .1)

#returns 1 if someone has won. 0 Otherwise
def getWinner(num):
    return num

#returns game statistics of: angle ball is travelling, distance from paddle
#1 to ball, distance of paddle 2 from ball
def getStatistics(circle_x, circle_y, bar1_x, bar1_y, bar2_x, bar2_y):
    out = np.zeros(INPUT_VECTOR_SIZE)
    midX = GLOBAL_WIDTH / 2
    midY = GLOBAL_HEIGHT / 2
    dx = midX - circle_x
    dy = midY - circle_y
    rads = atan2(-dy, dx)
    rads %= 2*pi
    angle = degrees(rads)
    if  (bar1_x - circle_x)**2 != 0:
        p1Distance = sqrt((bar1_y - circle_y)**2 / (bar1_x - circle_x)**2)
    if (bar2_x - circle_x)**2 != 0:
        p2Distance = sqrt((bar2_y - circle_y)**2 / (bar2_x - circle_x)**2)
    out[0] = angle
    out[1] = p1Distance
    out[2] = p2Distance
    return out

#determines how to move padel based on neural net input
def movePadel(currentPosition, changeAmount):
    if changeAmount >= 6 and changeAmount <= 9:
        currentPosition -= (changeAmount ) * GLOBAL_OFFSET #move up
        if currentPosition <= 0:
            currentPosition = 0
    elif changeAmount <= 4 and changeAmount >= 0:
        currentPosition += (changeAmount + 5) * GLOBAL_OFFSET #move down
        if currentPosition >= GLOBAL_HEIGHT - 50:
            currentPosition = GLOBAL_HEIGHT - 50
    return currentPosition

#main method- magic happens here
def realMain():
    initialArray = np.matrix(
[[0.08979856, 0.22049639, 0.08403051],
 [0.33365723, 0.3798235,  0.11734318],
 [0.16334221, 0.03554528, 0.28749734],
 [0.08412367, 0.1951593,  0.20303106],
 [0.35085411, 0.02784529, 0.27004963],
 [0.41107257, 0.19996041, 0.02709999],
 [0.3583569,  0.36080941, 0.14824126],
 [0.12279751, 0.0568518,  0.23538153],
 [0.07578117, 0.19402304, 0.29132547],
 [0.10965775, 0.1687085,  0.41158592]])

    #initialArray = [0.01, 0.01, 0.01, 0.01]
    count = 0
    winner1 = main(initialArray, count)
    count+=1
    print "Iteration " + str(count) + " = \n" + str(winner1)
    for i in range(1, 1000000):
        winner2 = main(winner1, count)
        winner1 = winner2
        #pongNet.evolv(winner1)
        #count+=1
        print "Iteration " + str(i) + " = \n" + str(winner2)

def main(inputMatrix, count):
    pygame.init()
    x = 0
    matrix1 = pongNet.evolve(inputMatrix)
    matrix2 = pongNet.evolve(inputMatrix)
    screen=pygame.display.set_mode((GLOBAL_WIDTH, GLOBAL_HEIGHT),0,32)

    pygame.display.set_caption("Pong Simulator")

    #Creating 2 bars, a ball and background.
    back = pygame.Surface((640,480)) #grid
    background = back.convert()
    background.fill((0,0,0)) #fill with black
    bar = pygame.Surface((10,50)) #make bar objet
    bar1 = bar.convert() #first bar
    bar1.fill((255, 255, 255)) #color
    bar2 = bar.convert() #second bar
    bar2.fill((255, 255, 255)) #color
    circ_sur = pygame.Surface((15,15))
    #surface, color, position, radius, width
    circ = pygame.draw.circle(circ_sur,(0,255,0),(15/2,15/2),15/2)
    circle = circ_sur.convert()
    circle.set_colorkey((0,0,0))

    # x and y coordinates / speeds
    bar1_x, bar2_x = 10. , 620.
    bar1_y, bar2_y = 215. , 215.
    circle_x, circle_y = 307.5, 232.5
    bar1_move, bar2_move = 0. , 0.

    speed_x, speed_y, speed_circ = GLOBAL_SPEED, GLOBAL_SPEED, GLOBAL_SPEED

    #clock and font objects
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("calibri",40)
    count = 0

    while True: #game logic
        #Gives ability to exit
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()

        #redraws game state
        screen.blit(background,(0,0))
        frame = pygame.draw.rect(screen,(255,255,255),Rect((5,5),(630,470)),2)
        middle_line = pygame.draw.aaline(screen,(255,255,255),(330,5),(330,475))
        screen.blit(bar1,(bar1_x,bar1_y))
        screen.blit(bar2,(bar2_x,bar2_y))
        screen.blit(circle,(circle_x,circle_y))


        #movement of circle
        if count == 0:
            randArray = [-1, 1] # to randomly decide starting direction of ball
            ballDirection = randArray[random.randrange(0,2)]
            time_passed = clock.tick(30)
            time_sec = time_passed / 1000.0 * ballDirection
            count+= 1
        else:
            time_passed = clock.tick(30)
            time_sec = time_passed / 1000.0 * ballDirection
        #time_sec = .9
        circle_x += speed_x * time_sec
        circle_y += speed_y * time_sec
        ai_speed = speed_circ * time_sec
        #ai_speed = 1
        inputs = getStatistics(circle_x, circle_y, bar1_x, bar1_y, bar2_x, bar2_y)
        #right side AI
        x = pongNet.neuralNetwork(inputs, matrix1)
    #    print x
        bar2_y = movePadel(bar2_y, x)
        #Left Side AI position
        #bar1_y = circle_y * getRandomNum();
        x = pongNet.neuralNetwork(inputs, matrix2)
        bar1_y = movePadel(bar1_y, x)

        #Collision for left side
        if circle_x <= bar1_x + 8:
            if circle_y >= bar1_y - 7.5 and circle_y <= bar1_y + 42.5:
                circle_x = 20
                speed_x = -speed_x * getRandomNum()
                if speed_x == 0: #in case the ball gets stuck moving up and down
                        speed_x = GLOBAL_SPEED / 3

        # Collision for right side
        if circle_x >= bar2_x - 17:
            if circle_y >= bar2_y - 7.5 and circle_y <= bar2_y + 42.5:
                circle_x = 605
                speed_x = -speed_x * getRandomNum()
                if speed_x == 0: #in case the ball gets stuck moving up and down
                        speed_x = (GLOBAL_SPEED / 3) * -1

        #Increments score
        if circle_x < 5.:
            #print "RIGHT AI WINS"
            #getWinner(1)
            print "matrix1: " + str(matrix1)
            return matrix1.copy()
            exit()
        elif circle_x > 620.:
            #print "LEFT AI WINS"
            #getWinner(1)
            print "matrix2: " + str(matrix2)
            return matrix2.copy()
            exit()

        #Constrains vertical range of ball
        if circle_y <= 10.:
            speed_y = -speed_y * getRandomNum()
            circle_y = 10.
        elif circle_y >= 457.5:
            speed_y = -speed_y * getRandomNum()
            circle_y = 457.5
        getWinner(0) # 0 since no one was won
        pygame.display.update() #updates game

realMain()
