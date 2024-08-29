import tkinter as tk
from tkinter import messagebox

class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic-Tac-Toe")
        self.master.geometry("800x600")
        self.current_player = 'Red'
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        # Create a frame for the game board that fills the window
        self.game_frame = tk.Frame(master)
        self.game_frame.pack(expand=True, fill=tk.BOTH)

        # Configure grid to expand with window
        for i in range(3):
            self.game_frame.grid_rowconfigure(i, weight=1)
            self.game_frame.grid_columnconfigure(i, weight=1)

        for i in range(3):
            for j in range(3):
                self.buttons[i][j] = tk.Button(self.game_frame, text=' ', font=('Arial', 60),
                                               command=lambda row=i, col=j: self.make_move(row, col))
                self.buttons[i][j].grid(row=i, column=j, sticky="nsew")

        self.status_label = tk.Label(master, text="Red's turn", font=('Arial', 24), fg='red')
        self.status_label.pack(pady=10)

    def make_move(self, row, col):
        if self.board[row][col] == ' ':
            self.board[row][col] = self.current_player
            color = 'red' if self.current_player == 'Red' else 'green'
            self.buttons[row][col].config(bg=color, state='disabled')

            winner = self.check_winner()
            if winner:
                messagebox.showinfo("Game Over", f"{winner} wins!")
                self.master.quit()
            elif self.is_full():
                messagebox.showinfo("Game Over", "It's a tie!")
                self.master.quit()
            else:
                self.current_player = 'Green' if self.current_player == 'Red' else 'Red'
                self.status_label.config(text=f"{self.current_player}'s turn", fg=self.current_player.lower())

    def check_winner(self):
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != ' ':
                return self.board[i][0]
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != ' ':
                return self.board[0][i]
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return self.board[0][2]
        return None

    def is_full(self):
        return all(cell != ' ' for row in self.board for cell in row)

if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()