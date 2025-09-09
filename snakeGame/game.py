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

class Solution {
    public int maxProfit(int[] prices) {
        int left=0;
        int right=prices.length;
        int min=Integer.MAX_VALUE;
        int max=0;
        while(left<right)
        {
            if(prices[min]>prices[left])
            min=left;
            if(prices[max]<prices[right])
            max=right;
            left++;
            left++;
            right--;
        }
        return right-left;
    }
}


