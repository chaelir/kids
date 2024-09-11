import pygame

class Arena:
    def __init__(self, game):
        self.game = game
        self.width = game.width
        self.height = game.height - 100  # Leave space for control panel
        self.grid_size = 21  # Odd number for the grid
        self.cell_size = min(self.width, self.height) // self.grid_size

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 200), (0, 0, self.width, self.height))
        
        # Draw grid lines
        for i in range(self.grid_size + 1):
            pygame.draw.line(screen, (150, 150, 150), 
                             (i * self.cell_size, 0), 
                             (i * self.cell_size, self.height))
            pygame.draw.line(screen, (150, 150, 150), 
                             (0, i * self.cell_size), 
                             (self.width, i * self.cell_size))