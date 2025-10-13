import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
BACKGROUND = (15, 20, 25)
SNAKE_HEAD = (50, 205, 50)
SNAKE_BODY = (34, 139, 34)
FOOD_COLOR = (220, 20, 60)
TEXT_COLOR = (220, 220, 220)
GRID_COLOR = (30, 35, 40)
GAME_OVER_BG = (0, 0, 0, 180)  # Semi-transparent black

# Game parameters
CELL_SIZE = 20
CELL_NUMBER_X = WIDTH // CELL_SIZE
CELL_NUMBER_Y = HEIGHT // CELL_SIZE
FPS = 10

# Font setup
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

class Snake:
    def __init__(self):
        # Initial snake body (3 segments)
        self.body = [pygame.Vector2(5, 10), pygame.Vector2(4, 10), pygame.Vector2(3, 10)]
        self.direction = pygame.Vector2(1, 0)  # Moving right initially
        self.new_block = False

    def draw_snake(self):
        # Draw each segment of the snake
        for index, block in enumerate(self.body):
            x_pos = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pos, y_pos, CELL_SIZE, CELL_SIZE)

            # Draw snake head differently
            if index == 0:
                pygame.draw.rect(screen, SNAKE_HEAD, block_rect)
                # Draw eyes
                eye_size = CELL_SIZE // 5

                # Determine eye positions based on direction
                if self.direction == pygame.Vector2(1, 0):  # Right
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + CELL_SIZE - eye_size, y_pos + eye_size*2), eye_size)
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + CELL_SIZE - eye_size, y_pos + CELL_SIZE - eye_size*2), eye_size)
                elif self.direction == pygame.Vector2(-1, 0):  # Left
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + eye_size, y_pos + eye_size*2), eye_size)
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + eye_size, y_pos + CELL_SIZE - eye_size*2), eye_size)
                elif self.direction == pygame.Vector2(0, 1):  # Down
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + eye_size*2, y_pos + CELL_SIZE - eye_size), eye_size)
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + CELL_SIZE - eye_size*2, y_pos + CELL_SIZE - eye_size), eye_size)
                elif self.direction == pygame.Vector2(0, -1):  # Up
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + eye_size*2, y_pos + eye_size), eye_size)
                    pygame.draw.circle(screen, (0, 0, 0), (x_pos + CELL_SIZE - eye_size*2, y_pos + eye_size), eye_size)
            else:
                # Draw body segments with a gradient effect
                pygame.draw.rect(screen, SNAKE_BODY, block_rect)
                # Draw a subtle border for body segments
                pygame.draw.rect(screen, (0, 100, 0), block_rect, 1)

    def move_snake(self):
        # Create a copy of the body without the last segment
        body_copy = self.body[:-1]
        # Add the head position to the beginning
        body_copy.insert(0, body_copy[0] + self.direction)
        # Update the body
        self.body = body_copy[:]

        # If we need to add a new block, add it to the end
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0, body_copy[0] + self.direction)
            self.body = body_copy[:]
            self.new_block = False

    def add_block(self):
        self.new_block = True

    def check_collision(self):
        # Check if snake hits the boundary
        if not 0 <= self.body[0].x < CELL_NUMBER_X or not 0 <= self.body[0].y < CELL_NUMBER_Y:
            return True

        # Check if snake hits itself
        for block in self.body[1:]:
            if block == self.body[0]:
                return True

        return False

    def check_fail(self):
        # Check if game is over
        if self.check_collision():
            return True
        return False

class Food:
    def __init__(self):
        self.randomize()

    def draw_food(self):
        # Draw the food as a circle
        food_rect = pygame.Rect(int(self.pos.x * CELL_SIZE), int(self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(screen, FOOD_COLOR, (food_rect.x + CELL_SIZE // 2, food_rect.y + CELL_SIZE // 2), CELL_SIZE // 2)
        # Draw a shine effect on the food
        pygame.draw.circle(screen, (255, 100, 100), (food_rect.x + CELL_SIZE // 3, food_rect.y + CELL_SIZE // 3), CELL_SIZE // 6)

    def randomize(self):
        # Generate random position for food
        self.x = random.randint(0, CELL_NUMBER_X - 1)
        self.y = random.randint(0, CELL_NUMBER_Y - 1)
        self.pos = pygame.Vector2(self.x, self.y)

class Game:
    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.game_active = True

    def update(self):
        if self.game_active:
            self.snake.move_snake()
            self.check_collision()
            self.check_fail()

    def draw_elements(self):
        # Draw grid background
        for x in range(0, WIDTH, CELL_SIZE):
            for y in range(0, HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

        # Draw food
        self.food.draw_food()

        # Draw snake
        self.snake.draw_snake()

        # Draw score
        score_text = f"Score: {self.score}"
        score_surface = font.render(score_text, True, TEXT_COLOR)
        score_rect = score_surface.get_rect(center=(WIDTH//2, 40))
        screen.blit(score_surface, score_rect)

        # Draw game over message if needed
        if not self.game_active:
            self.draw_game_over()

    def check_collision(self):
        # Check if snake head collides with food
        if self.food.pos == self.snake.body[0]:
            # Reposition food
            self.food.randomize()
            # Add new block to snake
            self.snake.add_block()
            # Increase score
            self.score += 1

            # Make sure food doesn't appear on snake
            for block in self.snake.body:
                if block == self.food.pos:
                    self.food.randomize()

    def check_fail(self):
        # Check if snake hits itself or boundary
        if self.snake.check_fail():
            self.game_active = False

    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_BG)
        screen.blit(overlay, (0, 0))

        # Game over text
        game_over_text = big_font.render("GAME OVER", True, (220, 20, 60))
        game_over_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        screen.blit(game_over_text, game_over_rect)

        # Score text
        score_text = font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        screen.blit(score_text, score_rect)

        # Restart instructions
        restart_text = font.render("Press SPACE to Restart", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 80))
        screen.blit(restart_text, restart_rect)

# Create game object
game = Game()

# Create clock object for controlling frame rate
clock = pygame.time.Clock()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # Change direction based on key pressed
            if event.key == pygame.K_UP:
                if game.snake.direction != pygame.Vector2(0, 1):
                    game.snake.direction = pygame.Vector2(0, -1)
            if event.key == pygame.K_DOWN:
                if game.snake.direction != pygame.Vector2(0, -1):
                    game.snake.direction = pygame.Vector2(0, 1)
            if event.key == pygame.K_RIGHT:
                if game.snake.direction != pygame.Vector2(-1, 0):
                    game.snake.direction = pygame.Vector2(1, 0)
            if event.key == pygame.K_LEFT:
                if game.snake.direction != pygame.Vector2(1, 0):
                    game.snake.direction = pygame.Vector2(-1, 0)

            # Restart game
            if event.key == pygame.K_SPACE and not game.game_active:
                game = Game()  # Reset the game

    # Fill the screen with background color
    screen.fill(BACKGROUND)

    # Update game state
    game.update()

    # Draw all elements
    game.draw_elements()

    # Update the display
    pygame.display.update()

    # Control the frame rate
    clock.tick(FPS)

