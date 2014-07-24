import pygame
import sys, math
from pygame.locals import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 10
MAX_DY = 10 
G = 9.81

class Level(object):
    def __init__(self):
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
                    objects.append(Badguy((x*pix,y*pix), 20, (0,255,0)))
                elif char == "L":
                    objects.append(Swing((x*pix,y*pix), (0,255,0)))
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
 
# PERLIN NOISE?
class Swing:
    def __init__(self, position, color):
        self.posx, self.posy = position
        self.rect = pygame.rect.Rect(self.posx, self.posy, 10, 20)
        self.color = color
        self.grabbed = False

        self.dt = 200/1000.0# milliseconds
        self.r = 100
        self.damp = 1/20.0
        self.phi = math.pi/32
        self.omega = 0
        self._updatependpos()
    def _updatependpos(self):
        dx = self.r*math.cos(self.phi)
        dy = self.r*math.sin(self.phi)
        self.pendx = self.posx + int(dx)
        self.pendy = self.posy + int(dy)

    def _integrate(self):
        """docstring for _integrateangles"""
        
        omega2 = self.omega + self.dt*(-G/self.r*math.sin(self.phi-math.pi/2)
                                       - self.damp*self.omega) 
        phi2 = self.phi + self.dt*self.omega 

        self.omega = omega2
        self.phi = phi2

    def update(self):

        if player.rect.colliderect(self.rect) and not (not player.swinging and self.grabbed):
            player.doswing(self)

        self._integrate()
        self._updatependpos()

        pygame.draw.line(screen, self.color,
                         (self.posx-camera.left, self.posy),
                         (self.pendx-camera.left, self.pendy),
                         2)
        self.rect.centerx = self.pendx-camera.left
        self.rect.centery = self.pendy
        screen.fill((255,255,0), self.rect)

class Ball:
    def __init__(self, position, size, color):
        self.posx, self.posy = position
        radius = size/2
        self.rect = pygame.rect.Rect(self.posx-radius, self.posy-radius, size, size)
        self.size = size
        self.color = color
        self.movingLeft = False
        self.movingRight = False
        self.facingForward = True
        self.jumping = False
        self.falling = True 
        self.swinging = False
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
        elif self.falling:
            if self.dy < MAX_DY:
                self.dy+=self.fallingFrames/4;
                self.fallingFrames +=1
        else:
            self.dy = 0
        self.posy += self.dy    

        if self.movingLeft:
            self.dx = 3
        elif self.movingRight:
            self.dx = -3
        else:
            self.dx = 0
        self.posx += self.dx    

        if self.swinging:
            if self.jumping:
                self.swinging = False
            self.posx = self.swing.pendx
            self.posy = self.swing.pendy


        pygame.draw.circle(screen, self.color,(self.posx-camera.left,
                                               self.posy), self.size)
        self.rect.centerx = self.posx-camera.left
        self.rect.centery = self.posy
        screen.fill((255,255,0), self.rect)

    def jump(self):
        self.jumping = True
        self.jumpFrames = 80;

# TODO: implement as states, i.e jumping, running, swinging
    def doswing(self, swing):
        self.swing = swing
        self.swinging = True


class Player(Ball):
    def __init__(self, position, size, color):
        Ball.__init__(self, position, size, color)
        self.framesSinceLastBottle = 40

    def update(self):
       Ball.update(self)
       if self.framesSinceLastBottle < 40:
            self.framesSinceLastBottle += 1
       camera.centerx = self.posx
    def throw_bottle(self):
        if self.framesSinceLastBottle >= 40:
                objects.append(Bottle((self.posx, self.posy-5), 10, (0,0,0),
                                     self.facingForward))
                self.framesSinceLastBottle = 0

class Badguy(Ball):
    def __init__(self, position, size, color):
        Ball.__init__(self, position, size, color)
        self.movingRight= True
    def update(self):
        Ball.update(self)
        #TODO: add code to make badguy change direction at end of platform

class Bottle(Ball):
    def __init__(self, position, size, color, facingForward):
        Ball.__init__(self, position, size, color)
        self.fallingFrames = 80
        if facingForward:
            self.dx = 4 
        else:
            self.dx = -4
    def update(self):
        self.posx += self.dx 

        self.dy=13-self.fallingFrames/4;
        self.fallingFrames -= 1
        self.posy += self.dy
        for badguy in badguys:
            if self.rect.colliderect(badguy.rect):
                badguys.remove(badguy)
                objects.remove(badguy)
                return

        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                objects.remove(self)
                return
         
        pygame.draw.circle(screen, self.color,(self.posx-camera.left,
                                               self.posy), self.size)
        self.rect.centerx = self.posx-camera.left
        self.rect.centery = self.posy
        screen.fill((255,255,0), self.rect)

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
framesSinceLastBottle = 0
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
                player.throw_bottle()
            elif event.key == K_w and not player.jumping:
                player.jump()
            elif event.key == K_a:
                player.movingLeft = True
                player.facingForward = False 
            elif event.key == K_d:
                player.movingRight = True
                player.facingForward = True
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
    if framesSinceLastBottle < 40:
        framesSinceLastBottle += 1
    clock.tick(60)
    pygame.display.flip()
