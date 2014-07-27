import pygame
import sys, math
from pygame.locals import *

FPS = 60
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

        self.dt = 100/1000.0# milliseconds
        self.r = 100
        self.damp = 1/20.0
        self.phi = math.pi/32
        self.omega = 0
        self._updatependpos()
        self.state = self.stationary

    def update(self):
        self.state()
        pygame.draw.line(screen, self.color,
                         (self.posx-camera.left, self.posy),
                         (self.pendx-camera.left, self.pendy),
                         2)
        self.rect.centerx = self.pendx-camera.left
        self.rect.centery = self.pendy
        screen.fill((255,255,0), self.rect)

    def stationary(self):
        if player.rect.colliderect(self.rect) and not self.grabbed:
            self.grabbed = True
            player.swingfrom(self)
            self.state = self.swinging

    def swinging(self):
        self._integrate()
        oldx = self.pendx
        self._updatependpos()
        if not player.rect.colliderect(self.rect):
            self.grabbed = False
            self.state = self.stationary

    def _integrate(self):
        
        omega2 = self.omega + self.dt*(-G/self.r*math.sin(self.phi-math.pi/2)
                                       - self.damp*self.omega) 
        phi2 = self.phi + self.dt*self.omega 

        self.omega = omega2
        self.phi = phi2

    def _updatependpos(self):
        x = self.r*math.cos(self.phi)
        y = self.r*math.sin(self.phi)
        self.pendx = self.posx + int(x)
        self.pendy = self.posy + int(y)



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
        self.fallingFrames = 1
        self.dx = 4
        self.dy = 0
        self.state = self.falling

    def update(self):
        self.state()
        self.resetSignals()
        self.updateCollisionRect()
        self.draw()

    def resetSignals(self):
        self.s_jump = False

    def falling(self):
        if self.dy < MAX_DY:
            self.dy+=self.fallingFrames/2;
            self.fallingFrames +=1

        drect = self.drect(0, self.dy)
        tile = getTouchingTile(drect)
        if tile:
            self.dy = tile.posy-(self.posy + self.size/2)+1
            self.state = self.grounded
            self.fallingFrames = 1

        self.posy += self.dy
        self.updateHorizontalMovement()

    def drect(self, dx, dy):
        """ returns the AABB encompassing the displacement (dx, dy)"""
        dimensions = (self.size+abs(dx),self.size+abs(dy))
        center = (self.posx-camera.left+dx, self.posy+dy)
        drect = pygame.rect.Rect((0,0),dimensions)
        drect.center = center
        return drect

    def jumping(self):
        self.dy=-self.jumpFrames/2;
        if self.dy <= 0:
            self.state = self.falling
        self.jumpFrames -= 1
        self.posy += self.dy
        self.updateHorizontalMovement()
    
    def grounded(self):
        self.updateHorizontalMovement()
        tile = getTouchingTile(self.rect)
        if tile:
            self.posy = tile.posy - self.size/2+1
        else:
            self.state = self.falling
        if self.s_jump:
            self.state = self.jumping

    def swinging(self):
        self.posx = self.swing.pendx
        self.posy = self.swing.pendy
        if self.s_jump:
            #TODO: conservation of velocity along x-axis
            self.dx = 3
            self.state = self.falling

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
        self.jumpFrames = 60;
        self.s_jump = True

    def swingfrom(self, swing):
        self.swing = swing
        self.state = self.swinging

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

    def grounded(self):
        Ball.grounded(self)
        tile = getTouchingTile(self.rect)
        if tile and tile.endTile:
            self.turnAround()
            self.state = self.turning

    def turning(self):
        Ball.grounded(self)
        tile = getTouchingTile(self.rect)
        if tile and not tile.endTile:
            self.state = self.grounded

        
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
        self.state = self.falling

    def checkForBadguys(self):
        drect = self.drect(self.dx, self.dy)
        for badguy in badguys:
            if drect.colliderect(badguy.rect):
                badguy.die()
                self.die()
                return
            
    def checkForGround(self):
        drect = self.drect(self.dx, self.dy)
        for tile in tiles:
            if drect.colliderect(tile.rect):
                self.die()
                return
            
    def falling(self):
        self.checkForBadguys()
        self.checkForGround()
        self.dy=13-self.fallingFrames/4;
        self.fallingFrames -=1
        self.posy += self.dy
        self.posx += self.dx

    def die(self):
        bottles.remove(self)

class BadBottle(Bottle):
        def checkForBadguys(self):
            if self.rect.colliderect(player.rect):
                player.die()
                self.die()

def getTouchingTile(rect):
    for tile in tiles:
        if rect.colliderect(tile.rect):
            return tile

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
            elif event.key == K_w:
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
    clock.tick(FPS)
    pygame.display.flip()
