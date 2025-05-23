import pygame
import random
import math
pygame.init()

window_width = 1600
window_height = 900
screen = pygame.display.set_mode((window_width, window_height))

#variables



class Car(pygame.sprite.Sprite):
    
    
    def __init__(self): #constructor, called when creating a new player object
        super().__init__()
        self.image = pygame.image.load("formula_nr1.png")
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(midbottom = (0.5*window_width, 0.5*window_height))
        self.Variables()

    def Variables(self):
        self.original_image = pygame.image.load("formula_nr1.png")
        self.original_image = pygame.transform.scale(self.original_image, (200, 200))
        self.image = self.original_image
        self.rect = self.image.get_rect(midbottom=(150, 0.75 * window_height))
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
        self.deceleration = -0.01

    def PlayerInput(self): #formula movement input
        keys = pygame.key.get_pressed()
        if GameActive == True:
            
            if keys [pygame.K_w]:
                if self.forward_speed < 0:
                    self.forward_a = 0.08
                elif self.forward_speed < 10:
                    self.forward_a = 0.02
                else:
                    self.forward_speed = 9.999

            elif keys [pygame.K_s] or keys [pygame.K_SPACE]:
                if self.forward_speed > 0:
                    self.forward_a = -0.08
                elif self.forward_speed <= 0 and self.forward_speed > -10:
                    self.forward_a = -0.02
                else:
                    self.forward_speed = -9.999
                
            if keys [pygame.K_a]:
                if self.forward_speed >= 2.33 or self.forward_speed < -2.33:
                    self.angle += (-self.forward_speed/8)+2
                elif self.forward_speed > 0.7 or self.forward_speed < -0.7:
                    self.angle += (1/(self.forward_speed**2+1.2)+1)
            if keys [pygame.K_d]:
                if self.forward_speed >= 2.33 or self.forward_speed < -2.33:
                    self.angle -= (-self.forward_speed/8)+2
                elif self.forward_speed > 0.7 or self.forward_speed < -0.7:
                    self.angle -= (1/(self.forward_speed**2+1.2)+1)
        if keys [pygame.K_DELETE]:
            if game_active == False and event.key == pygame.K_SPACE:
                game_active = True

    def Movement(self):
        keys = pygame.key.get_pressed()
        if keys [pygame.K_w] or keys [pygame.K_s] or keys [pygame.K_SPACE]:
            self.y_pos == self.y_pos_new
            self.x_pos == self.x_pos_new
            self.forward_speed += self.forward_a
            self.y_pos_new = self.y_pos + math.cos(self.angle/180*math.pi)*self.forward_speed
            self.x_pos_new = self.x_pos + math.sin(self.angle/180*math.pi)*self.forward_speed
            self.rect.y -= self.y_pos_new
            self.rect.x -= self.x_pos_new
            
        elif self.forward_speed > 0:
            self.y_pos == self.y_pos_new
            self.x_pos == self.x_pos_new
            self.forward_speed += self.deceleration
            self.y_pos_new = self.y_pos + math.cos(self.angle/180*math.pi)*self.forward_speed
            self.x_pos_new = self.x_pos + math.sin(self.angle/180*math.pi)*self.forward_speed
            self.rect.y -= self.y_pos_new
            self.rect.x -= self.x_pos_new

        elif self.forward_speed < 0:
            self.y_pos == self.y_pos_new
            self.x_pos == self.x_pos_new
            self.forward_speed -= self.deceleration
            self.y_pos_new = self.y_pos + math.cos(self.angle/180*math.pi)*self.forward_speed
            self.x_pos_new = self.x_pos + math.sin(self.angle/180*math.pi)*self.forward_speed
            self.rect.y -= self.y_pos_new
            self.rect.x -= self.x_pos_new
        
        if keys [pygame.K_a] or keys [pygame.K_d]:
            self.image = pygame.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
       
        print (self.angle)

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

while GameActive == True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        
    #screen.blit(sky_surface,(0,0)) # položíme sky_surface na souřadnice [0,0]
    screen.blit(ground_surface, (0, 0))

    player.update()
    player.draw(screen)
        
    
    pygame.display.update()
    clock.tick(120)