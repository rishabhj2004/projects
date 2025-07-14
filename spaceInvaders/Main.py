import pygame
import random
import math
from pygame import mixer

#initialise pygame
pygame.init() 

#create screen
screen=pygame.display.set_mode((800,600))

#title and icon(32 by 32)
pygame.display.set_caption("space invaders")
icon=pygame.image.load('icon.png')
pygame.display.set_icon(icon)

#adding bg
bg=pygame.image.load('bg.png')

#adding bg music
mixer.music.load('bgMusic.wav')
mixer.music.play(-1)

#game variables
gamePause=False

#loading button images
resume_img=pygame.image.load('resume.png').convert_alpha()

#create button instances

#player
playerImg=pygame.image.load('spaceship.png')
playerX=370
playerY=480
playerX_c=0

enemyImg=[]
enemyX=[]
enemyY=[]
enemyX_c=[]
enemyY_c=[]
n=6

#enemy
for i in range (n):
    enemyImg.append(pygame.image.load('ufo.png'))
    enemyX.append(random.randint(0,736))
    enemyY.append(random.randint(50,150))
    enemyX_c.append(0.3)
    enemyY_c.append(40)

#bullet
bulletImg=pygame.image.load('bullet.png')
bulletX=0
bulletY=480
bulletY_c=1
bulletState="ready"

#score
scoreVal=0
font=pygame.font.Font('freesansbold.ttf',32)
testX=10
testY=10

#game over text
overFont=pygame.font.Font('freesansbold.ttf',64)
d=True

#level font
levelFont=pygame.font.Font('freesansbold.ttf',32)
a=True
b=True
c=True

#game Pause
gamePause=False

def showScore(x,y):
    score=font.render("Score : "+str(scoreVal),True,(255,255,255))
    screen.blit(score,(x,y))

def lv(z):
    level=levelFont.render("Level: "+str(z),True,(255,255,255))
    screen.blit(level,(350,10))

def gameOver():
    over_text=overFont.render("GAME OVER",True,(255,255,255))
    screen.blit(over_text,(200,250))

def player(x,y):
    screen.blit(playerImg,(x,y))#drawing the image on the screen

def enemy(x,y,i):
    screen.blit(enemyImg[i],(x,y))

def fire_bullet(x,y):
    global bulletState
    bulletState="fire"
    screen.blit(bulletImg,(x+16,y+10))

def collision(x1,y1,x2,y2):#calculating distance
    distance=math.sqrt((math.pow((x2-x1),2))+(math.pow((y2-y1),2)))
    if distance<27:
        return True
    else:
        return False 

#game loop
running= True
while running:

    screen.fill((128,45,89)) #getting screen color
    if gamePause==True:
        running=False
    else:

        screen.blit(bg,(0,0)) #getting background
        if scoreVal<30:
            lv(0)
        elif scoreVal>=30 and scoreVal<=60:
            lv(1)
            if a==True:
                bulletSound=mixer.Sound('lvUP.wav')#lvUpSound
                bulletSound.play()
                a=False

        elif scoreVal>60 and scoreVal<100:
            lv(2)
            if b==True:
                bulletSound=mixer.Sound('lvUP.wav')#lvUpSound
                bulletSound.play()
                b=False

        elif scoreVal>=100:
            lv(3)
            if c==True:
                bulletSound=mixer.Sound('lvUP.wav')#lvUpSound
                bulletSound.play()
                c=False

        for event in pygame.event.get():

            #to get out of the game
            if event.type==pygame.QUIT:
                running= False

            #Check for keyboard input
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:#check for menu
                    gamePause=True
                if event.key==pygame.K_LEFT:
                    playerX_c=-0.3
                if event.key==pygame.K_RIGHT:
                    playerX_c=0.3
                if event.key==pygame.K_SPACE:
                    if bulletState is "ready":
                        bulletSound=mixer.Sound('lazer.wav')#bulletSound
                        bulletSound.play()
                        bulletX=playerX
                        fire_bullet(bulletX,bulletY)

            if event.type==pygame.KEYUP:
                if event.key==pygame.K_LEFT or event.key==pygame.K_RIGHT:
                    playerX_c=0
    
        for i in range(n):

            if enemyY[i]>440:#game over
                for j in range(n):
                    enemyY[j]=2000
                if d==True:
                    bulletSound=mixer.Sound('gameOver.wav')#gameoverSound
                    bulletSound.play()
                    d=False
                gameOver()
                break
            enemyX[i] +=enemyX_c[i]
            if scoreVal>60:
                enemyY_c[i]=50
            if enemyX[i]<=0:#checking boundary of enemies
                if scoreVal<30:
                    enemyX_c[i]=0.3
                    enemyY[i]+=enemyY_c[i]
                elif scoreVal>=30 and scoreVal<100:
                    enemyX_c[i]=0.4
                    enemyY[i]+=enemyY_c[i]
                elif scoreVal>=100:
                    enemyX_c[i]=0.5
                    enemyY[i]+=enemyY_c[i]

            elif enemyX[i]>=736:
                if scoreVal<30:
                    enemyX_c[i]=-0.3
                    enemyY[i]+=enemyY_c[i]
                elif scoreVal>=30 and scoreVal<100:
                    enemyX_c[i]=-0.4
                    enemyY[i]+=enemyY_c[i]
                elif scoreVal>=100:
                    enemyX_c[i]=-0.5
                    enemyY[i]+=enemyY_c[i]

            col=collision(enemyX[i],enemyY[i],bulletX,bulletY)
            if col:
                exSound=mixer.Sound('ex.wav')#explosionSound
                exSound.play()
                bulletY=480
                bulletState="ready"
                scoreVal+=1#score itteration
                enemyX[i]=random.randint(0,736)
                enemyY[i]=random.randint(50,150)
            enemy(enemyX[i],enemyY[i],i)

        playerX +=playerX_c

        if playerX<=0:#checking boundary of spaceship
            playerX=0
        elif playerX>=736:
            playerX=736

        if bulletY<=0:#multiple bullets
            bulletY=480
            bulletState="ready"

        if bulletState is "fire":#movement of bullet
            fire_bullet(bulletX,bulletY)
            bulletY-=bulletY_c

    
        showScore(testX,testY)
        player(playerX,playerY)   #calling the blit
        pygame.display.update()
