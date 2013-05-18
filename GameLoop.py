import pygame
import sys
from pygame.locals import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 10

class Ball:
    def __init__(self, position, size, color):
        self.posx, self.posy = position
        radius = size/2
        self.rect = pygame.rect.Rect(posx-radius, posy-radius, size, size)
        self.size = size
        self.color = color
        self.movingLeft = False
        self.movingRight = False
        self.jumping = False
    def update(self):
        #if not self.rect.collidelist(tiles):
            #self.falling = True
        if self.jumping:
            dy=10-self.jumpFrames/4;
            if self.jumpFrames <= 3:
                self.jumping = False
            self.jumpFrames -= 1
            self.posy += dy    
        #elif self.falling:

        dx = 2
        if self.movingLeft:
            self.posx += dx
        if self.movingRight:
            self.posx -= dx
        pygame.draw.circle(screen, self.color,(self.posx-camera.left,
                                               self.posy), self.size)
        self.rect.centerx = self.posx-camera.left
        self.rect.centery = self.posy
        #screen.fill((255,255,0), self.rect)
    def jump(self):
        self.jumping = True
        self.jumpFrames = 80;
class Player(Ball):
    def update(self):
       Ball.update(self)
       camera.centerx = self.posx
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
objects = []
posx = 200
posy = 500
player = Player((posx, posy), 20, (255,0,0))
objects.append(player)
camera = pygame.rect.Rect((0,0), (SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
marker = Ball((posx-camera.left, posy), 10, (0,0,0))
markerPos = (posx-camera.left, posy)
objects.append(marker)
while 1:
    screen.fill((0,0,255))
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            mouse_x,mouse_y=pygame.mouse.get_pos()
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()
            elif event.key == K_F1:
                pygame.display.toggle_fullscreen()
            elif event.key == K_SPACE:
                marker.posx = player.posx
                marker.posy = player.posy
            elif event.key == K_w and not player.jumping:
                player.jump()
            elif event.key == K_a:
                player.movingLeft = True
            elif event.key == K_d:
                player.movingRight = True
            elif event.key == K_g:
                pass
        elif event.type == KEYUP:
            if event.key == K_d:
                player.movingRight = False 
            elif event.key == K_a:
                player.movingLeft = False
    for i in range(10):
        pygame.draw.circle(screen, (0,222,0),(300+i*50-camera.left, 20+i*10), 20)
    for obj in objects:
        if camera.collidepoint((obj.posx, obj.posy)):
            obj.update()
    clock.tick(40)
    pygame.display.flip()
