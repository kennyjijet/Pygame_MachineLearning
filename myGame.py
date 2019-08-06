from pygame import *
import pygame
from os import path
from os.path import abspath, dirname
from random import randrange



BASE_PATH = abspath(dirname(__file__))
ASSETS = '/assets'
FONT_PATH = BASE_PATH + ASSETS + '/fonts/'
IMAGE_PATH = BASE_PATH + ASSETS + '/images/'
SOUND_PATH = BASE_PATH + ASSETS + '/sounds/'

# Colors (R, G, B)
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

WIDTH = 800
HEIGHT = 600

SCREEN = display.set_mode((WIDTH, HEIGHT))
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
          for name in IMG_NAMES}

BLOCKERS_POSITION = 450
ENEMY_DEFAULT_POSITION = 65  # Initial value for a new game
ENEMY_MOVE_DOWN = 35

class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, speed, filename):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed

class Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(WIDTH / 2, HEIGHT - 60))
        self.speed = 5
        self.decision = 1
        self.moveShipTime = 200

class Enemy(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['enemy1_1']
        self.image = transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(topleft=(WIDTH / 2, 50))
        self.speed = 5
        self.decision = 1
        self.moveEnemyTime = 200


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.message = message
        self.surface = self.font.render(self.message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))


class MyGame(object):
    def __init__(self):
        # It seems, in Linux buffersize=512 is not enough, use 4096 to prevent:
        #   ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred
        #mixer.pre_init(44100, -16, 1, 4096)
        #init()
        #self.clock = time.Clock()
        init()
        self.background = image.load(IMAGE_PATH + 'background_space.jpg').convert()
        self.clock = time.Clock()
        self.mainScreen = True
        self.screen = SCREEN

        self.player = Ship()
        self.bulletsShip = []
        self.bulletShip = None
        self.timerForShip = time.get_ticks()

        self.enemy = Enemy()
        self.bulletsEnemy = []
        self.bulletEnemy = None
        self.timerForEnemy = time.get_ticks()

        self.playerHit = 0;
        self.enemyHit = 0;
        self.titleTextPlayer = Text(FONT, 20, str("Enemy hit ") + str(self.playerHit), WHITE, 0, 0)
        self.titleTextEnemy = Text(FONT, 20, str("Player hit ") + str(self.enemyHit), WHITE, WIDTH - 170, HEIGHT - 25)

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)
    
    def create_new_ship(self):
        if self.player is not None:
            self.screen.blit(self.player.image, self.player.rect)

    def aiForShip(self, current_time):
        if current_time - self.timerForShip > self.player.moveShipTime:
            self.player.decision = randrange(0, 4)
            self.timerForShip += self.player.moveShipTime

    def shipShooting(self):
        self.bulletShip = Bullet(self.player.rect.x + 23, self.player.rect.y + 5, 15, "laser")
        self.bulletsShip.append(self.bulletShip)

    def runningBulletShip(self):
        for bulletShip in self.bulletsShip:
            bulletShip.rect.y -= bulletShip.speed
            if bulletShip.rect.y < 0:
                self.bulletsShip.remove(bulletShip)

    def updateShipShooting(self):
        if self.bulletsShip is not None:
            for bulletShip in self.bulletsShip:
                if bulletShip is not None:
                    self.screen.blit(bulletShip.image, bulletShip.rect)

    def updateShip(self):
        if self.player.decision == 0:
            self.player.rect.x += self.player.speed
            if self.player.rect.x > WIDTH - 50:
                self.player.rect.x += self.player.speed * -1
        elif self.player.decision == 1:
            self.player.rect.x -= self.player.speed
            if self.player.rect.x < 0:
                self.player.rect.x -= self.player.speed * -1

        elif self.player.decision == 2:
            self.shipShooting()

    def deleteShip(self):
        self.player = None

    #Enemy AI
    def create_enemy(self):
        if self.enemy is not None:
            self.screen.blit(self.enemy.image, self.enemy.rect)

    def aiForEnemy(self, current_time):
        if current_time - self.timerForEnemy > self.enemy.moveEnemyTime:
            self.enemy.decision = randrange(0, 4)
            self.timerForEnemy += self.enemy.moveEnemyTime

    def updateEnemy(self):
        if self.enemy.decision == 0:
            self.enemy.rect.x += self.enemy.speed
            if self.enemy.rect.x > WIDTH - 150:
                self.enemy.rect.x += self.enemy.speed * -1
        elif self.enemy.decision == 1:
            self.enemy.rect.x -= self.enemy.speed
            if self.enemy.rect.x < 150:
                self.enemy.rect.x -= self.enemy.speed * -1

        elif self.enemy.decision == 2:
            self.enemyShooting()


    def enemyShooting(self):
        self.bulletEnemy = Bullet(self.enemy.rect.x + 20, self.enemy.rect.y + 20, 15, "enemylaser")
        self.bulletsEnemy.append(self.bulletEnemy)

    def updateEnemyShooting(self):
        if self.bulletsEnemy is not None:
            for bulletEnemy in self.bulletsEnemy:
                if bulletEnemy is not None:
                    self.screen.blit(bulletEnemy.image, bulletEnemy.rect)
    

    def runningBulletEnemy(self):
        for bulletEnemy in self.bulletsEnemy:
            bulletEnemy.rect.y += bulletEnemy.speed
            if bulletEnemy.rect.y > HEIGHT:
                self.bulletsEnemy.remove(bulletEnemy)

    def collision_check_ship(self):
        #if (x < (x2 + w2) and (x + w) > x2 and y < (y2 + h2) and (h + y) > y2):
        for bulletEnemy in self.bulletsEnemy:
            if self.player.rect.colliderect(bulletEnemy):
                self.enemyHit += 1

    def collision_check_enemy(self):
        #if (x < (x2 + w2) and (x + w) > x2 and y < (y2 + h2) and (h + y) > y2):
        for bulletShip in self.bulletsShip:
            if self.enemy.rect.colliderect(bulletShip):
                self.playerHit += 1
    
    def drawUI(self):
        self.screen.blit(self.titleTextPlayer.surface, self.titleTextPlayer.rect)
        self.screen.blit(self.titleTextEnemy.surface, self.titleTextEnemy.rect)

        self.titleTextPlayer.message = str(self.playerHit)
        self.titleTextEnemy.message = str(self.enemyHit)

    def main(self):
        while True:
            if self.mainScreen:

                self.screen.blit(self.background, (0, 0))
                current_time = time.get_ticks()
                if self.player is not None:
                    self.create_new_ship()
                    self.aiForShip(current_time)
                    self.updateShip()

                if self.bulletShip is not None:
                    self.updateShipShooting()
                    self.runningBulletShip()

                if self.enemy is not None:
                    self.create_enemy()
                    self.aiForEnemy(current_time)
                    self.updateEnemy()

                if self.bulletsEnemy is not None:
                    self.updateEnemyShooting()
                    self.runningBulletEnemy()

                self.collision_check_ship()
                self.collision_check_enemy()
                self.drawUI()

                print("self.enemyHit " + str(self.enemyHit))
                print("self.playerHit " + str(self.playerHit))


                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
            display.update()
            self.clock.tick(60)