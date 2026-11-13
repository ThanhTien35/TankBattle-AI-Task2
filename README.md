# Tank Battle AI – Simultaneous Actions (Task 2)

**Quy tắc đã sửa theo xác nhận giảng viên:** Mỗi game cycle, **cả P1 và P2 cùng chọn một action từ cùng trạng thái**, sau đó Game Engine áp dụng đồng thời. Không có P1 đi trước rồi P2 nhìn thấy hành động đó. HP giữ nguyên: Tank 6, Base 9, Wall 3; đạn đi tối đa 3 ô/cycle.

## 1. Cài đặt và chạy (Windows PowerShell / VS Code)

Mở terminal trong thư mục chứa `main.py`:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

Các lần sau (nếu đã activate `.venv`):

```powershell
python main.py
```

Chạy thử **P1/P2 đồng thời** trong terminal, không cần PyGame:

```powershell
python main.py --headless --max-steps 10
```

Chọn map, thuật toán và vị trí spawn:

```powershell
python main.py --map "Open Arena" --depth 2 --p0 "Heuristic Alpha-Beta" --p1 "Heuristic Minimax"
python main.py --spawn random --seed 2026
```

Chế độ demo mặc định **Depth 2**, vì mỗi cycle có 6×6=36 cặp action; Depth 3 có thể chậm hơn nhiều.

## 2. Lệnh Benchmark và Tests (ngắn gọn)

```powershell
python benchmark.py                  # Benchmark 4 thuat toan, depth 2
python benchmark.py --all            # Benchmark depth 1, 2, 3 (co the cham)
python benchmark.py --tactical       # Benchmark tinh huong
python benchmark.py --tournament     # Tournament depth 1, 3 map
python benchmark.py --test           # Unit Tests cho game dong thoi
python benchmark.py --depth 3        # Tuy chinh depth
python benchmark.py --strict-search  # Khong dung root tactical bonus
```

`results/benchmark.csv`, `results/benchmark_all.csv`, `results/benchmark_tactical.csv`, `results/tournament.csv` và `results/tournament_summary.csv` được xuất tự động. Kết quả cũ từ phiên bản luân phiên **không được so trực tiếp** với kết quả mới do đơn vị depth và cơ chế cập nhật đã thay đổi.

## 3. Điều khiển

- `SPACE`: Play/Pause; `N`: Step **một cycle (hai action)**; `R`: Reset; `M`: đổi map; `G`: random spawn; `L`: Battle Log/Replay; `ESC`: thoát.
- Human: `W/A/S/D` di chuyển, `F` bắn, `X` đứng yên. Khi có Human, action được nhập trước khi cycle cập nhật.
- External Agent: `python main.py --p0 External --p1 "Heuristic Alpha-Beta" --external-module tankbattle.external_agents.example_agent`

## 4. Cơ chế đồng thời

1. Hai agent cùng nhận bản sao của `GameState` hiện tại và chọn `a0`, `a1` độc lập.
2. Di chuyển xử lý đồng thời; hai Tank không thể vào cùng ô, hoán đổi ô hay xuyên vật cản.
3. Hai phát bắn (nếu có) xuất hiện đồng thời. Toàn bộ đạn được cập nhật từng ô, tối đa 3 ô/cycle; sát thương cùng bước được áp dụng cùng lúc.
4. Kiểm tra thắng/thua/hòa sau cycle. Nếu cả hai Tank/Base cùng bị hạ ở một bước đạn, kết quả hòa.
5. Mỗi cycle tăng bộ đếm một đơn vị; mặc định giới hạn 160 cycle để demo tránh kéo dài vô hạn.

## 5. Thuật toán tìm kiếm

| Mode | Hàm đánh giá | Cắt tỉa |
|---|---|---|
| Minimax | Chỉ terminal | Không |
| Alpha-Beta | Chỉ terminal | Có |
| Heuristic Minimax | HP, vị trí, đường bắn, nguy cơ | Không |
| Heuristic Alpha-Beta | Như trên | Có |

Với game đồng thời, thuật toán sử dụng **pure-strategy maximin** theo cặp action:

`V(s) = max_{a0} min_{a1} V(T(s, a0, a1))` (đổi vai tương ứng cho P2).

Đây **không phải** Minimax luân phiên thông thường và **không phải Nash hỗn hợp**. Hai agent tính quyết định từ cùng trạng thái; benchmark ghi nhận thời gian và node của mỗi agent riêng. `--strict-search` loại bỏ hỗ trợ lựa chọn gameplay ở node gốc.

Depth đếm số **cycle**, vì vậy Depth 2 của bản mới không tương đương Depth 2 của bản cũ. Giới hạn ở Depth 1–2 khi demo, tăng lên 3 khi cần phân tích.

## 6. Cấu trúc

- `main.py`: chạy giao diện hoặc headless.
- `tankbattle/engine/game.py`: `apply_joint_actions(state, action0, action1)` – xử lý đồng thời.
- `tankbattle/agents/search.py`: bốn mode tìm kiếm maximin.
- `tankbattle/ui/pygame_app.py`: giao diện, Replay, CSV log.
- `benchmarks/` và `benchmark.py`: đo hiệu suất / đấu giải.
- `tests/test_simultaneous.py`: unit tests luật simultaneous.
- `docs/THUAT_TOAN.md`: lý thuyết thuật toán.

**Lưu ý:** Kết quả và tính phù hợp cuối cùng cần kiểm tra trên máy nộp bài; tuân thủ quy định môn học về công cụ hỗ trợ.
