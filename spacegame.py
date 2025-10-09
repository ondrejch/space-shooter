import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Battle")

# Colors
BACKGROUND = (10, 10, 30)
PLAYER_COLOR = (0, 200, 255)
ENEMY_COLOR = (255, 50, 50)
BULLET_COLOR = (255, 255, 100)
UI_COLOR = (200, 200, 255)
STAR_COLORS = [(200, 200, 255), (255, 255, 200), (200, 255, 200)]

# Player class
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 60
        self.width = 40
        self.height = 30
        self.speed = 5
        self.shoot_cooldown = 0
        self.lives = 3
        self.score = 0

    def draw(self):
        # Draw the player ship
        pygame.draw.polygon(screen, PLAYER_COLOR, [
            (self.x, self.y - self.height//2),
            (self.x - self.width//2, self.y + self.height//2),
            (self.x + self.width//2, self.y + self.height//2)
        ])
        # Draw engine glow
        pygame.draw.rect(screen, (0, 150, 255), (self.x - 10, self.y + self.height//2, 20, 10))
        pygame.draw.rect(screen, (0, 100, 255), (self.x - 5, self.y + self.height//2 + 10, 10, 5))

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > self.width//2:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width//2:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.height:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullets.append(Bullet(self.x, self.y - self.height//2))
            self.shoot_cooldown = 15

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

# Bullet class
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 4
        self.speed = 7

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, (255, 255, 200), (self.x, self.y), self.radius//2)

    def update(self):
        self.y -= self.speed
        return self.y > 0

# Enemy class
class Enemy:
    def __init__(self):
        self.x = random.randint(30, WIDTH - 30)
        self.y = random.randint(-100, -30)
        self.width = 30
        self.height = 30
        self.speed = random.uniform(1.0, 3.0)
        self.color = ENEMY_COLOR

    def draw(self):
        # Draw enemy ship
        pygame.draw.polygon(screen, self.color, [
            (self.x, self.y + self.height//2),
            (self.x - self.width//2, self.y - self.height//2),
            (self.x + self.width//2, self.y - self.height//2)
        ])
        # Draw enemy details
        pygame.draw.circle(screen, (200, 0, 0), (self.x, self.y), 8)
        pygame.draw.rect(screen, (150, 0, 0), (self.x - 15, self.y + 10, 30, 5))

    def update(self):
        self.y += self.speed
        return self.y < HEIGHT + 30

# Star background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.2, 0.8)
        self.color = random.choice(STAR_COLORS)
        self.brightness = random.randint(150, 255)

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

# Create game objects
player = Player()
bullets = []
enemies = []
stars = [Star() for _ in range(100)]

# Game variables
font = pygame.font.SysFont(None, 36)
game_over = False
spawn_timer = 0

# Main game loop
clock = pygame.time.Clock()
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                player.shoot()
            if event.key == pygame.K_r and game_over:
                # Reset game
                player = Player()
                bullets = []
                enemies = []
                game_over = False
                spawn_timer = 0

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        player.move(keys)
        player.update()

        # Shooting
        if keys[pygame.K_SPACE]:
            player.shoot()

        # Spawn enemies
        spawn_timer += 1
        if spawn_timer >= 30:  # Spawn enemy every 30 frames
            enemies.append(Enemy())
            spawn_timer = 0

        # Update bullets
        for bullet in bullets[:]:
            if not bullet.update():
                bullets.remove(bullet)

        # Update enemies
        for enemy in enemies[:]:
            if not enemy.update():
                enemies.remove(enemy)

        # Update stars
        for star in stars:
            star.update()

        # Collision detection
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                # Simple distance-based collision
                distance = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                if distance < bullet.radius + enemy.width//2:
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    player.score += 10
                    break

        # Check player-enemy collision
        for enemy in enemies[:]:
            distance = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
            if distance < 20 + enemy.width//2:
                enemies.remove(enemy)
                player.lives -= 1
                if player.lives <= 0:
                    game_over = True

    # Drawing
    screen.fill(BACKGROUND)
    
    # Draw stars
    for star in stars:
        star.draw()
    
    # Draw player
    player.draw()
    
    # Draw bullets
    for bullet in bullets:
        bullet.draw()
    
    # Draw enemies
    for enemy in enemies:
        enemy.draw()
    
    # Draw UI
    score_text = font.render(f"Score: {player.score}", True, UI_COLOR)
    lives_text = font.render(f"Lives: {player.lives}", True, UI_COLOR)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 120, 10))
    
    # Draw game over screen
    if game_over:
        game_over_text = font.render("GAME OVER", True, (255, 50, 50))
        restart_text = font.render("Press R to Restart", True, UI_COLOR)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 30))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))
    
    # Draw instructions
    if not game_over:
        controls_text = font.render("Arrow Keys: Move | Space: Shoot", True, (150, 150, 200))
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 40))
    
    pygame.display.flip()
    clock.tick(60)
