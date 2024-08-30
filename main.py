import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 836, 660
FPS = 80
GRAVITY = 0.5
JUMP_STRENGTH = -10
SCROLL_SPEED = 5
PIPE_WIDTH = 70
PIPE_GAP = 140
PIPE_FREQUENCY = 1500  # milliseconds
BACKGROUND_COLOR = (255, 255, 255)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird - Pygame')

# Load images
BACKGROUND_IMG = pygame.image.load('./assets/background.png')
GROUND_IMG = pygame.image.load('./assets/ground.png')
BIRD_IMAGES = [pygame.image.load(f'./assets/bird{num}.png') for num in range(1, 4)]
PIPE_IMAGE = pygame.image.load('./assets/pipe.png')
RESTART_BUTTON_IMG = pygame.image.load('./assets/restart_button.png')
RESTART_BUTTON_RECT = RESTART_BUTTON_IMG.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))


# Game variables
ground_scroll = 0
score = 0
is_flying = False
is_game_over = False
last_pipe_time = pygame.time.get_ticks() - PIPE_FREQUENCY

# Sprite groups
pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()


class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = BIRD_IMAGES
        self.current_image = 0
        self.animation_time = pygame.time.get_ticks()
        self.image = self.images[self.current_image]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.clicked = False

    def animate(self):
        if pygame.time.get_ticks() - self.animation_time > 100:
            self.current_image = (self.current_image + 1) % len(self.images)
            self.animation_time = pygame.time.get_ticks()
        self.image = self.images[self.current_image]

    def update(self):
        global is_flying, is_game_over
        if is_flying:
            self.velocity += GRAVITY
            self.velocity = min(self.velocity, 8)
            if self.rect.bottom < SCREEN_HEIGHT - 72:
                self.rect.y += int(self.velocity)
        if not is_game_over:
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.velocity = JUMP_STRENGTH
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
        self.animate()
        self.rotate()

    def rotate(self):
        self.image = pygame.transform.rotate(self.images[self.current_image], self.velocity * -2)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        super().__init__()
        self.image = pygame.transform.scale(PIPE_IMAGE, (PIPE_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(PIPE_GAP / 2)]
        else:
            self.rect.topleft = [x, y + int(PIPE_GAP / 2)]
        self.passed = False

    def update(self):
        if not is_game_over:
            self.rect.x -= SCROLL_SPEED
        if self.rect.right < 0:
            self.kill()


def draw_text(text, font, text_color, x, y):
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (x, y))


def draw_start_message():
    draw_text("Click to Start", font, (255, 255, 255), SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 100)


def reset_game():
    pipe_group.empty()
    bird.rect.center = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
    bird.velocity = 0
    global score, is_game_over, is_flying
    score = 0
    is_game_over = False
    is_flying = False


# Set up the bird object
bird = Bird(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
bird_group.add(bird)

# Font for score
font = pygame.font.Font('./assets/FlappyBirdRegular.ttf', 45)

# Main Game Loop
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(FPS)
    screen.fill(BACKGROUND_COLOR)
    screen.blit(BACKGROUND_IMG, (0, 0))

    # Draw the ground
    screen.blit(GROUND_IMG, (ground_scroll, SCREEN_HEIGHT - 72))

    pipe_group.draw(screen)
    bird_group.draw(screen)

    pipe_group.update()
    bird_group.update()

    # Update score display
    draw_text(str(int(score)), font, (255, 255, 255), SCREEN_WIDTH // 2, 20)

    # Collision check
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or bird.rect.top <= 0:
        is_game_over = True
        is_flying = False

    # Check if bird hit the ground
    if bird.rect.bottom >= SCREEN_HEIGHT - 72:
        is_game_over = True
        is_flying = False

    if not is_game_over and is_flying:
        # Generate new pipes
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT // 2 + pipe_height, -1)
            top_pipe = Pipe(SCREEN_WIDTH, SCREEN_HEIGHT // 2 + pipe_height, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe_time = current_time

        # Scroll the ground
        ground_scroll -= SCROLL_SPEED
        if abs(ground_scroll) > 15:
            ground_scroll = 0

    # Check for pipe passing
    for pipe in pipe_group:
        if pipe.rect.right < bird.rect.left and not pipe.passed:
            pipe.passed = True
            score += 0.5  # each pair of pipes adds 1 to the score

    # If game is not started, show the start message
    if not is_flying and not is_game_over:
        draw_start_message()

    # If game over, show the restart button
    if is_game_over:
        screen.blit(RESTART_BUTTON_IMG, RESTART_BUTTON_RECT)

    # Event checks
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if not is_flying and not is_game_over:
                is_flying = True
            if is_game_over:
                if RESTART_BUTTON_RECT.collidepoint(mouse_pos):
                    reset_game()

    pygame.display.update()

pygame.quit()


