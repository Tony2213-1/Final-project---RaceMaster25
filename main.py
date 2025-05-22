import pygame
import random
pygame.init()

window_width = 800
window_height = 450
screen = pygame.display.set_mode((window_width, window_height))

#variables



class Car(pygame.sprite.Sprite):
    
    
    def __init__(self): #constructor, called when creating a new player object
        super().__init__()
        self.image = pygame.image.load("formula_nr1.jpg")
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(midbottom = (150, 0.75*window_height))
        self.Variables()

    def Variables(self):
        self.x_pos = 0
        self.x_pos_new = 0
        self.y_pos = 0
        self.y_pos_new = 0
        self.z_pos = 0
        self.z_pos_new = 0
        self.angle = 0
        self.wheel_turn = 0
        self.forward_a = 0
        self.forward_speed = 0
        self.side_a = 0
        self.rotatiton_speed = 0
        self.d_rotatiton = 0
        self.deceleration = -0.08

    def PlayerInput(self): #formula movement input
        
        keys = pygame.key.get_pressed()
        if keys [pygame.K_w]:
            if self.forward_speed >= 5:
                self.forward_a = 0.2
            elif self.forward_speed <= 15:
                self.forward_a = 0.1
            elif self.forward_speed <= 25:
                self.forward_a = 0.05
            else:
                pass

        if keys [pygame.K_s] or [pygame.K_SPACE]:
            pass
        if keys [pygame.K_a]:
            pass
        if keys [pygame.K_d]:
            pass
        if keys [pygame.K_SPACE]:
            pass

    def Movement(self):
        keys = pygame.key.get_pressed()
        if keys [pygame.K_w]:
            self.forward_speed += self.forward_a
            self.x_pos_new = self.x_pos + self.forward_speed
            self.rect.x += self.x_pos_new
            print (self.forward_speed)
        elif self.forward_speed > 0:
            self.forward_speed += self.deceleration
            self.x_pos_new = self.x_pos + self.forward_speed
            self.rect.x += self.x_pos_new


    def update(self):

        self.PlayerInput()
        self.Movement()

player = pygame.sprite.GroupSingle()
player.add(Car())

clock = pygame.time.Clock()
#sky_surface = pygame.Surface((window_width,0.75*window_height))
#sky_surface.fill("darkslategray1")
ground_surface = pygame.Surface((window_width, window_height))
ground_surface.fill("gray")

GameActive = True

while True:
    if GameActive == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        #screen.blit(sky_surface,(0,0)) # položíme sky_surface na souřadnice [0,0]
        screen.blit(ground_surface, (0, 0))

        player.update()
        player.draw(screen)
        
    
    pygame.display.update()
    clock.tick(60)