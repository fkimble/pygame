

import pygame
import sys
import random

# --- 1. Game Constants and Configuration ---

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
CAPTION = "Simple Pygame Platformer"

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 255)
PLATFORM_COLOR = (150, 75, 0)  # Brown
ENEMY_COLOR = RED
BACKGROUND_COLOR = (255, 192, 203)  # Sky Blue

# Player properties
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 40
PLAYER_SPEED = 5

# NOTES FOR BEGINNERS:
# To adjust gravity or jump height:
GRAVITY = 0.8     # Higher value means faster fall
JUMP_STRENGTH = -15 # Higher negative value means higher jump

# --- 2. Pygame Initialization ---

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()
FONT = pygame.font.Font(None, 36) # Default font, size 36

# --- 3. Game State Variables ---

score = 0
game_state = "START" # Possible states: "START", "RUNNING", "GAME_OVER"

# --- 4. Game Classes ---

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # NOTES FOR BEGINNERS:
        # To change the player's sprite or color:
        # 1. For a simple color change:
        self.image = pygame.Surface([PLAYER_WIDTH, PLAYER_HEIGHT])
        self.image.fill(GREEN) # Change GREEN to another color
        # 2. To use an image:
        # self.image = pygame.image.load('player_sprite.png').convert_alpha()
        # self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def update(self, platforms):
        # 1. Apply Horizontal Movement
        self.rect.x += self.vel_x

        # 2. Apply Gravity
        self.vel_y += GRAVITY
        # Limit max falling speed
        if self.vel_y > 10:
            self.vel_y = 10

        # 3. Apply Vertical Movement
        self.rect.y += self.vel_y
        self.on_ground = False # Assume not on ground unless collision proves otherwise

        # 4. Collision Detection (Vertical)
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Only resolve collision if moving down (landing) or moving up (hitting ceiling)
                if self.vel_y > 0: # Moving down
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0: # Moving up (e.g., hitting the bottom of a platform)
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0

        # 5. Collision Detection (Screen Edges - Ground/Ceiling)
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.vel_y = 0
            self.on_ground = True
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

    def move(self, direction):
        if direction == "left":
            self.vel_x = -PLAYER_SPEED
        elif direction == "right":
            self.vel_x = PLAYER_SPEED
        elif direction == "stop":
            self.vel_x = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, is_moving=False, move_range=100):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_moving = is_moving
        self.start_x = x
        self.move_range = move_range
        self.speed = 1
        self.direction = 1

    def update(self):
        if self.is_moving:
            self.rect.x += self.speed * self.direction
            # Change direction if platform hits movement limits
            if self.rect.x > self.start_x + self.move_range or self.rect.x < self.start_x:
                self.direction *= -1


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 2 # Simple horizontal movement
        self.direction = 1 # 1 for right, -1 for left

    def update(self):
        self.rect.x += self.speed * self.direction
        # Simple boundary check: reverse direction at screen edges
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1


# --- 5. Game Setup Functions ---

def create_level(platforms, enemies):
    """
    Function to create all platforms and enemies for the level.
    NOTES FOR BEGINNERS:
    To add new levels or platform layouts:
    1. Clear the existing lists (done below).
    2. Add new Platform() and Enemy() objects with different coordinates.
    """
    platforms.empty()
    enemies.empty()
    
    # Ground platform (must be at the bottom)
    platforms.add(Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))

    # Static Platforms
    platforms.add(Platform(100, 500, 150, 20))
    platforms.add(Platform(550, 450, 150, 20))
    platforms.add(Platform(150, 300, 100, 20))

    # Moving Platform (x, y, width, height, is_moving, move_range)
    platforms.add(Platform(400, 350, 100, 20, is_moving=True, move_range=200))
    platforms.add(Platform(350, 150, 200, 20, is_moving=True, move_range=200))

    # Enemies (x, y, width, height)
    enemies.add(Enemy(600, SCREEN_HEIGHT - 40, 30, 20))
    enemies.add(Enemy(200, 480, 20, 20))
    enemies.add(Enemy(450, 330, 20, 20))


def reset_game(player, all_sprites, platforms, enemies):
    """Resets the game state and character positions."""
    global score
    score = 0
    all_sprites.empty()
    
    # Setup player and sprite groups
    player.__init__(50, SCREEN_HEIGHT - PLAYER_HEIGHT - 20) # Reset player to start position
    
    all_sprites.add(player)
    
    # Create the level layout
    create_level(platforms, enemies)
    all_sprites.add(platforms)
    all_sprites.add(enemies)


# --- 6. Screen Drawing Functions ---

def draw_text(surface, text, font, color, x, y):
    """Helper function to draw text on the screen."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)

def draw_start_screen():
    """Draws the initial screen."""
    screen.fill(BACKGROUND_COLOR) # NOTES: Change BACKGROUND_COLOR to another color to change background
    draw_text(screen, CAPTION, FONT, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, "Press SPACE to Start", FONT, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Controls: Left/Right Arrows to Move, Up Arrow or Z to Jump", FONT, BLACK, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
    pygame.display.flip()

def draw_game_over_screen():
    """Draws the game over screen."""
    screen.fill(BLACK)
    draw_text(screen, "GAME OVER", FONT, RED, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
    draw_text(screen, f"Final Score: {score}", FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    draw_text(screen, "Press SPACE to Play Again", FONT, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4)
    pygame.display.flip()

def draw_running_screen(all_sprites):
    """Draws the main game screen."""
    # NOTES: Change BACKGROUND_COLOR to another color to change background
    screen.fill(BACKGROUND_COLOR)
    
    # Draw all sprites
    all_sprites.draw(screen)
    
    # Draw Score
    draw_text(screen, f"Score: {score}", FONT, BLACK, 70, 20)
    
    pygame.display.flip()


# --- 7. Main Game Loop ---

def main():
    global game_state, score

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    
    # Create player and initialize the game elements
    player = Player(50, SCREEN_HEIGHT - PLAYER_HEIGHT - 20)
    reset_game(player, all_sprites, platforms, enemies) # Setup initial state

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_state == "START" or game_state == "GAME_OVER":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if game_state == "GAME_OVER":
                        reset_game(player, all_sprites, platforms, enemies) # Reset for new game
                    game_state = "RUNNING"
            
            elif game_state == "RUNNING":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.move("left")
                    elif event.key == pygame.K_RIGHT:
                        player.move("right")
                    elif event.key == pygame.K_UP or event.key == pygame.K_z:
                        player.jump()
                
                if event.type == pygame.KEYUP:
                    # Stop horizontal movement when key is released, but only if no other key is pressed
                    if event.key == pygame.K_LEFT and player.vel_x < 0:
                        player.move("stop")
                    elif event.key == pygame.K_RIGHT and player.vel_x > 0:
                        player.move("stop")


        # --- Game Logic (RUNNING state only) ---
        if game_state == "RUNNING":
            
            # 1. Update all sprites
            platforms.update()
            enemies.update()
            player.update(platforms)
            
            # 2. Player-Enemy Collision Check (Loss condition)
            if pygame.sprite.spritecollide(player, enemies, False):
                game_state = "GAME_OVER"

            # 3. Score Update (Simple time-based score)
            # This makes the score increase slowly over time while playing
            score += 1

            # 4. Drawing
            draw_running_screen(all_sprites)

        # --- Screen Drawing (State-dependent) ---
        elif game_state == "START":
            draw_start_screen()
        
        elif game_state == "GAME_OVER":
            draw_game_over_screen()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()