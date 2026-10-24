"""A bright, friendly Tic-Tac-Toe game with three computer difficulty levels."""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

Board = tuple[str | None, ...]

WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def winner(board: Board) -> str | None:
    """Return the winning mark, or None if the game has no winner yet."""
    for first, second, third in WINNING_LINES:
        mark = board[first]
        if mark is not None and mark == board[second] == board[third]:
            return mark
    return None


def available_moves(board: Board) -> list[int]:
    return [index for index, mark in enumerate(board) if mark is None]


def _minimax(board: Board, is_computer_turn: bool, depth: int = 0) -> int:
    result = winner(board)
    if result == "O":
        return 10 - depth
    if result == "X":
        return depth - 10
    moves = available_moves(board)
    if not moves:
        return 0

    scores = []
    mark = "O" if is_computer_turn else "X"
    for move in moves:
        next_board = list(board)
        next_board[move] = mark
        scores.append(_minimax(tuple(next_board), not is_computer_turn, depth + 1))
    return max(scores) if is_computer_turn else min(scores)


def choose_computer_move(
    board: Board,
    difficulty: str,
    rng: random.Random | None = None,
) -> int:
    """Choose a legal move for O at the requested difficulty."""
    moves = available_moves(board)
    if not moves:
        raise ValueError("There are no available moves.")
    chooser = rng or random.Random()

    if difficulty == "Entspannt":
        return chooser.choice(moves)

    if difficulty == "Knifflig":
        for mark in ("O", "X"):
            for move in moves:
                next_board = list(board)
                next_board[move] = mark
                if winner(tuple(next_board)) == mark:
                    return move
        preferred = [move for move in (4, 0, 2, 6, 8, 1, 3, 5, 7) if move in moves]
        return preferred[0]

    if difficulty == "Unschlagbar":
        scored_moves = []
        for move in moves:
            next_board = list(board)
            next_board[move] = "O"
            scored_moves.append((_minimax(tuple(next_board), False), move))
        best_score = max(score for score, _ in scored_moves)
        return chooser.choice([move for score, move in scored_moves if score == best_score])

    raise ValueError(f"Unknown difficulty: {difficulty}")


class TicTacToeApp:
    BACKGROUND = "#F4F7FF"
    INK = "#26325C"
    MUTED = "#7882A6"
    PURPLE = "#6C63FF"
    PINK = "#FF79A8"
    TEAL = "#46C9B5"
    TILE = "#FFFFFF"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Tic Tac Toe — Funkelrunde")
        self.root.configure(bg=self.BACKGROUND)
        self.root.resizable(False, False)

        self.board: Board = (None,) * 9
        self.game_over = False
        self.thinking = False
        self.round_number = 0
        self.player_score = 0
        self.computer_score = 0
        self.draw_score = 0
        self.difficulty = tk.StringVar(value="Knifflig")

        self._build_interface()
        self._refresh_board()
        self._set_status("Du bist ✕ — such dir ein Feld aus!")

    def _build_interface(self) -> None:
        self.root.geometry("520x760")
        outer = tk.Frame(self.root, bg=self.BACKGROUND, padx=32, pady=22)
        outer.pack(fill="both", expand=True)

        tk.Label(
            outer,
            text="✦  TIC TAC TOE  ✦",
            font=("Segoe UI", 12, "bold"),
            fg=self.PURPLE,
            bg=self.BACKGROUND,
        ).pack(pady=(4, 7))
        tk.Label(
            outer,
            text="Funkelrunde",
            font=("Segoe UI", 30, "bold"),
            fg=self.INK,
            bg=self.BACKGROUND,
        ).pack()
        tk.Label(
            outer,
            text="Drei in einer Reihe — schaffst du's?",
            font=("Segoe UI", 12),
            fg=self.MUTED,
            bg=self.BACKGROUND,
        ).pack(pady=(3, 19))

        score_card = tk.Frame(outer, bg="white", padx=12, pady=12)
        score_card.pack(fill="x", pady=(0, 18))
        self.player_score_label = self._score_column(score_card, "DU  ✕", self.PURPLE)
        tk.Frame(score_card, bg="#E9ECF7", width=1, height=38).pack(
            side="left", padx=6
        )
        self.draw_score_label = self._score_column(score_card, "REMIS", self.MUTED)
        tk.Frame(score_card, bg="#E9ECF7", width=1, height=38).pack(
            side="left", padx=6
        )
        self.computer_score_label = self._score_column(
            score_card, "ICH  ○", self.PINK
        )

        settings = tk.Frame(outer, bg=self.BACKGROUND)
        settings.pack(fill="x", pady=(0, 13))
        tk.Label(
            settings,
            text="COMPUTER-LEVEL",
            font=("Segoe UI", 9, "bold"),
            fg=self.MUTED,
            bg=self.BACKGROUND,
        ).pack(side="left")
        style = ttk.Style()
        style.configure("TCombobox", padding=5, font=("Segoe UI", 10))
        self.level_picker = ttk.Combobox(
            settings,
            textvariable=self.difficulty,
            values=("Entspannt", "Knifflig", "Unschlagbar"),
            state="readonly",
            width=15,
        )
        self.level_picker.pack(side="right")

        self.status_label = tk.Label(
            outer,
            text="",
            font=("Segoe UI", 12, "bold"),
            fg=self.INK,
            bg=self.BACKGROUND,
            height=2,
        )
        self.status_label.pack()

        tk.Button(
            outer,
            text="  Neues Spiel starten  ↻  ",
            command=self._new_round,
            font=("Segoe UI", 11, "bold"),
            fg="white",
            bg=self.PURPLE,
            activebackground="#5850E8",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2",
        ).pack(pady=(0, 8))

        grid = tk.Frame(outer, bg=self.BACKGROUND)
        grid.pack(pady=(0, 10))
        self.cells: list[tk.Button] = []
        for index in range(9):
            button = tk.Button(
                grid,
                text="",
                font=("Segoe UI", 34, "bold"),
                width=3,
                height=1,
                relief="flat",
                bd=0,
                bg=self.TILE,
                activebackground="#EDF0FF",
                cursor="hand2",
                command=lambda cell=index: self._play(cell),
            )
            button.grid(row=index // 3, column=index % 3, padx=6, pady=6, ipadx=5, ipady=4)
            self.cells.append(button)

        actions = tk.Frame(outer, bg=self.BACKGROUND)
        actions.pack(pady=(0, 6))
        tk.Button(
            actions,
            text="Punktestand löschen",
            command=self._reset_scores,
            font=("Segoe UI", 10),
            fg=self.MUTED,
            bg=self.BACKGROUND,
            activebackground="#E9ECF7",
            relief="flat",
            bd=0,
            padx=10,
            pady=10,
            cursor="hand2",
        ).pack(side="left", padx=5)

    @staticmethod
    def _score_column(parent: tk.Frame, title: str, color: str) -> tk.Label:
        column = tk.Frame(parent, bg="white")
        column.pack(side="left", fill="x", expand=True)
        tk.Label(
            column,
            text=title,
            font=("Segoe UI", 9, "bold"),
            fg=color,
            bg="white",
        ).pack()
        label = tk.Label(
            column,
            text="0",
            font=("Segoe UI", 19, "bold"),
            fg="#26325C",
            bg="white",
        )
        label.pack()
        return label

    def _set_status(self, message: str, color: str | None = None) -> None:
        self.status_label.config(text=message, fg=color or self.INK)

    def _refresh_board(self) -> None:
        for index, button in enumerate(self.cells):
            mark = self.board[index]
            button.config(
                text=mark or "",
                fg=self.PURPLE if mark == "X" else self.PINK,
                state=(
                    "disabled"
                    if self.game_over or self.thinking or mark is not None
                    else "normal"
                ),
                disabledforeground=self.PURPLE if mark == "X" else self.PINK,
            )

    def _play(self, index: int) -> None:
        if self.game_over or self.thinking or self.board[index] is not None:
            return
        next_board = list(self.board)
        next_board[index] = "X"
        self.board = tuple(next_board)
        self._refresh_board()

        if self._finish_if_over():
            return

        self.thinking = True
        self._set_status("Ich überlege mir einen Zug …", self.PINK)
        self._refresh_board()
        round_number = self.round_number
        self.root.after(380, lambda: self._computer_turn(round_number))

    def _computer_turn(self, round_number: int) -> None:
        if round_number != self.round_number or self.game_over:
            return
        move = choose_computer_move(self.board, self.difficulty.get())
        next_board = list(self.board)
        next_board[move] = "O"
        self.board = tuple(next_board)
        self.thinking = False
        self._refresh_board()
        if not self._finish_if_over():
            self._set_status("Du bist dran — kannst du mich schlagen?")

    def _finish_if_over(self) -> bool:
        result = winner(self.board)
        if result == "X":
            self.player_score += 1
            self._set_status("Juhu, du hast gewonnen!  🎉", self.PURPLE)
        elif result == "O":
            self.computer_score += 1
            self._set_status("Diesmal war ich schneller!  ✨", self.PINK)
        elif not available_moves(self.board):
            self.draw_score += 1
            self._set_status("Unentschieden — gut gespielt!  🌟", self.TEAL)
        else:
            return False

        self.game_over = True
        self._update_scoreboard()
        self._refresh_board()
        return True

    def _update_scoreboard(self) -> None:
        self.player_score_label.config(text=str(self.player_score))
        self.computer_score_label.config(text=str(self.computer_score))
        self.draw_score_label.config(text=str(self.draw_score))

    def _new_round(self) -> None:
        self.round_number += 1
        self.board = (None,) * 9
        self.game_over = False
        self.thinking = False
        self._refresh_board()
        self._set_status("Du bist ✕ — such dir ein Feld aus!")

    def _reset_scores(self) -> None:
        self.player_score = self.computer_score = self.draw_score = 0
        self._update_scoreboard()


def main() -> None:
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
