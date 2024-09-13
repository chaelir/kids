import pygame
import random
import json
from board import Board
from constants import RED, BLACK, BLUE, WHITE, SQUARE_SIZE, WIDTH, HEIGHT, FONT_SIZE, LARGE_FONT_SIZE

class Game:
    def __init__(self, win, ai_opponent=False):
        self.win = win
        self.board = Board()
        self.turn = RED
        self.selected_piece = None
        self.valid_moves = {}
        self.game_status = "In Progress"
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.large_font = pygame.font.SysFont(None, LARGE_FONT_SIZE)
        self.ai_opponent = ai_opponent

    def update(self):
        self.board.draw(self.win)
        self.draw_valid_moves()
        self.draw_game_info()
        pygame.display.update()

        if self.game_status != "In Progress":
            return

        if self.ai_opponent and self.turn == WHITE:
            self.ai_move()
        else:
            # Check if the current player has any valid moves
            current_player_moves = self.board.get_all_valid_moves(self.turn)
            if not current_player_moves:
                self.game_status = "White Wins" if self.turn == RED else "Red Wins"

    def select(self, row, col):
        if self.selected_piece:
            result = self._move(row, col)
            if not result:
                self.selected_piece = None
                self.select(row, col)
        
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected_piece = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        
        return False

    def _move(self, row, col):
        piece = self.board.get_piece(row, col)
        if self.selected_piece and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected_piece, row, col)
            skipped = self.valid_moves[(row, col)]
            if skipped:
                self.board.remove(skipped)
                if self.board.get_valid_moves(self.selected_piece):
                    self.valid_moves = self.board.get_valid_moves(self.selected_piece)
                    return True
            self.change_turn()
        else:
            return False
        
        return True

    def change_turn(self):
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED
        
        self.check_win_condition()

    def check_win_condition(self):
        if self.board.red_left == 0:
            self.game_status = "White Wins"
        elif self.board.white_left == 0:
            self.game_status = "Red Wins"
        else:
            current_player_moves = self.board.get_all_valid_moves(self.turn)
            if not any(current_player_moves.values()):
                self.game_status = "White Wins" if self.turn == RED else "Red Wins"

    def draw_valid_moves(self):
        for move in self.valid_moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def draw_game_info(self):
        # Turn indicator
        turn_text = self.font.render(f"Turn: {'Red' if self.turn == RED else 'White'}", True, WHITE)
        self.win.blit(turn_text, (10, HEIGHT - 60))

        # Captured pieces counter
        captured_red = self.font.render(f"Red captured: {12 - self.board.white_left}", True, WHITE)
        captured_white = self.font.render(f"White captured: {12 - self.board.red_left}", True, WHITE)
        self.win.blit(captured_red, (WIDTH - 150, 10))
        self.win.blit(captured_white, (WIDTH - 150, 40))

        # Game status
        status_text = self.large_font.render(self.game_status, True, WHITE)
        status_rect = status_text.get_rect(center=(WIDTH // 2, 30))
        self.win.blit(status_text, status_rect)

    def restart(self):
        self.__init__(self.win, self.ai_opponent)

    def ai_move(self):
        all_moves = self.board.get_all_valid_moves(WHITE)
        if not all_moves:
            # No valid moves available, game should end
            self.game_status = "Red Wins"
            return

        best_piece = None
        best_move = None
        max_captures = 0
        for piece, moves in all_moves.items():
            for move, captures in moves.items():
                if len(captures) > max_captures:
                    max_captures = len(captures)
                    best_piece = piece
                    best_move = move
        
        if best_piece is None or best_move is None:
            # No captures available, choose a random move
            pieces_with_moves = [piece for piece, moves in all_moves.items() if moves]
            if not pieces_with_moves:
                self.game_status = "Red Wins"
                return
            best_piece = random.choice(pieces_with_moves)
            best_move = random.choice(list(all_moves[best_piece].keys()))
        
        self.board.move(best_piece, best_move[0], best_move[1])
        skipped = all_moves[best_piece][best_move]
        if skipped:
            self.board.remove(skipped)
        self.change_turn()

    def save_game(self):
        game_state = {
            'board': self.board.get_board_state(),
            'turn': self.turn,
            'red_left': self.board.red_left,
            'white_left': self.board.white_left,
            'red_kings': self.board.red_kings,
            'white_kings': self.board.white_kings
        }
        with open('game_state.json', 'w') as f:
            json.dump(game_state, f)

    def load_game(self):
        try:
            with open('game_state.json', 'r') as f:
                game_state = json.load(f)
            self.board.set_board_state(game_state['board'])
            self.turn = game_state['turn']
            self.board.red_left = game_state['red_left']
            self.board.white_left = game_state['white_left']
            self.board.red_kings = game_state['red_kings']
            self.board.white_kings = game_state['white_kings']
        except FileNotFoundError:
            print("No saved game found.")