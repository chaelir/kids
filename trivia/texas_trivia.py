import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 36)
FONT_SMALL = pygame.font.Font(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Texas trivia questions
QUESTIONS = [
    {
        "question": "What is the capital of Texas?",
        "options": ["Houston", "Dallas", "Austin", "San Antonio"],
        "answer": "Austin"
    },
    {
        "question": "Which famous battle cry originated in Texas?",
        "options": ["Remember the Alamo!", "Don't Mess with Texas!", "Yeehaw!", "Go Longhorns!"],
        "answer": "Remember the Alamo!"
    },
    {
        "question": "What is the nickname of Texas?",
        "options": ["The Sunshine State", "The Lone Star State", "The Golden State", "The Peach State"],
        "answer": "The Lone Star State"
    },
    {
        "question": "Which famous musician was born in Lubbock, Texas?",
        "options": ["Elvis Presley", "Johnny Cash", "Buddy Holly", "Bob Dylan"],
        "answer": "Buddy Holly"
    },
    {
        "question": "What is the largest city in Texas?",
        "options": ["Dallas", "Austin", "San Antonio", "Houston"],
        "answer": "Houston"
    }
]

class TexasTrivia:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Texas Trivia Challenge")
        self.clock = pygame.time.Clock()
        self.score = 0
        self.current_question = None
        self.questions = QUESTIONS.copy()
        random.shuffle(self.questions)
        self.game_over = False

    def get_next_question(self):
        if self.questions:
            return self.questions.pop()
        else:
            self.game_over = True
            return None

    def draw_text(self, text, font, color, x, y):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def draw(self):
        self.screen.fill(WHITE)
        if self.game_over:
            self.draw_text("Game Over!", FONT_LARGE, BLACK, WIDTH // 2, HEIGHT // 3)
            self.draw_text(f"Final Score: {self.score}/{len(QUESTIONS)}", FONT_MEDIUM, BLACK, WIDTH // 2, HEIGHT // 2)
            self.draw_text("Press SPACE to play again", FONT_SMALL, BLACK, WIDTH // 2, HEIGHT * 2 // 3)
        elif self.current_question:
            self.draw_text(self.current_question["question"], FONT_MEDIUM, BLACK, WIDTH // 2, 100)
            for i, option in enumerate(self.current_question["options"]):
                self.draw_text(f"{i + 1}. {option}", FONT_SMALL, BLACK, WIDTH // 2, 200 + i * 50)
        self.draw_text(f"Score: {self.score}", FONT_MEDIUM, BLUE, WIDTH - 100, 30)

    def run(self):
        self.current_question = self.get_next_question()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.__init__()  # Reset the game
                            self.current_question = self.get_next_question()
                    elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        answer_index = event.key - pygame.K_1
                        if self.current_question["options"][answer_index] == self.current_question["answer"]:
                            self.score += 1
                        self.current_question = self.get_next_question()

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = TexasTrivia()
    game.run()