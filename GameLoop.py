import pygame
import sys, math
from pygame.locals import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 10
MAX_DY = 10 
G = 9.81

tiles = []
swings = []
badguys = []

class LevelManager(object):
    def __init__(self):
        self.level = 0
    def loadNextLevel(self):
        self.level += 1
        return self.load(self.level)
        
    def load(self, number):
        pix=PIXELS_PER_METER
        playerPos = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        self.level = number
        lvlStr = "levels/level%i.txt" % number
        res = open(lvlStr, "r")
        x,y = 0,0
        for line in res.readlines():
            for char in line:
                if char == "-":
                    tiles.append(Tile(position=(x*pix,y*pix)))
                elif char == "|":
                    tiles.append(Tile(position=(x*pix,y*pix), endTile=True))
                elif char == "p":
                    playerPos = (x*pix, y*pix)
                elif char == "x":
                    badguys.append(Badguy((x*pix,y*pix), 20, (0,255,0)))
                elif char == "L":
                    swings.append(Swing((x*pix,y*pix), (0,255,0)))
                elif char == "b":
                    badguys.append(BottleThrowingBadguy((x*pix,y*pix), 20, (122,122,0)))
                x += 1
            y += 1
            x=0
        return playerPos
    
class Tile(object):
    def __init__(self, position, color=(123,123,123), endTile=False):
        self.posx, self.posy = position
        self.rect = pygame.rect.Rect(position, (10, 10))
        self.color = color
        self.surface = pygame.Surface((10,10))
        self.surface.fill(color)
        self.endTile = endTile
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
        self.dx = 3
        self.dy = 0

    def update(self):
        
        self.checkForGround()
        self.updateVerticalMovement()
        self.updateHorizontalMovement()
        self.updateCollisionRect()
        self.draw()

    def checkForGround(self):
        self.falling = True 
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.dy > 0:
                    self.jumping = False
                self.falling = False 
                self.fallingFrames = 1

    def updateVerticalMovement(self):
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

        if self.swinging:
            if self.jumping:
                self.swinging = False
            self.posx = self.swing.pendx
            self.posy = self.swing.pendy

    def updateHorizontalMovement(self):
        if self.movingLeft:
            self.posx -= self.dx
        if self.movingRight:
            self.posx += self.dx

    def updateCollisionRect(self):
        self.rect.centerx = self.posx-camera.left
        self.rect.centery = self.posy
        
    def draw(self):
        pygame.draw.circle(screen, self.color,(self.posx-camera.left,
                                               self.posy), self.size)
        screen.fill((255,255,0), self.rect)
        
    def jump(self):
        self.jumping = True
        self.jumpFrames = 80;

# TODO: implement as states, i.e jumping, running, swinging
    def doswing(self, swing):
        self.swing = swing
        self.swinging = True


    def fire(self):
        bottles.append(Bottle((self.posx, self.posy-5), 10, (0,0,0),
                                     self.facingForward))

class Player(Ball):
    def __init__(self, position, size, color):
        Ball.__init__(self, position, size, color)
        self.framesSinceLastBottle = 40

    def update(self):
       Ball.update(self)
       camera.centerx = self.posx

    def die(self):
        print "GAME OVER!!"

class Badguy(Ball):
    def __init__(self, position, size, color):
        Ball.__init__(self, position, size, color)
        self.movingRight= True
        self.dx = 1
    def update(self):
        self.checkForPlayer()
        Ball.update(self)
        
    def checkForPlayer(self):
        if self.rect.colliderect(player.rect):
            if player.dy > 0:
                self.die()
            else:
                player.die()
    def checkForGround(self):
        self.falling = True 
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.dy > 0:
                    self.jumping = False
                self.falling = False 
                self.fallingFrames = 1
                
                if tile.endTile:
                    self.turnAround()
                return
            
    def turnAround(self):
            if self.movingRight:
                self.movingLeft = True
                self.movingRight = False
                self.facingForward = False
            elif self.movingLeft:
                self.movingRight = True
                self.movingLeft = False
                self.facingForward = True

    def die(self):
        badguys.remove(self)

class BottleThrowingBadguy(Badguy):
    def __init__(self, position, size, color):
        Badguy.__init__(self, position, size, color)
        radius = size/2
        self.triggerRect = pygame.rect.Rect(self.posx-radius-size*6, self.posy-radius, size*18, size)
        self.hasFired = False
    def update(self):
        Badguy.update(self)
        self.updateTriggerRect()
        
    def checkForPlayer(self):
        Badguy.checkForPlayer(self)
        
        if self.movingRight and self.posx-player.posx < 0 or self.movingLeft and self.posx-player.posx > 0:
            facingPlayer = True
        else:
            facingPlayer = False
        if not self.hasFired and facingPlayer and self.triggerRect.colliderect(player.rect):
            self.fire()
            self.hasFired = True
            
    def updateTriggerRect(self):
        self.triggerRect.centerx = self.posx-camera.left
        self.triggerRect.centery = self.posy
        
    def fire(self):
        bottles.append(BadBottle((self.posx, self.posy-5), 10, (0,0,0),
                                 self.facingForward))
class Bottle(Ball):
    def __init__(self, position, size, color, playerFacingForward):
        Ball.__init__(self, position, size, color)
        self.fallingFrames = 80
        if playerFacingForward:
            self.dx = 4 
        else:
            self.dx = -4
    def update(self):
        self.checkForBadguys()
        Ball.update(self)


    def checkForBadguys(self):
        for badguy in badguys:
            if self.rect.colliderect(badguy.rect):
                badguy.die()
                self.die()
                return
            
    def checkForGround(self):
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                self.die()
                return
            
    def updateHorizontalMovement(self):
        self.posx += self.dx
        
    def updateVerticalMovement(self):
        self.dy=13-self.fallingFrames/4;
        self.fallingFrames -= 1
        self.posy += self.dy
    def die(self):
        bottles.remove(self)

class BadBottle(Bottle):
        def checkForBadguys(self):
            if self.rect.colliderect(player.rect):
                player.die()
                self.die()

def updateAll(objects):
    for obj in objects:
        if camera.collidepoint((obj.posx, obj.posy)):
            obj.update()

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)
levelManager = LevelManager()
playerPos = levelManager.loadNextLevel()

player = Player(playerPos, 20, (255,0,0))
camera = pygame.rect.Rect((0,0), (SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
bottles = []
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
            elif event.key == K_SPACE and framesSinceLastBottle > 20:
                player.fire()
                framesSinceLastBottle = 0
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

    updateAll(tiles)
    updateAll(badguys)
    updateAll(bottles)
    updateAll(swings)
    player.update()
    
    if framesSinceLastBottle < 40:
        framesSinceLastBottle += 1
    clock.tick(60)
    pygame.display.flip()
