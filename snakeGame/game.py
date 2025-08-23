import pygame
import random
import math

pygame.init()

class Direction(Enum):
    RIGHT=1
    LEFT=2
    UP=3
    DOWN=4

block_size=20
speed=20

class SnakeGame:
    def __init__(self,w=640,h=480):
        screen=pygame.display.set_mode((800,600))
        pygame.display.set_caption("snake game")
        icon=pygame.image.load('snake.png')
        pygame.display.set_icon(icon)



