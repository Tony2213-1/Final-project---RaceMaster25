import pygame
import math
import time
import os
import json
pygame.init()
pygame.mixer.init()

window_width = 1600
window_height = 900
screen = pygame.display.set_mode((window_width, window_height))
Debug = False
no_input = True


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
music = True
sfx = True
#sound effects
CP_sfx = pygame.mixer.Sound("CP_cross.wav")
CP_channel = pygame.mixer.Channel(1)
CP_channel.set_volume(0.3)


Fin_sfx = pygame.mixer.Sound("Fin.mp3")
Fin_channel = pygame.mixer.Channel(2)
Fin_channel.set_volume(0.5)

engine_idle = pygame.mixer.Sound("Engine_idle.mp3")
engine_off= pygame.mixer.Sound("Engine_forward Clipchamp.mp3")
engine_on = pygame.mixer.Sound("engine_sloowdown.mp3")
Engine_channel = pygame.mixer.Channel(3)
Engine_channel.set_volume(0.5)

if music == True:   
    def play_music(filename, loop=-1, volume=0.5):
        pygame.mixer.music.load(filename)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loop)

engine_sfx_on = [False, False]

def sfxUpdate(engine_sfx_key_on):
    engine_sfx_on[1] = engine_sfx_key_on
    if engine_sfx_on[0] == False and engine_sfx_on[1] == True:
        Engine_channel.play(engine_idle, loops=-1)

    elif engine_sfx_on[0] == True and engine_sfx_on[1] == False:
        Engine_channel.stop()

    engine_sfx_on[0] = engine_sfx_on[1]
        


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
        self.Variables()
        self.original_image = pygame.image.load("formula_nr1.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1.0)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(0.5 * window_width, 0.5 * window_height))

    def StartPosition(self, x_pos_start, y_pos_start):
        if x_pos_start == None and y_pos_start == None:
            self.x_pos = 0
            self.y_pos = 0
        else:
            self.x_pos = x_pos_start
            self.y_pos = y_pos_start
            
            self.x_pos_start = x_pos_start
            self.y_pos_start = y_pos_start
            
    def Variables(self):
        self.StartPosition(None, None)
        self.x_pos_new = 0
        self.y_pos_new = 0
        self.angle = 0
        self.forward_a = 0
        self.forward_speed = 0
        self.max_speed = 14
        self.deceleration = -0.01
        self.turn_state = 0
        self.turn_state_active = False
        self.turn_state_max = 30
        self.trigger = False
        self.camera_x = self.x_pos
        self.camera_y = self.y_pos
        self.cam_speed = 1
        self.coA = 0.7
        self.coVA = 0.9
        self.slow_factor = 1
        self.penalty = 0.2
        self.backwards_ratio = 0.7
        self.no_engine = False
        self.in_the_air = False
        self.speed_display_color = (255, 255, 255)  # default white
        self.speed_display_color_timer = 0
        self.value_1 = 0

    def PlayerInput(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] and self.no_engine == False:
            if self.forward_speed < 0:
                self.forward_a = 0.1*self.coVA*self.slow_factor
            elif self.forward_speed < 10*self.slow_factor*self.coVA:
                self.forward_a = 0.03*self.coVA*self.slow_factor
            elif self.forward_speed < self.max_speed*self.coVA*self.slow_factor:
                self.forward_a = 0.005*self.coVA*self.slow_factor
            elif self.forward_speed < 1.05*self.max_speed*self.coVA*self.slow_factor:
                self.forward_speed = self.max_speed*self.coVA*self.slow_factor
            else:
                self.forward_speed -= 1/20*self.max_speed*self.coVA*self.slow_factor

        elif keys[pygame.K_s] or keys[pygame.K_SPACE]:
            if self.forward_speed > self.max_speed*self.coVA*self.slow_factor:
                self.forward_speed -= 1/60*self.max_speed*self.coVA*self.slow_factor
            if self.forward_speed > 0:
                self.forward_a = -0.1*self.coVA*self.slow_factor
            elif self.forward_speed <= 0 and self.forward_speed > -self.max_speed*self.coVA*self.slow_factor*self.backwards_ratio and self.no_engine == False:
                self.forward_a = -0.05*self.coVA*self.slow_factor*self.backwards_ratio
            else:
                self.forward_speed += 1/20*self.max_speed*self.coVA*self.slow_factor

        else:
            self.forward_a = 0

        if keys[pygame.K_a] or self.turn_state > 0:
            if keys[pygame.K_a] and abs(self.turn_state) < self.turn_state_max and (abs(self.forward_speed) > 0.75):
                self.turn_state += 1
                self.turn_state_active = True

            if keys[pygame.K_a] or self.turn_state > 0:
                self.trigger = True
                if self.forward_speed >= 3.74*self.coA:
                    self.angle += ((-self.forward_speed / 10) + 2) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed >= 0.75*self.coA:
                    self.angle += (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif -0.75*self.coA >= self.forward_speed > -3.74*self.coA:
                    self.angle -= (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed <= -3.74*self.coA:
                    self.angle -= ((self.forward_speed / 10) + 2) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                else:
                    self.angle += 0
            
        if keys[pygame.K_d] or abs(self.turn_state) > 0 and not self.trigger:
            if keys[pygame.K_d] and abs(self.turn_state) < self.turn_state_max and (abs(self.forward_speed) > 0.75):
                self.turn_state -= 1
                self.turn_state_active = True

            if keys[pygame.K_d] or self.turn_state < 0:
                if self.forward_speed >= 3.74*self.coA:
                    self.angle -= ((-self.forward_speed / 10) + 2) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed >= 0.75*self.coA:
                    self.angle -= (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif -0.75*self.coA >= self.forward_speed > -3.74*self.coA:
                    self.angle += (-2.5 / (self.forward_speed ** 2 + 0.9) + 1.7) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
                elif self.forward_speed <= -3.74*self.coA:
                    self.angle += ((self.forward_speed / 10) + 2) * 0.7 * ((10 + abs(self.turn_state)) / (10 + self.turn_state_max))*self.coA
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
            # world_x = self.x_pos + rotated_x
            # world_y = self.y_pos + rotated_y
            world_x = self.camera_x + rotated_x
            world_y = self.camera_y + rotated_y
            wheel_positions.append((int(world_x), int(world_y)))
        self.wheel_positions = wheel_positions
        return wheel_positions

    def adjust_for_terrain(self, track):
        wheel_positions = self.get_wheel_world_positions()
        grass_hits = 0
        for x, y in wheel_positions:
            color = track.get_color_at(x, y)
            if self.in_the_air == False:
                if color == None:
                    grass_hits += 1
                elif color[:3] == (74, 161, 74): # grass
                    grass_hits += 1
                    
                    if 0 < self.cam_speed < 0.04:
                        self.cam_speed += 1/400 * self.cam_speed
                    
                elif color[:3] == (146, 146, 56) or color[:3] == (209, 209, 108) or color[:3] == (208, 212, 168) or color[:3] == (147, 157, 76) or color[:3] == (209, 184, 108) or color[:3] == (142, 118, 53): # booster
                    if color[:3] == (208, 212, 168) or color[:3] == (147, 157, 76): #ice boost
                        self.cam_speed = 0.006
                    self.forward_speed += 0.05
                    if color[:3] == (209, 184, 108) or color[:3] == (142, 118, 53):
                        if self.cam_speed > 0.04:
                            self.cam_speed -= 1/400 * self.cam_speed
                    self.set_speed_color((255, 255, 0))

                elif color[:3] == (170, 95, 95) or color [:3] == (159, 31, 31) or color[:3] == (170, 112, 95) or color [:3] == (159, 55, 31): # engine-off
                    if color[:3] == (170, 112, 95) or color [:3] == (159, 55, 31):
                        if self.cam_speed > 0.04:
                            self.cam_speed -= 1/400 * self.cam_speed
                    self.no_engine = True
                    Engine_channel.set_volume(0)
                    

                elif color[:3] == (113, 206, 91) or color[:3] == (53, 136, 34) or color[:3] == (177, 206, 91) or color[:3] == (96, 136, 34): # reset
                    if color[:3] == (177, 206, 91) or color[:3] == (96, 136, 34):
                        if self.cam_speed > 0.04:
                            self.cam_speed -= 1/400 * self.cam_speed
                    self.no_engine = False
                    self.set_speed_color((100, 255, 100))
                    Engine_channel.set_volume(0.5)

                elif color[:3] == (179, 144, 197) or color[:3] == (151, 84, 168): #bumper
                    self.InTheAir()
                    self.in_the_air = True
                    self.set_speed_color((200, 100, 255))

                elif color[:3] == (187, 233, 235) or color[:3] == (137, 182, 184) or color[:3] == (227, 155, 171) or color[:3] == (182, 202, 201) or color[:3] == (195, 118, 136) or color[:3] == (164, 183, 182): #ice
                    if self.cam_speed > 0.006:
                        self.cam_speed -= 1/400 * self.cam_speed

                elif color[:3] == (127, 87, 55) or color[:3] == (95, 73, 57) or color[:3] == (180, 172, 166) or color[:3] == (198, 183, 163) or color[:3] == (255, 64, 0) or color[:3] == (199, 50, 0):
                    if self.cam_speed > 0.04:
                        self.cam_speed -= 1/400 * self.cam_speed

                elif color[:3] == (207, 218, 218):
                    if self.cam_speed > 0.005:
                        self.cam_speed -= 1/400 * self.cam_speed
                    grass_hits += 1

                else:
                    if self.cam_speed < 1:
                        self.cam_speed += 1/400 * self.cam_speed
        
        if self.no_engine == True:
            self.set_speed_color((255, 0, 0))
                            
        if grass_hits > 0:
            self.slow_factor = 1 - (self.penalty * grass_hits)
        elif grass_hits == 0:
            self.slow_factor = 1

    def set_speed_color(self, color):
        self.speed_display_color = color
        self.speed_display_color_timer = time.time()

    def InTheAir(self):
        
        if self.in_the_air == True and self.value_1 <= 120:
            
            self.scale = -0.01 * (self.value_1 ** 2) + 1.2 * self.value_1
            self.y_pos -= math.cos(math.radians(self.angle)) * self.forward_speed
            self.x_pos -= math.sin(math.radians(self.angle)) * self.forward_speed
            self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1+(self.scale/180))
            self.rect = self.image.get_rect(center=(window_width/2, window_height/2))
            self.value_1 += 1
        else:
            self.value_1 = 0
            self.in_the_air = False


    def Movement(self):
        keys = pygame.key.get_pressed()
        
        sfxUpdate(keys[pygame.K_w])
        
        
        if keys[pygame.K_s] or keys[pygame.K_SPACE] or (keys[pygame.K_w] and self.no_engine == False):
            self.forward_speed += self.forward_a
            

        elif self.forward_speed > 0:

            if self.forward_speed > self.max_speed * self.coVA * self.slow_factor:
                self.forward_speed -= 1/20*self.max_speed*self.coVA*self.slow_factor

            else:
                self.forward_speed += self.deceleration * (2/(self.slow_factor+1))
                
        elif abs(self.forward_speed) < -self.deceleration:
            self.forward_speed = 0

        elif self.forward_speed < 0:

            if self.forward_speed < self.max_speed * self.coVA * self.slow_factor:
                self.forward_speed += 1/20*self.max_speed*self.coVA*self.slow_factor

            else:
                self.forward_speed -= self.deceleration * (2/(self.slow_factor+1))

        self.y_pos -= math.cos(math.radians(self.angle)) * self.forward_speed
        self.x_pos -= math.sin(math.radians(self.angle)) * self.forward_speed

        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1.0)
        self.rect = self.image.get_rect(center=(window_width/2, window_height/2))

    def CameraMovement(self):
        # Smooth camera follows car with delay
        self.camera_x += (self.x_pos - self.camera_x) * self.cam_speed
        self.camera_y += (self.y_pos - self.camera_y) * self.cam_speed
        # self.camera_x = self.x_pos
        # self.camera_y = self.y_pos


    def Reset(self):
        self.__init__()
        self.StartPosition(x_pos_start, y_pos_start)
        if sfx == True:
            Engine_channel.set_volume(0.5)
        elif sfx == False:
            Engine_channel.set_volume(0)

    def update(self):
        if self.in_the_air == False:
            self.PlayerInput()
            self.Movement()
        self.InTheAir()
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
    def __init__(self, level_name="Track_A01", number_of_checkpoints=0):
        self.countdown_start = time.time()
        self.countdown_duration = 3
        self.start_time = None
        self.end_time = None
        self.finished = False
        self.level_name = level_name
        self.best_times = load_best_times()
        self.best_time = self.best_times.get(level_name, {}).get("PB", None)
        self.new_pb = False
        self.fin_diff = None
        self.cp_diffs = {}
        self.cp_diff_times = {}
        self.pause_time = None
        self.paused_duration = 0
        self.pb_flash_time = None
        self.name_input_active = False
        self.entered_name = ""
        self.input_start_time = None
        self.saved_names = {}  #store names per track
        initials = self.best_times.get(level_name, {}).get("initials")
        if initials:
            self.saved_names[level_name] = initials
            

        # Dynamically generate checkpoints
        checkpoint_colors = [
            (255, 159, 0),   # CP1
            (237, 148, 0),   # CP2
            (218, 136, 0),   # CP3
            (195, 122, 0),   # CP4
            (189, 119, 1),   # CP5
            (179, 112, 0),   # CP6
            (173, 108, 0)    # CP7
        ]
        self.checkpoints = {}
        for i in range(number_of_checkpoints):
            name = f"CP{i+1}"
            self.checkpoints[name] = {
                "color": checkpoint_colors[i],
                "time": None,
                "reached": False
            }

    def Update(self):
        if self.start_time is None and time.time() - self.countdown_start >= self.countdown_duration:
            self.start_time = time.time()  

    def GetTime(self):
        if self.start_time is None:
            return 0
        
        if self.end_time:
            return self.end_time - self.start_time - self.paused_duration
        now = time.time()

        if self.pause_time:
            return self.pause_time - self.start_time - self.paused_duration
        return now - self.start_time - self.paused_duration

    def Draw(self, screen):
        current_time = time.time()
        font_main = pygame.font.Font("Pixelon-OGALo.ttf", 54)
        font_big = pygame.font.Font("Pixelon-OGALo.ttf", 96)
        font_small = pygame.font.Font("Pixelon-OGALo.ttf", 26)
        font_big.set_bold(True)
        font_small.set_italic(True)
       

        if self.start_time is None:
            
            countdown_left = max(0, int(self.countdown_duration - (current_time - self.countdown_start)) + 1)
            text = font_big.render(str(countdown_left), True, (255, 255, 255))
            screen.blit(text, (0.483 * window_width, 0.3 * window_height))
            
            return
        
        
        elapsed = self.GetTime()
        

        # Display current run time
        time_text = font_main.render(f"{elapsed:.3f}s", True, (255, 255, 255))
        screen.blit(time_text, (0.46 * window_width, 0.92 * window_height))

        # Show PB
        if self.best_time is not None:
            if self.pb_flash_time and time.time() - self.pb_flash_time < 2.0:
                pb_color = (150, 150, 255)
            else:
                pb_color = (255, 255, 255)
            
            name = self.saved_names.get(self.level_name, "")
            pb_text_str = f"PB ({name}): {self.best_time:.3f}s" if name else f"PB: {self.best_time:.3f}s"
            pb_text = font_main.render(pb_text_str, True, pb_color)
        else:
            pb_text = font_main.render("PB: --:---", True, (255, 255, 255))
        screen.blit(pb_text, (0.7 * window_width, 0.92 * window_height))

        if self.pb_flash_time and time.time() - self.pb_flash_time < 2.0:
            newpb_font = pygame.font.Font("Pixelon-OGALo.ttf", 192)
            newpb_font.set_bold(True)
            newpb_text = newpb_font.render("NEW PB!", True, (100, 100, 255))
            screen.blit(newpb_text, (0.3 * window_width, 0.2 * window_height))
            return  # Don't draw anything else yet

        # After the flash, show name input if active
        if self.name_input_active:
            input_font = pygame.font.Font("Pixelon-OGALo.ttf", 54)
            prompt = input_font.render("Enter your initials:", True, (255, 255, 255))
            name = input_font.render(self.entered_name.ljust(3, "_"), True, (100, 200, 255))

            screen.blit(prompt, (0.4 * window_width, 0.2 * window_height))
            screen.blit(name, (0.48 * window_width, 0.3 * window_height))

        # Show checkpoint differences
        y_offset = 0.83 * window_height
        for cp_name, diff in self.cp_diffs.items():
            show_time = self.cp_diff_times.get(cp_name)
            if show_time and current_time - show_time <= 1.5:
                color = (100, 100, 255) if diff <= 0 else (255, 100, 100)
                sign = "" if diff <= 0 else "+"
                cp_text = font_small.render(f"{cp_name} {sign}{diff:.3f}", True, color)
                screen.blit(cp_text, (0.44 * window_width, y_offset))
                y_offset += 28

        # Final finish difference shown briefly
        for i in range (1):
            if self.finished == True:
               
                if self.fin_diff == None or self.fin_diff == 0 or self.fin_diff == "--:---":
                    color = (200, 200, 200)
                    sign = ""
                    self.fin_diff = "--:---"
                    diff_text = font_small.render(self.fin_diff, True, color)
                else:
                    if self.fin_diff > 0:
                        sign = "+"
                        color = (255, 100, 100)
                        
                    elif self.fin_diff < 0:
                        sign = ""
                        color = (100, 100, 255)
                        
                    else:
                        print("Error, NoSelfFinDiff")
                    diff_text = font_small.render(f"{sign}{self.fin_diff:.3f}s", True, color) 
        
                screen.blit(diff_text, (0.483 * window_width, 0.88 * window_height))
        if self.pb_flash_time and time.time() - self.pb_flash_time >= 2.0 and self.name_input_active and not self.input_start_time:
            self.input_start_time = time.time()

    def CheckFinish(self, car, track):
        if self.finished or self.start_time is None:
            return
        if not all(cp["reached"] for cp in self.checkpoints.values()):
            return

        for x, y in car.get_wheel_world_positions():
            color = track.get_color_at(x, y)
            if color and color[:3] == (0, 159, 255):  # Finish line color
                self.end_time = time.time()
                self.finished = True

                # Trigger PB check and flash here
                final_time = self.GetTime()
                previous_pb = self.best_times.get(self.level_name, {}).get("PB", None)

                if previous_pb is None or final_time < previous_pb:
                    self.pb_flash_time = time.time()

                Fin_channel.play(Fin_sfx, loops=0)
                break

    def check_checkpoints(self, car, track):
        if self.start_time is None:
            return

        for cp_name, cp_data in self.checkpoints.items():
            if cp_data["reached"]:
                
                continue


            for wx, wy in car.get_wheel_world_positions():
                color = track.get_color_at(wx, wy)
                if color and color[:3] == cp_data["color"]:
                    cp_data["time"] = self.GetTime()
                    cp_data["reached"] = True
                    CP_channel.play(CP_sfx, loops=0)

                    # Time difference from PB
                    pb_cp_time = self.best_times.get(self.level_name, {}).get(cp_name)
                    if pb_cp_time is not None:
                        diff = cp_data["time"] - pb_cp_time
                        self.cp_diffs[cp_name] = diff
                        self.cp_diff_times[cp_name] = time.time()
                 


    def BestTime(self):
        
        final_time = self.GetTime()
        best_time = self.best_times.get(self.level_name, {}).get("PB", None)
        if self.new_pb == False:
            if best_time != None :
                self.fin_diff = final_time - best_time
            else:
                self.fin_diff = None
            self.new_pb = True

        if best_time is None or final_time < best_time:
            best_time = final_time
            self.best_time = best_time

            self.pb_flash_time = time.time()
            self.name_input_active = True
            self.entered_name = ""
            self.input_start_time = time.time()
            
            

            if self.level_name not in self.best_times:
                    self.best_times[self.level_name] = {}

            self.best_times[self.level_name]["PB"] = final_time

                # Save checkpoints
            for cp_name, cp_data in self.checkpoints.items():
                if cp_data["reached"]:
                    self.best_times[self.level_name][cp_name] = cp_data["time"]
            if len(self.entered_name) == 3:
                self.saved_names[self.level_name] = self.entered_name.upper()
                self.best_times[self.level_name]["initials"] = self.entered_name.upper()
            save_best_times(self.best_times)    
        
       

    def Reset(self):
        
        self.countdown_start = time.time()
        self.start_time = None
        self.end_time = None
        self.finished = False
        self.fin_diff = None
        self.new_pb = False
        self.pause_time = None
        self.paused_duration = 0

        # Reset checkpoint status
        for cp in self.checkpoints.values():
            cp["reached"] = False
            cp["time"] = None

        self.cp_diffs.clear()
        self.cp_diff_times.clear()

    def Pause(self):
        if self.pause_time is None:
            self.pause_time = time.time()

    def Resume(self):
        if self.pause_time is not None:
            self.paused_duration += time.time() - self.pause_time
            self.pause_time = None
            
    def TimerUpdate(self):
        self.Update()
        self.CheckFinish(car, track)
        
        if self.finished:
            self.BestTime()
        self.Draw(screen)
        
class Button:
    def __init__(self, x, y, width, height, color, hover_color, text, callback):
        self.rect = pygame.Rect(x * window_width, y * window_height, width * window_width, height * window_height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover_color
        self.selected = False  # ← New
        self.font = pygame.font.Font("Pixelon-OGALo.ttf", 48)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.selected:
            draw_color = (100, 100, 155)  # ← Highlighted color
        elif self.rect.collidepoint(mouse_pos):
            draw_color = self.hover_color
        else:
            draw_color = self.color
        pygame.draw.rect(screen, draw_color, self.rect)
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if button.text == "Back To Main Menu" or button.text == "Start Game":
                self.callback()  
            elif button.text == "Music On" or button.text == "Music Off" or button.text == "Sounds (SFX) On" or button.text == "Sounds (SFX) Off":
                self.callback(self)
            else:
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
    timer.Reset()
    

def BackToTrackPlay():
    global game_state
    game_state = STATE_PLAYING
    timer.Resume()
    if music == True:
        play_music("ingame_music.mp3", -1, 0.3)

def TrackPlay():
    
    global game_state, timer, car, track, no_input, x_pos_start, y_pos_start

    if button.text == "A01":
        track = Track("track_A01.png")
        level_name = "Track_A01"
        number_of_checkpoints = 0
        no_input = False
        x_pos_start = 769
        y_pos_start = 4327

    elif button.text == "A02":
        track = Track("track_A02.png")
        level_name = "Track_A02"
        number_of_checkpoints = 2
        no_input = False
        x_pos_start = 1795
        y_pos_start = 2278
    
    elif button.text == "A03":
        track = Track("track_A03.png")
        level_name = "Track_A03"
        number_of_checkpoints = 3
        no_input = False
        x_pos_start = 1790
        y_pos_start = 1765

    elif button.text == "A04":
        track = Track("track_A04.png")
        level_name = "Track_A04"
        number_of_checkpoints = 2
        no_input = False
        x_pos_start = 258
        y_pos_start = 1253

    elif button.text == "A05":
        track = Track("track_A05.png")
        level_name = "Track_A05"
        number_of_checkpoints = 2
        no_input = False
        x_pos_start = 1791
        y_pos_start = 2789
        

    elif button.text == "A06":
        track = Track("track_A06.png")
        level_name = "Track_A06"
        number_of_checkpoints = 2
        no_input = False
        x_pos_start = 767
        y_pos_start = 3306
        

    elif button.text == "A07":
        track = Track("track_A07.png")
        level_name = "Track_A07"
        number_of_checkpoints = 4
        no_input = False
        x_pos_start = 2816
        y_pos_start = 3305
        

    elif button.text == "A08":
        track = Track("track_A08.png")
        level_name = "Track_A08"
        number_of_checkpoints = 0
        no_input = False
        x_pos_start = 1791
        y_pos_start = 3815

    elif button.text == "A09":
        track = Track("track_A09.png")
        level_name = "Track_A09"
        number_of_checkpoints = 7
        no_input = False
        x_pos_start = 766
        y_pos_start = 7400
    
    timer = Timer(level_name=level_name, number_of_checkpoints=number_of_checkpoints)
    car.StartPosition(x_pos_start, y_pos_start)
    car.Reset()
    game_state = STATE_PLAYING
    
    if music == True:   
        play_music("ingame_music.mp3", -1, 0.3)
    
    

def QuitGame():
    pygame.quit()
    exit()


def GeneralSettings(clicked_button=None):
    global game_state, general_settings_buttons, music

    game_state = STATE_GENERAL_SETTINGS

    # --- CALLBACKS ---
    def handle_music_click(btn):
        global music
        # Deselect both music buttons
        for b in general_settings_buttons:
            if b.text.startswith("Music"):
                b.selected = False
        # Select current
        btn.selected = True

        if btn.text == "Music On":
            music = True
            pygame.mixer.music.set_volume(0.5)
            

        else:
            music = False
            pygame.mixer.music.stop()

    def handle_sfx_click(btn):
        global sfx
        # Deselect both SFX buttons
        for b in general_settings_buttons:
            if b.text.startswith("Sounds"):
                b.selected = False
        # Select current
        btn.selected = True

        if btn.text == "Sounds (SFX) On":
            CP_channel.set_volume(0.3)
            Fin_channel.set_volume(0.3)
            Engine_channel.set_volume(0.3)
            sfx = True
        else:
            CP_channel.set_volume(0)
            Fin_channel.set_volume(0)
            Engine_channel.set_volume(0)
            sfx = False

    # --- BUTTON CREATION ---
    general_settings_buttons = [
        Button(0.2, 0.225, 0.25, 0.12, (150, 150, 170), (150, 150, 250), "Music On", handle_music_click),
        Button(0.55, 0.225, 0.25, 0.12, (150, 150, 170), (150, 150, 250), "Music Off", handle_music_click),
        Button(0.2, 0.425, 0.25, 0.12, (150, 150, 170), (150, 150, 250), "Sounds (SFX) On", handle_sfx_click),
        Button(0.55, 0.425, 0.25, 0.12, (150, 150, 170), (150, 150, 250), "Sounds (SFX) Off", handle_sfx_click),
        Button(0.325, 0.6, 0.35, 0.12, (150, 150, 170), (150, 150, 250), "Back To Main Menu", BackToMainMenu)
    ]

    # --- SET DEFAULT SELECTED STATES ---
    for b in general_settings_buttons:
        if b.text == "Music On":
            b.selected = music
        elif b.text == "Music Off":
            b.selected = not music
        elif b.text == "Sounds (SFX) On":
            b.selected = CP_channel.get_volume() > 0
        elif b.text == "Sounds (SFX) Off":
            b.selected = CP_channel.get_volume() == 0
def GameMenu():
    
    global game_state, game_menu_buttons
    pygame.mixer.music.stop()
    timer.Pause()
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

        if timer.name_input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if len(timer.entered_name) == 3:
                    initials = timer.entered_name.upper()
                    timer.saved_names[timer.level_name] = initials
                    timer.best_times[timer.level_name]["initials"] = initials
                    save_best_times(timer.best_times)

                    # 🔧 Update the displayed best_time with the new initials
                    timer.best_time = timer.best_times[timer.level_name]["PB"]

                    timer.name_input_active = False
            elif event.key == pygame.K_BACKSPACE:
                timer.entered_name = timer.entered_name[:-1]
            elif len(timer.entered_name) < 3 and event.unicode.isalpha():
                timer.entered_name += event.unicode.upper()

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

        if keys[pygame.K_DELETE] and timer.start_time != None:
            car.Reset()
            timer.Reset()
            car.CameraMovement()

        if keys[pygame.K_ESCAPE] and timer.start_time != None:
            if game_state == STATE_PLAYING:
                GameMenu()

            
        
        
        offset_x = car.camera_x - window_width / 2
        offset_y = car.camera_y - window_height / 2
        
        screen.fill((74, 161, 74))
            
        track.draw(screen, offset_x, offset_y)
        overlay_height = int(window_height * 0.09)
        overlay_surface = pygame.Surface((window_width, overlay_height), pygame.SRCALPHA)
        overlay_surface.fill((50, 50, 50, 160))  # RGBA: last value is transparency (0–255)
        screen.blit(overlay_surface, (0, window_height - overlay_height))
        if timer.start_time is not None:
            player.update()
        else:
            car.Movement()
            car.CameraMovement()
        car.adjust_for_terrain(track)
        timer.check_checkpoints(car, track)
        if game_state == STATE_INGAME_MENU:
            pass
        elif game_state == STATE_PLAYING:
            timer.TimerUpdate()
        player.draw(screen)
        # Speed display logic
        speed_text_color = car.speed_display_color

        # Revert to white after 1 second
        if time.time() - car.speed_display_color_timer > 0.3:
            speed_text_color = (255, 255, 255)

        speed_font = pygame.font.Font("Pixelon-OGALo.ttf", 54)
        speed_font.get_bold()
        speed_text = speed_font.render(f"{car.forward_speed*20:.0f}", True, speed_text_color)
        screen.blit(speed_text, (30, window_height - 60))

        
        if Debug == True:
            for wx, wy in car.wheel_positions:
                color = track.get_color_at(wx, wy)
                if color == None:
                    c = (255, 0, 0)
                elif color[:3] == (74, 161, 74):
                    c = (255, 0, 0)
                else:
                    c = (240, 240, 120)
                screen_x = int(wx - offset_x)
                screen_y = int(wy - offset_y)
                    
                pygame.draw.circle(screen, c, (screen_x, screen_y), 5)
         
    pygame.display.update()
    
    clock.tick(120)
