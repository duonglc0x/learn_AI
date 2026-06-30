import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
import random
import copy
import math
GOAL_STATE = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
ACTIONS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
ACTION_NAMES = {'U': 'Up', 'D': 'Down', 'L': 'Left', 'R': 'Right'}
BG_DARK       = "#0f0f1a"
BG_CARD       = "#1a1a2e"
BG_CARD_ALT   = "#16213e"
ACCENT_BLUE   = "#0f3460"
ACCENT_CYAN   = "#00d2ff"
ACCENT_PURPLE = "#7b2ff7"
ACCENT_PINK   = "#e94560"
ACCENT_GREEN  = "#00e676"
ACCENT_ORANGE = "#ff9100"
TEXT_PRIMARY   = "#e0e0e0"
TEXT_SECONDARY = "#9e9e9e"
TEXT_BRIGHT    = "#ffffff"
TILE_COLORS   = [
    "#2c2c3e",   # 0 - empty
    "#e94560",   # 1
    "#ff6b6b",   # 2
    "#ffa726",   # 3
    "#ffee58",   # 4
    "#66bb6a",   # 5
    "#26c6da",   # 6
    "#42a5f5",   # 7
    "#ab47bc",   # 8
]
TILE_TEXT_COLORS = [
    "#2c2c3e",   # 0
    "#ffffff",   # 1
    "#ffffff",   # 2
    "#1a1a2e",   # 3
    "#1a1a2e",   # 4
    "#1a1a2e",   # 5
    "#1a1a2e",   # 6
    "#ffffff",   # 7
    "#ffffff",   # 8
]

class Node:
    """
    Đại diện cho một node trong cây tìm kiếm.
    - state: ma trận 3x3 (list of list)
    - action: hành động từ node cha ('L','R','U','D' hoặc None)
    - depth: số bước (hành động) đã thực hiện từ trạng thái ban đầu
    - parent: node cha (Node hoặc None)
    """
    def __init__(self, state, action=None, depth=0, parent=None):
        self.state = state
        self.action = action
        self.depth = depth
        self.parent = parent

    def state_tuple(self):
        return tuple(tuple(row) for row in self.state)

    def __repr__(self):
        action_str = self.action if self.action else "—"
        return f"Action={action_str}, Depth={self.depth}"

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None

def get_children(node):
    """Sinh ra tất cả các node con từ node hiện tại."""
    children = []
    bi, bj = find_blank(node.state)
    for action, (di, dj) in ACTIONS.items():
        ni, nj = bi + di, bj + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            new_state = copy.deepcopy(node.state)
            new_state[bi][bj], new_state[ni][nj] = new_state[ni][nj], new_state[bi][bj]
            child = Node(new_state, action, node.depth + 1, node)
            children.append(child)
    return children


def h(node):
    """
    Hàm đánh giá Greedy: đếm số ô SAI vị trí so với GOAL_STATE.
    Ô trống (0) không tính.
    """
    count = 0
    for i in range(3):
        for j in range(3):
            val = node.state[i][j]
            if val != 0 and val != GOAL_STATE[i][j]:
                count += 1
    return count

def is_solvable(state):
    flat = [x for row in state for x in row if x != 0]
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1
    return inversions % 2 == 0

def generate_random_state():
    while True:
        nums = list(range(9))
        random.shuffle(nums)
        state = [nums[i*3:(i+1)*3] for i in range(3)]
        if is_solvable(state) and state != GOAL_STATE:
            return state

class StepRecord:
    """Lưu trạng thái tại mỗi bước của thuật toán."""
    def __init__(self, current_node, frontier_list, reached_set, description=""):
        self.current_node = current_node
        self.frontier_list = list(frontier_list)
        self.reached_set = set(reached_set)
        self.description = description

def solve_steps_greedy(initial_state):
    """
    Greedy Best-First Search:
    - Hàm đánh giá h(node) = số ô SAI vị trí trong trạng thái của node.
    - Mỗi lần sinh con, tính h() cho từng con rồi chọn node có h() nhỏ nhất
      đưa vào đầu frontier (ưu tiên xét trước).
    - Frontier luôn được sắp xếp theo h() tăng dần.
    """
    steps = []
    root = Node(initial_state, None, 0, None)
    root.h_val = h(root) 

    frontier = [root]
    reached = set()

    steps.append(StepRecord(
        current_node=None,
        frontier_list=[root],
        reached_set=set(),
        description=f"Khởi tạo: Frontier = [root], h(root) = {root.h_val}"
    ))

    max_steps = 5000

    while frontier and len(steps) < max_steps:
        current = frontier.pop(0)
        state_t = current.state_tuple()

        if state_t in reached:
            continue

        reached.add(state_t)

        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Xét node (depth={current.depth}, action={current.action or 'Start'}, "
                f"h={current.h_val})"
            )
        ))

        if current.state == GOAL_STATE:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL!"
            ))
            return steps

        children = get_children(current)
        new_children = []
        for child in children:
            if child.state_tuple() not in reached:
                child.h_val = h(child)
                frontier.append(child)
                new_children.append(child)

        frontier.sort(key=lambda nd: nd.h_val)

        h_vals = [c.h_val for c in new_children]
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Sinh {len(new_children)} node con → h={h_vals} → "
                f"Sắp xếp Frontier theo h() tăng dần"
            )
        ))

    if len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=[],
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))

    return steps


def solve_steps_astar(initial_state):
    """
    A* Search:
    - f(n) = g(n) + h(n)
    - g(n) = node.depth (số hành động từ đầu đến n)
    - h(n) = số ô SAI vị trí (misplaced tiles)
    - Frontier được sắp xếp theo f(n) tăng dần.
    """
    steps = []
    root = Node(initial_state, None, 0, None)
    root.h_val = h(root)
    root.f_val = root.h_val + root.depth  

    frontier = [root]
    reached = set()

    steps.append(StepRecord(
        current_node=None,
        frontier_list=[root],
        reached_set=set(),
        description=(
            f"Khởi tạo: h={root.h_val}, g={root.depth}, "
            f"f={root.f_val}"
        )
    ))

    max_steps = 5000

    while frontier and len(steps) < max_steps:
        current = frontier.pop(0)
        state_t = current.state_tuple()

        if state_t in reached:
            continue

        reached.add(state_t)

        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Xét node: g={current.depth}, "
                f"h={current.h_val}, f={current.f_val} "
                f"(action={current.action or 'Start'})"
            )
        ))

        if current.state == GOAL_STATE:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL! (A*)"
            ))
            return steps

        children = get_children(current)
        new_children = []
        for child in children:
            if child.state_tuple() not in reached:
                child.h_val = h(child)
                child.f_val = child.depth + child.h_val
                frontier.append(child)
                new_children.append(child)

        frontier.sort(key=lambda nd: nd.f_val)

        f_vals = [c.f_val for c in new_children]
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Sinh {len(new_children)} con → f={f_vals} → "
                f"Sắp xếp Frontier theo f()=g+h"
            )
        ))

    if len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=[],
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))

    return steps


def solve_steps_ids(initial_state):
    """
    Iterative Deepening Search (IDS):
    - Khởi tạo depth limit = 0.
    - Chạy DFS giới hạn độ sâu (DLS). Nếu không thấy, tăng limit lên 1 và lặp lại.
    """
    steps = []
    max_total_steps = 5000
    
    for limit in range(100):
        root = Node(initial_state, None, 0, None)
        frontier = [root]
        reached = {root.state_tuple(): 0}
        
        steps.append(StepRecord(
            current_node=None,
            frontier_list=[root],
            reached_set=set(reached.keys()),
            description=f"--- Bắt đầu IDS với Limit = {limit} ---"
        ))
        
        while frontier and len(steps) < max_total_steps:
            current = frontier.pop()
            
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached.keys()),
                description=f"Xét node (depth={current.depth}/{limit}, action={current.action or 'Start'})"
            ))
            
            if current.state == GOAL_STATE:
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached.keys()),
                    description=f"✅ ĐÃ TÌM THẤY GOAL ở limit {limit}!"
                ))
                return steps
                
            if current.depth < limit:
                children = get_children(current)
                new_children = []
                for child in children:
                    child_t = child.state_tuple()
                    if child_t not in reached or reached[child_t] > child.depth:
                        reached[child_t] = child.depth
                        frontier.append(child)
                        new_children.append(child)
                
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached.keys()),
                    description=f"Sinh {len(new_children)} node con (còn hạn mức depth={limit})"
                ))
            else:
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached.keys()),
                    description=f"Đạt giới hạn depth={limit}, không sinh con."
                ))
                
        if len(steps) >= max_total_steps:
            steps.append(StepRecord(
                current_node=None,
                frontier_list=[],
                reached_set=set(reached.keys()),
                description="⚠️ Đã đạt giới hạn bước mô phỏng tổng cộng."
            ))
            return steps
            
    return steps


def solve_steps_lddg(initial_state):
    """
    Leo đồi đơn giản (LĐĐG):
    - h(node) = số ô SAI vị trí.
    - Lần lượt sinh các con. Node con nào sinh ra sẽ được đưa vào frontier.
    - Nếu h(con) < h(node hiện tại): lấy làm node xét tiếp theo (frontier bị clear).
    - Nếu h(con) >= h(node hiện tại): loại ra khỏi frontier.
    - Dừng nếu đã thử hết các con mà không có con nào tốt hơn.
    """
    steps = []
    current = Node(initial_state, None, 0, None)
    current.h_val = h(current)
    
    reached = set()
    frontier = []
    
    steps.append(StepRecord(
        current_node=None,
        frontier_list=[current],
        reached_set=set(),
        description=f"Khởi tạo: h(root) = {current.h_val}"
    ))
    
    max_steps = 5000
    
    while current and len(steps) < max_steps:
        state_t = current.state_tuple()
        reached.add(state_t)
        
        # Thêm current vào frontier để hiển thị ở bước hiện tại
        if not frontier:
            frontier = [current]
            
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Xét node (depth={current.depth}, action={current.action or 'Start'}, "
                f"h={current.h_val})"
            )
        ))
        
        if current.state == GOAL_STATE:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL!"
            ))
            return steps
            
        children = get_children(current)
        found_better = False
        frontier.clear()
        
        for child in children:
            child.h_val = h(child)
            frontier.append(child)
            
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description=f"Sinh node con (action={child.action}), h={child.h_val} → Đưa vào frontier."
            ))
            
            if child.h_val < current.h_val:
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached),
                    description=f"Node con có h={child.h_val} < {current.h_val} (node hiện tại). Lấy làm node xét tiếp theo!"
                ))
                current = child
                frontier = [child]
                found_better = True
                break
            else:
                frontier.pop()
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached),
                    description=f"Node con có h={child.h_val} >= {current.h_val}. Loại ra khỏi frontier."
                ))
                
        if not found_better:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="Không có node con nào có h() nhỏ hơn node hiện tại. Dừng leo đồi."
            ))
            return steps

    if len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=list(frontier),
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))

    return steps


def solve_steps_lddn(initial_state):
    """
    Leo đồi dốc nhất (LĐDN):
    - h(node) = số ô SAI vị trí.
    - Sinh ra tất cả các con.
    - So sánh và chọn node con có h() nhỏ nhất.
    - Nếu h(con nhỏ nhất) < h(node hiện tại): lấy làm gốc tiếp theo.
    - Dừng nếu không có con nào có h() < h(node hiện tại) hoặc tìm thấy Goal.
    """
    steps = []
    current = Node(initial_state, None, 0, None)
    current.h_val = h(current)
    
    reached = set()
    frontier = []
    
    steps.append(StepRecord(
        current_node=None,
        frontier_list=[current],
        reached_set=set(),
        description=f"Khởi tạo: h(root) = {current.h_val}"
    ))
    
    max_steps = 5000
    
    while current and len(steps) < max_steps:
        state_t = current.state_tuple()
        reached.add(state_t)
        
        if not frontier:
            frontier = [current]
            
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Xét node (depth={current.depth}, action={current.action or 'Start'}, "
                f"h={current.h_val})"
            )
        ))
        
        if current.state == GOAL_STATE:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL!"
            ))
            return steps
            
        children = get_children(current)
        best_child = None
        best_h = float('inf')
        
        frontier.clear()
        for child in children:
            child.h_val = h(child)
            frontier.append(child)
            if child.h_val < best_h:
                best_h = child.h_val
                best_child = child
                
        h_vals = [c.h_val for c in children]
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=f"Sinh tất cả {len(children)} node con → h={h_vals} → Đưa vào frontier để so sánh."
        ))
        
        if best_child and best_child.h_val < current.h_val:
            frontier = [best_child]
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier), 
                reached_set=set(reached),
                description=(
                    f"Chọn node con có h() nhỏ nhất (h={best_child.h_val} < {current.h_val}) làm gốc tiếp theo. "
                    f"Xóa các node con khác khỏi frontier."
                )
            ))
            current = best_child
        else:
            frontier.clear()
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description=(
                    f"Không có con nào h() < {current.h_val} (nhỏ nhất là {best_child.h_val if best_child else 'N/A'}). "
                    f"Xóa các node con khỏi frontier và dừng leo đồi."
                )
            ))
            return steps

    if len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=list(frontier),
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))

    return steps


def solve_steps_ldnn(initial_state):
    """
    Leo đồi ngẫu nhiên (LĐNN - Random Restart Hill Climbing):
    - h(node) = số ô SAI vị trí.
    - Tại mỗi bước, sinh tất cả các node con và chọn NGẪU NHIÊN một node
      trong số các node có h() < h(node hiện tại).
    - Nếu không có node con nào tốt hơn (cục bộ tối ưu), thực hiện
      "khởi động lại ngẫu nhiên" (random restart) từ một trạng thái mới.
    - Dừng nếu tìm thấy Goal hoặc đã đạt giới hạn bước.
    """
    steps = []
    max_steps = 5000
    max_restarts = 10
    restart_count = 0

    current = Node(initial_state, None, 0, None)
    current.h_val = h(current)

    reached = set()
    frontier = [current]

    steps.append(StepRecord(
        current_node=None,
        frontier_list=[current],
        reached_set=set(),
        description=f"Khởi tạo LĐNN: h(root) = {current.h_val} | Restart #{restart_count}"
    ))

    while current and len(steps) < max_steps:
        state_t = current.state_tuple()
        reached.add(state_t)

        if not frontier:
            frontier = [current]

        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"[Restart #{restart_count}] Xét node "
                f"(depth={current.depth}, action={current.action or 'Start'}, "
                f"h={current.h_val})"
            )
        ))

        if current.state == GOAL_STATE:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL! (LĐNN)"
            ))
            return steps

        children = get_children(current)
        better_children = []
        frontier_all = []

        for child in children:
            child.h_val = h(child)
            frontier_all.append(child)
            if child.h_val < current.h_val:
                better_children.append(child)

        frontier = frontier_all
        h_vals = [c.h_val for c in children]
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Sinh {len(children)} node con → h={h_vals} → "
                f"Có {len(better_children)} node con tốt hơn (h < {current.h_val})"
            )
        ))

        if better_children:
            chosen = random.choice(better_children)
            frontier = [chosen]
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description=(
                    f"🎲 Chọn NGẪU NHIÊN node con: action={chosen.action}, "
                    f"h={chosen.h_val} (trong {len(better_children)} node tốt hơn)"
                )
            ))
            current = chosen
        else:
            # Cục bộ tối ưu → khởi động lại ngẫu nhiên
            if restart_count < max_restarts and len(steps) < max_steps:
                restart_count += 1
                new_state = generate_random_state()
                current = Node(new_state, None, 0, None)
                current.h_val = h(current)
                reached = set()
                frontier = [current]
                steps.append(StepRecord(
                    current_node=None,
                    frontier_list=list(frontier),
                    reached_set=set(reached),
                    description=(
                        f"⚠️ Cục bộ tối ưu! Không có con nào h() < {h(Node(initial_state))}. "
                        f"🔄 Khởi động lại ngẫu nhiên #{restart_count} với h={current.h_val}"
                    )
                ))
            else:
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=[],
                    reached_set=set(reached),
                    description=(
                        f"❌ Đã thử {restart_count} lần khởi động lại nhưng không tìm thấy Goal. Dừng."
                    )
                ))
                return steps

    if len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=list(frontier),
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))

    return steps


def solve_steps_mplk(initial_state):
    """
    Mô Phỏng Luyện Kim (MPLK - Simulated Annealing):
    - Bắt đầu với nhiệt độ cao (T = 20) và giảm dần.
    - Tại mỗi bước, chọn ngẫu nhiên một node con.
    - Nếu h(con) < h(hiện tại): chấp nhận.
    - Nếu h(con) >= h(hiện tại): chấp nhận với xác suất e^(-(h_con - h_hiện)/T).
    - Nhiệt độ giảm theo công thức: T = T * cooling_rate.
    - Dừng khi T quá nhỏ hoặc tìm thấy Goal.
    """
    steps = []
    
    current = Node(initial_state, None, 0, None)
    current.h_val = h(current)
    
    # Tham số Simulated Annealing
    T = 20.0  # Nhiệt độ ban đầu
    T_min = 0.01  # Nhiệt độ tối thiểu
    cooling_rate = 0.95  # Tỷ lệ hạ nhiệt độ
    max_steps = 5000
    
    reached = set()
    frontier = [current]
    iteration = 0
    
    steps.append(StepRecord(
        current_node=None,
        frontier_list=[current],
        reached_set=set(),
        description=f"Khởi tạo MPLK: h(root) = {current.h_val} | Nhiệt độ T = {T:.2f}"
    ))
    
    while T > T_min and len(steps) < max_steps:
        state_t = current.state_tuple()
        reached.add(state_t)
        iteration += 1
        
        frontier = [current]
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"[Lần lặp {iteration}] Xét node (depth={current.depth}, "
                f"action={current.action or 'Start'}, h={current.h_val}) | "
                f"T = {T:.3f}"
            )
        ))
        
        if current.state == GOAL_STATE:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL! (MPLK)"
            ))
            return steps
        
        # Sinh tất cả các node con
        children = get_children(current)
        if not children:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=[],
                reached_set=set(reached),
                description="Không có node con. Dừng."
            ))
            return steps
        
        # Chọn ngẫu nhiên một node con
        child = random.choice(children)
        child.h_val = h(child)
        
        frontier.append(child)
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=(
                f"Sinh {len(children)} node con. Chọn NGẪU NHIÊN: "
                f"action={child.action}, h={child.h_val}"
            )
        ))
        
        # Tính Delta h
        delta_h = child.h_val - current.h_val
        
        # Quyết định chấp nhận
        if delta_h < 0:
            # Node con tốt hơn → chấp nhận
            frontier = [child]
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description=(
                    f"Δh = {delta_h:.0f} < 0 (tốt hơn) → ✅ Chấp nhận node con!"
                )
            ))
            current = child
        else:
            # Node con không tốt hơn → chấp nhận với xác suất
            acceptance_prob = math.exp(-delta_h / T) if T > 0 else 0
            rand = random.random()
            
            if rand < acceptance_prob:
                frontier = [child]
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached),
                    description=(
                        f"Δh = {delta_h:.0f} ≥ 0, nhưng P = e^(-{delta_h:.0f}/{T:.3f}) = {acceptance_prob:.3f} > "
                        f"random({rand:.3f}) → ✅ Chấp nhận (thoát cục bộ)!"
                    )
                ))
                current = child
            else:
                frontier = []
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached),
                    description=(
                        f"Δh = {delta_h:.0f} ≥ 0, P = {acceptance_prob:.3f} ≤ "
                        f"random({rand:.3f}) → ❌ Từ chối node con, giữ node hiện tại."
                    )
                ))
        
        # Hạ nhiệt độ
        T = T * cooling_rate
    
    if T <= T_min:
        steps.append(StepRecord(
            current_node=current,
            frontier_list=[],
            reached_set=set(reached),
            description=f"⚠️ Nhiệt độ quá thấp (T = {T:.4f} ≤ {T_min}). Dừng MPLK."
        ))
    elif len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=[],
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))
    
    return steps


def solve_steps(initial_state, algorithm='BFS c1'):
    """
    Chạy thuật toán và lưu lại từng bước.
    Trả về list các StepRecord.
    """
    steps = []
    root = Node(initial_state, None, 0, None)

    if 'LĐĐG' in algorithm:
        return solve_steps_lddg(initial_state)

    if 'LĐDN' in algorithm:
        return solve_steps_lddn(initial_state)

    if 'LĐDN' in algorithm:
        return solve_steps_lddn(initial_state)

    if 'LĐNN' in algorithm:
        return solve_steps_ldnn(initial_state)

    if 'IDS' in algorithm:
        return solve_steps_ids(initial_state)

    if 'Greedy' in algorithm:
        return solve_steps_greedy(initial_state)

    if 'A*' in algorithm:
        return solve_steps_astar(initial_state)

    if 'MPLK' in algorithm:
        return solve_steps_mplk(initial_state)

    is_bfs = 'BFS' in algorithm
    is_c2 = 'c2' in algorithm

    if is_bfs:
        frontier = deque([root])
    else: 
        frontier = [root]

    reached = set()

    steps.append(StepRecord(
        current_node=None,
        frontier_list=[root],
        reached_set=set(),
        description="Khởi tạo: Frontier chứa trạng thái ban đầu"
    ))

    if is_c2 and root.state == GOAL_STATE:
        steps.append(StepRecord(
            current_node=root,
            frontier_list=list(frontier),
            reached_set=set(),
            description="✅ ĐÃ TÌM THẤY GOAL ở trạng thái ban đầu!"
        ))
        return steps

    max_steps = 5000  # giới hạn để tránh treo

    while frontier and len(steps) < max_steps:
        if is_bfs:
            current = frontier.popleft()
        else:
            current = frontier.pop()

        state_t = current.state_tuple()

        if state_t in reached:
            continue

        reached.add(state_t)

        # Ghi bước: đang xét node
        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=f"Xét node (depth={current.depth}, action={current.action or 'Start'})"
        ))

        # Đối với c1: Kiểm tra goal khi xét node
        if not is_c2:
            if current.state == GOAL_STATE:
                steps.append(StepRecord(
                    current_node=current,
                    frontier_list=list(frontier),
                    reached_set=set(reached),
                    description="✅ ĐÃ TÌM THẤY GOAL!"
                ))
                return steps

        # Sinh con
        children = get_children(current)
        new_children = []
        goal_child = None

        for child in children:
            if child.state_tuple() not in reached:
                frontier.append(child)
                new_children.append(child)
                if is_c2 and child.state == GOAL_STATE:
                    goal_child = child
                    break

        if goal_child is not None:
            steps.append(StepRecord(
                current_node=current,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description=f"Sinh {len(new_children)} node con → Phát hiện node con trùng khớp với ĐÍCH!"
            ))
            steps.append(StepRecord(
                current_node=goal_child,
                frontier_list=list(frontier),
                reached_set=set(reached),
                description="✅ ĐÃ TÌM THẤY GOAL khi sinh node con!"
            ))
            return steps

        steps.append(StepRecord(
            current_node=current,
            frontier_list=list(frontier),
            reached_set=set(reached),
            description=f"Sinh {len(new_children)} node con → thêm vào Frontier"
        ))

    if len(steps) >= max_steps:
        steps.append(StepRecord(
            current_node=None,
            frontier_list=[],
            reached_set=reached,
            description="⚠️ Đã đạt giới hạn bước mô phỏng."
        ))

    return steps


class PuzzleApp:
    def __init__(self, root, top_root=None):
        self.root = root
        self.top_root = top_root if top_root else root
        self.root.configure(bg=BG_DARK)

        self.initial_state = generate_random_state()
        self.steps = []
        self.current_step_idx = -1
        self.algorithm = tk.StringVar(value="BFS c1")

        self._build_ui()
        self._display_initial()

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG_CARD, pady=12)
        header.pack(fill=tk.X, padx=0)

        title_lbl = tk.Label(header, text="🧩  8-Puzzle Simulator",
                             font=("Segoe UI", 20, "bold"), fg=ACCENT_CYAN, bg=BG_CARD)
        title_lbl.pack(side=tk.LEFT, padx=24)

        # Tạo container có thanh lăng ngang cho các nút thuật toán
        algo_container = tk.Frame(header, bg=BG_CARD)
        algo_container.pack(side=tk.RIGHT, padx=24, fill=tk.X, expand=True)

        tk.Label(algo_container, text="Thuật toán:", font=("Segoe UI", 12),
                 fg=TEXT_SECONDARY, bg=BG_CARD).pack(side=tk.LEFT, padx=(0, 8))

        # Canvas và scrollbar cho các nút
        algo_canvas = tk.Canvas(algo_container, bg=BG_CARD, height=50,
                                highlightthickness=0, cursor="hand2")
        algo_scrollbar = tk.Scrollbar(algo_container, orient=tk.HORIZONTAL,
                                      command=algo_canvas.xview)
        algo_frame = tk.Frame(algo_canvas, bg=BG_CARD)

        algo_frame.bind("<Configure>",
            lambda e: algo_canvas.configure(scrollregion=algo_canvas.bbox("all")))
        algo_canvas.create_window((0, 0), window=algo_frame, anchor="nw")
        algo_canvas.configure(xscrollcommand=algo_scrollbar.set)

        algo_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        algo_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Cho phép cuộn bằng mouse wheel
        algo_canvas.bind("<Enter>", lambda e: self._bind_mousewheel_horizontal(algo_canvas))
        algo_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Algo.TRadiobutton", background=BG_CARD, foreground=TEXT_PRIMARY,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("Algo.TRadiobutton",
                  foreground=[('selected', ACCENT_CYAN), ('active', ACCENT_CYAN)])

        ttk.Radiobutton(algo_frame, text="BFS c1", variable=self.algorithm,
                        value="BFS c1", style="Algo.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo_frame, text="BFS c2", variable=self.algorithm,
                        value="BFS c2", style="Algo.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo_frame, text="DFS c1", variable=self.algorithm,
                        value="DFS c1", style="Algo.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo_frame, text="DFS c2", variable=self.algorithm,
                        value="DFS c2", style="Algo.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("Greedy.TRadiobutton", background=BG_CARD,
                        foreground=ACCENT_ORANGE,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("Greedy.TRadiobutton",
                  foreground=[('selected', ACCENT_ORANGE), ('active', ACCENT_ORANGE)])

        ttk.Radiobutton(algo_frame, text="Greedy", variable=self.algorithm,
                        value="Greedy", style="Greedy.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("AStar.TRadiobutton", background=BG_CARD,
                        foreground=ACCENT_PURPLE,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("AStar.TRadiobutton",
                  foreground=[('selected', ACCENT_PURPLE), ('active', ACCENT_PURPLE)])

        ttk.Radiobutton(algo_frame, text="A*", variable=self.algorithm,
                        value="A*", style="AStar.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("IDS.TRadiobutton", background=BG_CARD,
                        foreground=ACCENT_PINK,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("IDS.TRadiobutton",
                  foreground=[('selected', ACCENT_PINK), ('active', ACCENT_PINK)])

        ttk.Radiobutton(algo_frame, text="IDS", variable=self.algorithm,
                        value="IDS", style="IDS.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("LDDG.TRadiobutton", background=BG_CARD,
                        foreground=ACCENT_GREEN,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("LDDG.TRadiobutton",
                  foreground=[('selected', ACCENT_GREEN), ('active', ACCENT_GREEN)])

        ttk.Radiobutton(algo_frame, text="LĐĐG", variable=self.algorithm,
                        value="LĐĐG", style="LDDG.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("LDDN.TRadiobutton", background=BG_CARD,
                        foreground=ACCENT_CYAN,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("LDDN.TRadiobutton",
                  foreground=[('selected', ACCENT_CYAN), ('active', ACCENT_CYAN)])

        ttk.Radiobutton(algo_frame, text="LĐDN", variable=self.algorithm,
                        value="LĐDN", style="LDDN.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("LDNN.TRadiobutton", background=BG_CARD,
                        foreground=ACCENT_PINK,
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("LDNN.TRadiobutton",
                  foreground=[('selected', ACCENT_PINK), ('active', ACCENT_PINK)])

        ttk.Radiobutton(algo_frame, text="LĐNN", variable=self.algorithm,
                        value="LĐNN", style="LDNN.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        tk.Label(algo_frame, text="│", font=("Segoe UI", 14),
                 fg="#444466", bg=BG_CARD).pack(side=tk.LEFT, padx=4)

        style.configure("MPLK.TRadiobutton", background=BG_CARD,
                        foreground="#ffb300",
                        font=("Segoe UI", 12, "bold"), focuscolor=BG_CARD)
        style.map("MPLK.TRadiobutton",
                  foreground=[('selected', "#ffb300"), ('active', "#ffb300")])

        ttk.Radiobutton(algo_frame, text="MPLK", variable=self.algorithm,
                        value="MPLK", style="MPLK.TRadiobutton",
                        command=self._on_algo_change).pack(side=tk.LEFT, padx=6)

        main_frame = tk.Frame(self.root, bg=BG_DARK)

        left_frame = tk.Frame(main_frame, bg=BG_DARK)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.step_label = tk.Label(left_frame, text="Bước: —",
                                   font=("Segoe UI", 13, "bold"),
                                   fg=ACCENT_ORANGE, bg=BG_DARK, anchor="w")
        self.step_label.pack(fill=tk.X, pady=(0, 4))

        self.desc_label = tk.Label(left_frame, text="",
                                   font=("Segoe UI", 11),
                                   fg=TEXT_SECONDARY, bg=BG_DARK, anchor="w",
                                   wraplength=320, justify=tk.LEFT)
        self.desc_label.pack(fill=tk.X, pady=(0, 8))

        self.puzzle_size = 300
        self.puzzle_canvas = tk.Canvas(left_frame, width=self.puzzle_size,
                                       height=self.puzzle_size,
                                       bg=BG_CARD, highlightthickness=2,
                                       highlightbackground=ACCENT_BLUE)
        self.puzzle_canvas.pack(pady=4)

        node_info_frame = tk.Frame(left_frame, bg=BG_CARD_ALT, padx=12, pady=8)
        node_info_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(node_info_frame, text="NODE ĐANG XÉT",
                 font=("Segoe UI", 11, "bold"),
                 fg=ACCENT_PINK, bg=BG_CARD_ALT).pack(anchor="w")

        self.node_info_text = tk.Label(node_info_frame, text="(rỗng)",
                                       font=("Consolas", 10),
                                       fg=TEXT_PRIMARY, bg=BG_CARD_ALT,
                                       anchor="w", justify=tk.LEFT, wraplength=300)
        self.node_info_text.pack(anchor="w", pady=(2, 0))

        goal_frame = tk.Frame(left_frame, bg=BG_CARD_ALT, padx=12, pady=8)
        goal_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Label(goal_frame, text="TRẠNG THÁI ĐÍCH",
                 font=("Segoe UI", 10, "bold"),
                 fg=ACCENT_GREEN, bg=BG_CARD_ALT).pack(anchor="w")

        self.goal_canvas = tk.Canvas(goal_frame, width=120, height=120,
                                     bg=BG_CARD_ALT, highlightthickness=0)
        self.goal_canvas.pack(pady=4)
        self._draw_mini_board(self.goal_canvas, GOAL_STATE, 120)

        right_frame = tk.Frame(main_frame, bg=BG_DARK)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        frontier_card = tk.Frame(right_frame, bg=BG_CARD, padx=12, pady=8)
        frontier_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        frontier_header = tk.Frame(frontier_card, bg=BG_CARD)
        frontier_header.pack(fill=tk.X)

        tk.Label(frontier_header, text="📋  FRONTIER",
                 font=("Segoe UI", 12, "bold"),
                 fg=ACCENT_CYAN, bg=BG_CARD).pack(side=tk.LEFT)

        self.frontier_count_lbl = tk.Label(frontier_header, text="(0)",
                                           font=("Segoe UI", 11),
                                           fg=TEXT_SECONDARY, bg=BG_CARD)
        self.frontier_count_lbl.pack(side=tk.LEFT, padx=8)

        self.frontier_canvas = tk.Canvas(frontier_card, bg=BG_CARD,
                                          highlightthickness=0)
        frontier_scrollbar = tk.Scrollbar(frontier_card, orient=tk.VERTICAL,
                                          command=self.frontier_canvas.yview)
        self.frontier_inner = tk.Frame(self.frontier_canvas, bg=BG_CARD)

        self.frontier_inner.bind("<Configure>",
            lambda e: self.frontier_canvas.configure(scrollregion=self.frontier_canvas.bbox("all")))
        self.frontier_canvas.create_window((0, 0), window=self.frontier_inner, anchor="nw")
        self.frontier_canvas.configure(yscrollcommand=frontier_scrollbar.set)

        self.frontier_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=4)
        frontier_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.frontier_canvas.bind("<Enter>", lambda e: self._bind_mousewheel(self.frontier_canvas))
        self.frontier_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        reached_card = tk.Frame(right_frame, bg=BG_CARD, padx=12, pady=8)
        reached_card.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        reached_header = tk.Frame(reached_card, bg=BG_CARD)
        reached_header.pack(fill=tk.X)

        tk.Label(reached_header, text="✅  REACHED",
                 font=("Segoe UI", 12, "bold"),
                 fg=ACCENT_GREEN, bg=BG_CARD).pack(side=tk.LEFT)

        self.reached_count_lbl = tk.Label(reached_header, text="(0)",
                                          font=("Segoe UI", 11),
                                          fg=TEXT_SECONDARY, bg=BG_CARD)
        self.reached_count_lbl.pack(side=tk.LEFT, padx=8)

        self.reached_canvas = tk.Canvas(reached_card, bg=BG_CARD,
                                         highlightthickness=0)
        reached_scrollbar = tk.Scrollbar(reached_card, orient=tk.VERTICAL,
                                         command=self.reached_canvas.yview)
        self.reached_inner = tk.Frame(self.reached_canvas, bg=BG_CARD)

        self.reached_inner.bind("<Configure>",
            lambda e: self.reached_canvas.configure(scrollregion=self.reached_canvas.bbox("all")))
        self.reached_canvas.create_window((0, 0), window=self.reached_inner, anchor="nw")
        self.reached_canvas.configure(yscrollcommand=reached_scrollbar.set)

        self.reached_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=4)
        reached_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.reached_canvas.bind("<Enter>", lambda e: self._bind_mousewheel(self.reached_canvas))
        self.reached_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

        btn_bar = tk.Frame(self.root, bg=BG_CARD, pady=12)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)

        btn_style = {
            "font": ("Segoe UI", 12, "bold"),
            "bd": 0,
            "padx": 20,
            "pady": 8,
            "cursor": "hand2",
            "activeforeground": TEXT_BRIGHT,
        }

        self.btn_random = tk.Button(btn_bar, text="🎲  Random",
                                    bg=ACCENT_PURPLE, fg=TEXT_BRIGHT,
                                    activebackground="#9c4dff",
                                    command=self._on_random, **btn_style)
        self.btn_random.pack(side=tk.LEFT, padx=16)

        self.btn_manual = tk.Button(btn_bar, text="✏️  Nhập tay",
                                    bg="#5d4037", fg=TEXT_BRIGHT,
                                    activebackground="#8d6e63",
                                    command=self._on_manual_input, **btn_style)
        self.btn_manual.pack(side=tk.LEFT, padx=4)

        self.btn_solve = tk.Button(btn_bar, text="⚡  Giải",
                                   bg=ACCENT_BLUE, fg=TEXT_BRIGHT,
                                   activebackground="#1a4a8a",
                                   command=self._on_solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=4)

        self.btn_prev = tk.Button(btn_bar, text="◀  Trước",
                                  bg="#37474f", fg=TEXT_PRIMARY,
                                  activebackground="#546e7a",
                                  command=self._on_prev, state=tk.DISABLED,
                                  **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=4)

        self.btn_next = tk.Button(btn_bar, text="Tiếp  ▶",
                                  bg=ACCENT_GREEN, fg="#1a1a2e",
                                  activebackground="#69f0ae",
                                  command=self._on_next, state=tk.DISABLED,
                                  **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=4)

        self.step_counter_lbl = tk.Label(btn_bar, text="",
                                         font=("Segoe UI", 11),
                                         fg=TEXT_SECONDARY, bg=BG_CARD)
        self.step_counter_lbl.pack(side=tk.RIGHT, padx=24)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def _bind_mousewheel(self, canvas):
        self._active_canvas = canvas
        self.top_root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.top_root.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if hasattr(self, '_active_canvas'):
            self._active_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel_horizontal(self, canvas):
        self._active_canvas = canvas
        self.top_root.bind_all("<MouseWheel>", self._on_mousewheel_horizontal)

    def _on_mousewheel_horizontal(self, event):
        if hasattr(self, '_active_canvas'):
            self._active_canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _draw_board(self, canvas, state, size, highlight_action=None):
        canvas.delete("all")
        cell = size / 3
        pad = 4

        for i in range(3):
            for j in range(3):
                val = state[i][j]
                x0 = j * cell + pad
                y0 = i * cell + pad
                x1 = (j + 1) * cell - pad
                y1 = (i + 1) * cell - pad

                if val == 0:
                    canvas.create_rectangle(x0, y0, x1, y1,
                                            fill=BG_CARD, outline="#333355",
                                            width=2)
                else:
                    canvas.create_rectangle(x0, y0, x1, y1,
                                            fill=TILE_COLORS[val],
                                            outline="#222244", width=1)

                    canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                       text=str(val),
                                       font=("Segoe UI", int(cell * 0.35), "bold"),
                                       fill=TILE_TEXT_COLORS[val])

    def _draw_mini_board(self, canvas, state, size):
        canvas.delete("all")
        cell = size / 3
        pad = 2
        for i in range(3):
            for j in range(3):
                val = state[i][j]
                x0 = j * cell + pad
                y0 = i * cell + pad
                x1 = (j + 1) * cell - pad
                y1 = (i + 1) * cell - pad

                if val == 0:
                    canvas.create_rectangle(x0, y0, x1, y1,
                                            fill=BG_CARD_ALT, outline="#333355")
                else:
                    canvas.create_rectangle(x0, y0, x1, y1,
                                            fill=TILE_COLORS[val], outline="")
                    canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                                       text=str(val),
                                       font=("Segoe UI", int(cell * 0.3), "bold"),
                                       fill=TILE_TEXT_COLORS[val])

    def _draw_node_card(self, parent, node, index=None, bg=BG_CARD):
        """Vẽ một thẻ node nhỏ gọn hiển thị trạng thái + thông tin."""
        algo = self.algorithm.get()
        is_greedy = 'Greedy' in algo
        is_astar  = 'A*' in algo
        is_ids    = 'IDS' in algo
        is_lddg   = 'LĐĐG' in algo
        is_lddn   = 'LĐDN' in algo
        is_ldnn   = 'LĐNN' in algo
        is_mplk   = 'MPLK' in algo

        if is_astar:
            border_color = ACCENT_PURPLE
        elif is_greedy:
            border_color = ACCENT_ORANGE
        elif is_ids:
            border_color = ACCENT_PINK
        elif is_lddg:
            border_color = ACCENT_GREEN
        elif is_lddn:
            border_color = ACCENT_CYAN
        elif is_ldnn:
            border_color = "#ff6b35"
        elif is_mplk:
            border_color = "#ffb300"
        else:
            border_color = "#333355"

        frame = tk.Frame(parent, bg=bg, padx=6, pady=4,
                         highlightbackground=border_color, highlightthickness=1)
        frame.pack(side=tk.LEFT, padx=3, pady=3)

        action_str = node.action if node.action else "Start"
        info = f"Act: {action_str}  |  g={node.depth}"
        tk.Label(frame, text=info, font=("Consolas", 8),
                 fg=TEXT_SECONDARY, bg=bg).pack(anchor="w")

        if (is_greedy or is_lddg or is_lddn or is_ldnn or is_mplk) and hasattr(node, 'h_val'):
            h_color = ACCENT_GREEN if node.h_val == 0 else ACCENT_ORANGE
            tk.Label(frame, text=f"h = {node.h_val}",
                     font=("Consolas", 8, "bold"),
                     fg=h_color, bg=bg).pack(anchor="w")

        if is_astar and hasattr(node, 'f_val'):
            f_color = ACCENT_GREEN if node.h_val == 0 else ACCENT_PURPLE
            tk.Label(frame,
                     text=f"h={node.h_val}  g={node.depth}  f={node.f_val}",
                     font=("Consolas", 8, "bold"),
                     fg=f_color, bg=bg).pack(anchor="w")

        mini = tk.Canvas(frame, width=78, height=78, bg=bg, highlightthickness=0)
        mini.pack()
        self._draw_mini_board(mini, node.state, 78)

        return frame

    def _draw_state_card(self, parent, state_tuple, bg=BG_CARD):
        """Vẽ thẻ nhỏ cho reached (chỉ hiển thị trạng thái)."""
        frame = tk.Frame(parent, bg=bg, padx=4, pady=4,
                         highlightbackground="#2e4a2e", highlightthickness=1)
        frame.pack(side=tk.LEFT, padx=2, pady=2)

        mini = tk.Canvas(frame, width=60, height=60, bg=bg, highlightthickness=0)
        mini.pack()
        state = [list(state_tuple[i]) for i in range(3)]
        self._draw_mini_board(mini, state, 60)

        return frame

    def _display_initial(self):
        self._draw_board(self.puzzle_canvas, self.initial_state, self.puzzle_size)
        self.step_label.config(text="Bước: — (chưa giải)")
        self.desc_label.config(text="Nhấn '⚡ Giải' để bắt đầu mô phỏng thuật toán.")
        self.node_info_text.config(text="(rỗng)")
        self._clear_panel(self.frontier_inner)
        self._clear_panel(self.reached_inner)
        self.frontier_count_lbl.config(text="(0)")
        self.reached_count_lbl.config(text="(0)")
        self.step_counter_lbl.config(text="")
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)

    def _display_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return

        step = self.steps[idx]
        self.current_step_idx = idx

        self.step_label.config(text=f"Bước: {idx} / {len(self.steps) - 1}")
        self.desc_label.config(text=step.description)
        self.step_counter_lbl.config(text=f"Step {idx}/{len(self.steps)-1}")

        if step.current_node:
            self._draw_board(self.puzzle_canvas, step.current_node.state, self.puzzle_size)
            action_str = step.current_node.action if step.current_node.action else "—"
            self.node_info_text.config(
                text=f"Trạng thái: {self._state_str(step.current_node.state)}\n"
                     f"Hành động:  {action_str}\n"
                     f"Số bước:    {step.current_node.depth}")
        else:
            self._draw_board(self.puzzle_canvas, self.initial_state, self.puzzle_size)
            self.node_info_text.config(text="(rỗng)")

        self._clear_panel(self.frontier_inner)
        displayed = min(len(step.frontier_list), 50) 
        self.frontier_count_lbl.config(text=f"({len(step.frontier_list)})")

        row_frame = None
        for i, node in enumerate(step.frontier_list[:displayed]):
            if i % 5 == 0:
                row_frame = tk.Frame(self.frontier_inner, bg=BG_CARD)
                row_frame.pack(fill=tk.X, anchor="w")
            self._draw_node_card(row_frame, node, i)

        if len(step.frontier_list) > displayed:
            tk.Label(self.frontier_inner,
                     text=f"... và {len(step.frontier_list) - displayed} node khác",
                     font=("Segoe UI", 9, "italic"),
                     fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", padx=8, pady=4)

        self._clear_panel(self.reached_inner)
        reached_list = list(step.reached_set)
        displayed_r = min(len(reached_list), 60)
        self.reached_count_lbl.config(text=f"({len(reached_list)})")

        row_frame_r = None
        for i, st in enumerate(reached_list[:displayed_r]):
            if i % 7 == 0:
                row_frame_r = tk.Frame(self.reached_inner, bg=BG_CARD)
                row_frame_r.pack(fill=tk.X, anchor="w")
            self._draw_state_card(row_frame_r, st)

        if len(reached_list) > displayed_r:
            tk.Label(self.reached_inner,
                     text=f"... và {len(reached_list) - displayed_r} trạng thái khác",
                     font=("Segoe UI", 9, "italic"),
                     fg=TEXT_SECONDARY, bg=BG_CARD).pack(anchor="w", padx=8, pady=4)

        self.btn_prev.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if idx < len(self.steps) - 1 else tk.DISABLED)

    def _state_str(self, state):
        return " | ".join([" ".join(str(x) for x in row) for row in state])

    def _clear_panel(self, panel):
        for widget in panel.winfo_children():
            widget.destroy()
    def _on_algo_change(self):
        self.steps = []
        self.current_step_idx = -1
        self._display_initial()

    def _on_manual_input(self):
        """Mở dialog nhập tay trạng thái ban đầu 3x3."""
        dialog = tk.Toplevel(self.top_root)
        dialog.title("Nhập trạng thái ban đầu")
        dialog.configure(bg=BG_DARK)
        dialog.resizable(False, False)
        dialog.grab_set()  # Modal

        dw, dh = 400, 530
        sw = self.top_root.winfo_screenwidth()
        sh = self.top_root.winfo_screenheight()
        dialog.geometry(f"{dw}x{dh}+{(sw-dw)//2}+{(sh-dh)//2}")

        tk.Label(dialog, text="✏️  Nhập trạng thái ban đầu",
                 font=("Segoe UI", 14, "bold"),
                 fg=ACCENT_CYAN, bg=BG_DARK).pack(pady=(14, 4))

        tk.Label(dialog,
                 text="Nhập số từ 0–8 (0 = ô trống), mỗi số xuất hiện đúng 1 lần.",
                 font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK,
                 wraplength=340).pack(pady=(0, 12))

        grid_frame = tk.Frame(dialog, bg=BG_CARD, padx=14, pady=12)
        grid_frame.pack(padx=24)

        entries = []
        for i in range(3):
            row_entries = []
            for j in range(3):
                vcmd = (dialog.register(lambda P: P == '' or (P.isdigit() and len(P) == 1)), '%P')
                e = tk.Entry(grid_frame, width=4,
                             font=("Segoe UI", 22, "bold"),
                             fg=TEXT_BRIGHT, bg=ACCENT_BLUE,
                             insertbackground=ACCENT_CYAN,
                             justify=tk.CENTER, bd=0,
                             highlightthickness=2,
                             highlightcolor=ACCENT_CYAN,
                             highlightbackground="#333355",
                             validate='key', validatecommand=vcmd)
                e.grid(row=i, column=j, padx=6, pady=5, ipady=8)
                def make_advance(r, c):
                    def advance(event):
                        if event.char.isdigit():
                            next_r, next_c = (r, c + 1) if c < 2 else (r + 1, 0)
                            if next_r < 3:
                                entries[next_r][next_c].focus_set()
                    return advance
                e.bind('<KeyRelease>', make_advance(i, j))
                row_entries.append(e)
            entries.append(row_entries)

        for i in range(3):
            for j in range(3):
                entries[i][j].insert(0, str(self.initial_state[i][j]))

        entries[0][0].focus_set()

        err_lbl = tk.Label(dialog, text="", font=("Segoe UI", 10),
                           fg=ACCENT_PINK, bg=BG_DARK)
        err_lbl.pack(pady=(6, 0))

        def validate_and_apply():
            try:
                values = []
                for i in range(3):
                    for j in range(3):
                        txt = entries[i][j].get().strip()
                        if txt == '':
                            err_lbl.config(text=f"⚠ Ô [{i+1},{j+1}] còn trống!")
                            return
                        v = int(txt)
                        if v < 0 or v > 8:
                            err_lbl.config(text=f"⚠ Giá trị phải từ 0 đến 8!")
                            return
                        values.append(v)

                if len(set(values)) != 9:
                    err_lbl.config(text="⚠ Các số phải khác nhau (0–8 mỗi số 1 lần)!")
                    return

                state = [values[i*3:(i+1)*3] for i in range(3)]

                if state == GOAL_STATE:
                    err_lbl.config(text="⚠ Đây đã là trạng thái đích rồi!")
                    return

                if not is_solvable(state):
                    err_lbl.config(text="⚠ Trạng thái này không thể giải được!")
                    return

                self.initial_state = state
                self.steps = []
                self.current_step_idx = -1
                self._display_initial()
                dialog.destroy()

            except ValueError:
                err_lbl.config(text="⚠ Chỉ nhập số nguyên!")

        btn_frame = tk.Frame(dialog, bg=BG_DARK)
        btn_frame.pack(pady=12)

        tk.Button(btn_frame, text="✅  Áp dụng",
                  font=("Segoe UI", 12, "bold"),
                  bg=ACCENT_GREEN, fg="#1a1a2e",
                  activebackground="#69f0ae",
                  bd=0, padx=18, pady=8, cursor="hand2",
                  command=validate_and_apply).pack(side=tk.LEFT, padx=8)

        tk.Button(btn_frame, text="❌  Huỷ",
                  font=("Segoe UI", 12, "bold"),
                  bg="#37474f", fg=TEXT_PRIMARY,
                  activebackground="#546e7a",
                  bd=0, padx=18, pady=8, cursor="hand2",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=8)

        dialog.bind('<Return>', lambda e: validate_and_apply())
        dialog.bind('<Escape>', lambda e: dialog.destroy())

    def _on_random(self):
        self.initial_state = generate_random_state()
        self.steps = []
        self.current_step_idx = -1
        self._display_initial()

    def _on_solve(self):
        algo = self.algorithm.get()
        self.top_root.config(cursor="wait")
        self.top_root.update()

        try:
            self.steps = solve_steps(self.initial_state, algo)
            self.current_step_idx = 0
            self._display_step(0)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi giải: {e}")
        finally:
            self.top_root.config(cursor="")

    def _on_prev(self):
        if self.current_step_idx > 0:
            self._display_step(self.current_step_idx - 1)

    def _on_next(self):
        if self.current_step_idx < len(self.steps) - 1:
            self._display_step(self.current_step_idx + 1)
# =====================================================================
# THUẬT TOÁN CSP & MÔ PHỎNG BÀI TOÁN TÔ MÀU BÀN ĐỒ (MAP COLORING)
# =====================================================================

class StepRecordCSP:
    """Lưu lại trạng thái của mỗi bước trong thuật toán CSP."""
    def __init__(self, assignment, domains, current_var, description, status):
        self.assignment = assignment      # dict: var_idx -> màu ('red', 'green', 'yellow')
        self.domains = domains            # dict: var_idx -> list màu còn lại
        self.current_var = current_var    # Tỉnh hiện tại đang xét
        self.description = description    # Mô tả chi tiết bằng tiếng Việt
        self.status = status              # 'init', 'assign', 'forward_checking', 'backtrack', 'success'

def ccw(A, B, C):
    """Kiểm tra xem 3 điểm A, B, C có ngược chiều kim đồng hồ hay không."""
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

def intersect(A, B, C, D):
    """Kiểm tra xem đoạn thẳng AB và CD có cắt nhau hay không (loại trừ trường hợp chung đỉnh)."""
    if A == C or A == D or B == C or B == D:
        return False
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def solve_csp_check(graph, variables, domains, assignment):
    """Hàm giải nhanh CSP để kiểm tra xem đồ thị có giải được bằng 3 màu hay không."""
    if len(assignment) == len(variables):
        return True
    
    # MRV heuristic
    unassigned = [v for v in variables if v not in assignment]
    curr_var = min(unassigned, key=lambda v: (len(domains[v]), -len(graph[v])))
    
    for color in domains[curr_var]:
        conflict = False
        temp_domains = copy.deepcopy(domains)
        for neighbor in graph[curr_var]:
            if neighbor not in assignment:
                if color in temp_domains[neighbor]:
                    temp_domains[neighbor].remove(color)
                    if len(temp_domains[neighbor]) == 0:
                        conflict = True
                        break
        if not conflict:
            assignment[curr_var] = color
            if solve_csp_check(graph, variables, temp_domains, assignment):
                return True
            del assignment[curr_var]
            
    return False

def generate_planar_graph():
    """Tự sinh đồ thị phẳng liên thông từ 6-10 đỉnh không giao nhau và có 3-colorability."""
    while True:
        n = random.randint(6, 10)
        cx, cy = 270, 210
        
        # Chia vòng tròn thành n phần để phân bổ góc
        angles = []
        for i in range(n):
            a_min = i * (2 * math.pi / n)
            a_max = (i + 1) * (2 * math.pi / n)
            angles.append(random.uniform(a_min, a_max))
            
        coords = []
        for a in angles:
            r = random.uniform(110, 160)
            x = cx + r * math.cos(a)
            y = cy + r * math.sin(a)
            coords.append((x, y))
            
        # Nối vòng tròn (outer boundary) để đảm bảo liên thông và phẳng
        edges = set()
        for i in range(n):
            u, v = i, (i + 1) % n
            edges.add(tuple(sorted((u, v))))
            
        # Thêm ngẫu nhiên một số dây cung (chords) không giao nhau
        chords_to_add = random.randint(1, 4)
        attempts = 0
        chords_added = 0
        while chords_added < chords_to_add and attempts < 150:
            attempts += 1
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)
            
            if u == v or abs(u - v) <= 1 or (u == 0 and v == n - 1) or (u == n - 1 and v == 0):
                continue
                
            edge = tuple(sorted((u, v)))
            if edge in edges:
                continue
                
            # Kiểm tra xem dây cung mới có cắt các cạnh hiện có hay không
            crossed = False
            pA, pB = coords[u], coords[v]
            for existing_edge in edges:
                pC, pD = coords[existing_edge[0]], coords[existing_edge[1]]
                if intersect(pA, pB, pC, pD):
                    crossed = True
                    break
                    
            if not crossed:
                edges.add(edge)
                chords_added += 1
                
        # Dựng danh sách kề
        adj = {i: [] for i in range(n)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
            
        # Xác minh đồ thị có thể tô được bằng 3 màu
        variables = list(range(n))
        domains = {i: ['red', 'green', 'yellow'] for i in range(n)}
        if solve_csp_check(adj, variables, domains, {}):
            return n, coords, adj

def solve_steps_csp(graph, coords):
    """Giải bài toán CSP từng bước và trả về danh sách StepRecordCSP."""
    n = len(coords)
    variables = list(range(n))
    domains = {i: ['red', 'green', 'yellow'] for i in range(n)}
    assignment = {}
    steps = []
    
    # Bước khởi tạo
    steps.append(StepRecordCSP(
        assignment={},
        domains=copy.deepcopy(domains),
        current_var=None,
        description="Khởi tạo: Tất cả các tỉnh đều chưa được tô màu. Miền giá trị ban đầu của mỗi tỉnh là {Đỏ, Xanh, Vàng}.",
        status="init"
    ))
    
    _backtrack_log(graph, variables, domains, assignment, steps)
    return steps

def _backtrack_log(graph, variables, domains, assignment, steps):
    if len(assignment) == len(variables):
        steps.append(StepRecordCSP(
            assignment=copy.deepcopy(assignment),
            domains=copy.deepcopy(domains),
            current_var=None,
            description="✅ ĐÃ HOÀN THÀNH: Tất cả các tỉnh đã được tô màu hợp lệ và không có mâu thuẫn kề!",
            status="success"
        ))
        return True
        
    # Heuristic MRV: chọn biến có miền giá trị nhỏ nhất, tie-breaker là bậc cao nhất
    unassigned = [v for v in variables if v not in assignment]
    curr_var = min(unassigned, key=lambda v: (len(domains[v]), -len(graph[v])))
    curr_name = chr(65 + curr_var)
    
    for color in domains[curr_var]:
        color_vn = COLOR_NAMES_VN[color]
        
        temp_assignment = copy.deepcopy(assignment)
        temp_assignment[curr_var] = color
        
        # Bước gán thử
        steps.append(StepRecordCSP(
            assignment=copy.deepcopy(temp_assignment),
            domains=copy.deepcopy(domains),
            current_var=curr_var,
            description=f"👉 Thử gán màu {color_vn} cho tỉnh {curr_name}.",
            status="assign"
        ))
        
        # Forward Checking
        temp_domains = copy.deepcopy(domains)
        temp_domains[curr_var] = [color]
        
        conflict = False
        fc_logs = []
        
        for neighbor in graph[curr_var]:
            neigh_name = chr(65 + neighbor)
            if neighbor not in temp_assignment:
                if color in temp_domains[neighbor]:
                    temp_domains[neighbor].remove(color)
                    fc_logs.append(f"loại {color_vn} khỏi miền {neigh_name}")
                    if len(temp_domains[neighbor]) == 0:
                        conflict = True
                        fc_logs.append(f"⚠️ miền {neigh_name} rỗng (mâu thuẫn!)")
                        
        if fc_logs:
            desc_fc = f"🔍 Forward Checking từ {curr_name}: {', '.join(fc_logs)}."
        else:
            desc_fc = f"🔍 Forward Checking từ {curr_name}: Không ảnh hưởng các tỉnh kề."
            
        steps.append(StepRecordCSP(
            assignment=copy.deepcopy(temp_assignment),
            domains=copy.deepcopy(temp_domains),
            current_var=curr_var,
            description=desc_fc,
            status="forward_checking"
        ))
        
        if not conflict:
            if _backtrack_log(graph, variables, temp_domains, temp_assignment, steps):
                return True
        else:
            # Ghi bước quay lui
            steps.append(StepRecordCSP(
                assignment=copy.deepcopy(assignment),
                domains=copy.deepcopy(domains),
                current_var=curr_var,
                description=f"❌ Thất bại: Rút lại màu {color_vn} của tỉnh {curr_name} do mâu thuẫn (quay lui).",
                status="backtrack"
            ))
            
    # Hết màu mà vẫn thất bại
    steps.append(StepRecordCSP(
        assignment=copy.deepcopy(assignment),
        domains=copy.deepcopy(domains),
        current_var=None,
        description=f"⏮️ Tất cả các màu thử cho tỉnh {curr_name} đều không hợp lệ. Quay lui về biến trước.",
        status="backtrack"
    ))
    return False


COLOR_MAP = {
    'red': '#ff5252',
    'green': '#00e676',
    'yellow': '#ffd740'
}

COLOR_NAMES_VN = {
    'red': 'Đỏ',
    'green': 'Xanh',
    'yellow': 'Vàng'
}

class CSPMapColoringApp:
    def __init__(self, root, top_root=None):
        self.root = root
        self.top_root = top_root if top_root else root
        self.root.configure(bg=BG_DARK)
        
        self.n = 0
        self.coords = []
        self.graph = {}
        self.steps = []
        self.current_step_idx = -1
        
        self.is_playing = False
        self.play_job = None
        self.play_speed = tk.IntVar(value=1000)
        
        self._build_ui()
        self._on_random_map()
        
    def _build_ui(self):
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        left_pane = tk.Frame(self.root, bg=BG_DARK, padx=10, pady=10)
        left_pane.grid(row=0, column=0, sticky="nsew")
        
        right_pane = tk.Frame(self.root, bg=BG_DARK, padx=10, pady=10)
        right_pane.grid(row=0, column=1, sticky="nsew")
        
        # --- Left Pane Content ---
        # Title
        header_frame = tk.Frame(left_pane, bg=BG_DARK)
        header_frame.pack(fill=tk.X, pady=(0, 6))
        
        title_lbl = tk.Label(header_frame, text="🗺️  Mô phỏng CSP Tô màu bản đồ", 
                             font=("Segoe UI", 16, "bold"), fg=ACCENT_CYAN, bg=BG_DARK)
        title_lbl.pack(anchor="w")
        
        # Info Box (Step description)
        info_frame = tk.Frame(left_pane, bg=BG_CARD_ALT, padx=12, pady=10, highlightthickness=1, highlightbackground="#333355")
        info_frame.pack(fill=tk.X, pady=(0, 6))
        
        self.step_label = tk.Label(info_frame, text="Bước: —", font=("Segoe UI", 13, "bold"), fg=ACCENT_ORANGE, bg=BG_CARD_ALT)
        self.step_label.pack(anchor="w")
        
        self.desc_label = tk.Label(info_frame, text="Nhấn '⚡ Giải CSP' để bắt đầu giải từng bước.", font=("Segoe UI", 11), fg=TEXT_PRIMARY, bg=BG_CARD_ALT, justify=tk.LEFT, wraplength=520)
        self.desc_label.pack(anchor="w", pady=(4, 0))
        
        # Canvas
        self.canvas_width = 540
        self.canvas_height = 420
        self.canvas = tk.Canvas(left_pane, width=self.canvas_width, height=self.canvas_height, bg=BG_CARD, highlightthickness=2, highlightbackground=ACCENT_BLUE)
        self.canvas.pack(fill=tk.BOTH, expand=True, pady=4)
        
        # Controls Bar
        ctrl_frame = tk.Frame(left_pane, bg=BG_CARD, pady=8, padx=10)
        ctrl_frame.pack(fill=tk.X, pady=(6, 0))
        
        btn_style = {
            "font": ("Segoe UI", 11, "bold"),
            "bd": 0,
            "padx": 12,
            "pady": 6,
            "cursor": "hand2",
            "activeforeground": TEXT_BRIGHT
        }
        
        self.btn_random = tk.Button(ctrl_frame, text="🎲 Bản đồ mới", bg=ACCENT_PURPLE, fg=TEXT_BRIGHT, activebackground="#9c4dff", command=self._on_random_map, **btn_style)
        self.btn_random.pack(side=tk.LEFT, padx=4)
        
        self.btn_solve = tk.Button(ctrl_frame, text="⚡ Giải CSP", bg=ACCENT_GREEN, fg="#1a1a2e", activebackground="#69f0ae", command=self._on_solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=4)
        
        self.btn_prev = tk.Button(ctrl_frame, text="◀ Trước", bg="#37474f", fg=TEXT_BRIGHT, activebackground="#546e7a", command=self._on_prev, state=tk.DISABLED, **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=4)
        
        self.btn_next = tk.Button(ctrl_frame, text="Tiếp ▶", bg=ACCENT_BLUE, fg=TEXT_BRIGHT, activebackground="#1a4a8a", command=self._on_next, state=tk.DISABLED, **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=4)
        
        self.btn_play = tk.Button(ctrl_frame, text="▶ Tự động", bg=ACCENT_BLUE, fg=TEXT_BRIGHT, activebackground="#1a4a8a", command=self._toggle_play, **btn_style)
        self.btn_play.pack(side=tk.LEFT, padx=4)
        
        # Speed slider
        speed_frame = tk.Frame(ctrl_frame, bg=BG_CARD)
        speed_frame.pack(side=tk.RIGHT, padx=6)
        tk.Label(speed_frame, text="Tốc độ:", font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_CARD).pack(side=tk.LEFT, padx=(0, 4))
        
        speed_slider = tk.Scale(speed_frame, from_=200, to=3000, resolution=100, orient=tk.HORIZONTAL, variable=self.play_speed, bg=BG_CARD, fg=TEXT_PRIMARY, highlightthickness=0, length=90, showvalue=False)
        speed_slider.pack(side=tk.LEFT)
        
        # --- Right Pane Content ---
        # 1. Variables status table (card)
        table_card = tk.Frame(right_pane, bg=BG_CARD, padx=12, pady=10, highlightthickness=1, highlightbackground="#333355")
        table_card.pack(fill=tk.X, pady=(0, 10))
        
        table_title = tk.Label(table_card, text="📋  MIỀN GIÁ TRỊ CÁC BIẾN", font=("Segoe UI", 12, "bold"), fg=ACCENT_CYAN, bg=BG_CARD)
        table_title.pack(anchor="w", pady=(0, 6))
        
        self.var_table_frame = tk.Frame(table_card, bg=BG_CARD_ALT, padx=6, pady=6)
        self.var_table_frame.pack(fill=tk.X)
        
        # 2. History steps list (card)
        history_card = tk.Frame(right_pane, bg=BG_CARD, padx=12, pady=10, highlightthickness=1, highlightbackground="#333355")
        history_card.pack(fill=tk.BOTH, expand=True)
        
        history_title = tk.Label(history_card, text="📜  LỊCH SỬ BƯỚC ĐI", font=("Segoe UI", 12, "bold"), fg=ACCENT_CYAN, bg=BG_CARD)
        history_title.pack(anchor="w", pady=(0, 6))
        
        # Listbox & Scrollbar container
        list_container = tk.Frame(history_card, bg=BG_CARD)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        y_scrollbar = tk.Scrollbar(list_container, orient=tk.VERTICAL)
        x_scrollbar = tk.Scrollbar(list_container, orient=tk.HORIZONTAL)
        
        self.history_listbox = tk.Listbox(list_container, bg=BG_DARK, fg=TEXT_PRIMARY, 
                                          selectbackground=ACCENT_BLUE, selectforeground=TEXT_BRIGHT, 
                                          font=("Segoe UI", 9), bd=0, highlightthickness=0,
                                          xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
        
        y_scrollbar.config(command=self.history_listbox.yview)
        x_scrollbar.config(command=self.history_listbox.xview)
        
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.history_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

    def _on_random_map(self):
        # Tạm dừng nếu đang chạy tự động
        if self.is_playing:
            self._toggle_play()
            
        # Sinh đồ thị phẳng ngẫu nhiên mới
        self.n, self.coords, self.graph = generate_planar_graph()
        self.steps = []
        self.current_step_idx = -1
        
        # Khởi tạo hiển thị bước đầu tiên
        initial_domains = {i: ['red', 'green', 'yellow'] for i in range(self.n)}
        dummy_step = StepRecordCSP({}, initial_domains, None, "Đã tạo bản đồ ngẫu nhiên mới. Nhấn 'Giải CSP' để chạy thuật toán.", "init")
        
        self.step_label.config(text="Bước: — (chưa giải)")
        self.desc_label.config(text=dummy_step.description)
        
        self._draw_map(dummy_step)
        self._update_var_table(dummy_step)
        
        self.history_listbox.delete(0, tk.END)
        self.history_listbox.insert(tk.END, "0. Nhấn 'Giải CSP' để bắt đầu...")
        
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.NORMAL)
        
    def _on_solve(self):
        self.top_root.config(cursor="wait")
        self.top_root.update()
        
        try:
            self.steps = solve_steps_csp(self.graph, self.coords)
            self.current_step_idx = 0
            
            # Populate history listbox
            self.history_listbox.delete(0, tk.END)
            for idx, step in enumerate(self.steps):
                self.history_listbox.insert(tk.END, f"{idx:02d}. {step.description}")
                
            self._display_step(0)
            self.btn_solve.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi giải CSP: {e}")
        finally:
            self.top_root.config(cursor="")
            
    def _display_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
            
        self.current_step_idx = idx
        step = self.steps[idx]
        
        self.step_label.config(text=f"Bước: {idx} / {len(self.steps) - 1}")
        self.desc_label.config(text=step.description)
        
        self._draw_map(step)
        self._update_var_table(step)
        
        # Highlight trong listbox
        self.history_listbox.selection_clear(0, tk.END)
        self.history_listbox.selection_set(idx)
        self.history_listbox.see(idx)
        
        # Cập nhật trạng thái nút bấm
        self.btn_prev.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if idx < len(self.steps) - 1 else tk.DISABLED)
        
    def _on_prev(self):
        if self.current_step_idx > 0:
            self._display_step(self.current_step_idx - 1)
            
    def _on_next(self):
        if self.current_step_idx < len(self.steps) - 1:
            self._display_step(self.current_step_idx + 1)
            
    def _toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="▶ Tự động", bg=ACCENT_BLUE)
            if self.play_job:
                self.root.after_cancel(self.play_job)
                self.play_job = None
        else:
            if not self.steps:
                self._on_solve()
            if not self.steps:
                return
            if self.current_step_idx >= len(self.steps) - 1:
                self._display_step(0)
                
            self.is_playing = True
            self.btn_play.config(text="⏸ Tạm dừng", bg="#e94560")
            self._play_next()
            
    def _play_next(self):
        if not self.is_playing:
            return
        if self.current_step_idx < len(self.steps) - 1:
            self._on_next()
            speed = self.play_speed.get()
            self.play_job = self.root.after(speed, self._play_next)
        else:
            self.is_playing = False
            self.btn_play.config(text="▶ Tự động", bg=ACCENT_BLUE)
            self.play_job = None
            
    def _on_listbox_select(self, event):
        sel = self.history_listbox.curselection()
        if sel:
            idx = sel[0]
            # Tạm dừng chạy tự động nếu người dùng click chọn trực tiếp
            if self.is_playing:
                self._toggle_play()
            self._display_step(idx)

    def _draw_map(self, step):
        self.canvas.delete("all")
        
        # 1. Vẽ các cạnh (đường nối giữa các tỉnh)
        edges = set()
        for u in self.graph:
            for v in self.graph[u]:
                edges.add(tuple(sorted((u, v))))
                
        for u, v in edges:
            x1, y1 = self.coords[u]
            x2, y2 = self.coords[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="#444466", width=2)
            
        # 2. Vẽ các đỉnh (tỉnh thành)
        for i in range(self.n):
            x, y = self.coords[i]
            name = chr(65 + i)
            assigned = step.assignment.get(i, None)
            
            # Vẽ vòng hào quang xung quanh biến đang xét
            if step.current_var == i:
                self.canvas.create_oval(x-28, y-28, x+28, y+28, outline=ACCENT_CYAN, width=3)
                
            # Thân đỉnh (tròn)
            node_fill = COLOR_MAP[assigned] if assigned else BG_CARD_ALT
            node_outline = "#ffffff" if step.current_var == i else (ACCENT_BLUE if assigned else "#444466")
            self.canvas.create_oval(x-22, y-22, x+22, y+22, fill=node_fill, outline=node_outline, width=2)
            
            # Tên đỉnh
            text_color = "#1a1a2e" if assigned else TEXT_PRIMARY
            self.canvas.create_text(x, y, text=name, font=("Segoe UI", 12, "bold"), fill=text_color)
            
            # 3. Vẽ miền giá trị còn lại (dưới dạng 3 chấm màu nhỏ dưới tỉnh)
            domain = step.domains[i]
            # Khoảng cách chấm dưới tỉnh
            dot_y = y + 29
            # Chấm 1: Đỏ
            r_fill = COLOR_MAP['red'] if 'red' in domain else "#1a1a2e"
            r_outline = COLOR_MAP['red'] if 'red' in domain else "#444466"
            self.canvas.create_oval(x-14, dot_y-4, x-6, dot_y+4, fill=r_fill, outline=r_outline, width=1)
            
            # Chấm 2: Xanh
            g_fill = COLOR_MAP['green'] if 'green' in domain else "#1a1a2e"
            g_outline = COLOR_MAP['green'] if 'green' in domain else "#444466"
            self.canvas.create_oval(x-4, dot_y-4, x+4, dot_y+4, fill=g_fill, outline=g_outline, width=1)
            
            # Chấm 3: Vàng
            y_fill = COLOR_MAP['yellow'] if 'yellow' in domain else "#1a1a2e"
            y_outline = COLOR_MAP['yellow'] if 'yellow' in domain else "#444466"
            self.canvas.create_oval(x+6, dot_y-4, x+14, dot_y+4, fill=y_fill, outline=y_outline, width=1)

    def _update_var_table(self, step):
        # Xóa các dòng cũ
        for widget in self.var_table_frame.winfo_children():
            widget.destroy()
            
        # Vẽ Header của bảng miền giá trị
        tk.Label(self.var_table_frame, text="Tỉnh", font=("Segoe UI", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD_ALT, width=6, anchor="w").grid(row=0, column=0, padx=4, pady=2)
        tk.Label(self.var_table_frame, text="Màu đã tô", font=("Segoe UI", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD_ALT, width=10, anchor="w").grid(row=0, column=1, padx=4, pady=2)
        tk.Label(self.var_table_frame, text="Miền giá trị", font=("Segoe UI", 9, "bold"), fg=ACCENT_CYAN, bg=BG_CARD_ALT, width=18, anchor="w").grid(row=0, column=2, padx=4, pady=2)
        
        # Điền thông tin từng tỉnh thành
        for i in range(self.n):
            name = chr(65 + i)
            assigned = step.assignment.get(i, None)
            assigned_text = COLOR_NAMES_VN[assigned] if assigned else "—"
            assigned_color = COLOR_MAP[assigned] if assigned else TEXT_SECONDARY
            
            domain = step.domains[i]
            domain_text = ", ".join([COLOR_NAMES_VN[c] for c in domain])
            if not domain:
                domain_text = "⚠️ Rỗng"
                
            is_curr = (step.current_var == i)
            row_bg = "#1f3154" if is_curr else BG_CARD_ALT
            row_fg = TEXT_BRIGHT if is_curr else TEXT_PRIMARY
            
            lbl_name = tk.Label(self.var_table_frame, text=name, font=("Segoe UI", 9, "bold" if is_curr else "normal"), fg=ACCENT_ORANGE if is_curr else row_fg, bg=row_bg, width=6, anchor="w")
            lbl_name.grid(row=i+1, column=0, padx=4, pady=1)
            
            lbl_color = tk.Label(self.var_table_frame, text=assigned_text, font=("Segoe UI", 9, "bold" if assigned else "normal"), fg=assigned_color, bg=row_bg, width=10, anchor="w")
            lbl_color.grid(row=i+1, column=1, padx=4, pady=1)
            
            lbl_domain = tk.Label(self.var_table_frame, text=domain_text, font=("Segoe UI", 9), fg="#ff5252" if not domain else row_fg, bg=row_bg, width=18, anchor="w")
            lbl_domain.grid(row=i+1, column=2, padx=4, pady=1)




class StepRecordCaro:
    def __init__(self, board, depth, is_maximizing, action, alpha, beta, score, description):
        self.board = list(board)
        self.depth = depth
        self.is_maximizing = is_maximizing
        self.action = action
        self.alpha = alpha
        self.beta = beta
        self.score = score
        self.description = description

class CaroMinimax:
    def __init__(self, root, top_root=None):
        self.root = root
        self.top_root = top_root if top_root else root
        self.root.configure(bg=BG_DARK)
        
        self.algorithm = tk.StringVar(value="Alpha-Beta")
        self.board = [' '] * 9
        self.current_winner = None
        
        self.steps = []
        self.current_step_idx = -1
        self.buttons = []
        
        self._build_ui()
        self._display_initial()
        
    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG_CARD, pady=12)
        header.pack(fill=tk.X, padx=0)
        
        title_lbl = tk.Label(header, text="⭕ Cờ Caro (Minimax Simulator)",
                             font=("Segoe UI", 20, "bold"), fg=ACCENT_CYAN, bg=BG_CARD)
        title_lbl.pack(side=tk.LEFT, padx=24)
        
        algo_container = tk.Frame(header, bg=BG_CARD)
        algo_container.pack(side=tk.RIGHT, padx=24)
        
        tk.Label(algo_container, text="Thuật toán:", font=("Segoe UI", 12), fg=TEXT_SECONDARY, bg=BG_CARD).pack(side=tk.LEFT, padx=(0, 8))
        
        style = ttk.Style()
        style.configure("Caro.TRadiobutton", background=BG_CARD, foreground=TEXT_PRIMARY, font=("Segoe UI", 12, "bold"))
        
        ttk.Radiobutton(algo_container, text="Minimax", variable=self.algorithm, value="Minimax", style="Caro.TRadiobutton", command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo_container, text="Alpha-Beta", variable=self.algorithm, value="Alpha-Beta", style="Caro.TRadiobutton", command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo_container, text="Expectimax", variable=self.algorithm, value="Expectimax", style="Caro.TRadiobutton", command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        ttk.Radiobutton(algo_container, text="Expectimax", variable=self.algorithm, value="Expectimax", style="Caro.TRadiobutton", command=self._on_algo_change).pack(side=tk.LEFT, padx=6)
        
        main_frame = tk.Frame(self.root, bg=BG_DARK)
        
        btn_bar = tk.Frame(self.root, bg=BG_CARD, pady=12)
        btn_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        left_frame = tk.Frame(main_frame, bg=BG_DARK)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.step_label = tk.Label(left_frame, text="Bước: —", font=("Segoe UI", 13, "bold"), fg=ACCENT_ORANGE, bg=BG_DARK, anchor="w")
        self.step_label.pack(fill=tk.X, pady=(0, 4))
        
        self.desc_label = tk.Label(left_frame, text="", font=("Segoe UI", 11), fg=TEXT_SECONDARY, bg=BG_DARK, anchor="w", wraplength=320, justify=tk.LEFT)
        self.desc_label.pack(fill=tk.X, pady=(0, 8))
        
        self.board_frame = tk.Frame(left_frame, bg=BG_CARD, padx=10, pady=10)
        self.board_frame.pack(pady=4)
        
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.board_frame, text=' ', font=('Arial', 40, 'bold'), width=4, height=1,
                                bg='#1a1a2e', fg='white', bd=2, relief=tk.RAISED,
                                command=lambda row=i, col=j: self.on_click(row, col))
                btn.grid(row=i, column=j, padx=4, pady=4)
                self.buttons.append(btn)
                
        right_frame = tk.Frame(main_frame, bg=BG_DARK)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        log_card = tk.Frame(right_frame, bg=BG_CARD, padx=12, pady=8)
        log_card.pack(fill=tk.BOTH, expand=True)
        
        log_header = tk.Frame(log_card, bg=BG_CARD)
        log_header.pack(fill=tk.X)
        tk.Label(log_header, text="🔍 LỊCH SỬ DUYỆT CÂY MINIMAX", font=("Segoe UI", 12, "bold"), fg=ACCENT_PINK, bg=BG_CARD).pack(side=tk.LEFT)
        self.log_count_lbl = tk.Label(log_header, text="(0 node)", font=("Segoe UI", 11), fg=TEXT_SECONDARY, bg=BG_CARD)
        self.log_count_lbl.pack(side=tk.LEFT, padx=8)
        
        self.log_canvas = tk.Canvas(log_card, bg=BG_CARD, highlightthickness=0)
        log_scrollbar = tk.Scrollbar(log_card, orient=tk.VERTICAL, command=self.log_canvas.yview)
        self.log_inner = tk.Frame(self.log_canvas, bg=BG_CARD)
        
        self.log_inner.bind("<Configure>", lambda e: self.log_canvas.configure(scrollregion=self.log_canvas.bbox("all")))
        self.log_canvas.create_window((0, 0), window=self.log_inner, anchor="nw")
        self.log_canvas.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=4)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_canvas.bind("<Enter>", lambda e: self._bind_mousewheel(self.log_canvas))
        self.log_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())
        
        btn_style = {"font": ("Segoe UI", 12, "bold"), "bd": 0, "padx": 20, "pady": 8, "cursor": "hand2"}
        
        self.btn_reset = tk.Button(btn_bar, text="🔄 Reset", bg=ACCENT_PURPLE, fg=TEXT_BRIGHT, command=self.reset_game, **btn_style)
        self.btn_reset.pack(side=tk.LEFT, padx=16)
        
        self.btn_manual = tk.Button(btn_bar, text="✏️ Nhập tay", bg="#5d4037", fg=TEXT_BRIGHT, command=self._on_manual_input, **btn_style)
        self.btn_manual.pack(side=tk.LEFT, padx=4)
        
        self.btn_solve = tk.Button(btn_bar, text="⚡ AI Giải", bg=ACCENT_BLUE, fg=TEXT_BRIGHT, command=self._on_solve, **btn_style)
        self.btn_solve.pack(side=tk.LEFT, padx=4)
        
        self.btn_prev = tk.Button(btn_bar, text="◀ Trước", bg="#37474f", fg=TEXT_PRIMARY, command=self._on_prev, state=tk.DISABLED, **btn_style)
        self.btn_prev.pack(side=tk.LEFT, padx=4)
        
        self.btn_next = tk.Button(btn_bar, text="Tiếp ▶", bg=ACCENT_GREEN, fg="#1a1a2e", command=self._on_next, state=tk.DISABLED, **btn_style)
        self.btn_next.pack(side=tk.LEFT, padx=4)
        
        self.step_counter_lbl = tk.Label(btn_bar, text="", font=("Segoe UI", 11), fg=TEXT_SECONDARY, bg=BG_CARD)
        self.step_counter_lbl.pack(side=tk.RIGHT, padx=24)

    def _bind_mousewheel(self, canvas):
        self._active_canvas = canvas
        self.top_root.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.top_root.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if hasattr(self, '_active_canvas'):
            self._active_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_algo_change(self):
        self.reset_game()
        
    def reset_game(self):
        self.board = [' '] * 9
        self.current_winner = None
        self.steps = []
        self.current_step_idx = -1
        self._display_initial()
        
    def _display_initial(self):
        self._update_board_ui(self.board)
        self.step_label.config(text="Bước: — (Đang chơi)")
        self.desc_label.config(text="Lượt của bạn (X). Hãy click vào ô trống hoặc nhấn 'AI Giải'.")
        self._clear_log()
        self.log_count_lbl.config(text="(0 node)")
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)
        self.step_counter_lbl.config(text="")
        
    def _update_board_ui(self, board, highlight_idx=None):
        for i in range(9):
            letter = board[i]
            color = ACCENT_CYAN if letter == 'X' else ACCENT_PINK
            bg_color = "#1f3154" if letter == 'X' else ("#4a192c" if letter == 'O' else "#1a1a2e")
            if i == highlight_idx:
                bg_color = ACCENT_GREEN
            self.buttons[i].config(text=letter, fg=color, bg=bg_color)
            
    def _clear_log(self):
        for w in self.log_inner.winfo_children():
            w.destroy()
            
    def _add_log_item(self, step_record, idx):
        frame = tk.Frame(self.log_inner, bg=BG_CARD_ALT, padx=8, pady=6, highlightbackground="#333355", highlightthickness=1)
        frame.pack(fill=tk.X, pady=2, padx=4)
        
        header = f"[{idx}] Độ sâu (Depth): {step_record.depth} | Lượt: {'O (Max)' if step_record.is_maximizing else 'X (Min)'}"
        if step_record.action is not None:
            header += f" | Thử đánh ô số: {step_record.action}"
            
        tk.Label(frame, text=header, font=("Segoe UI", 10, "bold"), fg=ACCENT_CYAN if step_record.is_maximizing else ACCENT_PINK, bg=BG_CARD_ALT).pack(anchor="w")
        
        info = f"Điểm số (Score): {step_record.score}"
        if self.algorithm.get() == "Alpha-Beta":
            info += f" | α = {step_record.alpha}, β = {step_record.beta}"
            
        tk.Label(frame, text=info, font=("Consolas", 10), fg=TEXT_PRIMARY, bg=BG_CARD_ALT).pack(anchor="w")
        tk.Label(frame, text=step_record.description, font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_CARD_ALT).pack(anchor="w")

    def _display_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
        step = self.steps[idx]
        self.current_step_idx = idx
        
        self.step_label.config(text=f"Bước: {idx} / {len(self.steps) - 1}")
        self.desc_label.config(text=step.description)
        self.step_counter_lbl.config(text=f"Step {idx}/{len(self.steps)-1}")
        
        highlight = step.action
        if idx == len(self.steps) - 1:
            highlight = step.action # Final move
        self._update_board_ui(step.board, highlight)
        
        self.btn_prev.config(state=tk.NORMAL if idx > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if idx < len(self.steps) - 1 else tk.DISABLED)

    def on_click(self, row, col):
        idx = row * 3 + col
        if self.board[idx] == ' ' and not self.current_winner and self.current_step_idx == -1:
            self.make_move(idx, 'X')
            if not self.current_winner and ' ' in self.board:
                self.desc_label.config(text="AI đang suy nghĩ... đang nạp dữ liệu log.")
                self.root.update()
                self.simulate_ai_move()
                self._display_step(0)

    def make_move(self, idx, letter):
        self.board[idx] = letter
        self._update_board_ui(self.board)
        
        if self.check_winner(self.board, letter):
            self.current_winner = letter
            messagebox.showinfo("Kết thúc", f"Người chơi {letter} chiến thắng!")
        elif ' ' not in self.board:
            messagebox.showinfo("Kết thúc", "Hòa!")

    def check_winner(self, board, player):
        wins = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        return any(all(board[i] == player for i in c) for c in wins)

    def get_empty(self, board):
        return [i for i, spot in enumerate(board) if spot == ' ']

    def simulate_ai_move(self):
        self.steps = []
        self._clear_log()
        
        self.steps.append(StepRecordCaro(self.board, 0, True, None, -math.inf, math.inf, 0, "Bắt đầu tìm kiếm Minimax tại gốc."))
        
        if self.algorithm.get() == "Minimax":
            best_move = self._minimax_log(self.board, 0, True, -math.inf, math.inf)
        elif self.algorithm.get() == "Alpha-Beta":
            best_move = self._alphabeta_log(self.board, 0, True, -math.inf, math.inf)
        else:
            best_move = self._expectimax_log(self.board, 0, True)
            
        final_board = list(self.board)
        if best_move is not None:
            final_board[best_move] = 'O'
            self.board[best_move] = 'O'
            
        self.steps.append(StepRecordCaro(final_board, 0, True, best_move, -math.inf, math.inf, 0, f"✅ Đã tìm thấy nước đi tối ưu: {best_move}"))
        
        self.log_count_lbl.config(text=f"({len(self.steps)} node)")
        
        for i, st in enumerate(self.steps):
            if i > 800:
                tk.Label(self.log_inner, text="... Vượt giới hạn hiển thị log để tránh giật lag", fg="red", bg=BG_CARD_ALT).pack()
                break
            self._add_log_item(st, i)
            
        self.current_step_idx = 0
        
        if self.check_winner(self.board, 'O'):
            self.current_winner = 'O'
        elif ' ' not in self.board:
            self.current_winner = 'Draw'

    def _minimax_log(self, board, depth, is_max, alpha, beta):
        if self.check_winner(board, 'O'): return 10 - depth
        if self.check_winner(board, 'X'): return depth - 10
        if ' ' not in board: return 0

        if is_max:
            best = -math.inf
            best_move = None
            for move in self.get_empty(board):
                board[move] = 'O'
                self.steps.append(StepRecordCaro(board, depth+1, False, move, alpha, beta, best, f"O thử đánh ô {move}"))
                score = self._minimax_log(board, depth + 1, False, alpha, beta)
                board[move] = ' '
                
                if score > best:
                    best = score
                    best_move = move
                    
                self.steps.append(StepRecordCaro(board, depth, True, None, alpha, beta, best, f"O lùi lại. Điểm nhánh {move} là {score}. Điểm tốt nhất của O hiện = {best}"))
            return best_move if depth == 0 else best
        else:
            best = math.inf
            for move in self.get_empty(board):
                board[move] = 'X'
                self.steps.append(StepRecordCaro(board, depth+1, True, move, alpha, beta, best, f"X thử đánh ô {move}"))
                score = self._minimax_log(board, depth + 1, True, alpha, beta)
                board[move] = ' '
                
                if score < best:
                    best = score
                    
                self.steps.append(StepRecordCaro(board, depth, False, None, alpha, beta, best, f"X lùi lại. Điểm nhánh {move} là {score}. Điểm tốt nhất của X hiện = {best}"))
            return best

    def _alphabeta_log(self, board, depth, is_max, alpha, beta):
        if self.check_winner(board, 'O'): return 10 - depth
        if self.check_winner(board, 'X'): return depth - 10
        if ' ' not in board: return 0

        if is_max:
            best = -math.inf
            best_move = None
            for move in self.get_empty(board):
                board[move] = 'O'
                self.steps.append(StepRecordCaro(board, depth+1, False, move, alpha, beta, best, f"O thử đánh ô {move}"))
                score = self._alphabeta_log(board, depth + 1, False, alpha, beta)
                board[move] = ' '
                
                if score > best:
                    best = score
                    best_move = move
                
                alpha = max(alpha, score)
                self.steps.append(StepRecordCaro(board, depth, True, None, alpha, beta, best, f"O lùi lại. Điểm nhánh = {score}. Alpha mới = {alpha}"))
                
                if beta <= alpha:
                    self.steps.append(StepRecordCaro(board, depth, True, None, alpha, beta, best, f"✂️ Cắt tỉa nhánh! (beta {beta} <= alpha {alpha})"))
                    break
            return best_move if depth == 0 else best
        else:
            best = math.inf
            for move in self.get_empty(board):
                board[move] = 'X'
                self.steps.append(StepRecordCaro(board, depth+1, True, move, alpha, beta, best, f"X thử đánh ô {move}"))
                score = self._alphabeta_log(board, depth + 1, True, alpha, beta)
                board[move] = ' '
                
                if score < best:
                    best = score
                    
                beta = min(beta, score)
                self.steps.append(StepRecordCaro(board, depth, False, None, alpha, beta, best, f"X lùi lại. Điểm nhánh = {score}. Beta mới = {beta}"))
                
                if beta <= alpha:
                    self.steps.append(StepRecordCaro(board, depth, False, None, alpha, beta, best, f"✂️ Cắt tỉa nhánh! (beta {beta} <= alpha {alpha})"))
                    break
            return best


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


    def _on_prev(self):
        if self.current_step_idx > 0:
            self._display_step(self.current_step_idx - 1)
            
    def _on_next(self):
        if self.current_step_idx < len(self.steps) - 1:
            self._display_step(self.current_step_idx + 1)
            
    def _on_solve(self):
        if self.current_winner is not None or ' ' not in self.board:
            messagebox.showinfo("Lỗi", "Ván cờ đã kết thúc.")
            return
            
        self.simulate_ai_move()
        self._display_step(len(self.steps) - 1)
        
    def _on_manual_input(self):
        dialog = tk.Toplevel(self.top_root)
        dialog.title("Nhập tay bàn cờ Caro")
        dialog.configure(bg=BG_DARK)
        
        dw, dh = 350, 450
        sw = self.top_root.winfo_screenwidth()
        sh = self.top_root.winfo_screenheight()
        dialog.geometry(f"{dw}x{dh}+{(sw-dw)//2}+{(sh-dh)//2}")
        dialog.grab_set()
        
        tk.Label(dialog, text="Nhập X, O hoặc để trống", font=("Segoe UI", 12, "bold"), fg=ACCENT_CYAN, bg=BG_DARK).pack(pady=10)
        
        grid_f = tk.Frame(dialog, bg=BG_CARD, padx=10, pady=10)
        grid_f.pack()
        
        entries = []
        for i in range(3):
            for j in range(3):
                e = tk.Entry(grid_f, width=2, font=("Segoe UI", 30, "bold"), justify=tk.CENTER, bg=BG_CARD_ALT, fg=TEXT_BRIGHT)
                e.insert(0, self.board[i*3+j].replace(' ', ''))
                e.grid(row=i, column=j, padx=4, pady=4)
                entries.append(e)
                
        def apply():
            vals = [e.get().upper() for e in entries]
            for v in vals:
                if v not in ['X', 'O', '']:
                    messagebox.showerror("Lỗi", "Chỉ nhập chữ X hoặc chữ O (hoặc để trống)!")
                    return
            self.board = [v if v else ' ' for v in vals]
            self.current_winner = None
            self.steps = []
            self.current_step_idx = -1
            self._display_initial()
            dialog.destroy()
            
        tk.Button(dialog, text="Áp dụng thế cờ", bg=ACCENT_GREEN, command=apply, font=("Segoe UI", 12, "bold")).pack(pady=20)
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
            # Chance node
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


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trình Mô Phỏng Giải Thuật Tìm Kiếm (8-Puzzle) & CSP & Cờ Caro")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(1200, 880)
        self.root.resizable(True, True)
        
        # Thiết lập style cho Notebook (Thẻ Tab)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_CARD, foreground=TEXT_SECONDARY,
                        font=("Segoe UI", 11, "bold"), padding=[16, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", BG_CARD_ALT)],
                  foreground=[("selected", ACCENT_CYAN)])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Các Frame Tab tương ứng
        self.tab1 = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab2 = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab3 = tk.Frame(self.notebook, bg=BG_DARK)
        
        self.notebook.add(self.tab1, text="🧩 8-Puzzle Simulator")
        self.notebook.add(self.tab2, text="🗺️ CSP Map Coloring")
        self.notebook.add(self.tab3, text="⭕ Cờ Caro (Minimax)")
        
        # Khởi tạo các ứng dụng con bên trong Tab
        self.puzzle_app = PuzzleApp(self.tab1, top_root=self.root)
        self.csp_app = CSPMapColoringApp(self.tab2, top_root=self.root)
        self.caro_app = CaroMinimax(self.tab3)


if __name__ == "__main__":
    root = tk.Tk()
    win_w, win_h = 1200, 880
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - win_w) // 2
    y = (sh - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    app = MainApp(root)
    root.mainloop()
