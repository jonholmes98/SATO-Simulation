import ctypes, pygame, sys
import random
import pandas as pd
import os

# Maintain resolution regardless of Windows scaling settings
ctypes.windll.user32.SetProcessDPIAware()
total_clicks_list = []
total_hits_list = []
accuracy_list = []

TITLE_STRING = 'SATO2D'
FPS = 120
HEIGHT = 1080
WIDTH = 1920

# Images
BG_IMAGE_PATH = 'data\wbg.jpg'
TARGET_IMAGE = 'data\circle-60.png'

# Text config (font from DaFont)
COUNTDOWN_FONT = 'data/Vanilla Caramel.otf'
FONT_SIZE = 300
TEXT_COLOR = 'Black'


class TitleScreen():
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(COUNTDOWN_FONT, FONT_SIZE)
        self.space_font = pygame.font.Font(COUNTDOWN_FONT, 60)

    def update(self):
        # Load background image and create text objects
        title_image = pygame.image.load(BG_IMAGE_PATH).convert_alpha()
        aim_trainer_text = self.font.render("SATO2D", True, (0, 0, 0))
        press_space_text = self.space_font.render(f"Press Space to Start", True, (0, 0, 0))

        # Create rectangles from text objects
        aim_trainer_rect = aim_trainer_text.get_rect()
        press_space_rect = press_space_text.get_rect()

        aim_trainer_rect.centerx, aim_trainer_rect.centery = self.display_surface.get_rect().centerx, self.display_surface.get_rect().centery
        press_space_rect.centerx, press_space_rect.centery = self.display_surface.get_rect().centerx, self.display_surface.get_rect().centery + 200

        # Draw
        self.display_surface.blit(title_image, (0, 0))
        self.display_surface.blit(aim_trainer_text, aim_trainer_rect)
        self.display_surface.blit(press_space_text, press_space_rect)


class Countdown():
    def __init__(self, seconds):
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(COUNTDOWN_FONT, 80)
        self.decrement_time = pygame.time.get_ticks()
        self.should_decrement = False
        self.time_left = int(seconds)
        self.initial_countdown_length = self.time_left
        self.target_group = pygame.sprite.Group()
        self.targets_spawned = 0

    def cooldowns(self):
        curr_time = pygame.time.get_ticks()

        if not self.should_decrement and self.time_left > 0:
            if curr_time - self.decrement_time > 999:
                self.should_decrement = True

    def draw_timer(self):
        if self.should_decrement:
            self.time_left -= 1
            self.decrement_time = pygame.time.get_ticks()
            self.should_decrement = False
        if self.time_left > 0:
            count_string = str(self.time_left)
        else:
            count_string = ""

        # Draw current value of count_string
        count_surf = self.font.render(count_string, True, TEXT_COLOR, None)
        x, y = WIDTH - 20, HEIGHT - 10
        count_rect = count_surf.get_rect(bottomright = (x, y))
        self.display_surface.blit(count_surf, count_rect)

    # Target is a 60x60 pixel red square
    def spawn_target(self):
        # Check to see if there is time left in the countdown and spawn a randomly located target if none are in sprite group
        if self.time_left > 0 and len(list(item for item in self.target_group)) < 1:
            x, y = random.randint(0, 1860), random.randint(0, 1020)
            spawned_target = Target(x, y)
            self.target_group.add(spawned_target)
            self.targets_spawned += 1
        self.target_group.draw(self.display_surface)

    def update(self):
        self.cooldowns()
        self.draw_timer()
        self.spawn_target()


class PostGame():
    def __init__(self, total_clicks, total_hits):
        self.display_surface = pygame.display.get_surface()
        self.total_clicks, self.total_hits = total_clicks, total_hits
        self.misses = self.total_clicks - self.total_hits
        self.font = pygame.font.Font(COUNTDOWN_FONT, FONT_SIZE)
        self.base_font_size = 60
        self.multiplier = 1





        # Increase multiplier based on number of total hits; penalty for misses
        if self.total_hits > 1:
            self.multiplier = self.get_new_multiplier(self.total_hits, self.misses)

        self.score_font = pygame.font.Font(COUNTDOWN_FONT, self.base_font_size + (7 * self.total_hits))
        self.stats_font = pygame.font.Font(COUNTDOWN_FONT, self.base_font_size)

        if self.total_clicks > 0:
            self.accuracy = round(((self.total_hits / self.total_clicks) * 100) * 2, 2)
            self.final_score = "{:,}".format(int(self.accuracy * self.total_hits) * self.multiplier)
        else:
            self.accuracy, self.final_score = 0, 0

        #data points
        accuracy_pt = self.accuracy
        clicks = self.total_clicks
        hits = self.total_hits
        temp_df = pd.DataFrame(columns=['Accuracy', 'Total Clicks', 'Final Score'])

        #writing local csv
        filename = 'data_csv'
        current_dir = os.getcwd()
        filepath = os.path.join(current_dir, filename)

        temp_df = temp_df.append({'Accuracy':accuracy_pt, 'Total Clicks':clicks/2, 'Total Hits':hits}, ignore_index=True)
        with open(filepath, 'a') as f:
            temp_df.to_csv(f, header=False, index=False)


    def get_new_multiplier(self, num_hits, num_misses):
        basis = num_hits - num_misses
        if basis > 3 and basis < 6:
            return 2
        elif basis > 5 and basis < 10:
            return 3
        elif basis > 9 and basis < 15:
            return 4
        elif basis > 14:
            return 5
        else:
            return 1

    def update(self):
        # Load background image and create text objects
        postgame_image = pygame.image.load(BG_IMAGE_PATH).convert_alpha()
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        stats_numbers_text = self.score_font.render(f"SCORE: {self.final_score}", True, (255, 255, 255))
        stats_percentage_text = self.stats_font.render(f"Press Space to Try Again", True, (255, 255, 255))
        if stats_numbers_text.get_width() > 1920:
            # Scale the score surface down and maintain aspect ratio
            new_height = int((stats_numbers_text.get_height() / stats_numbers_text.get_width()) * 1920)
            stats_numbers_text = pygame.transform.scale(stats_numbers_text, (1920, new_height))

        # Create rectangles from text objects
        game_over = game_over_text.get_bounding_rect()
        stats_numbers = stats_numbers_text.get_bounding_rect()
        stats_percentage = stats_percentage_text.get_bounding_rect()

        height = game_over_text.get_height() + stats_numbers_text.get_height() + stats_percentage_text.get_height()
        final_surface = pygame.Surface((1920, 1080))
        final_surface_rect = final_surface.get_rect()
        final_surface_rect.centerx, final_surface_rect.centery = self.display_surface.get_rect().centerx, self.display_surface.get_rect().centery

        # Adjusting rectangle locations to match final_surface_rect
        game_over.centerx, game_over.y = 960, (1080 - height) / 2
        stats_numbers.centerx, stats_numbers.y = 960, game_over.bottom + 60
        stats_percentage.centerx, stats_percentage.y = 960, stats_numbers.bottom + 60

        final_surface.blit(game_over_text, game_over)
        final_surface.blit(stats_numbers_text, stats_numbers)
        final_surface.blit(stats_percentage_text, stats_percentage)

        self.display_surface.blit(postgame_image, (0, 0))
        self.display_surface.blit(final_surface, (0, 0))


class Target(pygame.sprite.Sprite):
    kill_count = 0
    def __init__(self, x, y, *groups):
        super().__init__(*groups)
        pygame.mixer.init()
        self.image = pygame.image.load(TARGET_IMAGE)
        self.radius = 30
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 0, 0), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(topleft = (x, y))
        self.hit_sound = pygame.mixer.Sound('data/hit.mp3')
        self.hit_channel = pygame.mixer.Channel(5)

    def update(self):
        # Get the x and y coordinates of the mouse cursor and check for a collision
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            self.hit_channel.play(self.hit_sound)
            self.kill()
            Target.kill_count += 1





class Game:
    def __init__(self):

        # General setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE_STRING)
        self.clock = pygame.time.Clock()
        self.click_count = 0
        self.game_state = "waiting"

        # Background image and shot sound
        self.bg_image = pygame.image.load(BG_IMAGE_PATH)
        self.shot_sound = pygame.mixer.Sound('data/shot.mp3')

        # Create objects of relevant classes
        self.title = TitleScreen()



    def run(self):
        while True:
            # Handle quit operation
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and self.game_state == "waiting":
                    if event.key == pygame.K_SPACE:
                        self.countdown = Countdown(10)
                        self.game_state = "playing"
                elif event.type == pygame.KEYDOWN and self.game_state == "gameover":
                    # Reset the game state and clear click/target details
                    if event.key == pygame.K_SPACE:
                        self.click_count = 0
                        self.countdown.targets_spawned = 0
                        self.game_state = "waiting"
                        del self.countdown
                elif event.type == pygame.MOUSEBUTTONUP and self.game_state == "playing":
                    self.click_count += 1
                    self.click_count += 1
                    self.shot_sound.play()
                    self.countdown.target_group.update()

            pygame.display.update()
            self.screen.blit(self.bg_image, (0, 0))
            self.clock.tick(FPS)

            # Game specific updates
            if self.game_state == "waiting":
                self.title.update()
            elif self.game_state == "playing" and self.countdown.time_left > 0:
                self.countdown.update()
            elif self.game_state == "playing" and self.countdown.time_left == 0:
                self.game_state = "gameover"
                self.postgame = PostGame(self.click_count, self.countdown.targets_spawned - 1) # total_clicks, total_hits
            elif self.game_state == "gameover":
                self.postgame.update()



if __name__ == '__main__':
    game = Game()
    game.run()
