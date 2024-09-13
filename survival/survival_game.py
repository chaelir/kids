import pygame
import random

# Initialize Pygame
pygame.init()

# Grid settings
GRID_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15

# Set up the display
WIDTH = GRID_SIZE * GRID_WIDTH
HEIGHT = GRID_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Survival Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
GRAY = (100, 100, 100)

# Player
player_x = GRID_WIDTH // 2
player_y = GRID_HEIGHT - 2

# Resources
resources = []

# Game variables
health = 100
food = 50
water = 50

# Font
font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 100
        self.hunger = 0
        self.thirst = 0

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def update(self):
        self.hunger = min(100, self.hunger + 0.1)
        self.thirst = min(100, self.thirst + 0.2)
        if self.hunger >= 100 and self.thirst >= 100:
            self.health -= 0.5  # Health decreases by 0.5 points when both hunger and thirst are at 100
        elif self.hunger >= 100 or self.thirst >= 100:
            self.health -= 0.1  # Normal health decrease when either hunger or thirst is at 100
        self.health = max(0, self.health)  # Ensure health doesn't go below 0

    def hunt(self):
        if random.random() < 0.6:  # 60% chance of successful hunt
            food_gained = random.randint(10, 30)
            self.hunger = max(0, self.hunger - food_gained)
            return f"Successful hunt! You gained {food_gained} food."
        else:
            return "The hunt was unsuccessful."

class Resource:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type  # 'food' or 'water'

class Game:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.player = Player(self.width // 2, self.height // 2)
        self.resources = []
        self.font = pygame.font.Font(None, 24)
        self.message = ""
        self.message_timer = 0

    def spawn_resource(self):
        if random.random() < 0.02:  # 2% chance each frame
            resource_type = random.choice(['food', 'water'])
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.resources.append(Resource(x, y, resource_type))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        self.message = self.player.hunt()
                        self.message_timer = 180  # Display message for 3 seconds (60 frames per second)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move(-2, 0)
            if keys[pygame.K_RIGHT]:
                self.player.move(2, 0)
            if keys[pygame.K_UP]:
                self.player.move(0, -2)
            if keys[pygame.K_DOWN]:
                self.player.move(0, 2)

            self.player.update()
            self.spawn_resource()

            # Check for game over condition
            if self.player.health <= 0:
                running = False
                print("Game Over! You died.")
                break

            # Check for resource collection
            for resource in self.resources[:]:
                if abs(resource.x - self.player.x) < 20 and abs(resource.y - self.player.y) < 20:
                    if resource.type == 'food':
                        self.player.hunger = max(0, self.player.hunger - 20)
                    else:
                        self.player.thirst = max(0, self.player.thirst - 20)
                    self.resources.remove(resource)

            # Draw everything
            self.screen.fill((255, 255, 255))
            pygame.draw.circle(self.screen, (0, 0, 255), (int(self.player.x), int(self.player.y)), 20)
            for resource in self.resources:
                color = (0, 255, 0) if resource.type == 'food' else (0, 0, 255)
                pygame.draw.circle(self.screen, color, (int(resource.x), int(resource.y)), 10)

            # Draw status bars
            pygame.draw.rect(self.screen, (255, 0, 0), (10, 10, self.player.health * 2, 20))
            pygame.draw.rect(self.screen, (0, 255, 0), (10, 40, (100 - self.player.hunger) * 2, 20))
            pygame.draw.rect(self.screen, (0, 0, 255), (10, 70, (100 - self.player.thirst) * 2, 20))

            # Draw hunt message
            if self.message_timer > 0:
                text_surface = self.font.render(self.message, True, (0, 0, 0))
                self.screen.blit(text_surface, (10, self.height - 30))
                self.message_timer -= 1

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))

def draw_player():
    pygame.draw.rect(screen, RED, (player_x * GRID_SIZE, player_y * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def draw_resources():
    for resource in resources:
        color = GREEN if resource['type'] == 'food' else BLUE
        pygame.draw.rect(screen, color, (resource['x'] * GRID_SIZE, resource['y'] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

def spawn_resource():
    if random.random() < 0.05:  # 5% chance each frame
        resource_type = random.choice(['food', 'water'])
        resources.append({
            'x': random.randint(0, GRID_WIDTH - 1),
            'y': random.randint(0, GRID_HEIGHT - 1),
            'type': resource_type
        })

def draw_stats():
    health_text = font.render(f"Health: {health}", True, WHITE)
    food_text = font.render(f"Food: {food}", True, WHITE)
    water_text = font.render(f"Water: {water}", True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(food_text, (10, 50))
    screen.blit(water_text, (10, 90))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and player_x > 0:
                player_x -= 1
            elif event.key == pygame.K_RIGHT and player_x < GRID_WIDTH - 1:
                player_x += 1
            elif event.key == pygame.K_UP and player_y > 0:
                player_y -= 1
            elif event.key == pygame.K_DOWN and player_y < GRID_HEIGHT - 1:
                player_y += 1

    spawn_resource()

    # Check for collisions with resources
    for resource in resources[:]:
        if player_x == resource['x'] and player_y == resource['y']:
            if resource['type'] == 'food':
                food = min(100, food + 10)
            else:
                water = min(100, water + 10)
            resources.remove(resource)

    # Decrease food and water over time
    food = max(0, food - 0.1)
    water = max(0, water - 0.1)

    # Decrease health if food or water is zero
    if food == 0 or water == 0:
        health = max(0, health - 0.5)

    # Game over condition
    if health <= 0:
        running = False

    screen.fill(BLACK)
    draw_grid()
    draw_player()
    draw_resources()
    draw_stats()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()