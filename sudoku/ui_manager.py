import pygame

class UIManager:
    def __init__(self, screen, game_manager):
        self.screen = screen
        self.game_manager = game_manager
        self.cell_size = 50
        self.board_size = 9 * self.cell_size
        self.margin = 20
        self.button_width = 100
        self.button_height = 40
        self.selected_cell = None
        self.initialize_buttons()
    
    def initialize_buttons(self):
        self.buttons = {
            'New Game': pygame.Rect(self.margin, self.board_size + 2*self.margin, self.button_width, self.button_height),
            'Undo': pygame.Rect(self.margin + self.button_width + 10, self.board_size + 2*self.margin, self.button_width, self.button_height),
            'Hint': pygame.Rect(self.margin + 2*self.button_width + 20, self.board_size + 2*self.margin, self.button_width, self.button_height),
            'Check': pygame.Rect(self.margin + 3*self.button_width + 30, self.board_size + 2*self.margin, self.button_width, self.button_height),
            'Solve': pygame.Rect(self.margin + 4*self.button_width + 40, self.board_size + 2*self.margin, self.button_width, self.button_height),
        }
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if y < self.board_size:
                self.selected_cell = (y // self.cell_size, x // self.cell_size)
            else:
                for button, rect in self.buttons.items():
                    if rect.collidepoint(x, y):
                        self.handle_button_click(button)
        elif event.type == pygame.KEYDOWN and self.selected_cell:
            if event.unicode.isdigit() and event.unicode != '0':
                row, col = self.selected_cell
                self.game_manager.make_move(row, col, int(event.unicode))
    
    def handle_button_click(self, button):
        if button == 'New Game':
            self.game_manager.new_game()
        elif button == 'Undo':
            self.game_manager.undo()
        elif button == 'Hint':
            self.game_manager.hint()
        elif button == 'Check':
            if self.game_manager.check():
                print("The current board state is valid.")
            else:
                print("The current board state is invalid.")
        elif button == 'Solve':
            self.game_manager.solve()
    
    def draw(self):
        self.screen.fill((255, 255, 255))  # White background
        self.draw_board()
        self.draw_controls()
        self.draw_timer()
        self.draw_score()
    
    def draw_board(self):
        for i in range(9):
            for j in range(9):
                x = j * self.cell_size
                y = i * self.cell_size
                cell_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, (0, 0, 0), cell_rect, 1)
                
                if (i, j) == self.selected_cell:
                    pygame.draw.rect(self.screen, (200, 200, 200), cell_rect)
                
                value = self.game_manager.board.get_cell(i, j)
                if value != 0:
                    font = pygame.font.Font(None, 36)
                    text = font.render(str(value), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
                    self.screen.blit(text, text_rect)
        
        # Draw thicker lines for 3x3 boxes
        for i in range(0, 10, 3):
            pygame.draw.line(self.screen, (0, 0, 0), (0, i * self.cell_size), (self.board_size, i * self.cell_size), 3)
            pygame.draw.line(self.screen, (0, 0, 0), (i * self.cell_size, 0), (i * self.cell_size, self.board_size), 3)
    
    def draw_controls(self):
        for button, rect in self.buttons.items():
            pygame.draw.rect(self.screen, (200, 200, 200), rect)
            font = pygame.font.Font(None, 24)
            text = font.render(button, True, (0, 0, 0))
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
    
    def draw_timer(self):
        self.game_manager.update_time()
        font = pygame.font.Font(None, 36)
        timer_text = f"Time: {self.game_manager.elapsed_time}s"
        text = font.render(timer_text, True, (0, 0, 0))
        self.screen.blit(text, (self.margin, self.board_size + 3*self.margin + self.button_height))
    
    def draw_score(self):
        font = pygame.font.Font(None, 36)
        score_text = f"Score: {self.game_manager.score}"
        text = font.render(score_text, True, (0, 0, 0))
        self.screen.blit(text, (self.margin, self.board_size + 4*self.margin + self.button_height))