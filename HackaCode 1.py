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

# Scale factor based on screen resolution
SCALE_FACTOR = min(SCREEN_WIDTH / 1920, SCREEN_HEIGHT / 1080) * 1.5  # Adjust multiplier as needed

# Load game assets
def load_image(filename, size):
    try:
        img = pygame.image.load(f"assets/{filename}")
        return pygame.transform.scale(img, size)
    except:
        # Create a placeholder surface if image loading fails
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, WHITE, (0, 0, size[0], size[1]), 1)
        font = pygame.font.SysFont('Arial', 12)
        text = font.render(filename, True, WHITE)
        surf.blit(text, (size[0]//2 - text.get_width()//2, size[1]//2 - text.get_height()//2))
        return surf

# Load images with proper scaling
def load_game_assets():
    spaceship_size = (int(60 * SCALE_FACTOR), int(45 * SCALE_FACTOR))
    mothership_size = (int(180 * SCALE_FACTOR), int(90 * SCALE_FACTOR))
    squid_size = (int(30 * SCALE_FACTOR), int(30 * SCALE_FACTOR))
    crab_size = (int(45 * SCALE_FACTOR), int(45 * SCALE_FACTOR))
    octopus_size = (int(60 * SCALE_FACTOR), int(60 * SCALE_FACTOR))
    
    assets = {
        'spaceship': load_image("spaceship.png", spaceship_size),
        'mothership': load_image("mothership.png", mothership_size),
        'squid': load_image("squid.png", squid_size),
        'crab': load_image("crab.png", crab_size),
        'octopus': load_image("octopus.png", octopus_size)
    }
    
    return assets

# Create simple surfaces as fallbacks if images can't be loaded
def create_bullet_surface(color):
    width = int(6 * SCALE_FACTOR)
    height = int(15 * SCALE_FACTOR)
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, width, height))
    return surf

# Load assets
game_assets = load_game_assets()

# Create bullet surfaces
player_bullet_surface = create_bullet_surface(GREEN)
enemy_bullet_surface = create_bullet_surface(RED)

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
        # Use simple surfaces instead of PNGs for bullets
        image = player_bullet_surface if is_player else enemy_bullet_surface
        width = int(6 * SCALE_FACTOR)
        height = int(15 * SCALE_FACTOR)
        super().__init__(x, y, width, height, image)
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
        super().__init__(x, y, size, size, 1, 2 * SCALE_FACTOR, 10, 50, game_assets['squid'])
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
        super().__init__(x, y, size, size, 3, 1 * SCALE_FACTOR, 5, 100, game_assets['crab'])
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
        super().__init__(x, y, size, size, 8, 0.5 * SCALE_FACTOR, 3, 200, game_assets['octopus'])
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
        super().__init__(x, y, size_w, size_h, game_assets['spaceship'])
        self.health = 100
        self.max_health = 100
        self.movement_speed = 5 * SCALE_FACTOR
        self.reload_speed = 1
        self.reload_cooldown = 0
        self.money = 100
        self.bullet_damage = 1  # Starting damage
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
            if self.money >= cost:
                self.money -= cost
                self.reload_speed += 0.5
                return True
        elif upgrade_type == "health":
            cost = int(self.max_health * 0.5)
            if self.money >= cost:
                self.money -= cost
                self.max_health += 50
                self.health = min(self.health + 50, self.max_health)
                return True
        elif upgrade_type == "damage":  # Changed from "speed" to "damage"
            cost = int(self.bullet_damage * 50)  # Cost based on current damage
            if self.money >= cost:
                self.money -= cost
                self.bullet_damage += 1  # Increase bullet damage by 1
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
        super().__init__(x, y, width, height, game_assets['mothership'])
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
        if self.health < 0:
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
        self.start_screen = True  # Added start screen flag
        
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
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                
                if event.key == pygame.K_g and not self.start_screen:
                    self.help_screen = True
                    self.paused = True
                
                # Start screen controls
                if self.start_screen:
                    if event.key == pygame.K_RETURN:
                        self.start_screen = False
                
                # Game over controls
                elif self.game_over:
                    # Restart game on Enter if game is over
                    if event.key == pygame.K_RETURN:
                        self.__init__()  # Reset the game
                        self.start_screen = False  # Skip start screen on restart
                
                # Game controls
                elif not self.paused and not self.game_over:
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
                        self.spaceship.purchase_upgrade("damage")  # Changed from "speed" to "damage"
                    
                    # Toggle autofire
                    if event.key == pygame.K_f:
                        self.spaceship.toggle_autofire()
                    
                    # Mothership player controls
                    if event.key == pygame.K_q:
                        self.mothership.select_prev_alien()
                    elif event.key == pygame.K_e:
                        self.mothership.select_next_alien()
            
            # Key releases
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_g:
                    self.help_screen = False
                    self.paused = False
            
            # Mouse position tracking
            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            
            # Mouse click for spawning aliens
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over and not self.paused and not self.start_screen:
                if event.button == 1:  # Left mouse button
                    # Check if we're in the top half of the screen (mothership territory)
                    if event.pos[1] < SCREEN_HEIGHT // 2:
                        new_alien = self.mothership.spawn_alien(event.pos[0])
                        if new_alien:
                            self.aliens.append(new_alien)
    
    def update(self):
        if self.game_over or self.paused or self.start_screen:
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
        
        # Check which screen to draw
        if self.start_screen:
            self.draw_start_screen()
        elif self.help_screen:
            self.draw_help_screen()
        else:
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
    
    def draw_start_screen(self):
        # Draw start menu screen
        # Fill background with starry background
        screen.fill(BLACK)
        
        # Draw stars
        for _ in range(200):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)
        
        # Draw title
        title_font = pygame.font.SysFont('Arial', int(60 * SCALE_FACTOR), bold=True)
        title_text = title_font.render("SPACE INVADERS", True, WHITE)
        subtitle_text = title_font.render("DEFENDER VS MOTHERSHIP", True, PURPLE)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, int(SCREEN_HEIGHT * 0.2)))
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, int(SCREEN_HEIGHT * 0.3)))
        
        # Draw instructions
        instruction_font = pygame.font.SysFont('Arial', int(28 * SCALE_FACTOR))
        instruction_text = instruction_font.render("Press ENTER to Start", True, GREEN)
        help_text = instruction_font.render("Press G during the game for help", True, YELLOW)
        
        screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, int(SCREEN_HEIGHT * 0.6)))
        screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, int(SCREEN_HEIGHT * 0.65)))
        
        # Draw game description
        desc_font = pygame.font.SysFont('Arial', int(20 * SCALE_FACTOR))
        desc1 = desc_font.render("Player 1: Control the Spaceship and defend Earth", True, CYAN)
        desc2 = desc_font.render("Player 2: Control the Mothership and invade Earth", True, RED)
        
        screen.blit(desc1, (SCREEN_WIDTH // 2 - desc1.get_width() // 2, int(SCREEN_HEIGHT * 0.75)))
        screen.blit(desc2, (SCREEN_WIDTH // 2 - desc2.get_width() // 2, int(SCREEN_HEIGHT * 0.78)))
    
    def draw_help_screen(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Create a help box with margin
        margin = int(50 * SCALE_FACTOR)
        help_box = pygame.Rect(margin, margin, SCREEN_WIDTH - 2 * margin, SCREEN_HEIGHT - 2 * margin)
        pygame.draw.rect(screen, BLACK, help_box)
        pygame.draw.rect(screen, WHITE, help_box, 3)
        
        # Title
        title_font = pygame.font.SysFont('Arial', int(40 * SCALE_FACTOR), bold=True)
        title_text = title_font.render("GAME CONTROLS", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, margin + int(20 * SCALE_FACTOR)))
        
        # Help content
        help_font = pygame.font.SysFont('Arial', int(20 * SCALE_FACTOR))
        line_height = int(30 * SCALE_FACTOR)
        start_y = margin + int(80 * SCALE_FACTOR)
        
        help_lines = [
            "Spaceship Controls:",
            "- Arrow Keys: Move left/right",
            "- Space: Shoot",
            "- F: Toggle autofire",
            "- 1: Upgrade reload speed",
            "- 2: Upgrade health",
            "- 3: Upgrade bullet damage",  # Updated to reflect damage upgrade
            "",
            "Mothership Controls:",
            "- Mouse: Click to spawn aliens",
            "- Q/E: Select previous/next alien type",
            "",
            "Game Controls:",
            "- ESC: Quit game",
            "- G: Show/hide this help screen",
            "",
            "Hold G to keep help visible. Release to continue playing."
        ]
        
        for i, line in enumerate(help_lines):
            text = help_font.render(line, True, WHITE)
            screen.blit(text, (margin + int(20 * SCALE_FACTOR), start_y + i * line_height))
    
    def draw_ui(self):
        # Draw Mothership stats at top-left
        mothership_money_text = font_medium.render(f"Money: ${int(self.mothership.money)}", True, YELLOW)
        screen.blit(mothership_money_text, (int(10 * SCALE_FACTOR), int(10 * SCALE_FACTOR)))
        
        # Draw selected alien indicators (colored rectangles)
        alien_size = int(30 * SCALE_FACTOR)
        alien_spacing = int(10 * SCALE_FACTOR)
        alien_y = int(60 * SCALE_FACTOR)
        
        # Squid indicator (blue)
        squid_rect = pygame.Rect(int(10 * SCALE_FACTOR), alien_y, alien_size, alien_size)
        pygame.draw.rect(screen, BLUE, squid_rect)
        if self.mothership.selected_alien == "squid":
            pygame.draw.rect(screen, WHITE, squid_rect, 2)  # Highlight selected
        
        # Crab indicator (red)
        crab_rect = pygame.Rect(int(10 * SCALE_FACTOR) + alien_size + alien_spacing, alien_y, alien_size, alien_size)
        pygame.draw.rect(screen, RED, crab_rect)
        if self.mothership.selected_alien == "crab":
            pygame.draw.rect(screen, WHITE, crab_rect, 2)  # Highlight selected
        
        # Octopus indicator (yellow)
        octopus_rect = pygame.Rect(int(10 * SCALE_FACTOR) + (alien_size + alien_spacing) * 2, alien_y, alien_size, alien_size)
        pygame.draw.rect(screen, YELLOW, octopus_rect)
        if self.mothership.selected_alien == "octopus":
            pygame.draw.rect(screen, WHITE, octopus_rect, 2)  # Highlight selected
        
        # Draw alien cost text
        alien_cost_font = pygame.font.SysFont('Arial', int(16 * SCALE_FACTOR))
        alien_cost_text = alien_cost_font.render(f"Cost: ${self.mothership.alien_costs[self.mothership.selected_alien]}", True, YELLOW)
        screen.blit(alien_cost_text, (int(10 * SCALE_FACTOR) + (alien_size + alien_spacing) * 3, alien_y + alien_size//2 - alien_cost_text.get_height()//2))
        
        # Draw Mothership health bar (purple) at top-right
        mothership_health_width = int(200 * SCALE_FACTOR)
        mothership_health_height = int(40 * SCALE_FACTOR)
        mothership_health_x = SCREEN_WIDTH - mothership_health_width - int(10 * SCALE_FACTOR)
        mothership_health_y = int(10 * SCALE_FACTOR)
        
        # Draw mothership health bar with trapezoid shape
        points = [
            (mothership_health_x, mothership_health_y),
            (mothership_health_x + mothership_health_width, mothership_health_y),
            (mothership_health_x + mothership_health_width - int(20 * SCALE_FACTOR), mothership_health_y + mothership_health_height),
            (mothership_health_x + int(20 * SCALE_FACTOR), mothership_health_y + mothership_health_height)
        ]
        
        # Draw health bar background
        pygame.draw.polygon(screen, (80, 0, 80), points)  # Darker purple
        
        # Calculate current health width
        health_percentage = self.mothership.health / self.mothership.max_health
        if health_percentage > 0:
            current_width = int(mothership_health_width * health_percentage)
            current_points = [
                (mothership_health_x, mothership_health_y),
                (mothership_health_x + current_width, mothership_health_y),
                (mothership_health_x + current_width - int(20 * SCALE_FACTOR * health_percentage), mothership_health_y + mothership_health_height),
                (mothership_health_x + int(20 * SCALE_FACTOR), mothership_health_y + mothership_health_height)
            ]
            pygame.draw.polygon(screen, PURPLE, current_points)
        
        # Draw health bar border
        pygame.draw.polygon(screen, (200, 0, 200), points, 2)  # Light purple border
        
        # Draw spaceship UI at bottom
        # Draw health bar (green) at bottom-left
        health_width = int(220 * SCALE_FACTOR)
        health_height = int(20 * SCALE_FACTOR)
        health_x = int(40 * SCALE_FACTOR)
        health_y = SCREEN_HEIGHT - health_height - int(10 * SCALE_FACTOR)
        
        # Background (empty health)
        pygame.draw.rect(screen, RED, (health_x, health_y, health_width, health_height))
        
        # Current health
        current_health_width = int(health_width * (self.spaceship.health / self.spaceship.max_health))
        pygame.draw.rect(screen, GREEN, (health_x, health_y, current_health_width, health_height))
        
        # Health text label
        hp_text = font_medium.render(f"HP: {int(self.spaceship.health)}/{int(self.spaceship.max_health)}", True, WHITE)
        screen.blit(hp_text, (int(10 * SCALE_FACTOR), health_y - int(5 * SCALE_FACTOR)))
        
        # Draw spaceship stats at bottom (single line)
        stats_y = SCREEN_HEIGHT - int(40 * SCALE_FACTOR)
        stats_x = int(10 * SCALE_FACTOR)
        
        # Display reload, damage and autofire status in one line
        reload_text = font_medium.render(f"Reload: {self.spaceship.reload_speed:.1f}x", True, WHITE)
        damage_text = font_medium.render(f"Damage: {int(self.spaceship.bullet_damage)}", True, WHITE)  # Changed from Speed to Damage
        autofire_text = font_medium.render(f"Autofire: {'ON' if self.spaceship.autofire else 'OFF'}", True, WHITE)
        
        screen.blit(reload_text, (stats_x, stats_y))
        screen.blit(damage_text, (stats_x + reload_text.get_width() + int(20 * SCALE_FACTOR), stats_y))
        screen.blit(autofire_text, (stats_x + reload_text.get_width() + damage_text.get_width() + int(40 * SCALE_FACTOR), stats_y))
        
        # Display money
        money_text = font_medium.render(f"Money: ${int(self.spaceship.money)}", True, YELLOW)
        screen.blit(money_text, (stats_x, stats_y - int(30 * SCALE_FACTOR)))
        
        # Draw upgrade options at bottom-right
        upgrade_font = pygame.font.SysFont('Arial', int(20 * SCALE_FACTOR))
        
        reload_cost = int(100 * self.spaceship.reload_speed)
        health_cost = int(self.spaceship.max_health * 0.5)
        damage_cost = int(self.spaceship.bullet_damage * 50)  # Changed from speed to damage
        
        upgrade_text1 = upgrade_font.render(f"1: Upgrade Reload (${reload_cost})", True, CYAN)
        upgrade_text2 = upgrade_font.render(f"2: Upgrade Health (${health_cost})", True, CYAN)
        upgrade_text3 = upgrade_font.render(f"3: Upgrade Damage (${damage_cost})", True, CYAN)  # Changed from Speed to Damage
        
        # Position at bottom-right of screen
        upgrade_y = SCREEN_HEIGHT - int(80 * SCALE_FACTOR)
        upgrade_x = SCREEN_WIDTH - max(upgrade_text1.get_width(), upgrade_text2.get_width(), upgrade_text3.get_width()) - int(10 * SCALE_FACTOR)
        
        screen.blit(upgrade_text1, (upgrade_x, upgrade_y))
        screen.blit(upgrade_text2, (upgrade_x, upgrade_y + int(25 * SCALE_FACTOR)))
        screen.blit(upgrade_text3, (upgrade_x, upgrade_y + int(50 * SCALE_FACTOR)))
        
        # Draw "Press G for help" at bottom center
        help_text = font_medium.render("Press G for help", True, YELLOW)
        screen.blit(help_text, (SCREEN_WIDTH // 2 - help_text.get_width() // 2, SCREEN_HEIGHT - help_text.get_height() - int(10 * SCALE_FACTOR)))
    
    def draw_game_over(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_font = pygame.font.SysFont('Arial', int(80 * SCALE_FACTOR), bold=True)
        winner_font = pygame.font.SysFont('Arial', int(60 * SCALE_FACTOR))
        restart_font = pygame.font.SysFont('Arial', int(30 * SCALE_FACTOR))
        
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        winner_text = winner_font.render(f"{self.winner} Wins!", True, YELLOW if self.winner == "Spaceship" else PURPLE)
        restart_text = restart_font.render("Press ENTER to Restart", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 3))
        screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 3 + int(100 * SCALE_FACTOR)))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 3 + int(200 * SCALE_FACTOR)))
    
    def run(self):
        while self.is_running:
            # Limit frame rate
            clock.tick(FPS)
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update()
            
            # Draw game
            self.draw()
        
        # Clean up
        pygame.quit()
        sys.exit()

# Create and run the game
if __name__ == "__main__":
    game = Game()
    game.run()