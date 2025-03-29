import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Get the screen info for fullscreen mode
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Create the screen (fullscreen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Invaders: Defender vs Mothership")
clock = pygame.time.Clock()

# Load game assets with scaling for fullscreen
# Scale factor based on screen resolution
SCALE_FACTOR = min(SCREEN_WIDTH / 1920, SCREEN_HEIGHT / 1080) * 1.5  # Adjust multiplier as needed

def create_spaceship_surface():
    size = (int(60 * SCALE_FACTOR), int(45 * SCALE_FACTOR))
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.polygon(surf, GREEN, [(size[0]//2, 0), (0, size[1]), (size[0], size[1])])
    return surf

def create_mothership_surface():
    width = int(180 * SCALE_FACTOR)
    height = int(60 * SCALE_FACTOR)
    surf = pygame.Surface((width, height + int(30 * SCALE_FACTOR)), pygame.SRCALPHA)
    pygame.draw.rect(surf, PURPLE, (0, 0, width, height))
    pygame.draw.polygon(surf, PURPLE, [(0, height), (width, height), (width//2, height + int(30 * SCALE_FACTOR))])
    return surf

def create_squid_surface():
    size = int(30 * SCALE_FACTOR)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.rect(surf, BLUE, (0, size//2, size, size//2))
    pygame.draw.rect(surf, BLUE, (size//4, 0, size//2, size//2))
    pygame.draw.rect(surf, BLUE, (0, 0, size//4, size//4))
    pygame.draw.rect(surf, BLUE, (size - size//4, 0, size//4, size//4))
    return surf

def create_crab_surface():
    size = int(45 * SCALE_FACTOR)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, RED, (size//2, size//2), size//3)
    pygame.draw.rect(surf, RED, (size//10, size//3, size - size//5, size//3))
    pygame.draw.rect(surf, RED, (0, size//6, size//6, size//6))
    pygame.draw.rect(surf, RED, (size - size//6, size//6, size//6, size//6))
    pygame.draw.rect(surf, RED, (0, size - size//3, size//6, size//6))
    pygame.draw.rect(surf, RED, (size - size//6, size - size//3, size//6, size//6))
    return surf

def create_octopus_surface():
    size = int(60 * SCALE_FACTOR)
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surf, YELLOW, (size//2, size//2), size//3)
    for i in range(8):
        angle = math.pi * i / 4
        x = size//2 + (size//2 - 5) * math.cos(angle)
        y = size//2 + (size//2 - 5) * math.sin(angle)
        pygame.draw.circle(surf, YELLOW, (int(x), int(y)), size//10)
    return surf

def create_bullet_surface(color):
    width = int(6 * SCALE_FACTOR)
    height = int(15 * SCALE_FACTOR)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, width, height))
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
        self.max_health = health  # Store max health for health bar
        self.speed = speed
        self.damage = damage
        self.cost = cost
        self.direction = 1  # 1 for right, -1 for left
        self.y_offset = 0
    
    def move(self):
        self.x += self.speed * self.direction
        
        # Classic Space Invaders movement: move sideways until hitting edge, then down
        # Increased downward movement to traverse the board faster
        if self.x <= 0:
            self.direction = 1
            self.y += int(60 * SCALE_FACTOR)  # Increased from 20 to make path shorter
        elif self.x + self.width >= SCREEN_WIDTH:
            self.direction = -1
            self.y += int(60 * SCALE_FACTOR)  # Increased from 20 to make path shorter
        
        super().update()
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0
    
    def attack(self):
        # Default is no attack
        return None
        
    def draw(self, surface):
        # Draw the alien image
        super().draw(surface)
        
        # Draw health bar
        health_bar_width = self.width
        health_bar_height = int(5 * SCALE_FACTOR)
        border_color = WHITE
        
        # Health bar background (empty)
        pygame.draw.rect(surface, RED, (
            self.x, 
            self.y - health_bar_height - int(2 * SCALE_FACTOR), 
            health_bar_width, 
            health_bar_height
        ))
        
        # Health bar fill (current health)
        current_health_width = int(health_bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, GREEN, (
            self.x, 
            self.y - health_bar_height - int(2 * SCALE_FACTOR), 
            current_health_width, 
            health_bar_height
        ))
        
        # Health bar border
        pygame.draw.rect(surface, border_color, (
            self.x, 
            self.y - health_bar_height - int(2 * SCALE_FACTOR), 
            health_bar_width, 
            health_bar_height
        ), 1)

# Squid alien (kamikaze)
class Squid(Alien):
    def __init__(self, x, y):
        size = int(30 * SCALE_FACTOR)
        super().__init__(x, y, size, size, 1, 2 * SCALE_FACTOR, 10, 50, squid_img)
        self.kamikaze_mode = False
        self.kamikaze_speed = 3 * SCALE_FACTOR
        self.target_x = 0
        self.target_y = 0
        self.direction_timer = 0
        self.direction_change_interval = 20
    
    def move(self):
        # Check if we're close to the bottom of the screen to enter kamikaze mode
        if self.y > SCREEN_HEIGHT * 0.6 and not self.kamikaze_mode:
            self.kamikaze_mode = True
            
        if not self.kamikaze_mode:
            # Standard alien movement pattern
            self.x += self.speed * self.direction
            
            # Keep in bounds
            if self.x <= 0:
                self.direction = 1
                self.y += int(60 * SCALE_FACTOR)
            elif self.x + self.width >= SCREEN_WIDTH:
                self.direction = -1
                self.y += int(60 * SCALE_FACTOR)
        else:
            # Kamikaze mode - rapid movement toward spaceship
            # We'll update the target position periodically to follow the spaceship
            self.direction_timer += 1
            if self.direction_timer >= self.direction_change_interval:
                self.direction_timer = 0
                # This will be set in Game.update() to point to the current spaceship position
                
            # Move toward the target (if it's been set)
            if self.target_x != 0:
                dx = self.target_x - (self.x + self.width/2)
                dy = self.target_y - (self.y + self.height/2)
                distance = max(1, (dx**2 + dy**2)**0.5)  # Avoid division by zero
                
                # Normalize and multiply by speed
                self.x += (dx / distance) * self.kamikaze_speed
                self.y += (dy / distance) * self.kamikaze_speed
        
        super().update()
        
    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

# Crab alien (shooter)
class Crab(Alien):
    def __init__(self, x, y):
        size = int(45 * SCALE_FACTOR)
        super().__init__(x, y, size, size, 3, 1 * SCALE_FACTOR, 5, 100, crab_img)
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
            bullet_speed = int(5 * SCALE_FACTOR)
            return Bullet(self.x + self.width // 2, self.y + self.height, bullet_speed, self.bullet_damage, self, False)
        return None

# Octopus alien (tank)
class Octopus(Alien):
    def __init__(self, x, y):
        size = int(60 * SCALE_FACTOR)
        super().__init__(x, y, size, size, 8, 0.5 * SCALE_FACTOR, 3, 200, octopus_img)
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
        size_w = int(60 * SCALE_FACTOR)
        size_h = int(45 * SCALE_FACTOR)
        super().__init__(x, y, size_w, size_h, spaceship_img)
        self.health = 100
        self.max_health = 100
        self.movement_speed = 5 * SCALE_FACTOR
        self.reload_speed = 1
        self.reload_cooldown = 0
        self.money = 100
        self.bullet_damage = 1
        self.autofire = False  # Added autofire flag
        self.autofire_cooldown = 0
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.movement_speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.movement_speed
        
        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
            
        # Handle autofire
        if self.autofire:
            self.autofire_cooldown -= 1
            if self.autofire_cooldown <= 0:
                self.autofire_cooldown = int(60 / self.reload_speed)
                return self.shoot()
        
        super().update()
        return None  # Return None if no bullet was fired
    
    def shoot(self):
        if self.reload_cooldown <= 0:
            self.reload_cooldown = int(60 / self.reload_speed)
            bullet_speed = int(10 * SCALE_FACTOR)
            return Bullet(self.x + self.width // 2 - int(3 * SCALE_FACTOR), self.y, bullet_speed, self.bullet_damage, self)
        return None
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        return self.health <= 0
    
    def purchase_upgrade(self, upgrade_type):
        if upgrade_type == "reload":
            cost = int(100 * self.reload_speed)
            if self.money >= cost:  # Removed the cap
                self.money -= cost
                self.reload_speed += 0.5
                return True
        elif upgrade_type == "health":
            cost = int(self.max_health * 0.5)
            if self.money >= cost:  # Removed the cap
                self.money -= cost
                self.max_health += 50
                self.health = min(self.health + 50, self.max_health)
                return True
        elif upgrade_type == "speed":
            cost = int((self.movement_speed / SCALE_FACTOR) * 30)
            if self.money >= cost:  # Removed the cap
                self.money -= cost
                self.movement_speed += 1 * SCALE_FACTOR
                return True
        return False
    
    def toggle_autofire(self):
        self.autofire = not self.autofire
        return self.autofire
    
    def add_money(self, amount):
        self.money += amount

# Mothership (player 2)
class Mothership(GameObject):
    def __init__(self, x, y):
        width = int(180 * SCALE_FACTOR)
        height = int(90 * SCALE_FACTOR)
        super().__init__(x, y, width, height, mothership_img)
        self.health = 500
        self.max_health = 500
        self.money = 200
        self.money_growth_rate = 50  # Increased for discrete increments
        self.growth_factor = 0.1
        self.time = 0
        self.money_timer = 0
        self.money_interval = 60  # Add money every second (60 frames)
        self.spawn_cooldown = 0
        self.spawn_cooldown_time = 30  # Half a second cooldown between spawns
        self.selected_alien = "squid"  # Default selection
        
        # Position for alien preview
        self.preview_positions = {
            "squid": (int(SCREEN_WIDTH * 0.1), int(60 * SCALE_FACTOR)),
            "crab": (int(SCREEN_WIDTH * 0.2), int(60 * SCALE_FACTOR)),
            "octopus": (int(SCREEN_WIDTH * 0.3), int(60 * SCALE_FACTOR))
        }
        
        # Costs for each alien type
        self.alien_costs = {
            "squid": 50,
            "crab": 100,
            "octopus": 200
        }
    
    def update(self):
        self.time += 1
        
        # Earn money at discrete intervals with exponential growth
        self.money_timer += 1
        if self.money_timer >= self.money_interval:
            self.money_timer = 0
            growth_amount = self.money_growth_rate * (1 + self.growth_factor * (self.time / 600))
            self.money += int(growth_amount)
        
        # Update spawn cooldown
        if self.spawn_cooldown > 0:
            self.spawn_cooldown -= 1
        
        super().update()
    
    def spawn_alien(self, x):
        # Check cooldown first
        if self.spawn_cooldown > 0:
            return None
            
        # Spawn at the provided x coordinate
        y = self.y + self.height
        
        # Check if we have enough money
        if self.selected_alien == "squid" and self.money >= 50:
            self.money -= 50
            self.spawn_cooldown = self.spawn_cooldown_time
            return Squid(x, y)
        elif self.selected_alien == "crab" and self.money >= 100:
            self.money -= 100
            self.spawn_cooldown = self.spawn_cooldown_time
            return Crab(x, y)
        elif self.selected_alien == "octopus" and self.money >= 200:
            self.money -= 200
            self.spawn_cooldown = self.spawn_cooldown_time
            return Octopus(x, y)
        
        return None
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:  # Fixed typo: 'a' -> '0'
            self.health = 0
        return self.health <= 0
    
    def select_next_alien(self):
        if self.selected_alien == "squid":
            self.selected_alien = "crab"
        elif self.selected_alien == "crab":
            self.selected_alien = "octopus"
        elif self.selected_alien == "octopus":
            self.selected_alien = "squid"
    
    def select_prev_alien(self):
        if self.selected_alien == "squid":
            self.selected_alien = "octopus"
        elif self.selected_alien == "crab":
            self.selected_alien = "squid"
        elif self.selected_alien == "octopus":
            self.selected_alien = "crab"
    
    def draw(self, surface):
        # Draw the mothership
        super().draw(surface)
        
        # Draw health bar
        health_bar_width = self.width
        health_bar_height = int(10 * SCALE_FACTOR)
        
        # Health bar background (empty)
        pygame.draw.rect(surface, RED, (
            self.x, 
            self.y - health_bar_height - int(5 * SCALE_FACTOR), 
            health_bar_width, 
            health_bar_height
        ))
        
        # Health bar fill (current health)
        current_health_width = int(health_bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, PURPLE, (
            self.x, 
            self.y - health_bar_height - int(5 * SCALE_FACTOR), 
            current_health_width, 
            health_bar_height
        ))
        
        # Draw money
        money_font = pygame.font.SysFont('Arial', int(24 * SCALE_FACTOR))
        money_text = money_font.render(f"Money: ${int(self.money)}", True, YELLOW)
        surface.blit(money_text, (int(10 * SCALE_FACTOR), int(10 * SCALE_FACTOR)))

# Game class
class Game:
    def __init__(self):
        self.is_running = True
        self.game_over = False
        self.winner = None
        self.paused = False
        self.help_screen = False
        
        # Create game objects
        spaceship_x = SCREEN_WIDTH // 2 - int(30 * SCALE_FACTOR)
        spaceship_y = SCREEN_HEIGHT - int(60 * SCALE_FACTOR)
        mothership_x = SCREEN_WIDTH // 2 - int(90 * SCALE_FACTOR)
        mothership_y = int(20 * SCALE_FACTOR)
        
        self.spaceship = Spaceship(spaceship_x, spaceship_y)
        self.mothership = Mothership(mothership_x, mothership_y)
        
        # Lists to track game objects
        self.aliens = []
        self.bullets = []
        
        # Mouse position for mothership player
        self.mouse_pos = (0, 0)
        
        # Preview images
        self.squid_preview = squid_img
        self.crab_preview = crab_img
        self.octopus_preview = octopus_img
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                
                if event.key == pygame.K_g:
                    self.help_screen = True
                    self.paused = True
                
                if not self.paused and not self.game_over:
                    # Spaceship player controls
                    if event.key == pygame.K_SPACE:
                        bullet = self.spaceship.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                    
                    # Spaceship upgrade keys
                    if event.key == pygame.K_1:
                        self.spaceship.purchase_upgrade("reload")
                    elif event.key == pygame.K_2:
                        self.spaceship.purchase_upgrade("health")
                    elif event.key == pygame.K_3:
                        self.spaceship.purchase_upgrade("speed")
                    
                    # Toggle autofire
                    if event.key == pygame.K_f:
                        self.spaceship.toggle_autofire()
                    
                    # Mothership player controls
                    if event.key == pygame.K_q:
                        self.mothership.select_prev_alien()
                    elif event.key == pygame.K_e:
                        self.mothership.select_next_alien()
                
                elif self.game_over:
                    # Restart game on Enter if game is over
                    if event.key == pygame.K_RETURN:
                        self.__init__()  # Reset the game
            
            # Key releases
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_g:
                    self.help_screen = False
                    self.paused = False
            
            # Mouse position tracking
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            
            # Mouse click for spawning aliens
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.paused:
                if event.button == 1:  # Left mouse button
                    # Check if we're in the top half of the screen (mothership territory)
                    if event.pos[1] < SCREEN_HEIGHT // 2:
                        new_alien = self.mothership.spawn_alien(event.pos[0])
                        if new_alien:
                            self.aliens.append(new_alien)
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        # Update player
        self.spaceship.update()
        
        # Check for autofire
        auto_bullet = self.spaceship.update()
        if auto_bullet:
            self.bullets.append(auto_bullet)
        
        # Update mothership
        self.mothership.update()
        
        # Update aliens
        for alien in self.aliens[:]:
            # Set target for squids if they're in kamikaze mode
            if isinstance(alien, Squid) and alien.kamikaze_mode:
                alien.set_target(self.spaceship.x + self.spaceship.width/2, 
                                self.spaceship.y + self.spaceship.height/2)
            
            alien.update()
            
            # Check if aliens reached the spaceship
            if alien.y + alien.height >= self.spaceship.y:
                if alien.collides_with(self.spaceship):
                    self.spaceship.take_damage(alien.damage)
                    self.aliens.remove(alien)
                    continue
                
                # Octopus can deal tick damage when close
                if isinstance(alien, Octopus) and abs(alien.x - self.spaceship.x) < int(100 * SCALE_FACTOR):
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
            else:  # Enemy bullets hitting player or other aliens (friendly fire)
                # Check if bullet hits the player
                if bullet.collides_with(self.spaceship):
                    self.spaceship.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
                    continue
                
                # Check for friendly fire - aliens hitting other aliens
                for alien in self.aliens[:]:
                    # Don't check collision with the alien that fired the bullet
                    if alien != bullet.source and bullet.collides_with(alien):
                        if alien.take_damage(bullet.damage):
                            self.aliens.remove(alien)
                        
                        self.bullets.remove(bullet)
                        break
        
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
        
        if self.help_screen:
            self.draw_help_screen()
            return
        
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
    
    def draw_help_screen(self):
        # Draw help screen with all game instructions
        # Fill background with semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Adjust font sizes for screen resolution
        title_font = pygame.font.SysFont('Arial', int(40 * SCALE_FACTOR), bold=True)
        header_font = pygame.font.SysFont('Arial', int(30 * SCALE_FACTOR), bold=True)
        text_font = pygame.font.SysFont('Arial', int(20 * SCALE_FACTOR))
        
        # Title
        title = title_font.render("SPACE INVADERS: DEFENDER VS MOTHERSHIP", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, int(50 * SCALE_FACTOR)))
        
        # Instructions sections
        y_pos = int(120 * SCALE_FACTOR)
        line_height = int(26 * SCALE_FACTOR)
        
        # Game objective
        objective_header = header_font.render("Game Objective:", True, YELLOW)
        screen.blit(objective_header, (int(50 * SCALE_FACTOR), y_pos))
        y_pos += line_height * 1.5
        
        objective_text = [
            "This is a two-player competitive game based on Space Invaders.",
            "Player 1 (Mothership): Spawn aliens to defeat the Spaceship.",
            "Player 2 (Spaceship): Defend Earth by shooting aliens and the Mothership."
        ]
        
        for line in objective_text:
            text = text_font.render(line, True, WHITE)
            screen.blit(text, (int(70 * SCALE_FACTOR), y_pos))
            y_pos += line_height
        
        y_pos += line_height
        
        # Player 1 controls
        p1_header = header_font.render("Player 1 (Mothership) Controls:", True, PURPLE)
        screen.blit(p1_header, (int(50 * SCALE_FACTOR), y_pos))
        y_pos += line_height * 1.5
        
        p1_controls = [
            "Q/E: Select different alien types",
            "Left Mouse Click: Spawn selected alien at the clicked location",
            "Earn money over time to spawn more aliens",
            "Alien Types:",
            "  - Squid (Blue): Fast kamikaze aliens that charge at the Spaceship",
            "  - Crab (Red): Medium-health aliens that shoot at the Spaceship",
            "  - Octopus (Yellow): Tank aliens with high health that deal continuous damage"
        ]
        
        for line in p1_controls:
            text = text_font.render(line, True, WHITE)
            screen.blit(text, (int(70 * SCALE_FACTOR), y_pos))
            y_pos += line_height
        
        y_pos += line_height
        
        # Player 2 controls
        p2_header = header_font.render("Player 2 (Spaceship) Controls:", True, GREEN)
        screen.blit(p2_header, (int(50 * SCALE_FACTOR), y_pos))
        y_pos += line_height * 1.5
        
        p2_controls = [
            "Left/Right Arrow Keys: Move the spaceship",
            "Space: Shoot",
            "F: Toggle auto-fire",
            "1: Upgrade reload speed",
            "2: Upgrade max health",
            "3: Upgrade movement speed",
            "Earn money by destroying aliens"
        ]
        
        for line in p2_controls:
            text = text_font.render(line, True, WHITE)
            screen.blit(text, (int(70 * SCALE_FACTOR), y_pos))
            y_pos += line_height
        
        y_pos += line_height
        
        # General controls
        gen_header = header_font.render("General Controls:", True, CYAN)
        screen.blit(gen_header, (int(50 * SCALE_FACTOR), y_pos))
        y_pos += line_height * 1.5
        
        gen_controls = [
            "G: Show/hide this help screen",
            "Escape: Quit game",
            "Enter: Restart game (after game over)"
        ]
        
        for line in gen_controls:
            text = text_font.render(line, True, WHITE)
            screen.blit(text, (int(70 * SCALE_FACTOR), y_pos))
            y_pos += line_height
        
        # Press G instruction at bottom
        continue_text = text_font.render("Release G to continue playing", True, YELLOW)
        screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT - int(50 * SCALE_FACTOR)))
        
        pygame.display.flip()
    
    def draw_ui(self):
        # Adjust font sizes for scale
        font_small = pygame.font.SysFont('Arial', int(18 * SCALE_FACTOR))
        font_medium = pygame.font.SysFont('Arial', int(22 * SCALE_FACTOR))
        
        # Health bars
        # Player health bar
        bar_height = int(20 * SCALE_FACTOR)
        bar_width = int(200 * SCALE_FACTOR)
        margin = int(10 * SCALE_FACTOR)
        
        # Player health bar
        pygame.draw.rect(screen, RED, (margin, SCREEN_HEIGHT - bar_height - margin, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (margin, SCREEN_HEIGHT - bar_height - margin, 
                                        bar_width * (self.spaceship.health / self.spaceship.max_health), bar_height))
        health_text = font_small.render(f"HP: {int(self.spaceship.health)}/{int(self.spaceship.max_health)}", True, WHITE)
        screen.blit(health_text, (margin + 5, SCREEN_HEIGHT - bar_height - margin + 2))
        
        # Mothership health bar (already drawn in Mothership.draw method)
        
        # Player Money
        money_text = font_small.render(f"Money: ${int(self.spaceship.money)}", True, YELLOW)
        screen.blit(money_text, (margin, SCREEN_HEIGHT - bar_height * 2 - margin * 2))
        
        # Player Upgrades
        reload_text = font_small.render(f"1: Upgrade Reload (${int(100 * self.spaceship.reload_speed)})", True, CYAN)
        health_text = font_small.render(f"2: Upgrade Health (${int(self.spaceship.max_health * 0.5)})", True, CYAN)
        speed_text = font_small.render(f"3: Upgrade Speed (${int((self.spaceship.movement_speed / SCALE_FACTOR) * 30)})", True, CYAN)
        
        screen.blit(reload_text, (SCREEN_WIDTH - bar_width * 1.5, SCREEN_HEIGHT - bar_height * 3 - margin * 3))
        screen.blit(health_text, (SCREEN_WIDTH - bar_width * 1.5, SCREEN_HEIGHT - bar_height * 2 - margin * 2))
        screen.blit(speed_text, (SCREEN_WIDTH - bar_width * 1.5, SCREEN_HEIGHT - bar_height - margin))
        
        # Player Stats
        stats_text = font_small.render(f"Reload: {self.spaceship.reload_speed:.1f}x  Speed: {int(self.spaceship.movement_speed / SCALE_FACTOR)}  Autofire: {'ON' if self.spaceship.autofire else 'OFF'}", True, WHITE)
        screen.blit(stats_text, (margin, SCREEN_HEIGHT - bar_height * 3 - margin * 3))
        
        # Minimal instructions reminder
        help_text = font_small.render("Press G for help", True, YELLOW)
        screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, SCREEN_HEIGHT - margin * 2))
        
        # Mothership player UI elements
        # Selected alien indicator and costs
        squid_cost = font_small.render(f"Squid: $50", True, BLUE)
        crab_cost = font_small.render(f"Crab: $100", True, RED)
        octopus_cost = font_small.render(f"Octopus: $200", True, YELLOW)
        
        # Draw selection boxes
        box_size = int(30 * SCALE_FACTOR)
        box_margin = int(15 * SCALE_FACTOR)
        box_y = margin * 5
        
        # Squid selection
        pygame.draw.rect(screen, WHITE if self.mothership.selected_alien == "squid" else BLUE, 
                        (margin, box_y, box_size, box_size), 
                        2 if self.mothership.selected_alien == "squid" else 1)
        screen.blit(squid_img, (margin + 5, box_y + 5))
        screen.blit(squid_cost, (margin, box_y + box_size + 5))
        
        # Crab selection
        pygame.draw.rect(screen, WHITE if self.mothership.selected_alien == "crab" else RED, 
                        (margin + box_size + box_margin, box_y, box_size, box_size), 
                        2 if self.mothership.selected_alien == "crab" else 1)
        screen.blit(crab_img, (margin + box_size + box_margin + 5, box_y + 5))
        screen.blit(crab_cost, (margin + box_size + box_margin, box_y + box_size + 5))
        
        # Octopus selection
        pygame.draw.rect(screen, WHITE if self.mothership.selected_alien == "octopus" else YELLOW, 
                        (margin + 2 * (box_size + box_margin), box_y, box_size, box_size), 
                        2 if self.mothership.selected_alien == "octopus" else 1)
        screen.blit(octopus_img, (margin + 2 * (box_size + box_margin) + 5, box_y + 5))
        screen.blit(octopus_cost, (margin + 2 * (box_size + box_margin), box_y + box_size + 5))
    
    def draw_game_over(self):
        # Adjust font sizes for scale
        font_large = pygame.font.SysFont('Arial', int(48 * SCALE_FACTOR))
        font_medium = pygame.font.SysFont('Arial', int(32 * SCALE_FACTOR))
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = font_large.render("GAME OVER", True, WHITE)
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - int(50 * SCALE_FACTOR)))
        
        # Winner text
        winner_text = font_medium.render(f"{self.winner} wins!", True, WHITE)
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        # Restart text
        restart_text = font_medium.render("Press ENTER to restart", True, WHITE)
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + int(50 * SCALE_FACTOR)))

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