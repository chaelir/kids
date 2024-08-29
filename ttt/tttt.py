import tkinter as tk
from tkinter import messagebox
import random
from ai import get_best_move

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic-Tac-Toe")
        self.master.geometry("1400x1200")
        self.master.configure(bg='lightgray')
        self.current_player = 'Red'
        self.board = [[' ' for _ in range(4)] for _ in range(4)]
        self.buttons = [[None for _ in range(4)] for _ in range(4)]
        self.game_mode = None
        self.ai_player = 'Green'
        self.human_player = 'Red'
        self.replay_button = None

        self.start_frame = tk.Frame(master, bg='lightgray')
        self.start_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)

        self.pvp_button = tk.Button(self.start_frame, text="Player vs Player", font=('Arial', 56), command=lambda: self.start_game("PvP"), padx=20, pady=20)
        self.pvp_button.pack(expand=True, pady=40)

        self.pve_button = tk.Button(self.start_frame, text="Player vs AI", font=('Arial', 56), command=lambda: self.start_game("PvE"), padx=20, pady=20)
        self.pve_button.pack(expand=True, pady=40)

        self.game_frame = tk.Frame(master, bg='lightgray')
        self.status_label = tk.Label(master, text="Red's turn", font=('Arial', 64), fg='red', bg='lightgray')

    def start_game(self, mode):
        self.game_mode = mode
        self.start_frame.destroy()
        self.game_frame.pack(expand=True, fill=tk.BOTH, padx=50, pady=50)
        self.status_label.pack(pady=10)

        for i in range(4):
            self.game_frame.grid_rowconfigure(i, weight=1)
            self.game_frame.grid_columnconfigure(i, weight=1)

        for i in range(4):
            for j in range(4):
                self.buttons[i][j] = tk.Button(self.game_frame, text=' ', font=('Arial', 120, 'bold'),
                                               command=lambda row=i, col=j: self.make_move(row, col),
                                               relief=tk.RAISED, borderwidth=8, width=2, height=1)
                self.buttons[i][j].grid(row=i, column=j, sticky="nsew", padx=15, pady=15)

        if mode == "PvE":
            self.randomly_choose_first_player()
        else:
            self.current_player = self.human_player
        
        self.update_status_label()

        if self.game_mode == "PvE" and self.current_player == self.ai_player:
            self.master.after(500, self.ai_move)

    def make_move(self, row, col):
        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            color = 'red' if self.current_player == 'Red' else 'green'
            self.buttons[row][col].config(bg=color, state='disabled')

            winner = self.check_winner()
            if winner:
                self.end_game(f"{winner} wins!")
            elif self.is_full():
                self.end_game("It's a tie!")
            else:
                self.current_player = self.ai_player if self.current_player == self.human_player else self.human_player
                self.update_status_label()

                if self.game_mode == "PvE" and self.current_player == self.ai_player:
                    self.master.after(500, self.ai_move)

    def randomly_choose_first_player(self):
        self.current_player = random.choice([self.human_player, self.ai_player])

    def update_status_label(self):
        self.status_label.config(text=f"{self.current_player}'s turn", fg=self.current_player.lower(), font=('Arial', 64))

    def end_game(self, message):
        messagebox.showinfo("Game Over", message)
        self.status_label.config(text="Game Over")
        self.show_replay_button()

    def show_replay_button(self):
        self.replay_button = tk.Button(self.master, text="Play Again", font=('Arial', 36), command=self.replay_game, padx=20, pady=10)
        self.replay_button.pack(pady=20)

    def replay_game(self):
        self.board = [[' ' for _ in range(4)] for _ in range(4)]
        self.current_player = 'Red'
        
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.status_label.pack_forget()
        
        if self.replay_button:
            self.replay_button.destroy()
            self.replay_button = None
        
        self.start_game(self.game_mode)

    def ai_move(self):
        row, col = get_best_move(self.board)
        self.make_move(row, col)

    def check_winner(self):
        # Check rows and columns
        for i in range(4):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] == self.board[i][3] != ' ':
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] == self.board[3][i] != ' ':
                return self.board[0][i]
        
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] == self.board[3][3] != ' ':
            return self.board[0][0]
        if self.board[0][3] == self.board[1][2] == self.board[2][1] == self.board[3][0] != ' ':
            return self.board[0][3]
        
        return None

    def is_full(self):
        return all(cell != ' ' for row in self.board for cell in row)

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()