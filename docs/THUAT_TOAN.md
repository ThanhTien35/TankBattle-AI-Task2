# THUAT TOAN – SIMULTANEOUS GAME

Moi cycle, P1 va P2 chon action tu cung mot trang thai. Engine nhan cap
`(a0, a1)` va cap nhat ca hai cung luc. Depth la so cycle, khong phai so action.

- `Minimax`: pure-strategy maximin, chon action lam lon nhat gia tri te nhat
  qua cac action cua doi phuong, chi cham terminal trong Strict Search.
- `Alpha-Beta`: cung gia tri maximin nhung cat tia cac nhanh khong can.
- `Heuristic Minimax`: maximin voi evaluation khi het depth.
- `Heuristic Alpha-Beta`: ket hop heuristic va pruning.

Cong thuc: `V(s)=max_a min_b V(T(s,a,b))`.

Luu y: Day la **maximin thuan tuy**, khong phai nghiem Nash voi chien
luoc hon hop. Hai AI quyet dinh doc lap tu cung state, khong nhin truoc
action thuc te cua nhau. Chay `--strict-search` de tat root gameplay bonus.

HP: Tank=6; Base=9; Wall=3; dan toi da 3 o / cycle.
