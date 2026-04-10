import pygame
import random
import sys
import math

# SLIDER CLASS
class Slider:
    def __init__(self, y, name, initial_value=128):
        self.y = y
        self.name = name
        self.value = initial_value
        self.width = 400
        self.x = 200
        self.knob_width = 20

    def draw(self, screen, font):
        #draw slider track and knob
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, 10))
        
        knob_x = self.x + (self.value / 255.0) * self.width
        pygame.draw.rect(screen, (255, 255, 255), 
                        (knob_x - self.knob_width//2, self.y - 8, self.knob_width, 26))
        
        #draw label
        label = font.render(f"{self.name}: {self.value}", True, (255, 255, 255))
        screen.blit(label, (50, self.y - 5))

    def handle_drag(self, mouse_x):
        val = (mouse_x - self.x) / self.width * 255
        self.value = max(0, min(255, int(val)))


# BUTTON CLASS
class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = (0, 120, 255)
        self.hover_color = (0, 160, 255)

    def draw(self, screen, font, mouse_pos):
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        screen.blit(text_surf, (self.rect.centerx - text_surf.get_width()//2,
                                self.rect.centery - text_surf.get_height()//2))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


# MAIN GAME CLASS
class ColorMatchGame:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Color Match Game - OOP Version")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)

        #game variables
        self.target_color = (0, 0, 0)
        self.guess_color = [128, 128, 128]
        self.state = "show"
        self.start_time = 0
        self.time_left = 5

        #create sliders and button
        self.sliders = [
            Slider(300, "RED", initial_value=128),
            Slider(370, "GREEN", initial_value=128),
            Slider(440, "BLUE", initial_value=128)
        ]
        self.submit_button = Button(300, 520, 200, 50, "SUBMIT")
        
        self.dragging_slider = None

        self.generate_new_target()

    def generate_new_target(self):
        self.target_color = (
            random.randint(30, 225),
            random.randint(30, 225),
            random.randint(30, 225)
        )

    def calculate_similarity(self, c1, c2):
        diff = math.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2 + (c1[2]-c2[2])**2)
        max_diff = math.sqrt(3 * 255**2)
        similarity = max(0, int(100 * (1 - diff / max_diff)))
        return similarity

    def reset_game(self):
        #reset everything for a new round
        self.generate_new_target()
        self.guess_color = [128, 128, 128]
        for slider in self.sliders:
            slider.value = 128
        
        self.state = "show"
        self.start_time = pygame.time.get_ticks()
        self.time_left = 5
        self.dragging_slider = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                
                if self.state == "adjust":
                    #check slider for dragging
                    for slider in self.sliders:
                        knob_x = slider.x + (slider.value / 255.0) * slider.width
                        knob_rect = pygame.Rect(knob_x - slider.knob_width//2, 
                                              slider.y - 10, slider.knob_width, 30)
                        if knob_rect.collidepoint(mx, my):
                            self.dragging_slider = slider
                            break
                    
                    #check submit button
                    if self.submit_button.is_clicked((mx, my)):
                        self.state = "result"

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.state == "result":
                    self.reset_game()

        return True

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == "show":
            self.time_left = 5 - (current_time - self.start_time) // 1000
            if self.time_left <= 0:
                self.state = "adjust"

        #handle dragging slider
        if self.state == "adjust" and self.dragging_slider is not None:
            mx, _ = pygame.mouse.get_pos()
            self.dragging_slider.handle_drag(mx)
            self.guess_color = [s.value for s in self.sliders]

    def draw(self):
        self.screen.fill((40, 40, 40))
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "show":
            pygame.draw.rect(self.screen, self.target_color, (200, 100, 400, 250))
            pygame.draw.rect(self.screen, (255, 255, 255), (200, 100, 400, 250), 4)
            
            timer_text = self.font.render(f"Remember this color! {self.time_left}", True, (255, 255, 255))
            self.screen.blit(timer_text, (self.WIDTH//2 - timer_text.get_width()//2, 50))

        elif self.state == "adjust":
            text = self.font.render("Adjust the sliders to match the color", True, (255, 255, 255))
            self.screen.blit(text, (self.WIDTH//2 - text.get_width()//2, 50))

            #live changes of guess color
            pygame.draw.rect(self.screen, self.guess_color, (550, 120, 180, 180))
            pygame.draw.rect(self.screen, (255, 255, 255), (550, 120, 180, 180), 3)

            #draw sliders and submit button
            for slider in self.sliders:
                slider.draw(self.screen, self.small_font)
            self.submit_button.draw(self.screen, self.small_font, mouse_pos)

        elif self.state == "result":
            similarity = self.calculate_similarity(self.target_color, self.guess_color)

            #target color and guess color display
            target_label = self.small_font.render("Target Color", True, (255, 255, 255))
            self.screen.blit(target_label, (180, 80))
            pygame.draw.rect(self.screen, self.target_color, (150, 120, 200, 200))
            pygame.draw.rect(self.screen, (255, 255, 255), (150, 120, 200, 200), 4)

            guess_label = self.small_font.render("Your Guess", True, (255, 255, 255))
            self.screen.blit(guess_label, (480, 80))
            pygame.draw.rect(self.screen, self.guess_color, (450, 120, 200, 200))
            pygame.draw.rect(self.screen, (255, 255, 255), (450, 120, 200, 200), 4)

            result_text = self.font.render(f"Match: {similarity}%", True, (255, 255, 255))
            self.screen.blit(result_text, (self.WIDTH//2 - result_text.get_width()//2, 380))

            msg = "why are u lowkey a god" if similarity > 95 else "did you create color?" if similarity > 92 else "this is lowkey scary" if similarity > 90 else "you gotta be AI" if similarity > 87 else "are u a wizard?" if similarity > 82 else "okay, respectable" if similarity > 77 else "not quite there yet but alright" if similarity > 70 else "my grandma could do better" if similarity > 60 else "u perceive colors like a 2 year old" if similarity > 50 else "go touch some grass and come back"
            color = (0, 255, 0) if similarity > 70 else (255, 200, 0)
            msg_text = self.font.render(msg, True, color)
            self.screen.blit(msg_text, (self.WIDTH//2 - msg_text.get_width()//2, 440))

            again_text = self.small_font.render("Press R to play again", True, (255, 255, 255))
            self.screen.blit(again_text, (self.WIDTH//2 - again_text.get_width()//2, 530))

        pygame.display.flip()

    def run(self):
        running = True
        self.start_time = pygame.time.get_ticks()

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

# RUN THE GAME
if __name__ == "__main__":
    game = ColorMatchGame()
    game.run()