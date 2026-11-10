# Hướng dẫn đọc mã nguồn thuật toán

**File chính:** `tankbattle/agents/search.py`

Bốn chế độ dùng chung `SearchAgent` để tránh trùng lặp mã và bảo đảm đánh giá nhất quán.
Mỗi chế độ được chọn bằng `mode` ở hàm `__init__`:

| Chế độ | `use_pruning` | `use_heuristic` |
|---|---|---|
| Minimax | False | False |
| Alpha-Beta | True | False |
| Heuristic Minimax | False | True |
| Heuristic Alpha-Beta | True | True |

## Các bước khi AI chọn hành động

1. `choose_action(state)`: liệt kê 6 hành động, tạo trạng thái kế tiếp.
2. `_search(...)`: duyệt cây trò chơi đệ quy; MAX chọn điểm lớn nhất, MIN chọn nhỏ nhất.
3. `if self.use_pruning`: cập nhật alpha/beta và cắt nhánh khi `alpha >= beta`.
4. `evaluate(...)`: terminal utility cho mọi thuật toán; các chế độ Heuristic thêm HP, vị trí tấn công, nguy cơ trúng đạn.
5. `_root_rank(...)`: hỗ trợ chế độ gameplay tránh lặp hành động vô ích.

Các chú thích trong file dùng chữ không dấu để dễ tìm kiếm:
`THUAT TOAN 1`, `THUAT TOAN 2`, `THUAT TOAN 3`, `THUAT TOAN 4`.

**Lưu ý thực nghiệm:** Mặc định có hỗ trợ gameplay tại tầng gốc. Dùng `--strict-search` nếu cần so sánh bốn thuật toán không có hỗ trợ này. Điều kiện và vị trí spawn phải giống nhau khi so sánh.

## Nơi đọc các phần còn lại

- `tankbattle/engine/model.py`: GameState và HP theo đề (6/9/3).
- `tankbattle/engine/game.py`: hành động, đạn, va chạm, điều kiện kết thúc.
- `tankbattle/engine/maps.py`: ba bản đồ, Balanced Spawn, Random Spawn với seed.
- `tankbattle/ui/pygame_app.py`: giao diện PyGame, Replay.
- `benchmarks/compare.py`: đo thời gian/nodes/prunes.
- `benchmarks/tournament.py`: đối đầu và đổi vị trí P1/P2.
