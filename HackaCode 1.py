import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders: Defender vs Mothership")
clock = pygame.time.Clock()

# Load game assets
# You can replace these with your own images
def create_spaceship_surface():
    surf = pygame.Surface((40, 30), pygame.SRCALPHA)
    pygame.draw.polygon(surf, GREEN, [(20, 0), (0, 30), (40, 30)])
    return surf

def create_mothership_surface():
    surf = pygame.Surface((120, 40), pygame.SRCALPHA)
    pygame.draw.rect(surf, PURPLE, (0, 0, 120, 40))
    pygame.draw.polygon(surf, PURPLE, [(0, 40), (120, 40), (60, 60)])
    return surf

def create_squid_surface():
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.rect(surf, BLUE, (0, 10, 20, 10))
    pygame.draw.rect(surf, BLUE, (5, 0, 10, 10))
    pygame.draw.rect(surf, BLUE, (0, 0, 5, 5))
    pygame.draw.rect(surf, BLUE, (15, 0, 5, 5))
    return surf

def create_crab_surface():
    surf = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.circle(surf, RED, (15, 15), 12)
    pygame.draw.rect(surf, RED, (3, 10, 24, 10))
    pygame.draw.rect(surf, RED, (0, 5, 5, 5))
    pygame.draw.rect(surf, RED, (25, 5, 5, 5))
    pygame.draw.rect(surf, RED, (0, 20, 5, 5))
    pygame.draw.rect(surf, RED, (25, 20, 5, 5))
    return surf

def create_octopus_surface():
    surf = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(surf, YELLOW, (20, 20), 18)
    for i in range(8):
        angle = math.pi * i / 4
        x = 20 + 20 * math.cos(angle)
        y = 20 + 20 * math.sin(angle)
        pygame.draw.circle(surf, YELLOW, (int(x), int(y)), 6)
    return surf

def create_bullet_surface(color):
    surf = pygame.Surface((4, 10), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, 4, 10))
    return surf

# Game assets
spaceship_img = create_spaceship_surface()
mothership_img = create_mothership_surface()
squid_img = create_squid_surface()
crab_img = create_crab_surface()
octopus_img = create_octopus_surface()
bullet_player_img = create_bullet_surface(GREEN)
bullet_enemy_img = create_bullet_surface(RED)

# Font for text
font_small = pygame.font.SysFont('Arial', 20)
font_medium = pygame.font.SysFont('Arial', 32)
font_large = pygame.font.SysFont('Arial', 48)

# Base class for game objects
class GameObject:
    def __init__(self, x, y, width, height, image=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = image
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(surface, WHITE, self.rect)
    
    def collides_with(self, other):
        return self.rect.colliderect(other.rect)

# Bullet class
class Bullet(GameObject):
    def __init__(self, x, y, speed, damage, source, is_player=True):
        image = bullet_player_img if is_player else bullet_enemy_img
        super().__init__(x, y, 4, 10, image)
        self.speed = speed
        self.damage = damage
        self.source = source
        self.is_player = is_player
    
    def update(self):
        if self.is_player:
            self.y -= self.speed
        else:
            self.y += self.speed
        super().update()
    
    def is_off_screen(self):
        return self.y < 0 or self.y > SCREEN_HEIGHT

# Base class for aliens
class Alien(GameObject):
    def __init__(self, x, y, width, height, health, speed, damage, cost, image):
        super().__init__(x, y, width, height, image)
        self.health = health
        self.speed = speed
        self.damage = damage
        self.cost = cost
        self.direction = 1  # 1 for right, -1 for left
        self.y_offset = 0
    
    def move(self):
        self.x += self.speed * self.direction
        
        # Classic Space Invaders movement: move sideways until hitting edge, then down
        if self.x <= 0:
            self.direction = 1
            self.y += 20
        elif self.x + self.width >= SCREEN_WIDTH:
            self.direction = -1
            self.y += 20
        
        super().update()
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
    
    def attack(self):
        # Default is no attack
        return None

# Squid alien (kamikaze)
class Squid(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, 1, 2, 10, 50, squid_img)
        # Random movement component
        self.random_offset = 0
        self.random_counter = 0
    
    def move(self):
        # Base movement
        self.x += self.speed * self.direction
        
        # Add some random movement
        self.random_counter += 1
        if self.random_counter >= 15:
            self.random_counter = 0
            self.random_offset = random.randint(-20, 20)
        
        self.x += self.random_offset * 0.1
        
        # Keep in bounds
        if self.x <= 0:
            self.direction = 1
            self.y += 20
        elif self.x + self.width >= SCREEN_WIDTH:
            self.direction = -1
            self.y += 20
        
        # Move downward faster than other aliens
        self.y += 1
        
        super().update()

# Crab alien (shooter)
class Crab(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30, 3, 1, 5, 100, crab_img)
        self.bullet_damage = 5
        self.shoot_cooldown = 0
    
    def update(self):
        self.move()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def attack(self):
        # Random chance to shoot
        if self.shoot_cooldown <= 0 and random.random() < 0.01:
            self.shoot_cooldown = 60  # Wait 1 second between shots
            return Bullet(self.x + self.width // 2, self.y + self.height, 5, self.bullet_damage, self, False)
        return None

# Octopus alien (tank)
class Octopus(Alien):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40, 8, 0.5, 3, 200, octopus_img)
        self.ticking = False
        self.tick_timer = 0
    
    def update(self):
        self.move()
        if self.ticking:
            self.tick_timer += 1
            if self.tick_timer >= 60:  # Tick damage every second
                self.tick_timer = 0
                return self.damage
        return 0
    
    def start_ticking(self):
        self.ticking = True

# Spaceship (player)
class Spaceship(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 30, spaceship_img)
        self.health = 100
        self.max_health = 100
        self.movement_speed = 5
        self.reload_speed = 1
        self.reload_cooldown = 0
        self.money = 100
        self.bullet_damage = 1
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.movement_speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.movement_speed
        
        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
        
        super().update()
    
    def shoot(self):
        if self.reload_cooldown <= 0:
            self.reload_cooldown = int(60 / self.reload_speed)
            return Bullet(self.x + self.width // 2 - 2, self.y, 10, self.bullet_damage, self)
        return None
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        return self.health <= 0
    
    def purchase_upgrade(self, upgrade_type):
        if upgrade_type == "reload":
            cost = int(100 * self.reload_speed)
            if self.money >= cost and self.reload_speed < 5:
                self.money -= cost
                self.reload_speed += 0.5
                return True
        elif upgrade_type == "health":
            cost = int(self.max_health * 0.5)
            if self.money >= cost and self.max_health < 300:
                self.money -= cost
                self.max_health += 50
                self.health = min(self.health + 50, self.max_health)
                return True
        elif upgrade_type == "speed":
            cost = int(self.movement_speed * 30)
            if self.money >= cost and self.movement_speed < 10:
                self.money -= cost
                self.movement_speed += 1
                return True
        return False
    
    def add_money(self, amount):
        self.money += amount

# Mothership (enemy)
class Mothership(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 120, 60, mothership_img)
        self.health = 500
        self.max_health = 500
        self.money = 200
        self.money_growth_rate = 1
        self.growth_factor = 0.001
        self.time = 0
        self.spawn_cooldown = 0
        self.spawn_queue = []
    
    def update(self):
        self.time += 1
        # Earn money over time with soft exponential growth
        self.money += self.money_growth_rate * (1 + self.growth_factor * self.time)
        
        # Update spawn cooldown
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1
        
        super().update()
    
    def spawn_alien(self, alien_type):
        x = random.randint(50, SCREEN_WIDTH - 100)
        y = self.y + self.height
        
        if alien_type == "squid":
            if self.money >= 50:
                self.money -= 50
                return Squid(x, y)
        elif alien_type == "crab":
            if self.money >= 100:
                self.money -= 100
                return Crab(x, y)
        elif alien_type == "octopus":
            if self.money >= 200:
                self.money -= 200
                return Octopus(x, y)
        
        return None
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < a:
            self.health = 0
        return self.health <= 0
    
    def ai_decision(self, spaceship, aliens):
        # Simple AI for Mothership to decide what to spawn
        if self.spawn_cooldown <= 0:
            if len(aliens) < 20:  # Don't spawn too many aliens
                choice = random.random()
                
                # If player has high health, favor damage dealers
                if spaceship.health > spaceship.max_health * 0.7:
                    if choice < 0.5 and self.money >= 50:
                        self.spawn_queue.append("squid")
                        self.spawn_cooldown = 30
                    elif choice < 0.8 and self.money >= 100:
                        self.spawn_queue.append("crab")
                        self.spawn_cooldown = 45
                    elif self.money >= 200:
                        self.spawn_queue.append("octopus")
                        self.spawn_cooldown = 90
                
                # If player has medium health, mixed strategy
                elif spaceship.health > spaceship.max_health * 0.3:
                    if choice < 0.3 and self.money >= 50:
                        self.spawn_queue.append("squid")
                        self.spawn_cooldown = 30
                    elif choice < 0.7 and self.money >= 100:
                        self.spawn_queue.append("crab")
                        self.spawn_cooldown = 45
                    elif self.money >= 200:
                        self.spawn_queue.append("octopus")
                        self.spawn_cooldown = 90
                
                # If player has low health, spam cheap units
                else:
                    if choice < 0.6 and self.money >= 50:
                        self.spawn_queue.append("squid")
                        self.spawn_cooldown = 30
                    elif choice < 0.9 and self.money >= 100:
                        self.spawn_queue.append("crab")
                        self.spawn_cooldown = 45
                    elif self.money >= 200:
                        self.spawn_queue.append("octopus")
                        self.spawn_cooldown = 90
        
        # Process the spawn queue
        if self.spawn_queue and self.spawn_cooldown <= 0:
            alien_type = self.spawn_queue.pop(0)
            return self.spawn_alien(alien_type)
        
        return None

# Game class
class Game:
    def __init__(self):
        self.is_running = True
        self.game_over = False
        self.winner = None
        
        # Create game objects
        self.spaceship = Spaceship(SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT - 50)
        self.mothership = Mothership(SCREEN_WIDTH // 2 - 60, 20)
        
        # Lists to track game objects
        self.aliens = []
        self.bullets = []
        
        # Add some initial aliens
        for i in range(5):
            x = 50 + i * 100
            self.aliens.append(Squid(x, 100))
        
        for i in range(3):
            x = 100 + i * 150
            self.aliens.append(Crab(x, 150))
        
        self.aliens.append(Octopus(SCREEN_WIDTH // 2 - 20, 200))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                
                if not self.game_over:
                    if event.key == pygame.K_SPACE:
                        bullet = self.spaceship.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                    
                    # Upgrade keys
                    if event.key == pygame.K_1:
                        self.spaceship.purchase_upgrade("reload")
                    elif event.key == pygame.K_2:
                        self.spaceship.purchase_upgrade("health")
                    elif event.key == pygame.K_3:
                        self.spaceship.purchase_upgrade("speed")
                else:
                    # Restart game on Enter if game is over
                    if event.key == pygame.K_RETURN:
                        self.__init__()  # Reset the game
    
    def update(self):
        if self.game_over:
            return
        
        # Update player
        self.spaceship.update()
        
        # Update mothership
        self.mothership.update()
        
        # AI decision for mothership
        new_alien = self.mothership.ai_decision(self.spaceship, self.aliens)
        if new_alien:
            self.aliens.append(new_alien)
        
        # Update aliens
        for alien in self.aliens[:]:
            alien.update()
            
            # Check if aliens reached the spaceship
            if alien.y + alien.height >= self.spaceship.y:
                if alien.collides_with(self.spaceship):
                    self.spaceship.take_damage(alien.damage)
                    self.aliens.remove(alien)
                    continue
                
                # Octopus can deal tick damage when close
                if isinstance(alien, Octopus) and abs(alien.x - self.spaceship.x) < 100:
                    alien.start_ticking()
                    tick_damage = alien.update()
                    if tick_damage:
                        self.spaceship.take_damage(tick_damage)
            
            # Aliens can shoot
            bullet = alien.attack()
            if bullet:
                self.bullets.append(bullet)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            
            # Remove bullets that go off screen
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                continue
            
            # Check bullet collisions
            if bullet.is_player:  # Player bullets hitting aliens or mothership
                # Check if bullet hits the mothership
                if bullet.collides_with(self.mothership):
                    self.mothership.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
                    continue
                
                # Check if bullet hits aliens
                for alien in self.aliens[:]:
                    if bullet.collides_with(alien):
                        if alien.take_damage(bullet.damage):
                            # Alien destroyed, player gets money
                            self.spaceship.add_money(alien.cost)
                            self.aliens.remove(alien)
                        
                        self.bullets.remove(bullet)
                        break
            else:  # Enemy bullets hitting player
                if bullet.collides_with(self.spaceship):
                    self.spaceship.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
        
        # Check game over conditions
        if self.spaceship.health <= 0:
            self.game_over = True
            self.winner = "Mothership"
        
        if self.mothership.health <= 0:
            self.game_over = True
            self.winner = "Spaceship"
    
    def draw(self):
        # Clear the screen
        screen.fill(BLACK)
        
        # Draw mothership
        self.mothership.draw(screen)
        
        # Draw aliens
        for alien in self.aliens:
            alien.draw(screen)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # Draw spaceship
        self.spaceship.draw(screen)
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen if needed
        if self.game_over:
            self.draw_game_over()
        
        # Update the display
        pygame.display.flip()
    
    def draw_ui(self):
        # Health bars
        # Player health bar
        pygame.draw.rect(screen, RED, (10, SCREEN_HEIGHT - 30, 200, 20))
        pygame.draw.rect(screen, GREEN, (10, SCREEN_HEIGHT - 30, 200 * (self.spaceship.health / self.spaceship.max_health), 20))
        health_text = font_small.render(f"HP: {int(self.spaceship.health)}/{int(self.spaceship.max_health)}", True, WHITE)
        screen.blit(health_text, (15, SCREEN_HEIGHT - 28))
        
        # Mothership health bar
        pygame.draw.rect(screen, RED, (SCREEN_WIDTH - 210, 10, 200, 20))
        pygame.draw.rect(screen, PURPLE, (SCREEN_WIDTH - 210, 10, 200 * (self.mothership.health / self.mothership.max_health), 20))
        mothership_health_text = font_small.render(f"HP: {int(self.mothership.health)}/{int(self.mothership.max_health)}", True, WHITE)
        screen.blit(mothership_health_text, (SCREEN_WIDTH - 205, 12))
        
        # Money
        money_text = font_small.render(f"Money: ${int(self.spaceship.money)}", True, YELLOW)
        screen.blit(money_text, (10, SCREEN_HEIGHT - 60))
        
        # Upgrades
        reload_text = font_small.render(f"1: Upgrade Reload (${int(100 * self.spaceship.reload_speed)})", True, CYAN)
        health_text = font_small.render(f"2: Upgrade Health (${int(self.spaceship.max_health * 0.5)})", True, CYAN)
        speed_text = font_small.render(f"3: Upgrade Speed (${int(self.spaceship.movement_speed * 30)})", True, CYAN)
        
        screen.blit(reload_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 90))
        screen.blit(health_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 60))
        screen.blit(speed_text, (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 30))
        
        # Stats
        stats_text = font_small.render(f"Reload: {self.spaceship.reload_speed:.1f}x  Speed: {self.spaceship.movement_speed}", True, WHITE)
        screen.blit(stats_text, (10, SCREEN_HEIGHT - 90))
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = font_large.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        
        # Winner text
        winner_text = font_medium.render(f"{self.winner} wins!", True, WHITE)
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Restart text
        restart_text = font_medium.render("Press ENTER to restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

# Main game function
def main():
    game = Game()
    
    # Main game loop
    while game.is_running:
        # Handle events
        game.handle_events()
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw()
        
        # Cap the frame rate
        clock.tick(FPS)
    
    # Quit pygame
    pygame.quit()
    sys.exit()

# Run the game
if __name__ == "__main__":
    main()