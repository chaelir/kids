import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 4
CELL_SIZE = 100
MARGIN = 10
WIDTH = GRID_SIZE * (CELL_SIZE + MARGIN) + MARGIN
HEIGHT = WIDTH + 50  # Extra space for score
BACKGROUND_COLOR = (187, 173, 160)
EMPTY_CELL_COLOR = (205, 193, 180)
FONT = pygame.font.Font(None, 36)

# Color scheme for tiles
COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}

class Game2048:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2048")
        self.clock = pygame.time.Clock()
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(GRID_SIZE) for j in range(GRID_SIZE) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def move(self, direction):
        moved = False
        if direction == "UP":
            for j in range(GRID_SIZE):
                column = [self.grid[i][j] for i in range(GRID_SIZE) if self.grid[i][j] != 0]
                column = self.merge(column)
                for i in range(GRID_SIZE):
                    value = column[i] if i < len(column) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        elif direction == "DOWN":
            for j in range(GRID_SIZE):
                column = [self.grid[i][j] for i in range(GRID_SIZE-1, -1, -1) if self.grid[i][j] != 0]
                column = self.merge(column)
                for i in range(GRID_SIZE-1, -1, -1):
                    value = column[GRID_SIZE-1-i] if GRID_SIZE-1-i < len(column) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        elif direction == "LEFT":
            for i in range(GRID_SIZE):
                row = [self.grid[i][j] for j in range(GRID_SIZE) if self.grid[i][j] != 0]
                row = self.merge(row)
                for j in range(GRID_SIZE):
                    value = row[j] if j < len(row) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        elif direction == "RIGHT":
            for i in range(GRID_SIZE):
                row = [self.grid[i][j] for j in range(GRID_SIZE-1, -1, -1) if self.grid[i][j] != 0]
                row = self.merge(row)
                for j in range(GRID_SIZE-1, -1, -1):
                    value = row[GRID_SIZE-1-j] if GRID_SIZE-1-j < len(row) else 0
                    if self.grid[i][j] != value:
                        moved = True
                    self.grid[i][j] = value
        if moved:
            self.add_new_tile()

    def merge(self, line):
        for i in range(len(line) - 1):
            if line[i] == line[i + 1]:
                line[i] *= 2
                self.score += line[i]
                line.pop(i + 1)
                line.append(0)
        return line

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                value = self.grid[i][j]
                color = COLORS.get(value, COLORS[0])
                pygame.draw.rect(self.screen, color, (j*(CELL_SIZE+MARGIN)+MARGIN, i*(CELL_SIZE+MARGIN)+MARGIN, CELL_SIZE, CELL_SIZE))
                if value != 0:
                    text = FONT.render(str(value), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(j*(CELL_SIZE+MARGIN)+MARGIN+CELL_SIZE//2, i*(CELL_SIZE+MARGIN)+MARGIN+CELL_SIZE//2))
                    self.screen.blit(text, text_rect)
        
        score_text = FONT.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, HEIGHT - 40))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.move("UP")
                    elif event.key == pygame.K_DOWN:
                        self.move("DOWN")
                    elif event.key == pygame.K_LEFT:
                        self.move("LEFT")
                    elif event.key == pygame.K_RIGHT:
                        self.move("RIGHT")

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game2048()
    game.run()