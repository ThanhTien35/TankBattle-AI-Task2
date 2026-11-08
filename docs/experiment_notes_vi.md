# Ghi chu thuc nghiem - Tank Battle AI Task 2

## Muc tieu

- Benchmark: do thoi gian, so node, so la, so lan cat nhanh va action cho **mot quyet dinh**.
- Tactical test: kiem tra AI biet ne dan, di chuyen va ban khi co co hoi.
- Tournament: cho bon thuat toan dau voi nhau tren **3 map rieng**, dao vi tri P1/P2 va nguoi di truoc.
- Replay: ghi lai tung state va su kien sat thuong de phan tich tran dau.

## Ba map

- Classic Battlefield: nhieu tuong gach/thep, map goc.
- Open Arena: it vat can, duong ban rong.
- Tactical Maze: nhieu hanh lang, can di chuyen chon vi tri.

## Ham heuristic da dieu chinh

- HP Tank: trong so 85; HP Base: trong so 105.
- Khoang cach den Tank va Base doi phuong: phat theo Manhattan.
- Duong ban thang: thuong neu khong bi chan; thuong them neu nong sung dung huong.
- Dan dang bay: du doan va phat neu co nguy co trung Tank/Base.
- Utility terminal thang/thua duoc uu tien hon heuristic.

Day la cac trong so thuc nghiem, khong phai gia tri toi uu da duoc chung minh. Khong khang dinh heuristic manh hon neu tournament chua chung minh.

## Cach doc ket qua

- `avg_time_ms`: thoi gian trung binh mot lan ra quyet dinh.
- `avg_nodes`: so node da duyet (co root).
- `avg_prunes`: so lan cat nhanh, khong phai so node bi bo qua.
- `chosen_action`: action duoc chon tu state ban dau.
- `root_score`: chi so sanh giua cap thuat toan dung cung evaluator.
- `unfinished`: dung do `max_plies`, KHONG phai hoa.
- `completed_win_rate_pct`: ty le thang chi tren tran da ket thuc.

## Gioi han hoc thuat

- Minimax va Alpha-Beta la baseline depth-limited, nonterminal cutoff cho diem 0.
- Heuristic Minimax va Heuristic Alpha-Beta cung evaluation function.
- Ket qua co tinh xac dinh, khong coi cac lan lap la mau doc lap.
- Can do lai thoi gian tren may Windows/Python 3.14 hoac macOS theo yeu cau de bai.
- Quy uoc game cycle va cac hanh vi khong duoc de quy dinh chi tiet phai giai thich trong bao cao.

## Lenh chay

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m benchmarks.compare --suite maps --depths 2 3 4 --repeats 5 --output results/maps_depths234.csv
.\.venv\Scripts\python.exe -m benchmarks.compare --suite tactical --depth 3 --repeats 5 --output results/tactical_depth3.csv
.\.venv\Scripts\python.exe -m benchmarks.tournament --suite maps --depth 2 --rounds 2 --max-plies 60 --output results/tournament.csv --summary-output results/tournament_summary.csv
```

Hoac chay `run_experiments.bat` de thuc hien tat ca mot lan.
