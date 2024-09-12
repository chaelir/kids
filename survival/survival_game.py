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