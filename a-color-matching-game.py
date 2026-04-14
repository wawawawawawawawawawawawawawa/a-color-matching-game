import pygame
import random
import sys
import math

class Slider:
    def __init__(self, y, name, initial_value=128):
        self.y = y
        self.name = name
        self.value = initial_value
        self.width = 400
        self.x = 200
        self.knob_width = 20

    def draw(self, screen, font):
        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, 10))
        knob_x = self.x + (self.value / 255.0) * self.width
        pygame.draw.rect(screen, (255, 255, 255),
                         (knob_x - self.knob_width // 2, self.y - 8, self.knob_width, 26))
        label = font.render(f"{self.name}: {self.value}", True, (255, 255, 255))
        screen.blit(label, (50, self.y - 5))

    def handle_drag(self, mouse_x):
        val = (mouse_x - self.x) / self.width * 255
        self.value = max(0, min(255, int(val)))

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
        screen.blit(text_surf, (self.rect.centerx - text_surf.get_width() // 2,
                                self.rect.centery - text_surf.get_height() // 2))

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

class ColorMatchGame:
    TOTAL_ROUNDS = 3
    MEMORIZE_SECONDS = 5
    ADJUST_SECONDS = 15

    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Color Match Game")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)

        self.target_color = (0, 0, 0)
        self.guess_color = [128, 128, 128]
        self.state = "show"
        self.start_time = 0
        self.time_left = self.MEMORIZE_SECONDS

        # Round tracking
        self.current_round = 1
        self.round_scores = []

        self.sliders = [
            Slider(300, "RED",   initial_value=128),
            Slider(370, "GREEN", initial_value=128),
            Slider(440, "BLUE",  initial_value=128)
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
        diff = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2)
        max_diff = math.sqrt(3 * 255 ** 2)
        return max(0, int(100 * (1 - diff / max_diff)))

    def reset_round(self):
        self.generate_new_target()
        self.guess_color = [128, 128, 128]
        for slider in self.sliders:
            slider.value = 128
        self.state = "show"
        self.start_time = pygame.time.get_ticks()
        self.time_left = self.MEMORIZE_SECONDS
        self.dragging_slider = None

    def full_reset(self):
        self.current_round = 1
        self.round_scores = []
        self.reset_round()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if self.state == "adjust":
                    for slider in self.sliders:
                        knob_x = slider.x + (slider.value / 255.0) * slider.width
                        knob_rect = pygame.Rect(knob_x - slider.knob_width // 2,
                                               slider.y - 10, slider.knob_width, 30)
                        if knob_rect.collidepoint(mx, my):
                            self.dragging_slider = slider
                            break
                    if self.submit_button.is_clicked((mx, my)):
                        self._submit_round()

                elif self.state == "result":
                    if self.submit_button.is_clicked((mx, my)):
                        self._advance_after_result()

                elif self.state == "summary":
                    if self.submit_button.is_clicked((mx, my)):
                        self.full_reset()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_slider = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    if self.state == "result":
                        self._advance_after_result()
                    elif self.state == "summary":
                        self.full_reset()

        return True

    def _submit_round(self):
        score = self.calculate_similarity(self.target_color, self.guess_color)
        self.round_scores.append(score)
        self.state = "result"

    def _advance_after_result(self):
        if self.current_round < self.TOTAL_ROUNDS:
            self.current_round += 1
            self.reset_round()
        else:
            self.state = "summary"

    def update(self):
        current_time = pygame.time.get_ticks()

        if self.state == "show":
            self.time_left = self.MEMORIZE_SECONDS - (current_time - self.start_time) // 1000
            if self.time_left <= 0:
                self.state = "adjust"
                self.start_time = pygame.time.get_ticks()
                self.time_left = self.ADJUST_SECONDS

        elif self.state == "adjust":
            self.time_left = self.ADJUST_SECONDS - (current_time - self.start_time) // 1000
            if self.time_left <= 0:
                self._submit_round()

        if self.state == "adjust" and self.dragging_slider is not None:
            mx, _ = pygame.mouse.get_pos()
            self.dragging_slider.handle_drag(mx)
            self.guess_color = [s.value for s in self.sliders]

    def _draw_round_badge(self):
        badge = self.small_font.render(
            f"Round {self.current_round} / {self.TOTAL_ROUNDS}", True, (200, 200, 200))
        self.screen.blit(badge, (self.WIDTH - badge.get_width() - 20, 20))

    def _get_round_message(self, similarity):
        if similarity > 95:   return "why are u lowkey a god"
        if similarity > 92:   return "did you create color?"
        if similarity > 90:   return "this is lowkey scary"
        if similarity > 87:   return "you gotta be AI"
        if similarity > 83:   return "are u a wizard?"
        if similarity > 77:   return "okay, respectable"
        if similarity > 70:   return "u can do better cmon"
        if similarity > 65:   return "not quite there yet but alright"
        if similarity > 60:   return "my grandma could do better"
        if similarity > 50:   return "u perceive colors like a 2 year old"
        return "go touch some grass and come back"

    def _get_summary_verdict(self, avg):
        if avg >= 85:  return "EXCELLENT", (0, 220, 100)
        if avg >= 65:  return "GOOD",      (255, 200, 0)
        return "MEDIOCRE",                  (255, 90, 60)

    def draw(self):
        self.screen.fill((40, 40, 40))
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "show":
            self._draw_round_badge()
            pygame.draw.rect(self.screen, self.target_color, (200, 100, 400, 250))
            pygame.draw.rect(self.screen, (255, 255, 255), (200, 100, 400, 250), 4)
            timer_text = self.font.render(
                f"Remember this color! {self.time_left}s", True, (255, 255, 255))
            self.screen.blit(timer_text, (self.WIDTH // 2 - timer_text.get_width() // 2, 50))

        elif self.state == "adjust":
            self._draw_round_badge()

            # Countdown bar
            ratio = max(0, self.time_left / self.ADJUST_SECONDS)
            bar_color = (0, 200, 80) if ratio > 0.4 else (255, 160, 0) if ratio > 0.2 else (220, 50, 50)
            pygame.draw.rect(self.screen, (70, 70, 70),   (50, 240, 400, 14), border_radius=7)
            pygame.draw.rect(self.screen, bar_color,      (50, 240, int(400 * ratio), 14), border_radius=7)

            timer_label = self.small_font.render(f"Time left: {max(0, self.time_left)}s", True, (255, 255, 255))
            self.screen.blit(timer_label, (50, 218))

            text = self.font.render("Adjust the sliders to match the color", True, (255, 255, 255))
            self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, 50))

            pygame.draw.rect(self.screen, self.guess_color, (550, 120, 180, 180))
            pygame.draw.rect(self.screen, (255, 255, 255), (550, 120, 180, 180), 3)
            preview = self.small_font.render("Your color", True, (200, 200, 200))
            self.screen.blit(preview, (550, 100))

            for slider in self.sliders:
                slider.draw(self.screen, self.small_font)
            self.submit_button.draw(self.screen, self.small_font, mouse_pos)

        elif self.state == "result":
            self._draw_round_badge()
            similarity = self.round_scores[-1]

            target_label = self.small_font.render("Target Color", True, (255, 255, 255))
            self.screen.blit(target_label, (180, 80))
            pygame.draw.rect(self.screen, self.target_color, (150, 120, 200, 200))
            pygame.draw.rect(self.screen, (255, 255, 255), (150, 120, 200, 200), 4)

            guess_label = self.small_font.render("Your Guess", True, (255, 255, 255))
            self.screen.blit(guess_label, (480, 80))
            pygame.draw.rect(self.screen, self.guess_color, (450, 120, 200, 200))
            pygame.draw.rect(self.screen, (255, 255, 255), (450, 120, 200, 200), 4)

            result_text = self.font.render(f"Match: {similarity}%", True, (255, 255, 255))
            self.screen.blit(result_text, (self.WIDTH // 2 - result_text.get_width() // 2, 360))

            msg = self._get_round_message(similarity)
            color = (0, 255, 0) if similarity > 70 else (255, 200, 0)
            msg_text = self.font.render(msg, True, color)
            self.screen.blit(msg_text, (self.WIDTH // 2 - msg_text.get_width() // 2, 410))

            if self.current_round < self.TOTAL_ROUNDS:
                next_text = self.small_font.render(
                    f"Press R or click to continue to round {self.current_round + 1}", True, (200, 200, 200))
            else:
                next_text = self.small_font.render(
                    "Press R or click to see your final results", True, (200, 200, 200))
            self.screen.blit(next_text, (self.WIDTH // 2 - next_text.get_width() // 2, 470))

            # Reuse submit button as "Continue"
            self.submit_button.text = "CONTINUE"
            self.submit_button.draw(self.screen, self.small_font, mouse_pos)
            self.submit_button.text = "SUBMIT"  # reset for next time

        elif self.state == "summary":
            avg = sum(self.round_scores) / len(self.round_scores)
            verdict, v_color = self._get_summary_verdict(avg)

            title = self.font.render("Game Over — Results", True, (255, 255, 255))
            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 40))

            # Per-round scores
            for i, score in enumerate(self.round_scores):
                bar_w = int(score * 4)
                bar_color = (0, 200, 80) if score >= 85 else (255, 200, 0) if score >= 65 else (220, 50, 50)
                y = 110 + i * 60
                label = self.small_font.render(f"Round {i + 1}:", True, (200, 200, 200))
                self.screen.blit(label, (80, y))
                pygame.draw.rect(self.screen, (70, 70, 70),  (200, y + 2, 400, 24), border_radius=6)
                pygame.draw.rect(self.screen, bar_color,     (200, y + 2, bar_w, 24), border_radius=6)
                pct = self.small_font.render(f"{score}%", True, (255, 255, 255))
                self.screen.blit(pct, (610, y))

            # Divider
            pygame.draw.line(self.screen, (100, 100, 100), (80, 305), (720, 305), 1)

            # Average
            avg_label = self.font.render(f"Average:  {avg:.1f}%", True, (255, 255, 255))
            self.screen.blit(avg_label, (self.WIDTH // 2 - avg_label.get_width() // 2, 320))

            # Verdict
            v_text = pygame.font.SysFont(None, 56).render(verdict, True, v_color)
            self.screen.blit(v_text, (self.WIDTH // 2 - v_text.get_width() // 2, 380))

            # Thresholds hint
            hint = self.small_font.render("Excellent ≥85%  |  Good ≥65%  |  Mediocre <65%", True, (140, 140, 140))
            self.screen.blit(hint, (self.WIDTH // 2 - hint.get_width() // 2, 450))

            # Play again button
            self.submit_button.text = "PLAY AGAIN"
            self.submit_button.draw(self.screen, self.small_font, mouse_pos)
            self.submit_button.text = "SUBMIT"

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