import random
import unittest

from tic_tac_toe import available_moves, choose_computer_move, winner


class GameLogicTests(unittest.TestCase):
    def test_winner_detects_rows_columns_and_diagonals(self):
        for marks in (
            ("X", "X", "X", None, "O", None, "O", None, None),
            ("O", None, "X", "O", "X", None, "O", None, None),
            ("X", None, "O", None, "X", None, "O", None, "X"),
        ):
            with self.subTest(marks=marks):
                self.assertEqual(winner(marks), marks[next(
                    line[0] for line in (
                        (0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6),
                    )
                    if marks[line[0]] is not None
                    and marks[line[0]] == marks[line[1]] == marks[line[2]]
                )])

    def test_detects_full_board_draw(self):
        board = ("X", "O", "X", "X", "O", "O", "O", "X", "X")
        self.assertIsNone(winner(board))
        self.assertEqual(available_moves(board), [])

    def test_difficulty_levels_return_legal_moves(self):
        board = ("X", None, None, None, "O", None, None, None, None)
        for difficulty in ("Entspannt", "Knifflig", "Unschlagbar"):
            with self.subTest(difficulty=difficulty):
                move = choose_computer_move(board, difficulty, random.Random(1))
                self.assertIn(move, available_moves(board))

    def test_unbeatable_computer_never_loses(self):
        def explore(board, computer_turn):
            result = winner(board)
            if result is not None:
                return result != "X"
            moves = available_moves(board)
            if not moves:
                return True
            if computer_turn:
                move = choose_computer_move(board, "Unschlagbar", random.Random(0))
                next_board = list(board)
                next_board[move] = "O"
                return explore(tuple(next_board), False)
            for move in moves:
                next_board = list(board)
                next_board[move] = "X"
                if not explore(tuple(next_board), True):
                    return False
            return True

        self.assertTrue(explore((None,) * 9, False))


if __name__ == "__main__":
    unittest.main()
