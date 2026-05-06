import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import random, math, os

class Matrix:
    def __init__(self, rows=0, cols=0, data=None):
        self.rows = rows
        self.cols = cols
        self.data = [row[:] for row in data] if data else [[0.0]*cols for _ in range(rows)]

    @classmethod
    def from_random(cls, rows, cols, low=-10.0, high=10.0):
        m = cls(rows, cols)
        for i in range(rows):
            for j in range(cols):
                m.data[i][j] = round(random.uniform(low, high), 2)
        return m

    @classmethod
    def from_file(cls, path):
        with open(path, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        data = [list(map(float, l.split())) for l in lines]
        if not data: raise ValueError("Файл порожній")
        c = len(data[0])
        for row in data:
            if len(row) != c: raise ValueError("Рядки різної довжини")
        return cls(len(data), c, data)

    @classmethod
    def from_list(cls, data):
        return cls(len(data), len(data[0]) if data else 0, data)

    @classmethod
    def identity(cls, n):
        m = cls(n, n)
        for i in range(n): m.data[i][i] = 1.0
        return m

    def to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            for row in self.data:
                f.write(" ".join(f"{v:.4f}" for v in row) + "\n")

    def __add__(self, o):
        if self.rows!=o.rows or self.cols!=o.cols: raise ValueError("Різні розміри")
        r = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols): r.data[i][j]=self.data[i][j]+o.data[i][j]
        return r

    def __sub__(self, o):
        if self.rows!=o.rows or self.cols!=o.cols: raise ValueError("Різні розміри")
        r = Matrix(self.rows, self.cols)
        for i in range(self.rows):
            for j in range(self.cols): r.data[i][j]=self.data[i][j]-o.data[i][j]
        return r

    def __mul__(self, o):
        if isinstance(o, (int,float)):
            r = Matrix(self.rows, self.cols)
            for i in range(self.rows):
                for j in range(self.cols): r.data[i][j]=self.data[i][j]*o
            return r
        if self.cols!=o.rows: raise ValueError(f"Неможливо перемножити {self.rows}x{self.cols} і {o.rows}x{o.cols}")
        r = Matrix(self.rows, o.cols)
        for i in range(self.rows):
            for j in range(o.cols):
                r.data[i][j]=sum(self.data[i][k]*o.data[k][j] for k in range(self.cols))
        return r

    def __rmul__(self, s): return self.__mul__(s)

    def transpose(self):
        r = Matrix(self.cols, self.rows)
        for i in range(self.rows):
            for j in range(self.cols): r.data[j][i]=self.data[i][j]
        return r

    def norm_frobenius(self): return math.sqrt(sum(v**2 for row in self.data for v in row))
    def norm_max(self): return max(abs(v) for row in self.data for v in row)
    def norm_row(self): return max(sum(abs(v) for v in row) for row in self.data)
    def copy(self): return Matrix(self.rows, self.cols, self.data)

    def to_text(self):
        return "\n".join("  ".join(f"{v:9.3f}" for v in row) for row in self.data)

class Vector(Matrix):
    def __init__(self, size=0, values=None):
        data = [[v] for v in values] if values else [[0.0] for _ in range(size)]
        super().__init__(len(data), 1, data)

    @classmethod
    def from_random(cls, size, low=-10.0, high=10.0):
        return cls(size, [round(random.uniform(low,high),2) for _ in range(size)])

    def get(self, i): return self.data[i][0]

    def to_text(self): return "  ".join(f"{self.get(i):9.3f}" for i in range(self.rows))

class SLAR:
    def __init__(self, A, b):
        if A.rows!=b.rows: raise ValueError("Розміри A і b не збігаються")
        self.A=A.copy(); self.b=Vector(b.rows,[b.get(i) for i in range(b.rows)]); self.x=None

    def solve_gauss(self):
        n=self.A.rows
        if self.A.cols!=n: raise ValueError("A має бути квадратною")
        aug=Matrix(n,n+1)
        for i in range(n):
            for j in range(n): aug.data[i][j]=self.A.data[i][j]
            aug.data[i][n]=self.b.get(i)
        for col in range(n):
            mr=max(range(col,n),key=lambda r:abs(aug.data[r][col]))
            aug.data[col],aug.data[mr]=aug.data[mr],aug.data[col]
            p=aug.data[col][col]
            if abs(p)<1e-12: raise ValueError("Матриця вироджена")
            for j in range(col,n+1): aug.data[col][j]/=p
            for i in range(n):
                if i!=col:
                    f=aug.data[i][col]
                    for j in range(col,n+1): aug.data[i][j]-=f*aug.data[col][j]
        self.x=Vector(n,[aug.data[i][n] for i in range(n)])
        return self.x

    def residual(self):
        ax=self.A*self.x
        return Vector(self.A.rows,[self.b.get(i)-ax.data[i][0] for i in range(self.A.rows)])

EPS = 1e-12

def _fmt_aug(M, n):
    return "\n".join(
        "[ " + "  ".join(f"{v:8.3f}" for v in r[:n]) +
        "  |  " + "  ".join(f"{v:8.3f}" for v in r[n:]) + " ]"
        for r in M)

def lu_decompose(A):
    n = A.rows
    U, L, P = A.copy(), Matrix.identity(n), Matrix.identity(n)
    log = ["=== LU-РОЗКЛАДАННЯ ===\n\nA:\n", A.to_text(), "\n\n"]
    for col in range(n):
        mr = max(range(col, n), key=lambda r: abs(U.data[r][col]))
        if abs(U.data[mr][col]) < EPS:
            log.append(f"Крок {col+1}: pivot ≈ 0\n"); continue
        if mr != col:
            U.data[col], U.data[mr] = U.data[mr], U.data[col]
            P.data[col], P.data[mr] = P.data[mr], P.data[col]
            for k in range(col):
                L.data[col][k], L.data[mr][k] = L.data[mr][k], L.data[col][k]
            log.append(f"Крок {col+1}: R{col+1} <-> R{mr+1}\n")
        pivot = U.data[col][col]
        log.append(f"Крок {col+1}: pivot = {pivot:.4f}\n")
        for row in range(col+1, n):
            f = U.data[row][col] / pivot
            L.data[row][col] = f
            for j in range(col, n): U.data[row][j] -= f * U.data[col][j]
        log.append(f"U:\n{U.to_text()}\n\n")
    err = (P * A - L * U).norm_max()
    log += [f"L:\n{L.to_text()}\n\n", f"U:\n{U.to_text()}\n\n",
            f"P:\n{P.to_text()}\n\n", f"Перевірка ||PA-LU||∞ = {err:.2e}\n"]
    return L, U, P, "".join(log)

def inverse_gauss_jordan(A):
    n = A.rows
    M = [[A.data[i][j] for j in range(n)] + [1.0 if i==j else 0.0 for j in range(n)]
         for i in range(n)]
    log = ["=== ОБЕРНЕНА МАТРИЦЯ ===\n\n[A|I]:\n", _fmt_aug(M, n), "\n\n"]
    for col in range(n):
        mr = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[mr][col]) < EPS:
            return None, "".join(log) + "Матриця вироджена!\n", False
        if mr != col:
            M[col], M[mr] = M[mr], M[col]
        p = M[col][col]
        M[col] = [v/p for v in M[col]]
        for row in range(n):
            if row != col:
                f = M[row][col]
                M[row] = [M[row][k] - f*M[col][k] for k in range(2*n)]
        log.append(f"Крок {col+1}:\n{_fmt_aug(M, n)}\n\n")
    inv = Matrix.from_list([[M[i][n+j] for j in range(n)] for i in range(n)])
    err = (A * inv - Matrix.identity(n)).norm_max()
    log += [f"A⁻¹:\n{inv.to_text()}\n\n", f"||A·A⁻¹ - I||∞ = {err:.2e}\n"]
    return inv, "".join(log), True

def gauss_steps(A, b):
    n = A.rows
    aug = [[A.data[i][j] for j in range(n)] + [b.get(i)] for i in range(n)]
    log = ["=== МЕТОД ГАУСА (кроки) ===\n\n[A|b]:\n", _fmt_aug(aug, n), "\n\n"]
    for col in range(n):
        mr = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[mr][col]) < EPS:
            return None, "".join(log) + "Матриця вироджена!\n", "singular"
        if mr != col:
            aug[col], aug[mr] = aug[mr], aug[col]
            log.append(f"R{col+1} <-> R{mr+1}\n")
        p = aug[col][col]
        log.append(f"pivot[{col+1},{col+1}] = {p:.4f}\n")
        for row in range(col+1, n):
            f = aug[row][col] / p
            aug[row] = [aug[row][k] - f*aug[col][k] for k in range(n+1)]
            log.append(f"  R{row+1} -= {f:.4f}·R{col+1}\n")
        log.append(f"\n{_fmt_aug(aug, n)}\n\n")
    x_vals = [0.0]*n
    for i in range(n-1, -1, -1):
        x_vals[i] = (aug[i][n] - sum(aug[i][j]*x_vals[j] for j in range(i+1,n))) / aug[i][i]
    log.append("Зворотній хід:\n")
    for i,v in enumerate(x_vals): log.append(f"  x[{i+1}] = {v:.6f}\n")
    x = Vector(n, x_vals)
    res = Vector(n, [b.get(i) - sum(A.data[i][j]*x_vals[j] for j in range(n)) for i in range(n)])
    log.append(f"\n||r||∞ = {res.norm_max():.2e}\n")
    inv, _, ok = inverse_gauss_jordan(A)
    cond = A.norm_row() * inv.norm_row() if ok else float("inf")
    log.append(f"cond(A) = {cond:.3e}\n")
    status = "ill" if cond > 1e6 else "unique"
    if status == "ill": log.append("⚠ Матриця ПОГАНО ОБУМОВЛЕНА!\n")
    return x, "".join(log), status

def check_diagonal_dominance(A):
    n = A.rows
    dominant = True
    info = []
    for i in range(n):
        diag = abs(A.data[i][i])
        off  = sum(abs(A.data[i][j]) for j in range(n) if j != i)
        ratio = off / diag if diag > EPS else float('inf')
        status = "✔" if diag > off else "✖"
        info.append(f"  рядок {i+1}: |a_ii|={diag:.4f}  Σ|a_ij|={off:.4f}  {status}")
        if diag <= off:
            dominant = False
    return dominant, "\n".join(info)

def seidel_solve(A, b, tol=1e-6, max_iter=1000):
    n = A.rows
    if A.cols != n:
        raise ValueError("A має бути квадратною")

    dominant, dom_info = check_diagonal_dominance(A)

    log = ["=== МЕТОД ЗЕЙДЕЛЯ ===\n\n"]
    log.append("Умова діагонального переважання:\n")
    log.append(dom_info + "\n")
    if dominant:
        log.append("➜ Діагональне переважання виконується — збіжність гарантована.\n\n")
    else:
        log.append("➜ ⚠ Діагональне переважання НЕ виконується — збіжність не гарантована!\n\n")

    log.append(f"Матриця A ({n}x{n}):\n{A.to_text()}\n\n")
    log.append(f"Вектор b:\n{b.to_text()}\n\n")
    log.append(f"Точність ε = {tol:.2e},  макс. ітерацій = {max_iter}\n\n")
    log.append(f"{'Ітер':>6}  {'||x_new - x_old||∞':>22}  {'Статус'}\n")
    log.append("─" * 50 + "\n")

    x = [0.0] * n
    converged = False
    it = 0

    for it in range(1, max_iter + 1):
        x_old = x[:]
        for i in range(n):
            aii = A.data[i][i]
            if abs(aii) < EPS:
                raise ValueError(f"Нульовий діагональний елемент a[{i+1}][{i+1}]")
            s = b.get(i)
            for j in range(n):
                if j != i:
                    s -= A.data[i][j] * x[j]
            x[i] = s / aii

        delta = max(abs(x[k] - x_old[k]) for k in range(n))
        status = "збіжність ✔" if delta < tol else ""
        log.append(f"{it:>6}  {delta:>22.8e}  {status}\n")

        if delta < tol:
            converged = True
            break

    log.append("\n")
    if converged:
        log.append(f"✔ Збіжність досягнута за {it} ітерацій.\n\n")
    else:
        log.append(f"✖ Не збіглось за {max_iter} ітерацій.\n\n")

    xv = Vector(n, x)
    res = Vector(n, [b.get(i) - sum(A.data[i][j]*x[j] for j in range(n)) for i in range(n)])
    log.append("Розв'язок x:\n")
    for i in range(n):
        log.append(f"  x[{i+1}] = {x[i]:14.8f}\n")
    log.append(f"\nНев'язка:\n")
    for i in range(n):
        log.append(f"  r[{i+1}] = {res.get(i):12.2e}\n")
    log.append(f"\n||r||∞ = {res.norm_max():.2e}\n")
    log.append(f"||r||F = {res.norm_frobenius():.2e}\n")

    return xv, "".join(log), it, converged

class BandedMatrix:
    def __init__(self, n, p, band_data):
        self.n = n
        self.p = p
        self.band = band_data

    @classmethod
    def from_random(cls, n, p, lo=-9.0, hi=9.0):
        band = []
        for i in range(n):
            row = []
            off_sum = 0.0
            for j in range(max(0, i-p), min(n, i+p+1)):
                if j == i: continue
                v = round(random.uniform(lo, hi), 2)
                row.append((j, v))
                off_sum += abs(v)

            diag_val = round(random.uniform(off_sum + 1.0, off_sum + abs(hi) + 5.0), 2)
            if random.random() < 0.5: diag_val = -diag_val
            row.append((i, diag_val))
            row.sort(key=lambda x: x[0])
            band.append(row)
        return cls(n, p, band)

    @classmethod
    def from_random_no_dominance(cls, n, p, lo=-9.0, hi=9.0):
        band = []
        for i in range(n):
            row = []
            for j in range(max(0, i-p), min(n, i+p+1)):
                v = round(random.uniform(lo, hi), 2)
                row.append((j, v))
            row.sort(key=lambda x: x[0])
            band.append(row)
        return cls(n, p, band)

    def get(self, i, j):
        for col, val in self.band[i]:
            if col == j: return val
        return 0.0

    def set(self, i, j, val):
        for k, (col, _) in enumerate(self.band[i]):
            if col == j:
                if abs(val) < 1e-15:
                    self.band[i].pop(k)
                else:
                    self.band[i][k] = (col, val)
                return
        if abs(val) >= 1e-15:
            self.band[i].append((j, val))
            self.band[i].sort(key=lambda x: x[0])

    def to_full(self):
        m = Matrix(self.n, self.n)
        for i in range(self.n):
            for j, v in self.band[i]:
                m.data[i][j] = v
        return m

    def to_compact_text(self):
        lines = []
        lines.append(f"Стрічкова матриця {self.n}x{self.n}, напів-ширина смуги p={self.p}")
        lines.append(f"Компактне зберігання (ненульові елементи рядку):\n")
        for i, row in enumerate(self.band):
            pairs = "  ".join(f"[{j}]={v:7.3f}" for j, v in row)
            lines.append(f"  рядок {i+1:2d}: {pairs}")
        return "\n".join(lines)

    def to_full_text(self):
        return self.to_full().to_text()

def banded_gauss(BM, b_vals):
    n = BM.n
    p = BM.p

    band = [list(row) for row in BM.band]
    rhs  = list(b_vals)

    def g(i, j):
        for col, val in band[i]:
            if col == j: return val
        return 0.0

    def s(i, j, val):
        for k, (col, _) in enumerate(band[i]):
            if col == j:
                if abs(val) < 1e-15: band[i].pop(k)
                else: band[i][k] = (col, val)
                return
        if abs(val) >= 1e-15:
            band[i].append((j, val))
            band[i].sort(key=lambda x: x[0])

    log = ["=== МЕТОД ГАУСА ДЛЯ СТРІЧКОВОЇ МАТРИЦІ ===\n\n"]
    log.append(f"Розмір: {n}x{n},  напів-ширина смуги: p={p}\n\n")
    log.append("Компактне зберігання початкової матриці:\n")
    for i, row in enumerate(BM.band):
        pairs = "  ".join(f"[{j}]={v:7.3f}" for j, v in row)
        log.append(f"  рядок {i+1:2d}: {pairs}\n")
    log.append(f"\nВектор b: {' '.join(f'{v:.4f}' for v in b_vals)}\n\n")
    log.append("─"*60 + "\n\n")

    for col in range(n):
        pivot = g(col, col)
        if abs(pivot) < EPS:
            log.append(f"Крок {col+1}: pivot ≈ 0 — матриця вироджена!\n")
            return None, "".join(log)
        log.append(f"Крок {col+1}: pivot a[{col+1}][{col+1}] = {pivot:.6f}\n")

        for row in range(col+1, min(n, col+p+1)):
            f = g(row, col) / pivot
            if abs(f) < EPS: continue
            log.append(f"  R{row+1} -= {f:.4f} * R{col+1}\n")

            for jj in range(col, min(n, col+p+1)):
                old = g(row, jj)
                new = old - f * g(col, jj)
                s(row, jj, new)
            rhs[row] -= f * rhs[col]

    log.append("\nКомпактне зберігання після прямого ходу:\n")
    for i, row in enumerate(band):
        pairs = "  ".join(f"[{j}]={v:7.3f}" for j, v in row)
        log.append(f"  рядок {i+1:2d}: {pairs}\n")

    log.append("\nЗворотній хід:\n")
    x = [0.0] * n
    for i in range(n-1, -1, -1):
        aii = g(i, i)
        if abs(aii) < EPS:
            log.append(f"  a[{i+1}][{i+1}] ≈ 0 — вироджена!\n")
            return None, "".join(log)
        x[i] = rhs[i]
        for j in range(i+1, min(n, i+p+1)):
            x[i] -= g(i, j) * x[j]
        x[i] /= aii
        log.append(f"  x[{i+1}] = {x[i]:.8f}\n")

    res = []
    for i in range(n):
        ax_i = sum(BM.get(i, j) * x[j] for j in range(n))
        res.append(b_vals[i] - ax_i)

    r_max = max(abs(r) for r in res)
    r_frob = math.sqrt(sum(r**2 for r in res))
    log.append(f"\nНев'язка r = b - Ax:\n")
    for i, r in enumerate(res):
        log.append(f"  r[{i+1}] = {r:.2e}\n")
    log.append(f"\n||r||∞ = {r_max:.2e}\n")
    log.append(f"||r||F = {r_frob:.2e}\n")

    return x, "".join(log)

BG="#1e1e2e"; CARD="#2a2a3e"; ACNT="#7c9ef8"; GRN="#4ecca3"
YLW="#f9c74f"; RED="#f38ba8"; TXT="#cdd6f4"; MUT="#6c7086"; BRD="#45475a"

root = tk.Tk()
root.title("Matrix Lab")
root.geometry("1300x860")
root.configure(bg=BG)

mat_a = [None]
mat_b = [None]

hdr = tk.Frame(root, bg="#181825", height=48)
hdr.pack(fill="x")
hdr.pack_propagate(False)
tk.Label(hdr, text="Matrix Lab", bg="#181825", fg=ACNT,
         font=("Segoe UI",13,"bold")).pack(side="left", padx=16, pady=10)
tk.Label(hdr, text="Лаб. 1 + Завдання 2 + Завдання 3", bg="#181825",
         fg=MUT, font=("Segoe UI",9)).pack(side="left")
tk.Frame(root, bg=BRD, height=1).pack(fill="x")

tabbar = tk.Frame(root, bg="#181825", height=40)
tabbar.pack(fill="x")
tabbar.pack_propagate(False)
tk.Frame(root, bg=BRD, height=1).pack(fill="x")

status_var = tk.StringVar(value="Готово")
statusbar = tk.Frame(root, bg="#181825", height=26)
statusbar.pack(fill="x", side="bottom")
statusbar.pack_propagate(False)
status_lbl = tk.Label(statusbar, textvariable=status_var, bg="#181825",
                       fg=MUT, font=("Segoe UI",9))
status_lbl.pack(side="left", padx=12)

def ok(msg):  status_var.set("  ✔  " + msg); status_lbl.config(fg=GRN)
def err(msg): messagebox.showerror("Помилка", str(msg)); status_var.set("  ✖  "+str(msg)); status_lbl.config(fg=RED)

pages_frame = tk.Frame(root, bg=BG)
pages_frame.pack(fill="both", expand=True)
pages = []; tab_buttons = []

def show_page(idx):
    for i,(btn_w,pg) in enumerate(zip(tab_buttons, pages)):
        if i==idx:
            btn_w.config(bg=CARD, fg=ACNT, font=("Segoe UI",10,"bold"))
            pg.place(x=0, y=0, relwidth=1, relheight=1); pg.lift()
        else:
            btn_w.config(bg="#181825", fg=MUT, font=("Segoe UI",10))
            pg.place_forget()

def make_tab(label, idx):
    b = tk.Button(tabbar, text=f"  {label}  ", bg="#181825", fg=MUT,
                  font=("Segoe UI",10), activebackground=CARD, activeforeground=ACNT,
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda i=idx: show_page(i))
    b.pack(side="left", padx=2, pady=4, ipady=4); tab_buttons.append(b)

def make_page():
    p = tk.Frame(pages_frame, bg=BG); pages.append(p); return p

def card(parent, title):
    f = tk.Frame(parent, bg=BRD)
    inner = tk.Frame(f, bg=CARD); inner.pack(fill="both", expand=True, padx=1, pady=1)
    tk.Label(inner, text=title, bg=CARD, fg=ACNT,
             font=("Segoe UI",11,"bold")).pack(anchor="w", padx=10, pady=(8,4))
    tk.Frame(inner, bg=BRD, height=1).pack(fill="x")
    body = tk.Frame(inner, bg=CARD); body.pack(fill="both", expand=True, padx=10, pady=8)
    return f, body

def btn(parent, text, cmd, bg=CARD, fg=TXT):
    return tk.Button(parent, text=text, command=cmd, bg=bg, fg=fg,
                     font=("Segoe UI",9,"bold"), activebackground=bg, activeforeground=fg,
                     relief="flat", bd=0, cursor="hand2", padx=10, pady=5)

def lbl(parent, text):
    return tk.Label(parent, text=text, bg=CARD, fg=MUT, font=("Segoe UI",9))

def txt_area(parent, h=10):
    t = scrolledtext.ScrolledText(parent, height=h, font=("Courier New",10),
                                  bg="#11111b", fg=TXT, insertbackground=TXT,
                                  relief="flat", bd=0)
    t.pack(fill="both", expand=True, pady=(4,0)); return t

def fill(w, text):
    w.delete("1.0","end"); w.insert("end", text)

def parse_matrix(w):
    raw = w.get("1.0","end").strip()
    if not raw: err("Поле порожнє!"); return None
    try:
        data=[list(map(float,l.split())) for l in raw.splitlines() if l.strip()]
        return Matrix.from_list(data)
    except Exception as e:
        err(f"Помилка розбору: {e}"); return None

p1 = make_page()
make_tab("① Матриці", 0)

def mat_block(parent, label, mat_ref):
    cf, body = card(parent, f"Матриця  {label}")
    r1 = tk.Frame(body, bg=CARD); r1.pack(fill="x", pady=(0,6))
    rv=tk.IntVar(value=3); cv=tk.IntVar(value=3)
    lv=tk.StringVar(value="-10"); hv=tk.StringVar(value="10")
    for t,var,w in [("Рядки:",rv,4),("Стовпці:",cv,4)]:
        lbl(r1,t).pack(side="left")
        tk.Spinbox(r1,from_=1,to=20,textvariable=var,width=w,
                   bg="#11111b",fg=TXT,relief="flat",
                   buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(2,10))
    for t,var in [("Від:",lv),("До:",hv)]:
        lbl(r1,t).pack(side="left")
        tk.Entry(r1,textvariable=var,width=5,bg="#11111b",fg=TXT,
                 relief="flat",insertbackground=TXT).pack(side="left",padx=(2,8))
    t = scrolledtext.ScrolledText(body, height=10, font=("Courier New",10),
                                  bg="#11111b", fg=TXT, insertbackground=TXT,
                                  relief="flat", bd=0)
    t.pack(fill="both", expand=True)
    r2=tk.Frame(body,bg=CARD); r2.pack(fill="x",pady=(8,0))
    def gen():
        try: m=Matrix.from_random(rv.get(),cv.get(),float(lv.get()),float(hv.get()))
        except Exception as e: return err(e)
        fill(t, m.to_text()); mat_ref[0]=m; ok(f"Матриця {label} згенерована ({m.rows}x{m.cols})")
    def load():
        path=filedialog.askopenfilename(filetypes=[("Текст","*.txt"),("Всі","*.*")])
        if not path: return
        try: m=Matrix.from_file(path); fill(t, m.to_text()); mat_ref[0]=m; ok(f"Матриця {label} завантажена")
        except Exception as e: err(e)
    def save():
        m=parse_matrix(t)
        if not m: return
        path=filedialog.asksaveasfilename(defaultextension=".txt",
              filetypes=[("Текст","*.txt"),("Всі","*.*")])
        if not path: return
        try: m.to_file(path); ok(f"Матриця {label} збережена")
        except Exception as e: err(e)
    def apply_m():
        m=parse_matrix(t)
        if not m: return
        mat_ref[0]=m; ok(f"Матриця {label} прийнята ({m.rows}x{m.cols})")
    def norm():
        m=parse_matrix(t)
        if not m: return
        messagebox.showinfo(f"Норми {label}",
            f"Фробеніусова : {m.norm_frobenius():.6f}\n"
            f"Максимальна  : {m.norm_max():.6f}")
    btn(r2,"Генерувати",gen,  ACNT,"#fff").pack(side="left",padx=(0,4))
    btn(r2,"З файлу",   load, BRD, TXT  ).pack(side="left",padx=4)
    btn(r2,"У файл",    save, BRD, TXT  ).pack(side="left",padx=4)
    btn(r2,"Застосувати",apply_m,YLW,"#000").pack(side="left",padx=4)
    btn(r2,"‖·‖ Норма", norm, BRD, TXT  ).pack(side="left",padx=4)
    return cf, t

wrap1 = tk.Frame(p1, bg=BG)
wrap1.pack(fill="both", expand=True, padx=12, pady=12)
cf_a, tw_a = mat_block(wrap1,"A",mat_a); cf_a.pack(side="left", fill="both", expand=True, padx=(0,6))
cf_b, tw_b = mat_block(wrap1,"B",mat_b); cf_b.pack(side="left", fill="both", expand=True, padx=(6,0))

p2 = make_page()
make_tab("② Операції", 1)
wrap2 = tk.Frame(p2, bg=BG)
wrap2.pack(fill="both", expand=True, padx=12, pady=12)
lcf, lbody = card(wrap2, "Операції над A і B"); lcf.pack(side="left", fill="y", padx=(0,6))
rcf, rbody = card(wrap2, "Результат");          rcf.pack(side="left", fill="both", expand=True, padx=(6,0))
res_txt = scrolledtext.ScrolledText(rbody, font=("Courier New",10), bg="#11111b", fg=GRN,
                                    insertbackground=TXT, relief="flat", bd=0, state="disabled")
res_txt.pack(fill="both", expand=True)

def show_res(title, matrix=None, extra=""):
    res_txt.config(state="normal"); res_txt.delete("1.0","end")
    res_txt.insert("end", f"--- {title} ---\n\n")
    if matrix: res_txt.insert("end", f"Розмір: {matrix.rows} x {matrix.cols}\n\n{matrix.to_text()}")
    if extra:  res_txt.insert("end", "\n\n" + extra)
    res_txt.config(state="disabled"); ok(f"Обчислено: {title}")

def do_op(fn, name):
    if not mat_a[0] or not mat_b[0]: return err("Задайте матриці на вкладці Матриці!")
    try: show_res(name, fn(mat_a[0], mat_b[0]))
    except Exception as e: err(e)

kv = tk.StringVar(value="2")

def obtn(t, cmd, bg=BRD, fg=TXT):
    tk.Button(lbody, text=t, command=cmd, bg=bg, fg=fg, font=("Segoe UI",10),
              activebackground=bg, activeforeground=fg, relief="flat", bd=0,
              cursor="hand2", anchor="w", padx=12, pady=7, width=22).pack(fill="x", pady=2)

obtn("A + B",  lambda: do_op(lambda a,b:a+b,"A + B"), ACNT,"#fff")
obtn("A - B",  lambda: do_op(lambda a,b:a-b,"A - B"))
obtn("A x B",  lambda: do_op(lambda a,b:a*b,"A x B"))
tk.Frame(lbody,bg=BRD,height=1).pack(fill="x",pady=8)
kr=tk.Frame(lbody,bg=CARD); kr.pack(fill="x",pady=(0,4))
lbl(kr,"k =").pack(side="left")
tk.Entry(kr,textvariable=kv,width=7,bg="#11111b",fg=TXT,
         relief="flat",insertbackground=TXT).pack(side="left",padx=(4,0))
def do_scalar(w):
    m=mat_a[0] if w=="A" else mat_b[0]
    if not m: return err(f"Матриця {w} не задана")
    try: show_res(f"{w} x {kv.get()}", m*float(kv.get()))
    except Exception as e: err(e)
obtn("A x k", lambda: do_scalar("A"), YLW,"#000")
obtn("B x k", lambda: do_scalar("B"), YLW,"#000")
tk.Frame(lbody,bg=BRD,height=1).pack(fill="x",pady=8)
def do_transp(w):
    m=mat_a[0] if w=="A" else mat_b[0]
    if not m: return err(f"Матриця {w} не задана")
    show_res(f"{w} транспонована", m.transpose())
obtn("Aᵀ  транспонувати", lambda: do_transp("A"))
obtn("Bᵀ  транспонувати", lambda: do_transp("B"))
tk.Frame(lbody,bg=BRD,height=1).pack(fill="x",pady=8)
def do_norms(w):
    m=mat_a[0] if w=="A" else mat_b[0]
    if not m: return err(f"Матриця {w} не задана")
    show_res(f"Норми {w}", extra=
             f"  Фробеніусова : {m.norm_frobenius():.8f}\n"
             f"  Максимальна  : {m.norm_max():.8f}")
obtn("‖A‖ Норми", lambda: do_norms("A"))
obtn("‖B‖ Норми", lambda: do_norms("B"))

p3 = make_page()
make_tab("③ СЛАР", 2)
wrap3 = tk.Frame(p3, bg=BG)
wrap3.pack(fill="both", expand=True, padx=12, pady=12)
lcf3, lbody3 = card(wrap3, "Система Ax = b"); lcf3.pack(side="left", fill="both", expand=True, padx=(0,6))
rcf3, rbody3 = card(wrap3, "Розв'язок");      rcf3.pack(side="left", fill="both", expand=True, padx=(6,0))
slar_res = scrolledtext.ScrolledText(rbody3, font=("Courier New",10), bg="#11111b", fg=GRN,
                                     insertbackground=TXT, relief="flat", bd=0, state="disabled")
slar_res.pack(fill="both", expand=True)
sn=tk.IntVar(value=3); slo=tk.StringVar(value="-9"); shi=tk.StringVar(value="9")
sr1=tk.Frame(lbody3,bg=CARD); sr1.pack(fill="x",pady=(0,8))
lbl(sr1,"n =").pack(side="left")
tk.Spinbox(sr1,from_=1,to=15,textvariable=sn,width=5,bg="#11111b",fg=TXT,relief="flat",
           buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(4,16))
for t,var in [("Від:",slo),("До:",shi)]:
    lbl(sr1,t).pack(side="left")
    tk.Entry(sr1,textvariable=var,width=5,bg="#11111b",fg=TXT,
             relief="flat",insertbackground=TXT).pack(side="left",padx=(2,8))
lbl(lbody3,"Матриця A:").pack(anchor="w",pady=(4,2))
sA = scrolledtext.ScrolledText(lbody3, height=8, font=("Courier New",10),
                                bg="#11111b", fg=TXT, insertbackground=TXT, relief="flat", bd=0)
sA.pack(fill="both", expand=True)
lbl(lbody3,"Вектор b (через пробіл):").pack(anchor="w",pady=(8,2))
sb = scrolledtext.ScrolledText(lbody3, height=3, font=("Courier New",10),
                                bg="#11111b", fg=TXT, insertbackground=TXT, relief="flat", bd=0)
sb.pack(fill="x")
def slar_gen():
    try:
        n=sn.get(); lo=float(slo.get()); hi=float(shi.get())
        A=Matrix.from_random(n,n,lo,hi); b=Vector.from_random(n,lo,hi)
        fill(sA, A.to_text()); fill(sb, b.to_text()); ok(f"СЛАР {n}x{n} згенеровано")
    except Exception as e: err(e)
def slar_load():
    path=filedialog.askopenfilename(filetypes=[("Текст","*.txt"),("Всі","*.*")])
    if not path: return
    try:
        with open(path,encoding="utf-8") as f:
            lines=[l.strip() for l in f if l.strip()]
        A=Matrix.from_list([list(map(float,l.split())) for l in lines[:-1]])
        bv=list(map(float,lines[-1].split()))
        fill(sA, A.to_text()); fill(sb, Vector(len(bv),bv).to_text()); ok("СЛАР завантажено")
    except Exception as e: err(e)
def slar_solve():
    try:
        A=parse_matrix(sA)
        if not A: return
        bv=list(map(float,sb.get("1.0","end").strip().split()))
        b=Vector(len(bv),bv)
        s=SLAR(A,b); x=s.solve_gauss(); r=s.residual()
        slar_res.config(state="normal"); slar_res.delete("1.0","end")
        slar_res.insert("end","--- Метод Гауса з вибором головного елемента ---\n\n")
        slar_res.insert("end",f"Система: {A.rows} x {A.cols}\n\n")
        slar_res.insert("end","Вектор розв'язку x:\n")
        for i in range(x.rows): slar_res.insert("end",f"  x[{i+1}] = {x.get(i):14.6f}\n")
        slar_res.insert("end","\nНев'язка r = b - Ax:\n")
        for i in range(r.rows): slar_res.insert("end",f"  r[{i+1}] = {r.get(i):12.2e}\n")
        slar_res.insert("end",f"\n||r|| = {r.norm_frobenius():.2e}\n")
        slar_res.config(state="disabled"); ok("СЛАР розв'язано")
    except Exception as e: err(e)
sr2=tk.Frame(lbody3,bg=CARD); sr2.pack(fill="x",pady=(10,0))
btn(sr2,"Генерувати",        slar_gen,   ACNT,"#fff").pack(side="left",padx=(0,4))
btn(sr2,"З файлу",           slar_load,  BRD, TXT  ).pack(side="left",padx=4)
btn(sr2,"Розв'язати (Гаус)", slar_solve, GRN, "#064e3b").pack(side="left",padx=4)

p4 = make_page()
make_tab("④ Завдання 2", 3)

wrap4 = tk.Frame(p4, bg=BG)
wrap4.pack(fill="both", expand=True, padx=12, pady=12)

lcf4, lbody4 = card(wrap4, "Матриця A  та  вектор b")
lcf4.pack(side="left", fill="both", padx=(0,6))

z_n = tk.IntVar(value=3); z_lo = tk.StringVar(value="-9"); z_hi = tk.StringVar(value="9")
r0 = tk.Frame(lbody4, bg=CARD); r0.pack(fill="x", pady=(0,6))
lbl(r0,"n =").pack(side="left")
tk.Spinbox(r0,from_=2,to=12,textvariable=z_n,width=4,bg="#11111b",fg=TXT,
           relief="flat",buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(2,12))
for t,var in [("Від:",z_lo),("До:",z_hi)]:
    lbl(r0,t).pack(side="left")
    tk.Entry(r0,textvariable=var,width=5,bg="#11111b",fg=TXT,
             relief="flat",insertbackground=TXT).pack(side="left",padx=(2,8))

def z_gen():
    n=z_n.get(); lo=float(z_lo.get()); hi=float(z_hi.get())
    A=Matrix.from_random(n,n,lo,hi); b=Vector.from_random(n,lo,hi)
    fill(zA, A.to_text()); fill(zB, b.to_text()); ok(f"Згенеровано {n}x{n}")

def z_load():
    path=filedialog.askopenfilename(filetypes=[("Текст","*.txt"),("Всі","*.*")])
    if not path: return
    try:
        with open(path,encoding="utf-8") as f:
            lines=[l.strip() for l in f if l.strip()]
        A=Matrix.from_list([list(map(float,l.split())) for l in lines[:-1]])
        bv=list(map(float,lines[-1].split()))
        fill(zA, A.to_text()); fill(zB, Vector(len(bv),bv).to_text()); ok("Завантажено")
    except Exception as e: err(e)

def z_test1():
    A=Matrix.from_list([[2,1,-1],[-3,-1,2],[-2,1,2]])
    b=Vector(3,[8.0,-11.0,-3.0])
    fill(zA, A.to_text()); fill(zB, b.to_text()); ok("Тест 1 — унікальний розв'язок")

def z_test2():
    n=4; d=[[1/(i+j+1) for j in range(n)] for i in range(n)]
    A=Matrix.from_list(d); b=Vector(n,[sum(r) for r in d])
    fill(zA, A.to_text()); fill(zB, b.to_text()); ok("Тест 2 — матриця Гільберта (погано обумовлена)")

def do_gauss():
    A, b = z_get_Ab()
    if not A: return
    try: x, log, status = gauss_steps(A, b)
    except Exception as e: return err(e)
    set_panel("Кроки", log)
    if x is None:
        set_panel("Розв'язок", "Матриця вироджена!", RED); show_inner("Розв'язок"); return
    colors = {"unique": GRN, "ill": YLW}
    labels = {"unique": "Єдиний розв'язок", "ill": "⚠ Погано обумовлена матриця!"}
    out = labels.get(status,"") + f"\n\nСистема {A.rows}x{A.cols}\n\nВектор x:\n"
    for i in range(x.rows): out += f"  x[{i+1}] = {x.get(i):14.6f}\n"
    res = Vector(A.rows,[b.get(i)-sum(A.data[i][j]*x.get(j) for j in range(A.cols)) for i in range(A.rows)])
    out += f"\n||r||∞ = {res.norm_max():.2e}\n||r||F = {res.norm_frobenius():.2e}\n"
    set_panel("Розв'язок", out, colors.get(status, TXT))
    show_inner("Розв'язок"); ok(labels.get(status,"Готово"))

def do_lu():
    A, _ = z_get_Ab()
    if not A: return
    try: L, U, P, log = lu_decompose(A)
    except Exception as e: return err(e)
    set_panel("LU", log); show_inner("LU"); ok("LU-розкладання виконано")

def do_inverse():
    A, _ = z_get_Ab()
    if not A: return
    try: inv, log, success = inverse_gauss_jordan(A)
    except Exception as e: return err(e)
    set_panel("Обернена", log, GRN if success else RED)
    show_inner("Обернена")
    ok("A⁻¹ знайдено" if success else "Матриця вироджена")

rb = tk.Frame(lbody4, bg=CARD); rb.pack(fill="x", pady=(0,4))
btn(rb,"Генерувати",        z_gen,   BRD, TXT  ).pack(side="left",padx=(0,4))
btn(rb,"З файлу",           z_load,  BRD, TXT  ).pack(side="left",padx=4)
btn(rb,"Тест 1",            z_test1, BRD, TXT  ).pack(side="left",padx=4)
btn(rb,"Тест 2 (Гільберт)", z_test2, BRD, TXT  ).pack(side="left",padx=4)

act = tk.Frame(lbody4, bg=CARD); act.pack(fill="x", pady=(0,6))
btn(act,"▶ Розв'язати (Гаус)", do_gauss,  BRD, TXT  ).pack(side="left",padx=(0,4))
btn(act,"LU-розкладання",      do_lu,     BRD, TXT  ).pack(side="left",padx=4)
btn(act,"A⁻¹ Обернена",        do_inverse,BRD, TXT  ).pack(side="left",padx=4)

lbl(lbody4,"Матриця A:").pack(anchor="w", pady=(4,2))
zA = scrolledtext.ScrolledText(lbody4, height=8, font=("Courier New",10),
                                bg="#11111b", fg=TXT, insertbackground=TXT, relief="flat", bd=0)
zA.pack(fill="both", expand=True)

lbl(lbody4,"Вектор b:").pack(anchor="w", pady=(6,2))
zB = scrolledtext.ScrolledText(lbody4, height=3, font=("Courier New",10),
                                bg="#11111b", fg=TXT, insertbackground=TXT, relief="flat", bd=0)
zB.pack(fill="x")

rcf4, rbody4 = card(wrap4, "Результат")
rcf4.pack(side="left", fill="both", expand=True, padx=(6,0))

inner_tabs  = tk.Frame(rbody4, bg=CARD); inner_tabs.pack(fill="x")
inner_frame = tk.Frame(rbody4, bg="#11111b"); inner_frame.pack(fill="both", expand=True, pady=(6,0))
inner_frame.update_idletasks()

res_panels = {}; inner_btns = {}

for tab_name in ["Розв'язок", "Кроки", "LU", "Обернена"]:
    frame = tk.Frame(inner_frame, bg="#11111b")
    txt = scrolledtext.ScrolledText(frame, font=("Courier New",10),
                                    bg="#11111b", fg=TXT, insertbackground=TXT,
                                    relief="flat", bd=0, state="disabled")
    txt.pack(fill="both", expand=True)
    res_panels[tab_name] = (frame, txt)

def show_inner(name):
    for k, (fb, fp) in res_panels.items():
        if k == name:
            inner_btns[k].config(fg=ACNT, font=("Segoe UI", 9, "bold"))
            fb.place(x=0, y=0, relwidth=1, relheight=1)
            fb.lift()
        else:
            inner_btns[k].config(fg=MUT, font=("Segoe UI", 9))
            fb.place_forget()

def set_panel(name, text, fg=TXT):
    _, txt = res_panels[name]
    txt.config(state="normal", fg=fg); txt.delete("1.0","end")
    txt.insert("end", text); txt.config(state="disabled")

def z_get_Ab():
    A = parse_matrix(zA)
    if not A: return None, None
    raw = zB.get("1.0","end").strip()
    if not raw: err("b порожній!"); return None, None
    try: bv=list(map(float,raw.split())); b=Vector(len(bv),bv)
    except Exception as e: err(e); return None, None
    return A, b

for tab_name in ["Розв'язок", "Кроки", "LU", "Обернена"]:
    b = tk.Button(inner_tabs, text=tab_name, bg=CARD, fg=MUT,
                  font=("Segoe UI",9), relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=4,
                  command=lambda n=tab_name: show_inner(n))
    b.pack(side="left", padx=2); inner_btns[tab_name] = b

show_inner("Розв'язок")

p5 = make_page()
make_tab("⑤ Завдання 3", 4)

wrap5 = tk.Frame(p5, bg=BG)
wrap5.pack(fill="both", expand=True, padx=12, pady=12)

lcf5, lbody5 = card(wrap5, "Завдання 3")
lcf5.pack(side="left", fill="both", padx=(0,6))
lcf5.configure(width=420)
lcf5.pack_propagate(False)

subtab_bar = tk.Frame(lbody5, bg=CARD)
subtab_bar.pack(fill="x", pady=(0, 8))

subtab_content = tk.Frame(lbody5, bg=CARD)
subtab_content.pack(fill="both", expand=True)

sub_panels = {}
sub_btns   = {}

def show_sub(name):
    for k, f in sub_panels.items():
        if k == name:
            sub_btns[k].config(fg=ACNT, font=("Segoe UI",9,"bold"), bg="#11111b")
            f.place(x=0, y=0, relwidth=1, relheight=1); f.lift()
        else:
            sub_btns[k].config(fg=MUT, font=("Segoe UI",9), bg=CARD)
            f.place_forget()

def make_sub(name):
    f = tk.Frame(subtab_content, bg=CARD)
    sub_panels[name] = f
    b = tk.Button(subtab_bar, text=name, bg=CARD, fg=MUT,
                  font=("Segoe UI",9), relief="flat", bd=0, cursor="hand2",
                  padx=10, pady=4, command=lambda n=name: show_sub(n))
    b.pack(side="left", padx=2)
    sub_btns[name] = b
    return f

rcf5, rbody5 = card(wrap5, "Результат / Лог")
rcf5.pack(side="left", fill="both", expand=True, padx=(6,0))

res5_tab_bar   = tk.Frame(rbody5, bg=CARD); res5_tab_bar.pack(fill="x")
res5_frame     = tk.Frame(rbody5, bg="#11111b"); res5_frame.pack(fill="both", expand=True, pady=(6,0))

res5_panels = {}; res5_btns = {}

def show_res5(name):
    for k, (fb, _) in res5_panels.items():
        if k == name:
            res5_btns[k].config(fg=ACNT, font=("Segoe UI",9,"bold"))
            fb.place(x=0, y=0, relwidth=1, relheight=1); fb.lift()
        else:
            res5_btns[k].config(fg=MUT, font=("Segoe UI",9))
            fb.place_forget()

def make_res5_panel(name):
    frame = tk.Frame(res5_frame, bg="#11111b")
    txt   = scrolledtext.ScrolledText(frame, font=("Courier New",10),
                                       bg="#11111b", fg=TXT, insertbackground=TXT,
                                       relief="flat", bd=0, state="disabled")
    txt.pack(fill="both", expand=True)
    res5_panels[name] = (frame, txt)
    b = tk.Button(res5_tab_bar, text=name, bg=CARD, fg=MUT,
                  font=("Segoe UI",9), relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=4, command=lambda n=name: show_res5(n))
    b.pack(side="left", padx=2)
    res5_btns[name] = b

def set_res5(name, text, fg=TXT):
    _, txt = res5_panels[name]
    txt.config(state="normal", fg=fg); txt.delete("1.0","end")
    txt.insert("end", text); txt.config(state="disabled")

for pname in ["Зейдель", "Кроки (Зейдель)", "Стрічкова", "Кроки (Стрічкова)"]:
    make_res5_panel(pname)
show_res5("Зейдель")

sp_seidel = make_sub("① Метод Зейделя")

sc_r0 = tk.Frame(sp_seidel, bg=CARD); sc_r0.pack(fill="x", pady=(2,4))
sc_n   = tk.IntVar(value=4)
sc_lo  = tk.StringVar(value="-9"); sc_hi = tk.StringVar(value="9")
sc_tol = tk.StringVar(value="1e-6"); sc_max = tk.IntVar(value=500)

lbl(sc_r0,"n =").pack(side="left")
tk.Spinbox(sc_r0,from_=2,to=15,textvariable=sc_n,width=4,bg="#11111b",fg=TXT,
           relief="flat",buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(2,14))
for t,var in [("Від:",sc_lo),("До:",sc_hi)]:
    lbl(sc_r0,t).pack(side="left")
    tk.Entry(sc_r0,textvariable=var,width=6,bg="#11111b",fg=TXT,
             relief="flat",insertbackground=TXT).pack(side="left",padx=(2,10))

sc_r1 = tk.Frame(sp_seidel, bg=CARD); sc_r1.pack(fill="x", pady=(0,6))
lbl(sc_r1,"Точність ε:").pack(side="left")
tk.Entry(sc_r1,textvariable=sc_tol,width=8,bg="#11111b",fg=TXT,
         relief="flat",insertbackground=TXT).pack(side="left",padx=(2,14))
lbl(sc_r1,"Макс. ітерацій:").pack(side="left")
tk.Spinbox(sc_r1,from_=10,to=10000,textvariable=sc_max,width=7,bg="#11111b",fg=TXT,
           relief="flat",buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(2,0))

lbl(sp_seidel,"Матриця A:").pack(anchor="w",pady=(4,2))
sc_A = scrolledtext.ScrolledText(sp_seidel, height=7, font=("Courier New",10),
                                  bg="#11111b", fg=TXT, insertbackground=TXT, relief="flat", bd=0)
sc_A.pack(fill="both", expand=True)

lbl(sp_seidel,"Вектор b:").pack(anchor="w",pady=(6,2))
sc_b = scrolledtext.ScrolledText(sp_seidel, height=2, font=("Courier New",10),
                                  bg="#11111b", fg=TXT, insertbackground=TXT, relief="flat", bd=0)
sc_b.pack(fill="x")

def sc_gen_conv():
    n = sc_n.get()
    lo = float(sc_lo.get()); hi = float(sc_hi.get())
    rows = []
    for i in range(n):
        row = [round(random.uniform(lo, hi), 2) for _ in range(n)]
        off = sum(abs(row[j]) for j in range(n) if j!=i)
        row[i] = round(random.uniform(off+1, off+abs(hi)+5), 2)
        if random.random()<0.5: row[i]=-row[i]
        rows.append(row)
    A = Matrix.from_list(rows)
    bv = Vector.from_random(n, lo, hi)
    fill(sc_A, A.to_text()); fill(sc_b, bv.to_text())
    ok(f"Згенеровано {n}x{n} з діагональним переважанням (збіжність ✔)")

def sc_gen_noconv():
    n = sc_n.get()
    lo = float(sc_lo.get()); hi = float(sc_hi.get())
    A = Matrix.from_random(n, n, lo, hi)
    bv = Vector.from_random(n, lo, hi)
    fill(sc_A, A.to_text()); fill(sc_b, bv.to_text())
    ok(f"Згенеровано {n}x{n} БЕЗ гарантії збіжності ⚠")

def sc_test_conv():
    A = Matrix.from_list([
        [10, -1,  2,  0],
        [-1, 11, -1,  3],
        [ 2, -1, 10, -1],
        [ 0,  3, -1,  8],
    ])
    b = Vector(4, [6.0, 25.0, -11.0, 15.0])
    fill(sc_A, A.to_text()); fill(sc_b, b.to_text())
    ok("Тест зі збіжністю — діагональне переважання ✔")

def sc_test_noconv():
    A = Matrix.from_list([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ])
    b = Vector(3, [1.0, 2.0, 3.0])
    fill(sc_A, A.to_text()); fill(sc_b, b.to_text())
    ok("Тест БЕЗ збіжності — виняткова матриця ⚠")


def sc_load():
    path = filedialog.askopenfilename(filetypes=[("Текст","*.txt"),("Всі","*.*")])
    if not path: return
    try:
        with open(path, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        A = Matrix.from_list([list(map(float, l.split())) for l in lines[:-1]])
        bv = list(map(float, lines[-1].split()))
        fill(sc_A, A.to_text()); fill(sc_b, Vector(len(bv), bv).to_text())
        ok(f"Завантажено {A.rows}×{A.cols} з файлу")
    except Exception as e:
        err(e)

def sc_solve():
    try:
        A = parse_matrix(sc_A)
        if not A: return
        raw = sc_b.get("1.0","end").strip()
        bv  = list(map(float, raw.split()))
        b   = Vector(len(bv), bv)
        tol = float(sc_tol.get())
        mxi = sc_max.get()
        x, log, iters, conv = seidel_solve(A, b, tol, mxi)
    except Exception as e:
        return err(e)

    set_res5("Кроки (Зейдель)", log, TXT)

    color = GRN if conv else RED
    summary = f"{'✔ ЗБІГЛОСЬ' if conv else '✖ НЕ ЗБІГЛОСЬ'} за {iters} ітерацій\n"
    summary += f"ε = {tol:.2e},  макс. = {mxi}\n\n"
    if x:
        summary += "Розв'язок x:\n"
        for i in range(x.rows):
            summary += f"  x[{i+1}] = {x.get(i):14.8f}\n"
        res = Vector(A.rows, [b.get(i)-sum(A.data[i][j]*x.get(j) for j in range(A.cols)) for i in range(A.rows)])
        summary += f"\n||r||∞ = {res.norm_max():.2e}\n||r||F = {res.norm_frobenius():.2e}\n"
    set_res5("Зейдель", summary, color)
    show_res5("Зейдель")
    ok(f"Зейдель: {'збіжність' if conv else 'НЕ збіжність'} ({iters} іт.)")

sc_br1 = tk.Frame(sp_seidel, bg=CARD); sc_br1.pack(fill="x", pady=(8,3))
btn(sc_br1, "Генерувати (збіжн.)",    sc_gen_conv,   BRD,  TXT  ).pack(side="left", padx=(0,6))
btn(sc_br1, "Генерувати (незбіжн.)",  sc_gen_noconv, BRD,  TXT  ).pack(side="left", padx=(0,6))
btn(sc_br1, "З файлу",                 sc_load,       BRD,  TXT  ).pack(side="left", padx=(0,6))

sc_br2 = tk.Frame(sp_seidel, bg=CARD); sc_br2.pack(fill="x", pady=(0,3))
btn(sc_br2, "Тест 1 — збіжний",       sc_test_conv,  BRD,  TXT  ).pack(side="left", padx=(0,6))
btn(sc_br2, "Тест 2 — незбіжний",     sc_test_noconv,BRD,  TXT  ).pack(side="left", padx=(0,6))

sc_br3 = tk.Frame(sp_seidel, bg=CARD); sc_br3.pack(fill="x", pady=(0,4))
btn(sc_br3, "▶  Розв'язати методом Зейделя", sc_solve, BRD,  TXT  ).pack(side="left")

sp_band = make_sub("② Стрічкова матриця")

bd_r0 = tk.Frame(sp_band, bg=CARD); bd_r0.pack(fill="x", pady=(2,4))
bd_n = tk.IntVar(value=6); bd_p = tk.IntVar(value=2)
bd_lo = tk.StringVar(value="-9"); bd_hi = tk.StringVar(value="9")

lbl(bd_r0,"n =").pack(side="left")
tk.Spinbox(bd_r0,from_=3,to=20,textvariable=bd_n,width=4,bg="#11111b",fg=TXT,
           relief="flat",buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(2,14))
for t,var in [("Від:",bd_lo),("До:",bd_hi)]:
    lbl(bd_r0,t).pack(side="left")
    tk.Entry(bd_r0,textvariable=var,width=6,bg="#11111b",fg=TXT,
             relief="flat",insertbackground=TXT).pack(side="left",padx=(2,10))

bd_r1 = tk.Frame(sp_band, bg=CARD); bd_r1.pack(fill="x", pady=(0,6))
lbl(bd_r1,"Напів-ширина смуги  p =").pack(side="left")
tk.Spinbox(bd_r1,from_=1,to=10,textvariable=bd_p,width=4,bg="#11111b",fg=TXT,
           relief="flat",buttonbackground=BRD,insertbackground=TXT).pack(side="left",padx=(2,0))

lbl(sp_band,"Компактне зберігання (ненульові елементи):").pack(anchor="w",pady=(4,2))
bd_compact_txt = scrolledtext.ScrolledText(sp_band, height=8, font=("Courier New",9),
                                            bg="#11111b", fg=ACNT, insertbackground=TXT,
                                            relief="flat", bd=0, state="disabled")
bd_compact_txt.pack(fill="both", expand=True)

lbl(sp_band,"Повний вигляд матриці:").pack(anchor="w",pady=(6,2))
bd_full_txt = scrolledtext.ScrolledText(sp_band, height=6, font=("Courier New",9),
                                         bg="#11111b", fg=MUT, insertbackground=TXT,
                                         relief="flat", bd=0, state="disabled")
bd_full_txt.pack(fill="x")

lbl(sp_band,"Вектор b:").pack(anchor="w",pady=(6,2))
bd_b_txt = scrolledtext.ScrolledText(sp_band, height=2, font=("Courier New",10),
                                      bg="#11111b", fg=TXT, insertbackground=TXT,
                                      relief="flat", bd=0)
bd_b_txt.pack(fill="x")

current_banded = [None]

def bd_refresh_display(BM, bv):
    bd_compact_txt.config(state="normal"); bd_compact_txt.delete("1.0","end")
    bd_compact_txt.insert("end", BM.to_compact_text()); bd_compact_txt.config(state="disabled")
    bd_full_txt.config(state="normal"); bd_full_txt.delete("1.0","end")
    bd_full_txt.insert("end", BM.to_full_text()); bd_full_txt.config(state="disabled")
    fill(bd_b_txt, "  ".join(f"{v:.3f}" for v in bv))

def bd_gen():
    n=bd_n.get(); p=bd_p.get(); lo=float(bd_lo.get()); hi=float(bd_hi.get())
    BM = BandedMatrix.from_random(n, p, lo, hi)
    bv = [round(random.uniform(lo, hi), 2) for _ in range(n)]
    current_banded[0] = (BM, bv)
    bd_refresh_display(BM, bv)
    ok(f"Стрічкова матриця {n}x{n} p={p} (з діагон. переважанням)")

def bd_test1():
    data = [
        [(0, 4.0),  (1,-1.0)],
        [(0,-1.0),  (1, 4.0), (2,-1.0)],
        [(1,-1.0),  (2, 4.0), (3,-1.0)],
        [(2,-1.0),  (3, 4.0), (4,-1.0)],
        [(3,-1.0),  (4, 4.0)],
    ]
    BM = BandedMatrix(5, 1, data)
    bv = [3.0, 2.0, 2.0, 2.0, 3.0]
    current_banded[0] = (BM, bv)
    bd_refresh_display(BM, bv)
    ok("Тест 1 — тридіагональна 5x5")

def bd_test2():
    n=6; p=2
    d = [[0.0]*n for _ in range(n)]
    for i in range(n):
        d[i][i] = 10.0
        for j in [i-1,i+1,i-2,i+2]:
            if 0 <= j < n: d[i][j] = -1.0
    A = Matrix.from_list(d)

    band = []
    for i in range(n):
        row = [(j, d[i][j]) for j in range(max(0,i-p), min(n,i+p+1)) if abs(d[i][j])>1e-15]
        band.append(row)
    BM = BandedMatrix(n, p, band)
    bv = [round(random.uniform(-5,5),2) for _ in range(n)]
    current_banded[0] = (BM, bv)
    bd_refresh_display(BM, bv)
    ok("Тест 2 — пентадіагональна 6x6")


def bd_load():
    path = filedialog.askopenfilename(filetypes=[("Текст","*.txt"),("Всі","*.*")])
    if not path: return
    try:
        with open(path, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        # Format: rows of band matrix, last line = b
        # We reconstruct as full matrix then convert to banded
        A = Matrix.from_list([list(map(float, l.split())) for l in lines[:-1]])
        bv = list(map(float, lines[-1].split()))
        n = A.rows
        p = max(abs(i-j) for i in range(n) for j in range(n) if abs(A.data[i][j]) > 1e-14)
        band = []
        for i in range(n):
            row = [(j, A.data[i][j]) for j in range(max(0,i-p), min(n,i+p+1)) if abs(A.data[i][j]) > 1e-14]
            band.append(row)
        BM = BandedMatrix(n, p, band)
        current_banded[0] = (BM, bv)
        bd_refresh_display(BM, bv)
        ok(f"Завантажено {n}×{n} (p={p}) з файлу")
    except Exception as e:
        err(e)

def bd_solve():
    if not current_banded[0]:
        return err("Спочатку згенеруйте або завантажте матрицю!")
    BM, bv_raw = current_banded[0]
    try:
        raw = bd_b_txt.get("1.0","end").strip()
        bv  = list(map(float, raw.split()))
        if len(bv) != BM.n:
            return err(f"b має містити {BM.n} елементів, отримано {len(bv)}")
        x, log = banded_gauss(BM, bv)
    except Exception as e:
        return err(e)

    set_res5("Кроки (Стрічкова)", log, TXT)

    if x is None:
        set_res5("Стрічкова", "Матриця вироджена або помилка!\n\nДив. вкладку Кроки.", RED)
        show_res5("Стрічкова"); return

    summary  = f"✔ Система вирішена методом Гауса (стрічкова матриця)\n"
    summary += f"Розмір: {BM.n}x{BM.n},  напів-ширина смуги p={BM.p}\n\n"
    summary += "Розв'язок x:\n"
    for i,v in enumerate(x):
        summary += f"  x[{i+1}] = {v:14.8f}\n"
    res2 = [bv[i] - sum(BM.get(i,j)*x[j] for j in range(BM.n)) for i in range(BM.n)]
    r_max  = max(abs(r) for r in res2)
    r_frob = math.sqrt(sum(r**2 for r in res2))
    summary += f"\n||r||∞ = {r_max:.2e}\n||r||F = {r_frob:.2e}\n"
    set_res5("Стрічкова", summary, GRN)
    show_res5("Стрічкова")
    ok(f"Стрічкова СЛАР розв'язана ✔  ||r||∞={r_max:.2e}")

bd_br1 = tk.Frame(sp_band, bg=CARD); bd_br1.pack(fill="x", pady=(8,3))
btn(bd_br1,"Генерувати випадкову",    bd_gen,   BRD, TXT  ).pack(side="left",padx=(0,6))
btn(bd_br1,"Тест 1 — тридіагональна", bd_test1, BRD, TXT  ).pack(side="left",padx=(0,6))
btn(bd_br1,"З файлу",                  bd_load,  BRD, TXT  ).pack(side="left",padx=(0,6))

bd_br2 = tk.Frame(sp_band, bg=CARD); bd_br2.pack(fill="x", pady=(0,4))
btn(bd_br2,"Тест 2 — пентадіагональна", bd_test2, BRD, TXT  ).pack(side="left",padx=(0,6))
btn(bd_br2,"▶  Розв'язати (Гаус)",      bd_solve, BRD, TXT  ).pack(side="left")

show_sub("① Метод Зейделя")

p6 = make_page()
make_tab("⑥ Завдання 4", 5)

wrap6 = tk.Frame(p6, bg=BG)
wrap6.pack(fill="both", expand=True, padx=12, pady=12)

lcf6, lbody6 = card(wrap6, "Розріджені матриці / Алгоритм Катхіл-Маккі")
lcf6.pack(side="left", fill="both", padx=(0, 6))
lcf6.configure(width=440)
lcf6.pack_propagate(False)

rcf6, rbody6 = card(wrap6, "Результат / Лог")
rcf6.pack(side="left", fill="both", expand=True, padx=(6, 0))

# ── Результатні панелі (права сторона) ──────────────────
res6_tab_bar = tk.Frame(rbody6, bg=CARD); res6_tab_bar.pack(fill="x")
res6_frame   = tk.Frame(rbody6, bg="#11111b"); res6_frame.pack(fill="both", expand=True, pady=(6,0))

res6_panels = {}; res6_btns = {}

def show_res6(name):
    for k, (fb, _) in res6_panels.items():
        if k == name:
            res6_btns[k].config(fg=ACNT, font=("Segoe UI",9,"bold"))
            fb.place(x=0, y=0, relwidth=1, relheight=1); fb.lift()
        else:
            res6_btns[k].config(fg=MUT, font=("Segoe UI",9))
            fb.place_forget()

def make_res6_panel(name):
    frame = tk.Frame(res6_frame, bg="#11111b")
    txt   = scrolledtext.ScrolledText(frame, font=("Courier New",10),
                                       bg="#11111b", fg=TXT, insertbackground=TXT,
                                       relief="flat", bd=0, state="disabled")
    txt.pack(fill="both", expand=True)
    res6_panels[name] = (frame, txt)
    b = tk.Button(res6_tab_bar, text=name, bg=CARD, fg=MUT,
                  font=("Segoe UI",9), relief="flat", bd=0, cursor="hand2",
                  padx=8, pady=4, command=lambda n=name: show_res6(n))
    b.pack(side="left", padx=2)
    res6_btns[name] = b

def set_res6(name, text, fg=TXT):
    _, txt = res6_panels[name]
    txt.config(state="normal", fg=fg); txt.delete("1.0","end")
    txt.insert("end", text); txt.config(state="disabled")

for _pn in ["Граф / Шляхи", "Гібс / Псевдопериф.", "Катхіл-Маккі", "Розв'язок"]:
    make_res6_panel(_pn)
show_res6("Граф / Шляхи")


def build_graph(A):
    """Побудова графа зі СЛАР: ребро (i,j) якщо A[i][j]!=0 і i!=j"""
    n = A.rows
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and abs(A.data[i][j]) > 1e-14:
                adj[i].add(j)
                adj[j].add(i)
    return adj

def bfs_path(adj, src, dst):
    """BFS: повертає довжину найкоротшого шляху від src до dst, або -1"""
    n = len(adj)
    dist = [-1] * n
    dist[src] = 0
    queue = [src]
    head = 0
    while head < len(queue):
        u = queue[head]; head += 1
        for v in adj[u]:
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist[dst]

def bfs_distances(adj, src):
    """BFS з вершини src: повертає масив відстаней"""
    n = len(adj)
    dist = [-1] * n
    dist[src] = 0
    queue = [src]
    head = 0
    while head < len(queue):
        u = queue[head]; head += 1
        for v in sorted(adj[u]):
            if dist[v] == -1:
                dist[v] = dist[u] + 1
                queue.append(v)
    return dist

def gibbs_pseudo_peripheral(adj):
    """
    Метод Гібса для псевдопериферійної вершини.
    1. Обрати довільну початкову вершину u.
    2. BFS від u → знайти вершину v з максимальною відстанню (рівень L).
    3. BFS від v → якщо рівнева структура довша — оновити v, повторити.
    """
    n = len(adj)
    log = ["=== МЕТОД ГІБСА (Псевдопериферійна вершина) ===\n\n"]
    log.append("Алгоритм:\n"
               "  1. Обираємо довільну стартову вершину u.\n"
               "  2. BFS від u → вершина v з найбільшою відстанню (кінець рівневої структури).\n"
               "  3. BFS від v → якщо ширина рівнів менша ніж від u — v стає новим псевдо-периферійним.\n"
               "  4. Повторюємо до стабілізації.\n\n")

    start = min(range(n), key=lambda i: len(adj[i]))
    log.append(f"Початкова вершина (мін. ступінь): u = {start+1}\n\n")

    def level_width(src):
        dist = bfs_distances(adj, src)
        max_d = max(d for d in dist if d >= 0)
        levels = [0]*(max_d+1)
        for d in dist:
            if d >= 0: levels[d] += 1
        return dist, max_d, levels

    dist, ecc, levels = level_width(start)
    pseudo = start
    log.append(f"BFS від {start+1}: ексцентриситет = {ecc}, рівні = {levels}\n")

    for iteration in range(1, 30):
        candidate = max((i for i in range(n) if dist[i] >= 0), key=lambda i: dist[i])
        dist2, ecc2, levels2 = level_width(candidate)
        log.append(f"Ітерація {iteration}: кандидат = {candidate+1}, "
                   f"ексцентриситет = {ecc2}, рівні = {levels2}\n")
        if ecc2 > ecc or (ecc2 == ecc and max(levels2) < max(levels)):
            pseudo = candidate
            dist, ecc, levels = dist2, ecc2, levels2
            log.append(f"  → Оновлено псевдопериферійну вершину: {pseudo+1}\n")
        else:
            log.append(f"  → Стабілізація. Псевдопериферійна вершина: {pseudo+1}\n")
            break

    log.append(f"\nРезультат: псевдопериферійна вершина = {pseudo+1}\n")
    log.append(f"Рівнева структура BFS від {pseudo+1}: {levels}\n")
    log.append(f"Ширина смуги графа від цієї вершини: {ecc}\n")
    return pseudo, "".join(log)

def cuthill_mckee(adj, start=None):
    """
    Алгоритм Катхіл-Маккі (RCM — Reverse Cuthill-McKee).
    1. Псевдопериферійна вершина як стартова (або задана).
    2. BFS, сортуємо сусідів за зростанням ступеня.
    3. Обертаємо перестановку (RCM) → мінімальна ширина смуги.
    """
    n = len(adj)
    log = ["=== АЛГОРИТМ КАТХІЛ-МАККІ (RCM) ===\n\n"]
    log.append("Алгоритм:\n"
               "  1. Знайти псевдопериферійну вершину (метод Гібса).\n"
               "  2. BFS від цієї вершини; сусідів на кожному кроці впорядкувати\n"
               "     за зростанням ступеня.\n"
               "  3. Отримати перестановку P.\n"
               "  4. Обернути P → P_rev (Reverse Cuthill-McKee).\n\n")

    if start is None:
        start, gibbs_log = gibbs_pseudo_peripheral(adj)
        log.append(f"Псевдопериферійна вершина (Гібс): {start+1}\n\n")
    else:
        log.append(f"Стартова вершина задана: {start+1}\n\n")

    visited = [False]*n
    order = []
    queue = [start]
    visited[start] = True

    while queue:
        u = queue.pop(0)
        order.append(u)
        neighbors = sorted([v for v in adj[u] if not visited[v]], key=lambda v: len(adj[v]))
        for v in neighbors:
            if not visited[v]:
                visited[v] = True
                queue.append(v)

    for i in range(n):
        if not visited[i]:
            visited[i] = True
            queue2 = [i]
            while queue2:
                u = queue2.pop(0)
                order.append(u)
                for v in sorted([x for x in adj[u] if not visited[x]], key=lambda x: len(adj[x])):
                    if not visited[v]:
                        visited[v] = True
                        queue2.append(v)

    rcm_order = list(reversed(order))
    log.append(f"Порядок CM:  {[x+1 for x in order]}\n")
    log.append(f"Порядок RCM: {[x+1 for x in rcm_order]}\n\n")
    return rcm_order, log

def bandwidth(A):
    """Ширина смуги матриці"""
    n = A.rows
    bw = 0
    for i in range(n):
        for j in range(n):
            if abs(A.data[i][j]) > 1e-14:
                bw = max(bw, abs(i-j))
    return bw

def permute_matrix(A, b_vec, perm):
    """Перестановка рядків і стовпців матриці A та вектора b"""
    n = A.rows
    perm_inv = [0]*n
    for i, p in enumerate(perm): perm_inv[p] = i
    Ap = Matrix(n, n)
    bp = [0.0]*n
    for i in range(n):
        bp[i] = b_vec[perm[i]]
        for j in range(n):
            Ap.data[i][j] = A.data[perm[i]][perm[j]]
    return Ap, bp

def matrix_to_ascii_band(A, max_size=20):
    """Відображення матриці з позначенням ненульових елементів"""
    n = min(A.rows, max_size)
    lines = []
    for i in range(n):
        row_str = ""
        for j in range(n):
            if abs(A.data[i][j]) > 1e-14:
                row_str += "█"
            else:
                row_str += "·"
        lines.append(f"  {i+1:2d} | {row_str}")
    return "\n".join(lines)

def solve_gauss_full(A, b_vals):
    """Розв'язання Гаусом з повною матрицею, повертає (x, лог)"""
    n = A.rows
    aug = [[A.data[i][j] for j in range(n)] + [b_vals[i]] for i in range(n)]
    for col in range(n):
        mr = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[mr][col]) < EPS:
            return None, "Матриця вироджена!\n"
        if mr != col:
            aug[col], aug[mr] = aug[mr], aug[col]
        p = aug[col][col]
        aug[col] = [v/p for v in aug[col]]
        for row in range(n):
            if row != col:
                f = aug[row][col]
                aug[row] = [aug[row][k] - f*aug[col][k] for k in range(n+1)]
    x = [aug[i][n] for i in range(n)]
    res = [b_vals[i] - sum(A.data[i][j]*x[j] for j in range(n)) for i in range(n)]
    r_max = max(abs(r) for r in res)
    log = "Метод Гауса (повна матриця):\n"
    for i, v in enumerate(x):
        log += f"  x[{i+1}] = {v:14.8f}\n"
    log += f"\n||r||∞ = {r_max:.2e}\n"
    return x, log

def solve_gauss_banded_from_full(A, b_vals):
    """Визначає ширину смуги і розв'язує стрічковим методом"""
    n = A.rows
    p = bandwidth(A)
    band_data = []
    for i in range(n):
        row = []
        for j in range(max(0, i-p), min(n, i+p+1)):
            if abs(A.data[i][j]) > 1e-14:
                row.append((j, A.data[i][j]))
        band_data.append(row)
    BM = BandedMatrix(n, p, band_data)
    x, log_b = banded_gauss(BM, b_vals)
    return x, p, log_b

current_sparse = [None]   

def sparse_run_all(A_mat, b_vals, example_name):
    """Повний прогін: граф → Гібс → RCM → розв'язок"""
    n = A_mat.rows

    adj = build_graph(A_mat)
    degrees = [len(adj[i]) for i in range(n)]
    bw_orig = bandwidth(A_mat)

    log_graph = [f"=== {example_name} ===\n\n"]
    log_graph.append(f"Розмір матриці: {n}×{n}\n")
    log_graph.append(f"Ширина смуги початкової матриці: {bw_orig}\n\n")
    log_graph.append("Граф СЛАР (суміжність):\n")
    for i in range(n):
        nbrs = sorted(adj[i])
        log_graph.append(f"  вершина {i+1:2d}: ступінь={degrees[i]}, сусіди = {[x+1 for x in nbrs]}\n")

    log_graph.append("\nПатерн ненульових елементів початкової матриці:\n")
    log_graph.append(matrix_to_ascii_band(A_mat) + "\n")

    log_graph.append("\nПеревірка шляхів між вершинами (BFS):\n")
    pairs = []
    if n >= 4:
        pairs = [(0, n-1), (0, n//2), (1, n-2)]
    else:
        pairs = [(i, j) for i in range(n) for j in range(i+1, n)]
    for (i, j) in pairs:
        d = bfs_path(adj, i, j)
        if d == -1:
            log_graph.append(f"  {i+1} → {j+1}: шляху немає (різні компоненти)\n")
        elif d == 0:
            log_graph.append(f"  {i+1} → {j+1}: та сама вершина\n")
        else:
            log_graph.append(f"  {i+1} → {j+1}: найкоротший шлях = {d} ребр(о/а)\n")

    set_res6("Граф / Шляхи", "".join(log_graph)); show_res6("Граф / Шляхи")

    pseudo_v, gibbs_log = gibbs_pseudo_peripheral(adj)
    set_res6("Гібс / Псевдопериф.", gibbs_log)

    rcm_perm, rcm_log_list = cuthill_mckee(adj, start=pseudo_v)
    A_rcm, b_rcm = permute_matrix(A_mat, b_vals, rcm_perm)
    bw_rcm = bandwidth(A_rcm)

    rcm_log = "".join(rcm_log_list)
    rcm_log += f"\nШирина смуги ДО  RCM: {bw_orig}\n"
    rcm_log += f"Ширина смуги ПІСЛЯ RCM: {bw_rcm}\n"
    rcm_log += f"Зменшення: {bw_orig - bw_rcm} ({100*(bw_orig-bw_rcm)/max(bw_orig,1):.0f}%)\n\n"
    rcm_log += "Патерн ПІСЛЯ RCM:\n"
    rcm_log += matrix_to_ascii_band(A_rcm) + "\n"
    set_res6("Катхіл-Маккі", rcm_log)

    x_full, log_full = solve_gauss_full(A_rcm, b_rcm)
    x_band, p_band, log_band = solve_gauss_banded_from_full(A_rcm, b_rcm)

    sol_log  = f"=== {example_name} — РОЗВ'ЯЗОК ===\n\n"
    sol_log += f"Матриця після RCM: {n}×{n}, ширина смуги p={p_band}\n\n"
    sol_log += "── Повна матриця (Гаус) ──\n"
    sol_log += log_full + "\n"
    sol_log += "── Стрічкова матриця (Гаус) ──\n"

    if x_band is not None:
        sol_log += f"Напів-ширина смуги p={p_band}\n"
        for i, v in enumerate(x_band):
            sol_log += f"  x[{i+1}] = {v:14.8f}\n"
        if x_full is not None:
            max_diff = max(abs(x_full[i]-x_band[i]) for i in range(n))
            sol_log += f"\nРозбіжність між двома методами: {max_diff:.2e}\n"
    else:
        sol_log += "Стрічковий метод: помилка розв'язання\n"

    set_res6("Розв'язок", sol_log)
    show_res6("Граф / Шляхи")
    ok(f"{example_name}: ширина смуги {bw_orig} → {bw_rcm}")


def _sp6_load_into_fields(A, b):
    fill(sp6_A_txt, A.to_text())
    fill(sp6_b_txt, '  '.join(str(v) for v in b))

def sp6_example1():
    """Приклад 1: 5×5 тридіагональна (1D дифузія)"""
    n = 5
    d = [[0.0]*n for _ in range(n)]
    for i in range(n):
        d[i][i] = 4.0
        if i > 0:     d[i][i-1] = -1.0
        if i < n-1:   d[i][i+1] = -1.0
    A = Matrix.from_list(d)
    b = [3.0, 2.0, 2.0, 2.0, 3.0]
    current_sparse[0] = (A, b, "Приклад 1: 5×5 тридіагональна")
    _sp6_load_into_fields(A, b)
    sparse_run_all(A, b, "Приклад 1: 5×5 тридіагональна (1D дифузія)")

def sp6_example2():
    """Приклад 2: 7×7 розріджена з «неправильним» патерном"""
    n = 7
    edges = [(0,3),(0,5),(1,4),(1,6),(2,5),(3,6),(4,6),(2,3)]
    d = [[0.0]*n for _ in range(n)]
    for i in range(n): d[i][i] = 10.0
    for (i,j) in edges:
        d[i][j] = -1.0; d[j][i] = -1.0
    A = Matrix.from_list(d)
    b = [round(random.uniform(1,9),2) for _ in range(n)]
    current_sparse[0] = (A, b, "Приклад 2: 7×7 нерегулярна розріджена")
    _sp6_load_into_fields(A, b)
    sparse_run_all(A, b, "Приклад 2: 7×7 нерегулярна розріджена")

def sp6_example3():
    """Приклад 3: 9×9 сіткова матриця (2D сітка 3×3)"""
    n = 9   
    def idx(r,c): return r*3+c
    d = [[0.0]*n for _ in range(n)]
    for r in range(3):
        for c in range(3):
            i = idx(r,c)
            d[i][i] = 4.0
            for (dr,dc) in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr,nc = r+dr, c+dc
                if 0<=nr<3 and 0<=nc<3:
                    j = idx(nr,nc)
                    d[i][j] = -1.0
    A = Matrix.from_list(d)
    b = [round(random.uniform(1,9),2) for _ in range(n)]
    current_sparse[0] = (A, b, "Приклад 3: 9×9 сіткова (2D 3×3)")
    _sp6_load_into_fields(A, b)
    sparse_run_all(A, b, "Приклад 3: 9×9 сіткова (2D 3×3)")

def sp6_run_current():
    if not current_sparse[0]:
        err("Спочатку оберіть один з прикладів!"); return
    A, b, name = current_sparse[0]
    sparse_run_all(A, b, name)

def sp6_query_path():
    """Перевірка довільного шляху між вершинами i та j"""
    if not current_sparse[0]:
        err("Спочатку оберіть приклад!"); return
    A, b, name = current_sparse[0]
    try:
        i = int(sp6_src.get()) - 1
        j = int(sp6_dst.get()) - 1
        n = A.rows
        if not (0 <= i < n and 0 <= j < n):
            err(f"Вершини мають бути в діапазоні 1..{n}"); return
        adj = build_graph(A)
        d = bfs_path(adj, i, j)
        if d == -1:
            msg = f"Між вершинами {i+1} і {j+1} шляху НЕМАЄ (різні компоненти зв'язності)."
        else:
            msg = f"Найкоротший шлях між вершинами {i+1} і {j+1}: {d} ребр(о/а)."
        dists = bfs_distances(adj, i)
        full = f"{msg}\n\nВідстані від вершини {i+1}:\n"
        for k, dd in enumerate(dists):
            full += f"  до {k+1:2d}: {'∞' if dd==-1 else dd}\n"
        set_res6("Граф / Шляхи", full)
        show_res6("Граф / Шляхи")
        ok(msg)
    except Exception as e:
        err(e)

lbl(lbody6, "Приклади розріджених матриць:").pack(anchor="w", pady=(0,4))

ex_row = tk.Frame(lbody6, bg=CARD); ex_row.pack(fill="x", pady=(0,4))
btn(ex_row, "Приклад 1 — 5×5", sp6_example1, BRD, TXT).pack(side="left", padx=(0,4))
btn(ex_row, "Приклад 2 — 7×7", sp6_example2, BRD, TXT).pack(side="left", padx=(0,4))
btn(ex_row, "Приклад 3 — 9×9", sp6_example3, BRD, TXT).pack(side="left")

tk.Frame(lbody6, bg=BRD, height=1).pack(fill="x", pady=8)

lbl(lbody6, "Перевірка шляху між вершинами (поточний приклад):").pack(anchor="w", pady=(0,4))
path_row = tk.Frame(lbody6, bg=CARD); path_row.pack(fill="x", pady=(0,2))
lbl(path_row, "Від вершини i =").pack(side="left")
sp6_src = tk.Entry(path_row, width=4, bg="#11111b", fg=TXT, relief="flat", insertbackground=TXT)
sp6_src.insert(0, "1"); sp6_src.pack(side="left", padx=(4,12))
lbl(path_row, "до j =").pack(side="left")
sp6_dst = tk.Entry(path_row, width=4, bg="#11111b", fg=TXT, relief="flat", insertbackground=TXT)
sp6_dst.insert(0, "5"); sp6_dst.pack(side="left", padx=(4,12))
btn(path_row, "Знайти шлях", sp6_query_path, BRD, TXT).pack(side="left")

tk.Frame(lbody6, bg=BRD, height=1).pack(fill="x", pady=8)

manual_hdr = tk.Frame(lbody6, bg=CARD); manual_hdr.pack(fill="x", pady=(0,4))
lbl(manual_hdr, "Власна матриця A:").pack(side="left")
sp6_n = tk.IntVar(value=4)
sp6_lo = tk.StringVar(value="-9"); sp6_hi = tk.StringVar(value="9")
lbl(manual_hdr, "  n =").pack(side="left")
tk.Spinbox(manual_hdr, from_=2, to=20, textvariable=sp6_n, width=3,
           bg="#11111b", fg=TXT, relief="flat",
           buttonbackground=BRD, insertbackground=TXT).pack(side="left", padx=(2,10))
for _t, _v in [("Від:", sp6_lo), ("До:", sp6_hi)]:
    lbl(manual_hdr, _t).pack(side="left")
    tk.Entry(manual_hdr, textvariable=_v, width=4,
             bg="#11111b", fg=TXT, relief="flat",
             insertbackground=TXT).pack(side="left", padx=(2,8))

sp6_A_txt = scrolledtext.ScrolledText(lbody6, height=6, font=("Courier New",10),
                                       bg="#11111b", fg=TXT, insertbackground=TXT,
                                       relief="flat", bd=0)
sp6_A_txt.pack(fill="both", expand=True, pady=(0,2))

lbl(lbody6, "Вектор b (через пробіл):").pack(anchor="w", pady=(2,2))
sp6_b_txt = scrolledtext.ScrolledText(lbody6, height=2, font=("Courier New",10),
                                       bg="#11111b", fg=TXT, insertbackground=TXT,
                                       relief="flat", bd=0)
sp6_b_txt.pack(fill="x", pady=(0,4))

def sp6_gen_random():
    n = sp6_n.get(); lo = float(sp6_lo.get()); hi = float(sp6_hi.get())
    rows = []
    for i in range(n):
        row = []
        off = 0.0
        for j in range(n):
            if i == j:
                row.append(0.0)
            else:
                v = round(random.uniform(lo, hi), 2) if random.random() < 0.4 else 0.0
                row.append(v); off += abs(v)
        row[i] = round(random.uniform(off + 1.0, off + abs(hi) + 3.0), 2)
        rows.append(row)
    A = Matrix.from_list(rows)
    bv = [round(random.uniform(lo, hi), 2) for _ in range(n)]
    fill(sp6_A_txt, A.to_text())
    fill(sp6_b_txt, "  ".join(str(v) for v in bv))
    ok(f"Згенеровано розріджену {n}×{n}")

def sp6_load_file():
    path = filedialog.askopenfilename(filetypes=[("Текст","*.txt"),("Всі","*.*")])
    if not path: return
    try:
        with open(path, encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        A = Matrix.from_list([list(map(float, l.split())) for l in lines[:-1]])
        bv = list(map(float, lines[-1].split()))
        fill(sp6_A_txt, A.to_text())
        fill(sp6_b_txt, "  ".join(str(v) for v in bv))
        ok(f"Завантажено {A.rows}×{A.cols} з файлу")
    except Exception as e:
        err(e)

def sp6_save_file():
    raw_a = sp6_A_txt.get("1.0","end").strip()
    raw_b = sp6_b_txt.get("1.0","end").strip()
    if not raw_a or not raw_b:
        err("Матриця або вектор b порожні!"); return
    path = filedialog.asksaveasfilename(defaultextension=".txt",
           filetypes=[("Текст","*.txt"),("Всі","*.*")])
    if not path: return
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(raw_a + "\n" + raw_b + "\n")
        ok("Збережено у файл")
    except Exception as e:
        err(e)

def sp6_apply_manual():
    raw_a = sp6_A_txt.get("1.0","end").strip()
    raw_b = sp6_b_txt.get("1.0","end").strip()
    if not raw_a or not raw_b:
        err("Введіть матрицю A і вектор b!"); return
    try:
        data = [list(map(float, l.split())) for l in raw_a.splitlines() if l.strip()]
        A = Matrix.from_list(data)
        if A.rows != A.cols:
            err(f"Матриця має бути квадратною! ({A.rows}×{A.cols})"); return
        bv = list(map(float, raw_b.split()))
        if len(bv) != A.rows:
            err(f"Вектор b: очікується {A.rows} елементів, отримано {len(bv)}"); return
        current_sparse[0] = (A, bv, "Власна матриця")
        sparse_run_all(A, bv, "Власна матриця")
    except Exception as e:
        err(f"Помилка розбору: {e}")

file_row = tk.Frame(lbody6, bg=CARD); file_row.pack(fill="x", pady=(2,2))
btn(file_row, "Генерувати",   sp6_gen_random, BRD, TXT).pack(side="left", padx=(0,4))
btn(file_row, "З файлу",      sp6_load_file,  BRD,  TXT  ).pack(side="left", padx=(0,4))
btn(file_row, "У файл",       sp6_save_file,  BRD,  TXT  ).pack(side="left", padx=(0,4))
btn(file_row, "▶ Застосувати", sp6_apply_manual, BRD, TXT).pack(side="left", padx=(0,4))

show_page(0)
root.mainloop()