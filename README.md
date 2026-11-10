# TANK BATTLE AI – HƯỚNG DẪN CHẠY PROJECT

**Môn học:** Nhập môn Trí tuệ nhân tạo (Introduction to Artificial Intelligence)  
**Nội dung:** Task 2 – Adversarial Search / Tank Battle  
**Ngôn ngữ:** Python 3.10 trở lên (khuyến nghị Python 3.11 hoặc 3.12)  
**Giao diện:** PyGame (cài qua gói `pygame-ce`)  
**Hệ điều hành hướng dẫn:** Windows 10/11, PowerShell trong VS Code

> **Đọc nhanh:** Nếu đã cài Python 3.10 trở lên, mở đúng thư mục project trong VS Code và copy ba lệnh tại **Mục 2**. Những lần sau chỉ cần chạy một lệnh ở **Mục 3**. Không cần kích hoạt `.venv` thủ công.

---

## 1. Chuẩn bị

1. Giải nén project và mở **thư mục `TankBattle_AI_Task2_Clean`** bằng VS Code (`File > Open Folder`).
2. Mở `Terminal > New Terminal`. Terminal nên ở thư mục chứa `main.py`, `requirements.txt` và `run_windows.bat`.
3. Kiểm tra phiên bản Python 3 hiện có trên máy:

```powershell
py -3 --version
```

Kết quả hợp lệ: `Python 3.10.x` trở lên (ví dụ: 3.11, 3.12, 3.13, 3.14). Nếu phiên bản thấp hơn 3.10, hãy cài Python mới hơn. Dùng `py -0p` để xem các phiên bản đã cài. Nếu máy có nhiều phiên bản, có thể chỉ định `py -3.12` thay cho `py -3`.

## 2. Chạy lần đầu – COPY NGUYÊN 3 LỆNH

Chạy lần lượt trong PowerShell của VS Code:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

**Giải thích ngắn:**

- Lệnh 1: tạo môi trường Python riêng `.venv` cho project.
- Lệnh 2: cài `pygame-ce` từ bản dựng sẵn, giúp hạn chế lỗi biên dịch thư viện.
- Lệnh 3: mở giao diện Tank Battle AI.

Nếu cửa sổ game mở lên, quá trình cài đặt đã hoàn tất. **Không cần cài lại thư viện ở mỗi lần chạy.**

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

### Chọn bản đồ và thuật toán ngay khi khởi động

**Classic Battlefield – Minimax đấu Alpha-Beta, Depth 3:**

```powershell
.\.venv\Scripts\python.exe main.py --map "Classic Battlefield" --depth 3 --p0 Minimax --p1 Alpha-Beta
```

**Open Arena – Heuristic Minimax đấu Heuristic Alpha-Beta:**

```powershell
.\.venv\Scripts\python.exe main.py --map "Open Arena" --depth 3 --p0 "Heuristic Minimax" --p1 "Heuristic Alpha-Beta"
```

**Tactical Maze – hai thuật toán có Heuristic:**

```powershell
.\.venv\Scripts\python.exe main.py --map "Tactical Maze" --depth 3 --p0 "Heuristic Alpha-Beta" --p1 "Heuristic Minimax"
```

Các tên bản đồ hợp lệ: `Classic Battlefield`, `Open Arena`, `Tactical Maze`. Tên thuật toán có khoảng trắng phải đặt trong dấu nháy kép.

## 3.1. Spawn – Vị trí xuất hiện

**Giữ nguyên luật đề bài:** Tank = 6 HP, Base = 9 HP, Wall = 3 HP. Hai Tank được bố trí lệch hàng, tránh đối đầu trực diện ngay khi bắt đầu.

Spawn cân bằng (mặc định):

```powershell
.\.venv\Scripts\python.exe main.py --map "Classic Battlefield" --spawn balanced
```

Spawn ngẫu nhiên có kiểm soát (`seed` giúp tái lập kết quả):

```powershell
.\.venv\Scripts\python.exe main.py --map "Classic Battlefield" --spawn random --seed 2026
```

Trong game, nhấn **G** để tạo trận mới ở vị trí ngẫu nhiên (seed tăng 1).
Nhấn **R** để chơi lại đúng vị trí của trận hiện tại.

**Vị trí thuật toán:** `tankbattle/agents/search.py`. Tìm các chú thích `THUAT TOAN 1`, `THUAT TOAN 2`, `THUAT TOAN 3`, `THUAT TOAN 4` để theo dõi. Có giải thích trong `docs/THUAT_TOAN.md`.

## 4. Phím điều khiển trong game

| Phím / Nút | Chức năng |
|---|---|
| `SPACE` / `PLAY / PAUSE` | Chạy hoặc tạm dừng trận đấu |
| `N` / `STEP` | Thực hiện **một lượt hành động** rồi dừng; không phải một node của Minimax |
| `R` / `RESET` | Chơi lại từ trạng thái khởi đầu |
| `M` / `MAP` | Chuyển qua ba bản đồ (reset trận) |
| Chọn `P1` / `P2` | Đổi thuật toán hoặc chọn `Human` / `External` |
| `L` / `BATTLE LOG / REPLAY` | Mở lịch sử trận đấu |
| `PREVIOUS` / `NEXT` | Xem trạng thái trước/sau trong Replay |
| `EXPORT LOG CSV` | Xuất lịch sử trận vào `results/battle_logs/` |
| `BACK` | Quay lại trận đấu đang tạm dừng |
| `+` / `-` | Tăng / giảm tốc độ chuyển lượt |
| `W`, `A`, `S`, `D` | Di chuyển khi chọn `Human` |
| `F` hoặc `ENTER` | Bắn khi chọn `Human` |
| `X` | Đứng yên (`STAY`) khi chọn `Human` |
| `ESC` | Thoát game |

**Bốn thuật toán:** `Minimax`, `Alpha-Beta`, `Heuristic Minimax`, `Heuristic Alpha-Beta`. Chế độ `Human` do người chơi điều khiển; `External` gọi agent từ module Python bên ngoài.

## 5. BENCHMARK – So sánh hiệu suất 4 thuật toán

Benchmark đo **một quyết định tìm kiếm tại cùng trạng thái**, không phải một trận đấu hoàn chỉnh. Mỗi lệnh sẽ tự tạo thư mục `results/` nếu cần và lưu file CSV.

### 5.1. Benchmark nhanh – Depth 3

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depth 3 --repeats 5 --output results/benchmark_depth3.csv
```

### 5.2. Benchmark chính – Depth 2, 3, 4 trên cả 3 map

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --output results/maps_depths234.csv
```

- `--suite maps`: ba bản đồ chính.
- `--depths 2 3 4`: chạy lần lượt ba độ sâu.
- `--repeats 5`: đo năm lần cho mỗi cấu hình để lấy thời gian trung bình.
- `--output`: nơi lưu CSV.

### 5.3. Benchmark tình huống chiến thuật

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite tactical --depth 3 --repeats 5 --output results/tactical_depth3.csv
```

Các tình huống gồm: `Incoming bullet`, `Forced flank`, `Finishing shot`, `Brick barrier`.

### 5.4. Benchmark nguyên bản (Strict Search)

```powershell
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --strict-search --output results/strict_maps_depths234.csv
```

`--strict-search` tắt các cơ chế hỗ trợ chọn hành động ở tầng gốc (tactical tie-break / root bonus). Đây là lựa chọn phù hợp khi cần đối chiếu thuật toán tìm kiếm cơ bản. **Không trộn số liệu Strict Search với chế độ gameplay mặc định khi viết báo cáo.**

### 5.5. Đọc kết quả Benchmark

| Cột CSV | Ý nghĩa |
|---|---|
| `scenario` | Tên bản đồ hoặc tình huống |
| `algorithm` | Thuật toán |
| `depth` | Độ sâu tìm kiếm |
| `avg_time_ms` | Thời gian tìm kiếm trung bình (ms) |
| `avg_nodes` | Số node duyệt trung bình |
| `avg_leaves` | Số node lá được đánh giá trung bình |
| `avg_prunes` | Số lần cắt nhánh trung bình |
| `chosen_action` | Hành động AI chọn |
| `root_score` | Giá trị tìm kiếm tại gốc |

`Alpha-Beta` thường duyệt ít node hơn `Minimax` ở cùng điều kiện, nhưng thời gian thực tế còn phụ thuộc máy và thứ tự xét hành động.

## 6. TOURNAMENT – Cho 4 thuật toán đấu với nhau

Chạy giải đấu trên ba map, đổi vị trí P1/P2 và người đi trước để giảm thiên lệch:

```powershell
.\.venv\Scripts\python.exe -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --output results/tournament.csv --summary-output results/tournament_summary.csv
```

Hai file kết quả:

- `results/tournament.csv`: từng trận, người thắng, số lượt, HP còn lại và thống kê tìm kiếm.
- `results/tournament_summary.csv`: tổng số trận, thắng/thua/hòa, chưa kết thúc, win rate và số node trung bình.

**Chú ý:** `unfinished` là trận bị dừng vì chạm `--max-plies`; **không được tự tính là hòa**. Win rate trong file tổng hợp chỉ tính các trận đã kết thúc. Có thể tăng `--max-plies` để theo dõi lâu hơn, nhưng thời gian chạy sẽ tăng.

### Tournament nguyên bản

```powershell
.\.venv\Scripts\python.exe -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --strict-search --output results/tournament_strict.csv --summary-output results/tournament_strict_summary.csv
```

## 7. UNIT TESTS – Kiểm tra logic chương trình

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Nếu cuối Terminal hiển thị `OK` thì các bài kiểm thử đã đạt. Bài kiểm thử tự động **không thay thế** việc kiểm tra cửa sổ PyGame và các nút trên máy thực tế.

## 8. CHẠY TẤT CẢ THỰC NGHIỆM CHỈ VỚI MỘT LỆNH

**Sau khi đã cài môi trường ở Mục 2**, chạy:

```powershell
.\run_experiments.bat
```

Script sẽ chạy theo thứ tự: **Unit Tests → Benchmark 3 map / Depth 2–3–4 → Benchmark chiến thuật → Tournament**. Kết quả được lưu trong `results/`. Không cần mở PyGame để chạy thực nghiệm.

## 9. EXTERNAL AGENT – Tích hợp thuật toán bên ngoài

Có sẵn module mẫu `tankbattle.external_agents.example_agent`. Để kiểm tra module mẫu:

```powershell
.\.venv\Scripts\python.exe -m tankbattle.external_agents.validate --module tankbattle.external_agents.example_agent
```

Chạy External Agent (P1) đấu Heuristic Alpha-Beta (P2):

```powershell
.\.venv\Scripts\python.exe main.py --map "Open Arena" --p0 External --p1 "Heuristic Alpha-Beta" --external-module tankbattle.external_agents.example_agent
```

Khi có module riêng, thay `tankbattle.external_agents.example_agent` bằng tên module thực tế. Chỉ chạy code agent từ nguồn tin cậy.

## 10. CHẠY KHÔNG CẦN GIAO DIỆN (HEADLESS)

Dùng để xem diễn biến từng lượt trực tiếp trong Terminal:

```powershell
.\.venv\Scripts\python.exe main.py --headless --map "Open Arena" --depth 2 --p0 Minimax --p1 Alpha-Beta --max-steps 60
```

## 11. CẤU TRÚC THƯ MỤC CHÍNH

```text
TankBattle_AI_Task2_Clean/
├── main.py                    # Chay game va tham so CLI
├── requirements.txt           # pygame-ce
├── run_windows.bat            # Cai dat neu can va mo game
├── run_experiments.bat        # Chay test, benchmark, tournament
├── tankbattle/                # Toan bo ma nguon game
│   ├── engine/               # Game State, map, va cham, dan, HP
│   ├── agents/               # Minimax, Alpha-Beta, Heuristic
│   ├── external_agents/      # Module agent ngoai va kiem tra
│   └── ui/                   # Giao dien PyGame va replay
├── assets/pixel/              # Hinh anh pixel art
├── benchmarks/                # Benchmark va Tournament
├── tests/                     # Unit tests
├── docs/                      # Ghi chu va checklist Task 2
└── results/                   # File CSV sau khi chay
```

## 12. LỖI THƯỜNG GẶP VÀ CÁCH XỬ LÝ

**Lỗi 1: `The term '.\.venv\Scripts\python.exe' is not recognized`**  
Bạn đang ở sai thư mục hoặc chưa tạo `.venv`. Mở lại thư mục chứa `main.py`, sau đó chạy:

```powershell
py -3 -m venv .venv
```

**Lỗi 2: `No module named 'pygame'`**  
Cài lại đúng gói `pygame-ce` theo `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
```

Không cài đồng thời `pygame` cũ và `pygame-ce` trong cùng một môi trường.

**Lỗi 3: `py -3` không tìm thấy Python hoặc Python quá cũ**  
Kiểm tra:

```powershell
py -0p
```

Project yêu cầu Python 3.10 trở lên. Nếu `py` không hoạt động, hãy kiểm tra Python Launcher hoặc thử `python --version` và `python -m venv .venv`. Nếu đã tạo `.venv` bằng Python phiên bản cũ, xóa thư mục `.venv` rồi tạo lại bằng phiên bản phù hợp.

**Lỗi 4: `can't open file 'main.py'` / `No module named benchmarks`**  
Terminal đang ở sai thư mục. Hãy `cd` vào **thư mục gốc của project** trước khi chạy lệnh.

**Lỗi 5: Game chạy nhưng AI cứ bắn liên tục**  
Kiểm tra bạn có vô tình bật `--strict-search` không. Chế độ Strict Search có thể tạo hành động đồng điểm và ưu tiên `FIRE`. Để xem AI chơi với cơ chế chống lặp, chạy `main.py` **không kèm** `--strict-search`.

**Lỗi 6: Benchmark lâu**  
Thử `--depth 2 --repeats 3` trước. Depth 4 trở lên có thể chậm hơn đáng kể do số node tăng nhanh.

---

## 13. GHI CHÚ CHO BÁO CÁO

- Các thuật toán trong project đều có **giới hạn độ sâu**; Minimax và Alpha-Beta ở chế độ strict là baseline đánh giá trạng thái kết thúc, **không phải tìm kiếm toàn bộ cây game**.
- Chế độ gameplay mặc định có thêm cơ chế chọn hành động chiến thuật ở tầng gốc để giảm hiện tượng bắn/đứng yên vô ích. Cần ghi rõ khi trình bày thực nghiệm.
- Kết quả thời gian phải đo trên **máy thực tế dùng để báo cáo**; không lấy số liệu ví dụ trong `results/examples/` làm kết quả thực nghiệm của nhóm.
- Nếu nộp bài trong học phần có quy định riêng về công cụ được phép sử dụng, cần tuân thủ quy định đó.

**Thứ tự đề xuất:** Chạy app → kiểm tra 3 map → chạy Unit Tests → Benchmark Depth 2–3–4 → Tactical Benchmark → Tournament → lưu CSV và ảnh minh chứng.
