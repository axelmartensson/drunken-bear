import pygame
import sys
from pygame.locals import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 10

class Level(object):
    def __init__(self):
        print "Initializing Game"
        self.level = 0
    def load(self, number):
        pix=PIXELS_PER_METER
        self.level = number
        lvlStr = "levels/level%i.txt" % number
        res = open(lvlStr, "r")
        x,y = 0,0
        objects = []
        for line in res.readlines():
            for char in line:
                if char == "-":
                    objects.append(Tile(position=(x*pix,y*pix)))
                elif char == "x":
                    objects.append(Ball((x*pix,y*pix), 20, (0,255,0)))
                x += 1
            y += 1
            x=0
        return objects
    
class Tile(object):
    def __init__(self, position, color=(123,123,123)):
        self.posx, self.posy = position
        self.rect = pygame.rect.Rect(position, (10, 10))
        self.color = color
        self.surface = pygame.Surface((10,10))
        self.surface.fill(color)
    def update(self): 
        screen.blit(self.surface, (self.posx-camera.left,self.posy))
        self.rect.topleft=(self.posx-camera.left,self.posy)
        #screen.fill((255,255,0), self.rect)
 
class Ball:
    def __init__(self, position, size, color):
        self.posx, self.posy = position
        radius = size/2
        self.rect = pygame.rect.Rect(self.posx-radius, self.posy-radius, size, size)
        self.size = size
        self.color = color
        self.movingLeft = False
        self.movingRight = False
        self.jumping = False
        self.falling = True 
        self.fallingFrames = 1
        self.dy = 0

    def update(self):
        self.falling = True 
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.dy > 0:
                    self.jumping = False
                self.falling = False 
                self.fallingFrames = 1
                break

        if self.jumping:
            self.dy=10-self.jumpFrames/4;
            if self.jumpFrames <= 3:
                self.jumping = False
            self.jumpFrames -= 1
            self.posy += self.dy    

        elif self.falling:
            self.dy+=-self.fallingFrames/4;
            self.posy += self.dy    
            self.fallingFrames -=1
        else:
            self.dy = 0

        dx = 3
        if self.movingLeft:
            self.posx += dx
        if self.movingRight:
            self.posx -= dx
        pygame.draw.circle(screen, self.color,(self.posx-camera.left,
                                               self.posy), self.size)
        self.rect.centerx = self.posx-camera.left
        self.rect.centery = self.posy
        screen.fill((255,255,0), self.rect)

    def jump(self):
        self.jumping = True
        self.jumpFrames = 80;

class Player(Ball):
    def update(self):
       Ball.update(self)
       camera.centerx = self.posx

class Bottle(Ball):
    def update(self):
        Ball.update(self)
        for badguy in badguys:
            if self.rect.colliderect(badguy.rect):
                badguys.remove(badguy)
                objects.remove(badguy)
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
level = Level()
objects = level.load(1) 

tiles = []
badguys = []
for obj in objects:
    if isinstance(obj, Tile):
        tiles.append(obj)
    else:
        badguys.append(obj)
posx = 400
posy = 200
player = Player((posx, posy), 20, (255,0,0))
objects.append(player)
camera = pygame.rect.Rect((0,0), (SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
marker = Bottle((posx-camera.left, posy), 10, (0,0,0))
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
