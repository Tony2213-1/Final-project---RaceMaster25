import pygame # klíčová knihovna umožňující vytvářet jednoduše nejen hry
import random
pygame.init() # nutný příkaz hned na začátku pro správnou inicializaci knihovny

window_width = 1920
window_height = 1080
screen = pygame.display.set_mode((window_width, window_height))

class Player(pygame.sprite.Sprite):

    def __init__(self): #constructor, called when creating a new player object
        super().__init__()
        self.image = pygame.image.load("dinosaur.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom = (150, 0.75*window_height))
        

    def PlayerInput(self):
        keys = pygame.key.get_pressed()
        if keys [pygame.K_SPACE] and self.rect.bottom >= 0.75*window_height:
            self.gravity = -15

    def ApplyGravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 0.75*window_height: 
            self.rect.bottom = 0.75*window_height

    def update(self):
        self.PlayerInput()
        self.ApplyGravity()
