import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FONT_LARGE = pygame.font.Font(None, 48)
FONT_MEDIUM = pygame.font.Font(None, 32)
FONT_SMALL = pygame.font.Font(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Airbus trivia questions
QUESTIONS = [
    {
        "question": "Which Airbus aircraft is nicknamed 'The Whale'?",
        "options": ["A320", "A380", "A350", "A330"],
        "answer": "A380"
    },
    {
        "question": "In which year was Airbus founded?",
        "options": ["1960", "1970", "1980", "1990"],
        "answer": "1970"
    },
    {
        "question": "Which Airbus aircraft is known for its 'neo' (New Engine Option) variant?",
        "options": ["A320", "A380", "A350", "A330"],
        "answer": "A320"
    },
    {
        "question": "What does 'FBW' stand for in Airbus technology?",
        "options": ["Fast Build Wings", "Fly-By-Wire", "Forward Back Wing", "Full Body Width"],
        "answer": "Fly-By-Wire"
    },
    {
        "question": "Which city is the headquarters of Airbus?",
        "options": ["Paris", "Berlin", "Toulouse", "Hamburg"],
        "answer": "Toulouse"
    }
]

class TriviaGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Airbus Aviation Challenge")
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
    game = TriviaGame()
    game.run()