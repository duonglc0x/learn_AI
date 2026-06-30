import json

path = r'f:\AI\BT.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

source = nb['cells'][0]['source']

# 1. Add Expectimax radiobutton after Alpha-Beta in _build_ui
# Find the Alpha-Beta radiobutton line inside _build_ui
for i, line in enumerate(source):
    if 'value="Alpha-Beta"' in line and 'Caro.TRadiobutton' in line:
        source.insert(i + 1, '        ttk.Radiobutton(algo_container, text="Expectimax", variable=self.algorithm, value="Expectimax", style="Caro.TRadiobutton", command=self._on_algo_change).pack(side=tk.LEFT, padx=6)\n')
        break

# 2. Add _expectimax_log method before _on_prev
expectimax_method = '''
    def _expectimax_log(self, board, depth, is_max):
        if self.check_winner(board, 'O'): return 10 - depth
        if self.check_winner(board, 'X'): return depth - 10
        empty_squares = self.get_empty(board)
        if not empty_squares: return 0

        if is_max:
            best = -float('inf')
            best_move = None
            for move in empty_squares:
                board[move] = 'O'
                self.steps.append(StepRecordCaro(board, depth+1, False, move, None, None, best, f"O thử đánh ô {move}"))
                score = self._expectimax_log(board, depth + 1, False)
                board[move] = ' '
                if score > best:
                    best = score
                    best_move = move
                self.steps.append(StepRecordCaro(board, depth, True, None, None, None, best, f"O lùi lại. Điểm nhánh = {score:.2f}. Tốt nhất hiện = {best:.2f}"))
            return best_move if depth == 0 else best
        else:
            # Chance node: X đánh ngẫu nhiên
            expected_value = 0
            prob = 1.0 / len(empty_squares)
            for move in empty_squares:
                board[move] = 'X'
                self.steps.append(StepRecordCaro(board, depth+1, True, move, None, None, expected_value, f"Nút Chance (X) ngẫu nhiên ô {move} (xác suất {prob:.2f})"))
                score = self._expectimax_log(board, depth + 1, True)
                board[move] = ' '
                expected_value += prob * score
                self.steps.append(StepRecordCaro(board, depth, False, None, None, None, expected_value, f"X lùi lại. Điểm nhánh = {score:.2f}. Kỳ vọng cộng dồn = {expected_value:.2f}"))
            return expected_value

'''

# Find _on_prev method to insert before it
for i, line in enumerate(source):
    if '    def _on_prev(self):' in line:
        # Check context to make sure it's in CaroMinimax (after _alphabeta_log)
        recent = ''.join(source[max(0,i-50):i])
        if '_alphabeta_log' in recent:
            lines = [l + '\n' for l in expectimax_method.split('\n')]
            source = source[:i] + lines + source[i:]
            break

# 3. Update simulate_ai_move to include Expectimax branch
for i, line in enumerate(source):
    if 'best_move = self._alphabeta_log' in line:
        # Check the line before - should be "else:"
        if 'else:' in source[i-1]:
            source[i-1] = source[i-1].replace('else:', 'elif self.algorithm.get() == "Alpha-Beta":')
            # Insert Expectimax branch after
            source.insert(i+1, '        else:\n')
            source.insert(i+2, '            best_move = self._expectimax_log(self.board, 0, True)\n')
        break

nb['cells'][0]['source'] = source

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print("Done!")
