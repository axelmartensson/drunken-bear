import pygame
import sys
from pygame.locals import *
from Animation import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXELS_PER_METER = 10

def get_screenpos(x,y):
    screenx = SCREEN_WIDTH/2 + PIXELS_PER_METER*x
    screeny = SCREEN_HEIGHT/2 - PIXELS_PER_METER*y
    return int(screenx), int(screeny)

def get_worldpos(x,y):
    worldx = (x - SCREEN_WIDTH/2)/PIXELS_PER_METER
    worldy = -(y - SCREEN_HEIGHT/2)/PIXELS_PER_METER        
    return worldx, worldy

class ContactFilter(box2d.b2ContactFilter):
    def __init__(self):
        box2d.b2ContactFilter.__init__(self)
    def ShouldCollide(self, shape1, shape2):
        filter1 = shape1.filterData
        filter2 = shape2.filterData
        if filter1.groupIndex == filter2.groupIndex and filter1.groupIndex != 0:
            return filter1.groupIndex > 0
        collides = (filter1.maskBits & filter2.categoryBits) != 0 and (filter1.categoryBits & filter2.maskBits) != 0
        return collides

class ContactListener(box2d.b2ContactListener):
    def __init__(self):
        box2d.b2ContactListener.__init__(self)
    def BeginContact(self, contact):
        groupIndexA = contact.fixtureA.filterData.groupIndex
        groupIndexB = contact.fixtureB.filterData.groupIndex
        
        idA = contact.fixtureA.body.userData
        idB = contact.fixtureB.body.userData
        if groupIndexA != groupIndexB and groupIndexA!=0 and groupIndexB!=0:
            objects[idA].damage(objects[idB].damagefactor)
            objects[idB].damage(objects[idA].damagefactor)
        
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
                    objects.append(Tile(position=get_worldpos(x*pix,y*pix)))
                elif char == "x":
                    objects.append(Badguy(len(objects), position=get_worldpos(x*pix,y*pix)))
                x += 1
            y += 1
            x=0
        return objects
    
class Tile(object):
    def __init__(self, position, color=(123,123,123)):
        self.color = color
        self.body = world.CreateStaticBody(
                        position=position,
                        shapes=box2d.b2PolygonShape(box=(1,1))
                        )
        self.surface = pygame.Surface((10,10))
        self.surface.fill(color)
    def update(self): 
        x,y = get_screenpos(self.body.position.x, self.body.position.y)
        x = x-camera.left           #makes sure everything moves in relation to camera
        screen.blit(self.surface, (x,y))
        
class Actor(object):    
    def __init__(self,id,color=(255,0,0),position=(0,4), groupIndex=2):
        self.color = color
        self.flip = False
        self.damagefactor = -10
        self.health = 10

        self.body=world.CreateDynamicBody(position=position, userData=id)
        box=self.body.CreateCircleFixture(radius=1,
            density=.1, friction=0.3, restitution=0,
            groupIndex=groupIndex)
    
    def damage(self, damagefactor):
        self.health += damagefactor

    def die(self):
        objects[self.body.userData] = None
        world.DestroyBody(self.body)


    def update(self):
        if self.body.linearVelocity[0] < 0:
            self.flip = True
        else:
            self.flip = False

        if self.health <= 0:
            self.die()
        x,y = get_screenpos(self.body.position.x, self.body.position.y)
        x = x-camera.left           #makes sure everything moves in relation to camera
        pygame.draw.circle(screen,self.color,(x,y), 20)
        return x

class Badguy(Actor):
    def move(self):
        pass

class Player(Actor):
    def update(self):
        x = Actor.update(self)
        camera.centerx = x # this right here is what is causing the "shaking"
   
    def fire(self):
        return Arrow(len(objects),self.body.position, self.flip)

    def jump(self):
        v = self.body.linearVelocity[1]
        if v <= 0.2 and v >= 0:
            self.body.ApplyForce((0,300),self.body.position)

class Arrow(Actor):
    def __init__(self, id, position, flip, color=(255,0,0)):
        self.color = color
        self.damagefactor = -10
        self.health = 10
        self.body=world.CreateKinematicBody(position=position, bullet=True, userData=id)
        box=self.body.CreateCircleFixture(radius=0.15, density=10, friction=0.3, restitution=0, groupIndex=-2)
        if flip:
            self.body.linearVelocity = (-10,0)
        else:
            self.body.linearVelocity = (10,0)
    
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF)

camera = pygame.rect.Rect((0,0), (SCREEN_WIDTH, SCREEN_HEIGHT))
world = box2d.b2World(contactListener=ContactListener(), contactFilter=ContactFilter()) 

timeStep = 1.0 / 60
vel_iters, pos_iters = 10,10
level = Level()
objects = level.load(1)
player=Player(len(objects), (0,255,0), (0,0), -2)
objects.append(player)

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
                objects.append(player.fire())
            elif event.key == K_w:
                player.jump()
            elif event.key == K_a:
                player.body.ApplyForce((-100,0),player.body.position)
            elif event.key == K_d:
                player.body.ApplyForce((100,0),player.body.position)
            elif event.key == K_g:
                objects.append(Badguy(len(objects)))
    for object in objects:
        if object != None:
            object.update()
    world.Step(timeStep, vel_iters, pos_iters)
    pygame.time.wait(10)
    pygame.display.flip()
