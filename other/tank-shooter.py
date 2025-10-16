import pygame
import sys
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Shooter")

# Colors
BACKGROUND = (30, 30, 50)
TANK_COLOR = (50, 150, 50)
ENEMY_COLOR = (200, 50, 50)
BULLET_COLOR = (255, 255, 0)
OBSTACLE_COLOR = (100, 100, 100)
TEXT_COLOR = (220, 220, 220)
HEALTH_COLOR = (0, 200, 0)
HEALTH_BG_COLOR = (100, 0, 0)
GRID_COLOR = (40, 40, 60)
GRID_HIGHLIGHT = (60, 60, 90)

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
game_over = False
game_won = False

# Font
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

class Tank:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.color = color
        self.angle = 0
        self.speed = 3
        self.health = 100
        self.max_health = 100
        self.controls = controls  # Dictionary with keys for controls
        self.shoot_cooldown = 0
        self.bullets = []
        self.turret_speed = 0.05  # Turret rotation speed
        
    def draw(self, surface):
        # Draw tank body
        pygame.draw.rect(surface, self.color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        
        # Draw tank turret
        turret_length = 20
        turret_x = self.x + turret_length * math.cos(self.angle)
        turret_y = self.y - turret_length * math.sin(self.angle)
        pygame.draw.line(surface, (30, 100, 30), (self.x, self.y), (turret_x, turret_y), 6)
        
        # Draw tank tracks
        pygame.draw.rect(surface, (20, 20, 20), (self.x - self.width//2 - 5, self.y - self.height//2, 5, self.height))
        pygame.draw.rect(surface, (20, 20, 20), (self.x + self.width//2, self.y - self.height//2, 5, self.height))
        
        # Draw health bar
        bar_width = 40
        bar_height = 5
        health_width = bar_width * self.health / self.max_health
        pygame.draw.rect(surface, HEALTH_BG_COLOR, (self.x - bar_width//2, self.y - self.height//2 - 15, bar_width, bar_height))
        pygame.draw.rect(surface, HEALTH_COLOR, (self.x - bar_width//2, self.y - self.height//2 - 15, health_width, bar_height))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surface, BULLET_COLOR, (int(bullet.x), int(bullet.y)), 4)
    
    def move(self, keys, obstacles):
        if not game_over and not game_won:
            # Move tank based on key presses
            new_x = self.x
            new_y = self.y
            
            if keys[self.controls['left']]:
                new_x -= self.speed
            if keys[self.controls['right']]:
                new_x += self.speed
            if keys[self.controls['up']]:
                new_y -= self.speed
            if keys[self.controls['down']]:
                new_y += self.speed
                
            # Boundary checks
            if new_x < self.width//2:
                new_x = self.width//2
            if new_x > WIDTH - self.width//2:
                new_x = WIDTH - self.width//2
            if new_y < self.height//2:
                new_y = self.height//2
            if new_y > HEIGHT - self.height//2:
                new_y = HEIGHT - self.height//2
            
            # Check collision with obstacles
            tank_rect = pygame.Rect(new_x - self.width//2, new_y - self.height//2, self.width, self.height)
            collision = False
            for obstacle in obstacles:
                if tank_rect.colliderect(obstacle.get_rect()):
                    collision = True
                    break
            
            # Only move if no collision
            if not collision:
                self.x = new_x
                self.y = new_y
    
    def rotate_turret(self, keys):
        # Rotate turret with I and J keys
        if keys[pygame.K_j]:  # Rotate left
            self.angle += self.turret_speed
        if keys[pygame.K_i]:  # Rotate right
            self.angle -= self.turret_speed
            
        # Keep angle within bounds (0 to 2π)
        if self.angle < 0:
            self.angle += 2 * math.pi
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
    
    def shoot(self):
        if self.shoot_cooldown <= 0 and not game_over and not game_won:
            # Create a bullet at the turret tip
            turret_length = 20
            bullet_x = self.x + turret_length * math.cos(self.angle)
            bullet_y = self.y - turret_length * math.sin(self.angle)
            bullet_speed = 7
            bullet_dx = bullet_speed * math.cos(self.angle)
            bullet_dy = -bullet_speed * math.sin(self.angle)
            
            self.bullets.append(Bullet(bullet_x, bullet_y, bullet_dx, bullet_dy))
            self.shoot_cooldown = 15  # Cooldown period
    
    def update(self, obstacles):
        # Update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            
            # Check collision with obstacles
            bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, bullet.radius*2, bullet.radius*2)
            for obstacle in obstacles:
                if bullet_rect.colliderect(obstacle.get_rect()):
                    self.bullets.remove(bullet)
                    break
            else:
                # Remove bullets that go off-screen
                if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                    self.bullets.remove(bullet)

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 4
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 25
        self.color = ENEMY_COLOR
        self.speed = 1.5
        self.health = 50
        self.max_health = 50
        self.shoot_timer = random.randint(60, 180)
        self.move_timer = random.randint(30, 90)
        self.move_direction = random.choice(['left', 'right', 'up', 'down'])
        self.shoot_cooldown = 0
        self.bullets = []  # Initialize the bullets attribute
        self.turret_speed = 0.03  # Enemy turret rotation speed
        self.turret_angle = random.uniform(0, 2 * math.pi)
        
    def draw(self, surface):
        # Draw enemy tank body
        pygame.draw.rect(surface, self.color, (self.x - self.width//2, self.y - self.height//2, self.width, self.height))
        
        # Draw enemy tank turret
        turret_length = 15
        turret_x = self.x + turret_length * math.cos(self.turret_angle)
        turret_y = self.y - turret_length * math.sin(self.turret_angle)
        pygame.draw.line(surface, (100, 0, 0), (self.x, self.y), (turret_x, turret_y), 4)
        
        # Draw enemy tank tracks
        pygame.draw.rect(surface, (20, 20, 20), (self.x - self.width//2 - 4, self.y - self.height//2, 4, self.height))
        pygame.draw.rect(surface, (20, 20, 20), (self.x + self.width//2, self.y - self.height//2, 4, self.height))
        
        # Draw health bar
        bar_width = 30
        bar_height = 4
        health_width = bar_width * self.health / self.max_health
        pygame.draw.rect(surface, HEALTH_BG_COLOR, (self.x - bar_width//2, self.y - self.height//2 - 10, bar_width, bar_height))
        pygame.draw.rect(surface, HEALTH_COLOR, (self.x - bar_width//2, self.y - self.height//2 - 10, health_width, bar_height))
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(surface, (255, 100, 100), (int(bullet.x), int(bullet.y)), 3)
    
    def update(self, player, obstacles):
        if not game_over and not game_won:
            # Move randomly
            self.move_timer -= 1
            if self.move_timer <= 0:
                self.move_direction = random.choice(['left', 'right', 'up', 'down'])
                self.move_timer = random.randint(30, 90)
                
            # Calculate new position
            new_x = self.x
            new_y = self.y
            
            if self.move_direction == 'left':
                new_x -= self.speed
            elif self.move_direction == 'right':
                new_x += self.speed
            elif self.move_direction == 'up':
                new_y -= self.speed
            elif self.move_direction == 'down':
                new_y += self.speed
                
            # Boundary checks
            if new_x < self.width//2:
                new_x = self.width//2
                self.move_direction = random.choice(['right', 'up', 'down'])
            if new_x > WIDTH - self.width//2:
                new_x = WIDTH - self.width//2
                self.move_direction = random.choice(['left', 'up', 'down'])
            if new_y < self.height//2:
                new_y = self.height//2
                self.move_direction = random.choice(['left', 'right', 'down'])
            if new_y > HEIGHT - self.height//2:
                new_y = HEIGHT - self.height//2
                self.move_direction = random.choice(['left', 'right', 'up'])
                
            # Check collision with obstacles
            enemy_rect = pygame.Rect(new_x - self.width//2, new_y - self.height//2, self.width, self.height)
            collision = False
            for obstacle in obstacles:
                if enemy_rect.colliderect(obstacle.get_rect()):
                    collision = True
                    break
            
            # Only move if no collision
            if not collision:
                self.x = new_x
                self.y = new_y
                
            # Shoot at player
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot(player)
                self.shoot_timer = random.randint(120, 240)
                
            # Rotate turret towards player
            dx = player.x - self.x
            dy = player.y - self.y
            self.turret_angle = math.atan2(dy, dx)
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.update()
                
                # Check collision with obstacles
                bullet_rect = pygame.Rect(bullet.x - bullet.radius, bullet.y - bullet.radius, bullet.radius*2, bullet.radius*2)
                for obstacle in obstacles:
                    if bullet_rect.colliderect(obstacle.get_rect()):
                        self.bullets.remove(bullet)
                        break
                else:
                    # Remove bullets that go off-screen
                    if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                        self.bullets.remove(bullet)
                    
            # Update cooldown
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
    
    def shoot(self, player):
        if self.shoot_cooldown <= 0:
            # Create a bullet at the turret tip
            turret_length = 15
            bullet_x = self.x + turret_length * math.cos(self.turret_angle)
            bullet_y = self.y - turret_length * math.sin(self.turret_angle)
            # Calculate direction to player
            dx = player.x - self.x
            dy = player.y - self.y
            distance = math.sqrt(dx*dx + dy*dy)
            # Normalize and add some randomness
            bullet_dx = (dx / distance) * 5 + random.uniform(-0.5, 0.5)
            bullet_dy = (dy / distance) * 5 + random.uniform(-0.5, 0.5)
            
            self.bullets.append(Bullet(bullet_x, bullet_y, bullet_dx, bullet_dy))
            self.shoot_cooldown = 30  # Cooldown period

class Obstacle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = OBSTACLE_COLOR
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

# Create player tank
player_controls = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d
}
player = Tank(WIDTH//2, HEIGHT//2, TANK_COLOR, player_controls)

# Create enemy tanks
enemies = []
for i in range(5):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    enemies.append(Enemy(x, y))

# Create obstacles
obstacles = []
for i in range(10):
    x = random.randint(0, WIDTH - 30)
    y = random.randint(0, HEIGHT - 30)
    width = random.randint(20, 60)
    height = random.randint(20, 60)
    obstacles.append(Obstacle(x, y, width, height))

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_over or game_won:
                    # Reset game
                    game_over = False
                    game_won = False
                    player.health = player.max_health
                    score = 0
                    enemies = []
                    for i in range(5):
                        x = random.randint(50, WIDTH - 50)
                        y = random.randint(50, HEIGHT - 50)
                        enemies.append(Enemy(x, y))
                else:
                    player.shoot()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                player.shoot()
    
    # Get pressed keys
    keys = pygame.key.get_pressed()
    
    # Rotate turret with I and J keys
    player.rotate_turret(keys)
    
    # Update player
    player.move(keys, obstacles)
    player.update(obstacles)
    
    # Update enemies
    for enemy in enemies:
        enemy.update(player, obstacles)
    
    # Check collisions - player bullets with enemies
    for bullet in player.bullets[:]:
        for enemy in enemies[:]:
            if (abs(bullet.x - enemy.x) < 20 and abs(bullet.y - enemy.y) < 20):
                # Bullet hit enemy
                enemy.health -= 10
                if enemy.health <= 0:
                    enemies.remove(enemy)
                    score += 100
                if bullet in player.bullets:
                    player.bullets.remove(bullet)
    
    # Check collisions - enemy bullets with player
    for enemy in enemies:
        for bullet in enemy.bullets[:]:
            if (abs(bullet.x - player.x) < 20 and abs(bullet.y - player.y) < 20):
                # Bullet hit player
                player.health -= 10
                if bullet in enemy.bullets:
                    enemy.bullets.remove(bullet)
                if player.health <= 0:
                    game_over = True
    
    # Check collisions - tank with obstacles
    player_rect = pygame.Rect(player.x - player.width//2, player.y - player.height//2, player.width, player.height)
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle.get_rect()):
            # Move player back (this prevents the tank from getting stuck)
            player.x -= 5 if keys[player.controls['left']] else 0
            player.x += 5 if keys[player.controls['right']] else 0
            player.y -= 5 if keys[player.controls['up']] else 0
            player.y += 5 if keys[player.controls['down']] else 0
    
    # Check if all enemies are defeated
    if len(enemies) == 0:
        game_won = True
    
    # Drawing
    screen.fill(BACKGROUND)
    
    # Draw grid
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y), 1)
    
    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)
    
    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen)
    
    # Draw player
    player.draw(screen)
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))
    
    # Draw health
    health_text = font.render(f"Health: {player.health}", True, TEXT_COLOR)
    screen.blit(health_text, (WIDTH - 150, 10))
    
    # Draw game over or win message
    if game_over:
        game_over_text = big_font.render("GAME OVER", True, (255, 50, 50))
        restart_text = font.render("Press SPACE to restart", True, TEXT_COLOR)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    if game_won:
        win_text = big_font.render("YOU WIN!", True, (50, 255, 50))
        restart_text = font.render("Press SPACE to restart", True, TEXT_COLOR)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    # Draw instructions
    if not game_over and not game_won:
        instructions = font.render("WASD: Move | I/J: Rotate Turret | Left Click: Shoot", True, TEXT_COLOR)
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 40))
    
    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()
