import pygame
import random
import math
import time
import os
import json
pygame.init()

window_width = 1600
window_height = 900
screen = pygame.display.set_mode((window_width, window_height))
Debug = True

track_buttons = []
buttons = []
game_menu_buttons = []
general_settings_buttons = []
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_TRACK_MENU = "track_menu"
STATE_INGAME_MENU = "Ingame menu"
STATE_GENERAL_SETTINGS = "General settings"
game_state = STATE_MENU

PB_FILE = "pb_times.txt"

def load_best_times():
    if os.path.exists(PB_FILE):
        with open(PB_FILE, "r") as file:
            return json.load(file)
    return {}

def save_best_times(best_times):
    with open(PB_FILE, "w") as file:
        json.dump(best_times, file, indent=4)

class Car(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("formula_nr1.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(0.5 * window_width, 0.5 * window_height))
        self.Variables()
        
    def Variables(self, x_pos_start = 765, y_pos_start = 4325):
        self.x_pos = x_pos_start # Start in world coordinates
        self.y_pos = y_pos_start
        self.x_pos_new = 0
        self.y_pos_new = 0
        self.angle = 0
        self.forward_a = 0
        self.forward_speed = 0
        self.max_speed = 10
        self.deceleration = -0.01
        self.turn_state = 0
        self.turn_state_active = False
        self.turn_state_max = 30
        self.trigger = False
        self.camera_x = self.x_pos
        self.camera_y = self.y_pos
        self.coA = 0.7
        self.coVA = 0.9
        self.slow_factor = 1
        self.penalty = 0.2
        self.backwards_ratio = 0.7

    def PlayerInput(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            if self.forward_speed < 0:
                self.forward_a = 0.1*self.coVA*self.slow_factor
            elif self.forward_speed < self.max_speed*self.coVA*self.slow_factor:
                self.forward_a = 0.03*self.coVA*self.slow_factor
            elif self.forward_speed < 1.05*self.max_speed*self.coVA*self.slow_factor:
                self.forward_speed = self.max_speed*self.coVA*self.slow_factor
            else:
                self.forward_speed -= 1/20*self.max_speed*self.coVA*self.slow_factor

        elif keys[pygame.K_s] or keys[pygame.K_SPACE]:
            if self.forward_speed > 0:
                self.forward_a = -0.08*self.coVA*self.slow_factor
            elif self.forward_speed <= 0 and self.forward_speed > -self.max_speed*self.coVA*self.slow_factor*self.backwards_ratio:
                self.forward_a = -0.02*self.coVA*self.slow_factor*self.backwards_ratio
            else:
                self.forward_speed += 1/20*self.max_speed*self.coVA*self.slow_factor

        if keys[pygame.K_a] or self.turn_state > 0:
            if keys[pygame.K_a] and abs(self.turn_state) < self.turn_state_max and (abs(self.forward_speed) > 0.75):
                self.turn_state += 1
                self.turn_state_active = True

            if keys[pygame.K_a] or self.turn_state > 0:
                self.trigger = True
                if self.forward_speed >= 3.74*self.coA:
                    self.angle += ((-self.forward_speed / 8) + 2) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed >= 0.75*self.coA:
                    self.angle += (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif -0.75*self.coA >= self.forward_speed > -3.74*self.coA:
                    self.angle -= (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed <= -3.74*self.coA:
                    self.angle -= ((self.forward_speed / 8) + 2) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                else:
                    self.angle += 0
            
        if keys[pygame.K_d] or abs(self.turn_state) > 0 and not self.trigger:
            if keys[pygame.K_d] and abs(self.turn_state) < self.turn_state_max and (abs(self.forward_speed) > 0.75):
                self.turn_state -= 1
                self.turn_state_active = True

            if keys[pygame.K_d] or self.turn_state < 0:
                if self.forward_speed >= 3.74*self.coA:
                    self.angle -= ((-self.forward_speed / 8) + 2) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed >= 0.75*self.coA:
                    self.angle -= (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif -0.75*self.coA >= self.forward_speed > -3.74*self.coA:
                    self.angle += (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed <= -3.74*self.coA:
                    self.angle += ((self.forward_speed / 8) + 2) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                else:
                    self.angle += 0
            self.trigger = False

        if self.turn_state_active == True:
                
                if self.turn_state > 0 and keys [pygame.K_a] == False:
                    self.turn_state -= 1
                    

                elif self.turn_state > 0 and (self.forward_speed < 0.75*self.coA and self.forward_speed > -0.75*self.coA):
                    self.turn_state -= 1
                    

                elif self.turn_state < 0 and keys [pygame.K_d] == False:
                    self.turn_state += 1
                    

                elif self.turn_state < 0 and (self.forward_speed < 0.75*self.coA and self.forward_speed > -0.75*self.coA):
                    self.turn_state += 1

                elif self.turn_state == 0:
                    self.turn_state_active = False
                    
    def get_wheel_world_positions(self):
        wheel_offsets = [
            (-20, -21),  # Front left
            (-20, 36),   # Front right
            (20, -21),   # Rear left
            (20, 36)     # Rear right
        ]
        wheel_positions = []
        for ox, oy in wheel_offsets:
            rotated_x = ox * math.cos(math.radians(-self.angle)) - oy * math.sin(math.radians(-self.angle))
            rotated_y = ox * math.sin(math.radians(-self.angle)) + oy * math.cos(math.radians(-self.angle))
            world_x = self.x_pos + rotated_x
            world_y = self.y_pos + rotated_y
            wheel_positions.append((int(world_x), int(world_y)))
        self.wheel_positions = wheel_positions
        return wheel_positions

    def adjust_for_terrain(self, track):
        wheel_positions = self.get_wheel_world_positions()
        grass_hits = 0
        for x, y in wheel_positions:
            color = track.get_color_at(x, y)
            if color != None and color[:3] == (74, 161, 74) or color != None and color[:3] == (63, 138, 63):
                grass_hits += 1
        if grass_hits > 0:
            self.slow_factor = 1 - (self.penalty * grass_hits)
        elif grass_hits == 0:
            self.slow_factor = 1
        
    def Movement(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_SPACE]:
            self.forward_speed += self.forward_a
        
        elif self.forward_speed > 0:
            if self.forward_speed > self.max_speed * self.coVA * self.slow_factor:
                self.forward_speed -= 1/20*self.max_speed*self.coVA*self.slow_factor
            else:
                self.forward_speed += self.deceleration
        elif self.forward_speed < 0:
            if self.forward_speed < self.max_speed * self.coVA * self.slow_factor:
                self.forward_speed += 1/20*self.max_speed*self.coVA*self.slow_factor
            else:
                self.forward_speed -= self.deceleration

        self.y_pos -= math.cos(math.radians(self.angle)) * self.forward_speed
        self.x_pos -= math.sin(math.radians(self.angle)) * self.forward_speed

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=(window_width / 2, window_height / 2))

    def CameraMovement(self):
        # Smooth camera follows car with delay
        cam_speed = 0.8
        self.camera_x += (self.x_pos - self.camera_x) * cam_speed
        self.camera_y += (self.y_pos - self.camera_y) * cam_speed
    
    def Reset(self):
        self.__init__()

    def update(self):
        self.PlayerInput()
        self.Movement()
        self.CameraMovement()

class Track:

    def __init__(self, image_path):
        self.surface = pygame.image.load(image_path).convert()
        self.width, self.height = self.surface.get_size()

    def draw(self, screen, offset_x, offset_y):
        screen.blit(self.surface, (-offset_x, -offset_y))

    def get_color_at(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.surface.get_at((x, y))
        return None

class Timer:
    
    def __init__(self, level_name = "Track_A01"):
        self.countdown_start = time.time()
        self.countdown_duration = 3  # 3 seconds countdown
        self.start_time = None
        self.end_time = None
        self.finished = False
        self.best_time = None
        self.level_name = level_name
        self.best_times = load_best_times()
        self.best_time = self.best_times.get(level_name, None)
        self.difference = 0
    
        

    def Update(self):
        current_time = time.time()
        if self.start_time is None and current_time - self.countdown_start >= self.countdown_duration:
            self.start_time = current_time

    def GetTime(self):
        if self.start_time == 0:
            return 0
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time
        
    def Draw(self, screen):
        
        current_time = time.time()
        if self.start_time is None:
            font = pygame.font.Font("Pixelon-OGALo.ttf", 96)
            font.set_bold(True)
            countdown_left = max(0, int(self.countdown_duration - (current_time - self.countdown_start)) + 1)
            text = font.render(str(countdown_left), True, (255, 255, 255))
            screen.blit(text, (0.483*window_width, 0.3*window_height))
        else:
            elapsed = (self.GetTime())
            font = pygame.font.Font("Pixelon-OGALo.ttf", 54)
            text = font.render(f"{elapsed:.3f}s", True, (255, 255, 255))

            screen.blit(text, (0.46*window_width, 0.92*window_height))

            if self.best_time != None:
                best = font.render(f"PB: {self.best_time:.3f}s", True, (255, 255, 255))
                screen.blit(best, (0.8*window_width, 0.92*window_height))
                if self.best_time != None:
                    
                    if self.finished == True:
                        diff = elapsed - self.best_time
                        font = pygame.font.Font("Pixelon-OGALo.ttf", 26)
                        font.set_italic(True)
                        if diff > 0:
                            diff2 = font.render(f"+{diff:.3f}", True, (255, 100, 100))
                        elif diff <= 0:
                            diff2 = font.render(f"{self.difference:.3f}", True, (100, 100, 255))
                        screen.blit(diff2, (0.483*window_width, 0.88*window_height))
       
    def CheckFinish(self, car, track):
        if self.finished or self.start_time is None:
            return
        for x, y in car.get_wheel_world_positions():
            color = track.get_color_at(x, y)
            if color != None and color[:3] == (0, 159, 255):  # Finish line color
                self.end_time = time.time()
                self.finished = True
                break

    def BestTime(self):
        final_time = self.GetTime()
        if self.best_time is None or final_time < self.best_time:
            if self.best_time != None:
                self.difference = final_time - self.best_time
            self.best_time = final_time
            self.best_times[self.level_name] = self.best_time
            save_best_times(self.best_times)

    def Reset(self):
        self.countdown_start = time.time()
        self.start_time = None
        self.end_time = None
        self.finished = False

    def TimerUpdate(self):
        self.Update()

        self.CheckFinish(car, track)
        if self.finished:
            self.BestTime()
        self.Draw(screen)
        
        

class Button:

    def __init__(self, x, y, width, height, color, hover_color, text, callback,):
        self.rect = pygame.Rect(x*window_width, y*window_height, width*window_width, height*window_height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font("Pixelon-OGALo.ttf", 48)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.hover_color if self.rect.collidepoint(mouse_pos) else self.color, self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


car = Car()
player = pygame.sprite.GroupSingle()

player.add(car)
clock = pygame.time.Clock()
timer = Timer()

def TrackMenu():
    global game_state, track_buttons
    game_state = STATE_TRACK_MENU
    track_buttons = [
        Button(0.3, 0.225, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A01", TrackPlay),
        Button(0.45, 0.225, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A02", TrackPlay),
        Button(0.6, 0.225, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A03", TrackPlay),
        Button(0.3, 0.375, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A04", TrackPlay),
        Button(0.45, 0.375, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A05", TrackPlay),
        Button(0.6, 0.375, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A06", TrackPlay),
        Button(0.3, 0.525, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A07", TrackPlay),
        Button(0.45, 0.525, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A08", TrackPlay),
        Button(0.6, 0.525, 0.1, 0.12, (150, 150, 170), (150, 150, 250), "A09", TrackPlay),

        Button(0.3, 0.7, 0.4, 0.12, (150, 150, 170), (150, 150, 250), "Back", BackToMainMenu)
    ]

def BackToMainMenu():
    global game_state
    game_state = STATE_MENU

def BackToTrackPlay():
    global game_state
    game_state = STATE_PLAYING

def TrackPlay():
    global game_state, timer, car, track
    game_state = STATE_PLAYING
    timer = Timer()
    if button.text == "A01":
        track = Track("track_A01.png")
        timer.level_name = "Track_A01"
        car.Variables(760, 4325)
    
    elif button.text == "A02":
        track = Track("track_A02.png")
        timer.level_name = "Track_A02"
        car.Variables(300, 500)
    

def QuitGame():
    pygame.quit()
    exit()

def SettingsAudio():
    pass

def SettingsControls():
    pass

def GeneralSettings():
    global game_state, general_settings_buttons
    game_state = STATE_GENERAL_SETTINGS
    general_settings_buttons = [
        Button(0.15, 0.1, 0.2, 0.12, (150, 150, 170), (150, 150, 250), "Audio", SettingsAudio),
        Button(0.40, 0.1, 0.2, 0.12, (150, 150, 170), (150, 150, 250), "Controls", SettingsControls),
        Button(0.65, 0.1, 0.2, 0.12, (150, 150, 170), (150, 150, 250), "Back", BackToMainMenu)
    ]

def GameMenu():
    global game_state, game_menu_buttons
    game_state = STATE_INGAME_MENU
    game_menu_buttons = [
        Button(0.325, 0.3, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Resume", BackToTrackPlay),
        Button(0.325, 0.45, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Settings", GeneralSettings),
        Button(0.325, 0.6, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Quit to main menu", BackToMainMenu)
    ]

buttons = [
    Button(0.325, 0.3, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Start Game", TrackMenu),
    Button(0.325, 0.45, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Settings", GeneralSettings),
    Button(0.325, 0.6, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Quit", QuitGame)
]

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_state == STATE_MENU:
            for button in buttons:
                button.handle_event(event)
        elif game_state == STATE_TRACK_MENU:
            for button in track_buttons:
                button.handle_event(event)
        elif game_state == STATE_INGAME_MENU:
            for button in game_menu_buttons:
                button.handle_event(event)
        elif game_state == STATE_GENERAL_SETTINGS:
            for button in general_settings_buttons:
                button.handle_event(event)

    screen.fill((30, 30, 30))

    if game_state == STATE_MENU:
        for button in buttons:
            button.draw(screen)

    elif game_state == STATE_TRACK_MENU:
        for button in track_buttons:
            button.draw(screen)

    elif game_state == STATE_INGAME_MENU:
        for button in game_menu_buttons:
            button.draw(screen)
    
    elif game_state == STATE_GENERAL_SETTINGS:
        for button in general_settings_buttons:
            button.draw(screen)

    elif game_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_DELETE]:
            car.Reset()
            timer.Reset()
        if keys[pygame.K_ESCAPE]:
            
            GameMenu()

        offset_x = car.camera_x - window_width / 2
        offset_y = car.camera_y - window_height / 2

        screen.fill("black")
        track.draw(screen, offset_x, offset_y)

        if timer.start_time is not None:
            player.update()

        car.adjust_for_terrain(track)
        timer.TimerUpdate()
        player.draw(screen)

        
        if Debug == True:
            for wx, wy in car.wheel_positions:
                screen_x = int(wx - offset_x)
                screen_y = int(wy - offset_y)
                pygame.draw.circle(screen, (255, 0, 0), (screen_x, screen_y), 5)

    pygame.display.update()
    clock.tick(120)
