# TANK BATTLE AI – ADVERSARIAL SEARCH

**Course:** Introduction to Artificial Intelligence  
**Project:** Task 2 – Tank Battle Game  
**Language:** Python 3.10+  
**Interface:** PyGame (`pygame-ce`)

Ứng dụng Tank Battle AI sử dụng bốn thuật toán tìm kiếm đối kháng: Minimax, Alpha-Beta Pruning, Heuristic Minimax và Heuristic Alpha-Beta.

---

# 1. INSTALLATION & RUN

## 1.1. Yêu cầu môi trường

- Python 3.10 trở lên (khuyến nghị Python 3.11 hoặc 3.12)
- Visual Studio Code hoặc IDE hỗ trợ Python
- Git (nếu clone từ GitHub)

Mở Terminal tại thư mục gốc chứa `main.py`.

**Kiểm tra phiên bản Python:**

```powershell
python --version
```

## 1.2. Cài đặt lần đầu

**Windows – PowerShell:**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Kích hoạt môi trường ảo:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Sau khi kích hoạt thành công, Terminal thường xuất hiện `(.venv)`.

## 1.3. Chạy ứng dụng

```powershell
python main.py
```

Khởi động giao diện Tank Battle với cấu hình mặc định.

**Chạy trên bản đồ cụ thể:**

```powershell
python main.py --map "Classic Battlefield"
```

```powershell
python main.py --map "Open Arena"
```

```powershell
python main.py --map "Tactical Maze"
```

**Chọn thuật toán và Search Depth:**

```powershell
python main.py --depth 3 --p0 Minimax --p1 Alpha-Beta
```

**Chạy hai thuật toán Heuristic:**

```powershell
python main.py --depth 3 --p0 "Heuristic Minimax" --p1 "Heuristic Alpha-Beta"
```

**Random Spawn với seed cố định:**

```powershell
python main.py --spawn random --seed 2026
```

Seed giúp tái hiện cùng vị trí xuất phát để phục vụ kiểm thử.

---

# 2. BENCHMARK & EXPERIMENTS

Các lệnh dưới đây sử dụng file `benchmark.py` ở thư mục gốc.

## 2.1. Quick Benchmark

```powershell
python benchmark.py
```

So sánh bốn thuật toán trên ba bản đồ, sử dụng Depth 3 và số lần lặp mặc định.

Kết quả lưu tại:

`results/benchmark.csv`

## 2.2. Full Benchmark

```powershell
python benchmark.py --all
```

So sánh bốn thuật toán với Depth 2, 3 và 4.

Kết quả lưu tại:

`results/benchmark_all.csv`

## 2.3. Tactical Benchmark

```powershell
python benchmark.py --tactical
```

Kiểm tra khả năng lựa chọn hành động trong các tình huống chiến thuật:

- Incoming Bullet – Né đạn
- Forced Flank – Di chuyển tìm góc tấn công
- Finishing Shot – Kết liễu đối thủ
- Brick Barrier – Xử lý vật cản

Kết quả lưu tại:

`results/benchmark_tactical.csv`

## 2.4. AI Tournament

```powershell
python benchmark.py --tournament
```

Cho bốn thuật toán thi đấu trên ba bản đồ và đổi vị trí P1/P2.

Kết quả:

- `results/tournament.csv` – Thống kê từng trận đấu.
- `results/tournament_summary.csv` – Tổng hợp kết quả các thuật toán.

## 2.5. Custom Benchmark

**Thay đổi Search Depth:**

```powershell
python benchmark.py --depth 4
```

**Thay đổi số lần lặp:**

```powershell
python benchmark.py --repeats 10
```

**Strict Search:**

```powershell
python benchmark.py --all --strict-search
```

Strict Search được sử dụng để kiểm tra thuật toán tìm kiếm mà không áp dụng các cơ chế hỗ trợ lựa chọn hành động ở node gốc.

Nên tách riêng kết quả Strict Search và Gameplay Mode khi đánh giá.

## 2.6. Unit Tests

```powershell
python benchmark.py --test
```

Chạy toàn bộ Unit Tests để kiểm tra Game Engine, luật chơi, thuật toán và các thành phần liên quan.

Kết quả thành công:

```text
Ran 40 tests

OK
```

Số lượng bài kiểm thử có thể thay đổi khi cập nhật project.

---

# 3. GAME CONTROLS

| Phím / Chức năng | Mô tả |
|---|---|
| SPACE | Play / Pause |
| N | Step – Chạy một lượt |
| R | Reset trận hiện tại |
| G | Tạo trận mới với Random Spawn |
| M | Chuyển bản đồ |
| L | Mở Battle Log / Replay |
| + / - | Tăng / giảm tốc độ |
| ESC | Thoát ứng dụng |

**Human Mode:**

| Phím | Action |
|---|---|
| W / ↑ | MOVE_UP |
| S / ↓ | MOVE_DOWN |
| A / ← | MOVE_LEFT |
| D / → | MOVE_RIGHT |
| F / ENTER | FIRE |
| X | STAY |

---

# 4. EXTERNAL AGENT

External Mode cho phép sử dụng thuật toán AI từ module Python bên ngoài.

**Kiểm tra Agent mẫu:**

```powershell
python -m tankbattle.external_agents.validate --module tankbattle.external_agents.example_agent
```

**Chạy External Agent vs Heuristic Alpha-Beta:**

```powershell
python main.py --p0 External --p1 "Heuristic Alpha-Beta" --external-module tankbattle.external_agents.example_agent
```

Module mẫu được lưu tại:

`tankbattle/external_agents/example_agent.py`

External Agent không phải thuật toán tìm kiếm thứ năm mà là chức năng mở rộng để tích hợp AI bên ngoài.

---

# 5. PROJECT STRUCTURE

```text
TankBattle_AI_Task2/
│
├── main.py
├── benchmark.py
├── README.md
├── requirements.txt
├── run_windows.bat
├── run_experiments.bat
│
├── tankbattle/
│   ├── agents/
│   │   ├── search.py
│   │   └── registry.py
│   │
│   ├── engine/
│   │   ├── game.py
│   │   ├── model.py
│   │   └── maps.py
│   │
│   ├── external_agents/
│   └── ui/
│
├── assets/
├── benchmarks/
├── tests/
├── docs/
└── results/
```

**Các thành phần chính:**

- `main.py`: Điểm khởi chạy ứng dụng.
- `benchmark.py`: Điểm khởi chạy thực nghiệm.
- `tankbattle/agents/`: Các thuật toán tìm kiếm AI.
- `tankbattle/engine/`: Game State, luật chơi, xử lý hành động và bản đồ.
- `tankbattle/ui/`: Giao diện PyGame, Battle Log và Replay.
- `benchmarks/`: Các module so sánh thuật toán và Tournament.
- `tests/`: Các bài kiểm thử tự động.
- `results/`: Kết quả thực nghiệm dạng CSV.

---

# 6. GAME RULES

Tank Battle là trò chơi đối kháng hai người chơi với tổng lợi ích bằng không (Zero-Sum Game).

Mỗi Tank có thể thực hiện sáu hành động:

```text
MOVE_UP
MOVE_DOWN
MOVE_LEFT
MOVE_RIGHT
FIRE
STAY
```

**Thông số theo đề bài:**

| Đối tượng | HP |
|---|---:|
| Tank | 6 |
| Base | 9 |
| Wall (Brick) | 3 |

Các quy tắc chính:

- Mỗi Tank di chuyển tối đa một ô trong lượt.
- Đạn di chuyển tối đa ba ô trong mỗi game cycle.
- Va chạm của đạn được kiểm tra sau từng ô di chuyển.
- Một phát đạn gây một đơn vị sát thương khi trúng mục tiêu.
- Trận đấu kết thúc khi Tank hoặc Base của một bên bị phá hủy.
- Hai Tank thực hiện hành động theo cơ chế luân phiên P1 → P2.

Hệ thống cung cấp ba bản đồ: Classic Battlefield, Open Arena và Tactical Maze.

### Spawn System

Project hỗ trợ:

- **Balanced Spawn:** Hai Tank xuất hiện tại các vị trí tương đối cân bằng, cách xa nhau và tránh đường bắn trực diện từ đầu.
- **Random Spawn:** Vị trí xuất phát ngẫu nhiên có kiểm soát.
- **Seed:** Cho phép tái hiện vị trí xuất phát khi chạy thực nghiệm.

Việc bố trí Spawn giúp giảm lợi thế tấn công trực tiếp của người đi trước và tạo điều kiện để AI di chuyển tìm vị trí chiến đấu.

---

# 7. SEARCH ALGORITHMS

Project triển khai bốn cấu hình tìm kiếm đối kháng.

| Algorithm | Evaluation | Pruning |
|---|---|---|
| Minimax | Terminal-based | No |
| Alpha-Beta | Terminal-based | Yes |
| Heuristic Minimax | Heuristic Evaluation | No |
| Heuristic Alpha-Beta | Heuristic Evaluation | Yes |

### 7.1. Minimax

Minimax tìm kiếm các trạng thái trò chơi theo lượt, giả định hai người chơi đều đưa ra quyết định tối ưu.

Thuật toán lựa chọn hành động nhằm tối đa hóa giá trị của người chơi hiện tại, đồng thời xét đến phản ứng đối kháng của đối phương.

### 7.2. Alpha-Beta Pruning

Alpha-Beta cải tiến Minimax bằng cách loại bỏ những nhánh không thể ảnh hưởng đến quyết định tối ưu.

Mục tiêu là giảm số node phải duyệt mà vẫn giữ kết quả đánh giá tương đương Minimax khi sử dụng cùng hàm đánh giá và độ sâu.

### 7.3. Heuristic Minimax

Heuristic Minimax sử dụng Evaluation Function để ước lượng chất lượng của trạng thái khi chưa đạt Terminal State.

Các yếu tố đánh giá bao gồm:

- HP của Tank và Base.
- Khoảng cách và khả năng tiếp cận mục tiêu.
- Vị trí và đường bắn.
- Mức độ nguy hiểm từ đạn đối phương.
- Lợi thế tấn công và phòng thủ.

### 7.4. Heuristic Alpha-Beta

Kết hợp Evaluation Function với Alpha-Beta Pruning.

Thuật toán hướng đến việc giảm chi phí tìm kiếm trong khi vẫn đánh giá các trạng thái chiến thuật.

### 7.5. Search Depth

Search Depth quyết định độ sâu tối đa của cây tìm kiếm.

| Depth | Mục đích |
|---|---|
| 2 | Thực nghiệm nhanh |
| 3 | Cân bằng giữa thời gian và khả năng tìm kiếm |
| 4 | Đánh giá mức tăng chi phí tìm kiếm |

Các thuật toán sử dụng giới hạn độ sâu, không duyệt toàn bộ cây trạng thái đến khi trò chơi kết thúc.

---

# 8. EXPERIMENT RESULTS

Các kết quả dưới đây được ghi nhận từ lần thực nghiệm trên Windows với Python 3.14.3. Số liệu có thể thay đổi tùy môi trường và cấu hình.

## 8.1. Unit Tests

| Test Suite | Kết quả |
|---|---|
| AI Behavior | Passed |
| Benchmark & Scenarios | Passed |
| Game Rules | Passed |
| Spawn System | Passed |
| UI Assets & Logic | Passed |
| Integration & History | Passed |
| **Tổng cộng** | **40/40 Passed** |

## 8.2. Benchmark – Depth 4

Kết quả trên bản đồ Classic Battlefield:

| Algorithm | Time (ms) | Nodes | Prunes |
|---|---:|---:|---:|
| Minimax | 20.260 | 1,555 | 0 |
| Alpha-Beta | 2.688 | 130 | 45 |
| Heuristic Minimax | 138.899 | 1,555 | 0 |
| Heuristic Alpha-Beta | 47.187 | 579 | 72 |

**Nhận xét:**

- Alpha-Beta giảm khoảng 91,6% số node so với Minimax.
- Heuristic Alpha-Beta giảm khoảng 62,8% số node so với Heuristic Minimax.
- Hàm Heuristic có thêm chi phí tính toán nên thời gian thực thi không chỉ phụ thuộc số node.
- Khả năng cắt tỉa phụ thuộc trạng thái và thứ tự xét hành động.

## 8.3. AI Tournament

Tournament được chạy trên ba bản đồ với Depth 2, hai vòng thử nghiệm và giới hạn 80 plies.

**Tổng cộng: 72 trận, tất cả đều kết thúc.**

| Algorithm | Wins | Losses | Draws | Win Rate |
|---|---:|---:|---:|---:|
| Minimax | 14 | 22 | 0 | 38.89% |
| Alpha-Beta | 14 | 22 | 0 | 38.89% |
| Heuristic Minimax | 22 | 14 | 0 | 61.11% |
| Heuristic Alpha-Beta | 22 | 14 | 0 | 61.11% |

**Nhận xét:**

- Hai thuật toán Heuristic đạt tỷ lệ thắng 61,11% trong cấu hình thử nghiệm.
- Minimax và Alpha-Beta đạt cùng tỷ lệ thắng, phù hợp với việc chúng sử dụng cùng Evaluation Function trong chế độ so sánh tương ứng.
- Heuristic Minimax và Heuristic Alpha-Beta cũng đạt cùng tỷ lệ thắng; Alpha-Beta chủ yếu tạo lợi thế về hiệu quả tìm kiếm.
- Kết quả Tournament phụ thuộc vào bản đồ, Spawn, Depth và cấu hình đối thủ.

Các file CSV được lưu trong `results/` để phục vụ phân tích và báo cáo.

---

# 9. NOTES

- Kích hoạt `.venv` trước khi sử dụng các lệnh `python`.
- Sử dụng `python benchmark.py --test` để kiểm tra sau khi chỉnh sửa source code.
- Sử dụng `python benchmark.py --all` để đánh giá ảnh hưởng của Search Depth.
- Sử dụng `python benchmark.py --tournament` để đo kết quả thi đấu giữa các thuật toán.
- Để thực nghiệm công bằng, cần giữ cùng bản đồ, trạng thái xuất phát, Search Depth và môi trường phần cứng.
- Các số liệu đo được phản ánh cấu hình thực nghiệm, không chứng minh thuật toán luôn thắng hoặc luôn tối ưu trong mọi trạng thái.
- Cần tuân thủ quy định học phần về việc sử dụng công cụ hỗ trợ và nguồn mã.

---
