# TANK BATTLE AI – HƯỚNG DẪN CHẠY PROJECT

**Môn học:** Nhập môn Trí tuệ nhân tạo (Introduction to Artificial Intelligence)  
**Nội dung:** Task 2 – Adversarial Search / Tank Battle  
**Ngôn ngữ:** Python 3.10 trở lên (khuyến nghị Python 3.11 hoặc 3.12)  
**Giao diện:** PyGame (cài qua gói `pygame-ce`)  
**Hệ điều hành hướng dẫn:** Windows 10/11, PowerShell trong VS Code

> **Đọc nhanh:** Nếu đã cài Python 3.10 trở lên, mở đúng thư mục project trong VS Code và copy ba lệnh tại **Mục 2**. Những lần sau chỉ cần chạy một lệnh ở **Mục 3**. Không cần kích hoạt `.venv` thủ công.

---

## 1. Chuẩn bị

1. Giải nén project và mở **thư mục `TankBattle_AI_Task2_AI_Fixed`** bằng VS Code (`File > Open Folder`).
2. Mở `Terminal > New Terminal`. Terminal nên ở thư mục chứa `main.py`, `requirements.txt` và `run_windows.bat`.
3. Kiểm tra phiên bản Python 3 hiện có trên máy:

```powershell
py -3 --version
```

Kết quả hợp lệ: `Python 3.10.x` trở lên (ví dụ: 3.11, 3.12, 3.13, 3.14).

Nếu phiên bản thấp hơn 3.10, hãy cài Python mới hơn.

Dùng lệnh sau để xem các phiên bản đã cài:

```powershell
py -0p
```

Nếu máy có nhiều phiên bản, có thể chỉ định `py -3.12` thay cho `py -3`.

## 2. Chạy lần đầu – COPY NGUYÊN 3 LỆNH

Chạy lần lượt trong PowerShell của VS Code:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

**Giải thích:**

- Lệnh 1: Tạo môi trường Python riêng `.venv` cho project.
- Lệnh 2: Cài `pygame-ce` từ bản dựng sẵn, giúp hạn chế lỗi biên dịch thư viện.
- Lệnh 3: Mở giao diện Tank Battle AI.

Nếu cửa sổ game mở lên, quá trình cài đặt đã hoàn tất.

**Không cần cài lại thư viện ở mỗi lần chạy.**

### Cách tự động (không cần gõ ba lệnh)

Tại thư mục project, chạy:

```powershell
.\run_windows.bat
```

File này sẽ kiểm tra/tạo `.venv`, cài thư viện nếu thiếu và mở game.

## 3. Chạy ở những lần sau

Mở VS Code tại đúng thư mục project và chạy:

```powershell
.\.venv\Scripts\python.exe main.py
```

Hoặc:

```powershell
.\run_windows.bat
```

### 3.1. Classic Battlefield – Minimax vs Alpha-Beta

Depth 3:

```powershell
.\.venv\Scripts\python.exe main.py --map "Classic Battlefield" --depth 3 --p0 Minimax --p1 Alpha-Beta
```

### 3.2. Open Arena – Heuristic Minimax vs Heuristic Alpha-Beta

```powershell
.\.venv\Scripts\python.exe main.py --map "Open Arena" --depth 3 --p0 "Heuristic Minimax" --p1 "Heuristic Alpha-Beta"
```

### 3.3. Tactical Maze – Hai thuật toán Heuristic

```powershell
.\.venv\Scripts\python.exe main.py --map "Tactical Maze" --depth 3 --p0 "Heuristic Alpha-Beta" --p1 "Heuristic Minimax"
```

Project hỗ trợ ba bản đồ:

- **Classic Battlefield:** Bản đồ chiến đấu cơ bản.
- **Open Arena:** Bản đồ có không gian mở.
- **Tactical Maze:** Bản đồ có nhiều vật cản và hành lang.

Bốn thuật toán AI:

- Minimax
- Alpha-Beta
- Heuristic Minimax
- Heuristic Alpha-Beta

Tên bản đồ và thuật toán có khoảng trắng phải đặt trong dấu nháy kép.

## 4. Phím điều khiển trong game

| Phím / Nút | Chức năng |
|---|---|
| SPACE / PLAY / PAUSE | Chạy hoặc tạm dừng trận đấu |
| N / STEP | Thực hiện một lượt hành động rồi dừng |
| R / RESET | Chơi lại từ trạng thái khởi đầu |
| M / MAP | Chuyển qua ba bản đồ |
| Chọn P1 / P2 | Đổi thuật toán hoặc chọn Human / External |
| L / BATTLE LOG / REPLAY | Mở lịch sử trận đấu |
| PREVIOUS / NEXT | Xem trạng thái trước/sau trong Replay |
| EXPORT LOG CSV | Xuất lịch sử trận vào `results/battle_logs/` |
| BACK | Quay lại trận đấu đang tạm dừng |
| + / - | Tăng / giảm tốc độ chuyển lượt |
| ESC | Thoát game |

### Chế độ Human

| Phím | Hành động |
|---|---|
| W / ↑ | Di chuyển lên |
| S / ↓ | Di chuyển xuống |
| A / ← | Di chuyển trái |
| D / → | Di chuyển phải |
| F / ENTER | Bắn |
| X | Đứng yên (STAY) |

**Lưu ý:** STEP thực hiện một lượt hành động trong game, không phải một node của thuật toán Minimax.

## 5. BENCHMARK – So sánh hiệu suất 4 thuật toán

Benchmark đo **một quyết định tìm kiếm tại cùng trạng thái**, không phải một trận đấu hoàn chỉnh.

Các chỉ số được đánh giá:

- Execution Time (ms)
- Explored Nodes
- Evaluated Leaves
- Pruned Branches
- Search Depth
- Chosen Action
- Root Score

Kết quả được lưu dưới dạng CSV trong thư mục `results/`.

### 5.1. Benchmark nhanh – Depth 3

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depth 3 --repeats 5 --output results/benchmark_depth3.csv
```

### 5.2. Benchmark chính – Depth 2, 3, 4 trên cả 3 map

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --output results/maps_depths234.csv
```

**Giải thích tham số:**

- `--suite maps`: Chạy trên ba bản đồ chính.
- `--depths 2 3 4`: Chạy lần lượt ba độ sâu.
- `--repeats 5`: Đo năm lần cho mỗi cấu hình để lấy thời gian trung bình.
- `--output`: Nơi lưu file CSV.

### 5.3. Benchmark tình huống chiến thuật

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite tactical --depth 3 --repeats 5 --output results/tactical_depth3.csv
```

Các tình huống gồm:

| Scenario | Mục đích |
|---|---|
| Incoming Bullet | Kiểm tra phản ứng trước đạn |
| Forced Flank | Kiểm tra khả năng di chuyển để tấn công |
| Finishing Shot | Kiểm tra quyết định tiêu diệt đối thủ |
| Brick Barrier | Kiểm tra xử lý vật cản |

### 5.4. Benchmark nguyên bản (Strict Search)

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --strict-search --output results/strict_maps_depths234.csv
```

`--strict-search` tắt các cơ chế hỗ trợ chọn hành động ở tầng gốc (tactical tie-break / root bonus).

Đây là lựa chọn phù hợp khi cần đối chiếu thuật toán tìm kiếm cơ bản.

**Không trộn số liệu Strict Search với chế độ gameplay mặc định khi viết báo cáo.**

### 5.5. Đọc kết quả Benchmark

| Cột CSV | Ý nghĩa |
|---|---|
| scenario | Tên bản đồ hoặc tình huống |
| algorithm | Thuật toán |
| depth | Độ sâu tìm kiếm |
| avg_time_ms | Thời gian tìm kiếm trung bình |
| avg_nodes | Số node duyệt trung bình |
| avg_leaves | Số node lá được đánh giá trung bình |
| avg_prunes | Số lần cắt nhánh trung bình |
| chosen_action | Hành động AI chọn |
| root_score | Giá trị tìm kiếm tại gốc |

Alpha-Beta thường duyệt ít node hơn Minimax ở cùng điều kiện, nhưng thời gian thực tế còn phụ thuộc máy và thứ tự xét hành động.

## 6. TOURNAMENT – Cho 4 thuật toán đấu với nhau

Tournament cho phép bốn thuật toán thi đấu với nhau trên ba bản đồ.

Chạy giải đấu với Depth 2, hai vòng thử nghiệm:

```powershell
.\.venv\Scripts\python.exe -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --output results/tournament.csv --summary-output results/tournament_summary.csv
```

**Giải thích tham số:**

- `--suite maps`: Thi đấu trên ba bản đồ.
- `--depth 2`: Độ sâu tìm kiếm.
- `--rounds 2`: Hai vòng thử nghiệm.
- `--max-plies 60`: Giới hạn tối đa 60 lượt hành động mỗi trận.
- `--output`: File kết quả từng trận.
- `--summary-output`: File tổng hợp kết quả.

### 6.1. File kết quả Tournament

**results/tournament.csv**

Chứa thông tin từng trận:

- Thuật toán P1 và P2
- Người chiến thắng
- Số lượt đã thực hiện
- HP còn lại
- Thống kê tìm kiếm

**results/tournament_summary.csv**

Chứa kết quả tổng hợp:

- Wins
- Losses
- Draws
- Unfinished
- Win Rate
- Average Nodes per Decision

**Lưu ý:** `unfinished` là trận bị dừng khi đạt giới hạn lượt, không tự động được xem là hòa.

Win Rate trong file tổng hợp chỉ tính các trận đã kết thúc.

Có thể tăng `--max-plies` để theo dõi lâu hơn, nhưng thời gian chạy sẽ tăng.

### 6.2. Tournament Strict Search

```powershell
.\.venv\Scripts\python.exe -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --strict-search --output results/tournament_strict.csv --summary-output results/tournament_strict_summary.csv
```

## 7. UNIT TESTS – Kiểm tra logic chương trình

Chạy toàn bộ Unit Tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Nếu cuối Terminal hiển thị:

```text
Ran ... tests

OK
```

Nghĩa là các bài kiểm thử đã đạt.

Unit Tests giúp kiểm tra:

- Game State
- Game Rules
- Movement
- Collision
- Bullet Mechanics
- Terminal State
- Search Algorithms
- Các chức năng liên quan

**Lưu ý:** Unit Tests không thay thế việc kiểm tra cửa sổ PyGame và các nút điều khiển trên máy thực tế.

## 8. CHẠY TẤT CẢ THỰC NGHIỆM CHỈ VỚI MỘT LỆNH

Sau khi đã cài môi trường ở Mục 2, chạy:

```powershell
.\run_experiments.bat
```

Script sẽ thực hiện lần lượt:

1. Unit Tests
2. Benchmark trên ba bản đồ
3. Benchmark Depth 2, 3, 4
4. Tactical Benchmark
5. AI Tournament

Kết quả được lưu trong thư mục `results/`.

Không cần mở PyGame để chạy thực nghiệm.

## 9. EXTERNAL AGENT – Tích hợp thuật toán bên ngoài

Project hỗ trợ tích hợp AI từ module Python bên ngoài.

Module mẫu:

```text
external_agents/example_agent.py
```

### 9.1. Kiểm tra External Agent

```powershell
.\.venv\Scripts\python.exe -m external_agents.validate --module external_agents.example_agent
```

### 9.2. Chạy External Agent đấu với AI

```powershell
.\.venv\Scripts\python.exe main.py --map "Open Arena" --p0 External --p1 "Heuristic Alpha-Beta" --external-module external_agents.example_agent
```

Khi có module riêng, thay `external_agents.example_agent` bằng tên module thực tế.

Chỉ chạy code agent từ nguồn đáng tin cậy.

## 10. CHẠY KHÔNG CẦN GIAO DIỆN (HEADLESS)

Chế độ Headless cho phép theo dõi trận đấu trực tiếp trong Terminal.

```powershell
.\.venv\Scripts\python.exe main.py --headless --map "Open Arena" --depth 2 --p0 Minimax --p1 Alpha-Beta --max-steps 60
```

Chế độ này phù hợp để kiểm tra logic và quan sát hành động AI mà không cần mở cửa sổ PyGame.

## 11. CẤU TRÚC THƯ MỤC CHÍNH

```text
TankBattle_AI_Task2_AI_Fixed/
├── main.py
├── requirements.txt
├── README.md
├── run_windows.bat
├── run_experiments.bat
│
├── engine/
│   └── Game Engine, Game State, Map, Collision
│
├── agents/
│   └── Minimax, Alpha-Beta, Heuristic
│
├── external_agents/
│   └── External Agent, Validator
│
├── ui/
│   └── PyGame Interface, Battle Log, Replay
│
├── assets/
│   └── Pixel Art Sprites
│
├── benchmarks/
│   └── Benchmark, Tournament
│
├── tests/
│   └── Unit Tests
│
├── docs/
│   └── Task 2 Documentation
│
└── results/
    └── Benchmark CSV, Tournament CSV, Battle Logs
```

## 12. LỖI THƯỜNG GẶP VÀ CÁCH XỬ LÝ

### 12.1. Không tìm thấy Python trong .venv

Thông báo:

```text
.\.venv\Scripts\python.exe is not recognized
```

Nguyên nhân: Chưa tạo môi trường `.venv` hoặc Terminal đang ở sai thư mục.

Cách xử lý:

```powershell
py -3 -m venv .venv
```

### 12.2. Lỗi thiếu pygame

Thông báo:

```text
ModuleNotFoundError: No module named 'pygame'
```

Cách xử lý:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
```

Không cài đồng thời `pygame` cũ và `pygame-ce` trong cùng một môi trường.

### 12.3. Không tìm thấy Python hoặc Python quá cũ

Kiểm tra các phiên bản Python:

```powershell
py -0p
```

Project yêu cầu Python 3.10 trở lên.

Nếu `py` không hoạt động, hãy kiểm tra Python Launcher hoặc thử:

```powershell
python --version
python -m venv .venv
```

Nếu đã tạo `.venv` bằng Python phiên bản cũ, xóa thư mục `.venv` rồi tạo lại bằng phiên bản phù hợp.

### 12.4. Không tìm thấy main.py

Thông báo:

```text
can't open file 'main.py'
```

Hoặc:

```text
No module named benchmarks
```

Nguyên nhân: Terminal đang ở sai thư mục.

Cách xử lý: Mở đúng thư mục gốc chứa `main.py` bằng VS Code.

### 12.5. AI đứng yên hoặc bắn liên tục

Kiểm tra xem chương trình có đang sử dụng `--strict-search` hay không.

Ở chế độ Strict Search, nhiều hành động có thể cùng điểm đánh giá và thuật toán có thể ưu tiên `FIRE`.

Để sử dụng cơ chế lựa chọn hành động chiến thuật, chạy chế độ mặc định:

```powershell
.\.venv\Scripts\python.exe main.py
```

### 12.6. Benchmark chạy quá lâu

Giảm Search Depth và số lần lặp:

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depth 2 --repeats 3 --output results/benchmark_quick.csv
```

Depth 4 trở lên có thể chậm hơn đáng kể do số node tăng nhanh.

## 13. GHI CHÚ CHO BÁO CÁO

Project triển khai bốn cấu hình tìm kiếm:

1. Minimax
2. Alpha-Beta Pruning
3. Heuristic Minimax
4. Heuristic Minimax kết hợp Alpha-Beta Pruning

Các thuật toán trong project đều có **giới hạn độ sâu**.

Minimax và Alpha-Beta ở chế độ Strict Search đóng vai trò baseline đánh giá trạng thái kết thúc, không phải tìm kiếm toàn bộ cây game.

Chế độ gameplay mặc định bổ sung cơ chế chọn hành động chiến thuật ở tầng gốc để giảm hiện tượng bắn hoặc đứng yên vô ích.

### Nguyên tắc thực nghiệm

Khi thực hiện Benchmark và Tournament, cần bảo đảm:

- Cùng bản đồ.
- Cùng trạng thái ban đầu.
- Cùng Search Depth.
- Cùng môi trường phần cứng.
- Cùng số lần lặp.
- Cùng chế độ tìm kiếm.

Kết quả thời gian phải được đo trên máy thực tế dùng để báo cáo.

Không lấy số liệu ví dụ trong `results/examples/` làm kết quả thực nghiệm của nhóm.

Nếu học phần có quy định riêng về công cụ được phép sử dụng, cần tuân thủ quy định đó.

---

## QUY TRÌNH CHẠY ĐỀ XUẤT

**Bước 1 – Khởi động ứng dụng**

```powershell
.\.venv\Scripts\python.exe main.py
```

**Bước 2 – Kiểm tra Unit Tests**

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**Bước 3 – Benchmark Depth 2, 3, 4**

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --output results/maps_depths234.csv
```

**Bước 4 – Tactical Benchmark**

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite tactical --depth 3 --repeats 5 --output results/tactical_depth3.csv
```

**Bước 5 – AI Tournament**

```powershell
.\.venv\Scripts\python.exe -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --output results/tournament.csv --summary-output results/tournament_summary.csv
```

**Hoặc chạy toàn bộ thực nghiệm:**

```powershell
.\run_experiments.bat
```

Sau khi hoàn tất, kiểm tra các file CSV trong thư mục `results/` và lưu ảnh minh chứng phục vụ báo cáo.

---

**Tank Battle AI – Task 2: Adversarial Search**  
*Introduction to Artificial Intelligence*
