import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from matrix import Matrix
from vector import Vector
from slae import SLAE


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторна 1 — Матриці та СЛАР")
        self.root.geometry("1050x750")
        self.root.minsize(850, 600)

        self.matrix_a = None
        self.matrix_b = None
        self.vector_b = None

        self._build_gui()

    def _build_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        tab_matrix = ttk.Frame(notebook)
        notebook.add(tab_matrix, text="  Робота з матрицями  ")
        self._build_matrix_tab(tab_matrix)

        tab_vector = ttk.Frame(notebook)
        notebook.add(tab_vector, text="  Робота з векторами  ")
        self._build_vector_tab(tab_vector)

        tab_slae = ttk.Frame(notebook)
        notebook.add(tab_slae, text="  Розв'язок СЛАР методом Гауса  ")
        self._build_slae_tab(tab_slae)

    # вкладка матриць 
    def _build_matrix_tab(self, parent):
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        left_panel = ttk.Frame(paned)
        paned.add(left_panel, weight=1)

        right_panel = ttk.Frame(paned)
        paned.add(right_panel, weight=1)

        frame_a = ttk.LabelFrame(left_panel, text="Введення матриці A")
        frame_a.pack(fill=tk.BOTH, expand=True, padx=4, pady=(4, 2))

        self.text_matrix_a = tk.Text(frame_a, height=7, width=35, font=("Courier New", 10))
        self.text_matrix_a.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        ctrl_a = ttk.Frame(frame_a)
        ctrl_a.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(ctrl_a, text="n:").pack(side=tk.LEFT)
        self.entry_rows_a = ttk.Entry(ctrl_a, width=3)
        self.entry_rows_a.insert(0, "3")
        self.entry_rows_a.pack(side=tk.LEFT, padx=2)
        ttk.Label(ctrl_a, text="m:").pack(side=tk.LEFT)
        self.entry_cols_a = ttk.Entry(ctrl_a, width=3)
        self.entry_cols_a.insert(0, "3")
        self.entry_cols_a.pack(side=tk.LEFT, padx=2)
        ttk.Label(ctrl_a, text="від:").pack(side=tk.LEFT, padx=(6, 0))
        self.entry_low_a = ttk.Entry(ctrl_a, width=4)
        self.entry_low_a.insert(0, "-10")
        self.entry_low_a.pack(side=tk.LEFT, padx=2)
        ttk.Label(ctrl_a, text="до:").pack(side=tk.LEFT)
        self.entry_high_a = ttk.Entry(ctrl_a, width=4)
        self.entry_high_a.insert(0, "10")
        self.entry_high_a.pack(side=tk.LEFT, padx=2)
        self.int_var_a = tk.BooleanVar(value=False)
        ttk.Checkbutton(ctrl_a, text="цілі", variable=self.int_var_a).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_a, text="Згенерувати",
                   command=lambda: self._generate_random_matrix('A')).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl_a, text="Відкрити",
                   command=lambda: self._load_matrix('A')).pack(side=tk.RIGHT, padx=2)
        ttk.Button(ctrl_a, text="Записати",
                   command=lambda: self._save_matrix('A')).pack(side=tk.RIGHT, padx=2)

        frame_b = ttk.LabelFrame(left_panel, text="Введення матриці B")
        frame_b.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

        self.text_matrix_b = tk.Text(frame_b, height=7, width=35, font=("Courier New", 10))
        self.text_matrix_b.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        ctrl_b = ttk.Frame(frame_b)
        ctrl_b.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(ctrl_b, text="n:").pack(side=tk.LEFT)
        self.entry_rows_b = ttk.Entry(ctrl_b, width=3)
        self.entry_rows_b.insert(0, "3")
        self.entry_rows_b.pack(side=tk.LEFT, padx=2)
        ttk.Label(ctrl_b, text="m:").pack(side=tk.LEFT)
        self.entry_cols_b = ttk.Entry(ctrl_b, width=3)
        self.entry_cols_b.insert(0, "3")
        self.entry_cols_b.pack(side=tk.LEFT, padx=2)
        ttk.Label(ctrl_b, text="від:").pack(side=tk.LEFT, padx=(6, 0))
        self.entry_low_b = ttk.Entry(ctrl_b, width=4)
        self.entry_low_b.insert(0, "-10")
        self.entry_low_b.pack(side=tk.LEFT, padx=2)
        ttk.Label(ctrl_b, text="до:").pack(side=tk.LEFT)
        self.entry_high_b = ttk.Entry(ctrl_b, width=4)
        self.entry_high_b.insert(0, "10")
        self.entry_high_b.pack(side=tk.LEFT, padx=2)
        self.int_var_b = tk.BooleanVar(value=False)
        ttk.Checkbutton(ctrl_b, text="цілі", variable=self.int_var_b).pack(side=tk.LEFT, padx=2)
        ttk.Button(ctrl_b, text="Згенерувати",
                   command=lambda: self._generate_random_matrix('B')).pack(side=tk.LEFT, padx=4)
        ttk.Button(ctrl_b, text="Відкрити",
                   command=lambda: self._load_matrix('B')).pack(side=tk.RIGHT, padx=2)
        ttk.Button(ctrl_b, text="Записати",
                   command=lambda: self._save_matrix('B')).pack(side=tk.RIGHT, padx=2)

        # результат

        ops_frame = ttk.LabelFrame(right_panel, text="Обчислення")
        ops_frame.pack(fill=tk.X, padx=4, pady=(4, 2))

        ttk.Button(ops_frame, text="A + B", width=14,
                   command=self._add_matrices).grid(row=0, column=0, padx=4, pady=3)
        ttk.Button(ops_frame, text="A − B", width=14,
                   command=self._sub_matrices).grid(row=0, column=1, padx=4, pady=3)
        ttk.Button(ops_frame, text="A × B", width=14,
                   command=self._mul_matrices).grid(row=0, column=2, padx=4, pady=3)

        ttk.Button(ops_frame, text="Норма (макс)", width=14,
                   command=lambda: self._compute_norm("max")).grid(row=1, column=0, padx=4, pady=3)
        ttk.Button(ops_frame, text="Норма (Фроб.)", width=14,
                   command=lambda: self._compute_norm("frob")).grid(row=1, column=1, padx=4, pady=3)

        scalar_frame = ttk.Frame(ops_frame)
        scalar_frame.grid(row=1, column=2, padx=4, pady=3)
        ttk.Label(scalar_frame, text="k=").pack(side=tk.LEFT)
        self.entry_scalar = ttk.Entry(scalar_frame, width=4)
        self.entry_scalar.insert(0, "2")
        self.entry_scalar.pack(side=tk.LEFT, padx=1)
        ttk.Button(scalar_frame, text="A·k",
                   command=self._mul_scalar).pack(side=tk.LEFT, padx=2)

        result_frame = ttk.LabelFrame(right_panel, text="Результат обчислень")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(2, 4))

        self.text_result = tk.Text(result_frame, height=12, font=("Courier New", 10))
        self.text_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(result_frame, text="Експортувати результат у файл",
                   command=self._save_result).pack(pady=(0, 5))

    #вкладка векторів
    def _build_vector_tab(self, parent):
        # Вектор V1
        frame_v1 = ttk.LabelFrame(parent, text="Вектор V1 — введіть числа через пробіл")
        frame_v1.pack(fill=tk.X, padx=8, pady=(8, 3))

        top_v1 = ttk.Frame(frame_v1)
        top_v1.pack(fill=tk.X, padx=5, pady=4)

        self.entry_v1 = ttk.Entry(top_v1, width=50, font=("Courier New", 10))
        self.entry_v1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        ttk.Label(top_v1, text="n:").pack(side=tk.LEFT)
        self.entry_v1_size = ttk.Entry(top_v1, width=3)
        self.entry_v1_size.insert(0, "4")
        self.entry_v1_size.pack(side=tk.LEFT, padx=2)
        ttk.Label(top_v1, text="від:").pack(side=tk.LEFT, padx=(4, 0))
        self.entry_low_v1 = ttk.Entry(top_v1, width=4)
        self.entry_low_v1.insert(0, "-10")
        self.entry_low_v1.pack(side=tk.LEFT, padx=2)
        ttk.Label(top_v1, text="до:").pack(side=tk.LEFT)
        self.entry_high_v1 = ttk.Entry(top_v1, width=4)
        self.entry_high_v1.insert(0, "10")
        self.entry_high_v1.pack(side=tk.LEFT, padx=2)
        self.int_var_v1 = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_v1, text="цілі", variable=self.int_var_v1).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_v1, text="Згенерувати",
                   command=lambda: self._generate_random_vector(1)).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_v1, text="Відкрити",
                   command=lambda: self._load_vector(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_v1, text="Записати",
                   command=lambda: self._save_vector(1)).pack(side=tk.LEFT, padx=2)

        frame_v2 = ttk.LabelFrame(parent, text="Вектор V2 — введіть числа через пробіл")
        frame_v2.pack(fill=tk.X, padx=8, pady=3)

        top_v2 = ttk.Frame(frame_v2)
        top_v2.pack(fill=tk.X, padx=5, pady=4)

        self.entry_v2 = ttk.Entry(top_v2, width=50, font=("Courier New", 10))
        self.entry_v2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        ttk.Label(top_v2, text="n:").pack(side=tk.LEFT)
        self.entry_v2_size = ttk.Entry(top_v2, width=3)
        self.entry_v2_size.insert(0, "4")
        self.entry_v2_size.pack(side=tk.LEFT, padx=2)
        ttk.Label(top_v2, text="від:").pack(side=tk.LEFT, padx=(4, 0))
        self.entry_low_v2 = ttk.Entry(top_v2, width=4)
        self.entry_low_v2.insert(0, "-10")
        self.entry_low_v2.pack(side=tk.LEFT, padx=2)
        ttk.Label(top_v2, text="до:").pack(side=tk.LEFT)
        self.entry_high_v2 = ttk.Entry(top_v2, width=4)
        self.entry_high_v2.insert(0, "10")
        self.entry_high_v2.pack(side=tk.LEFT, padx=2)
        self.int_var_v2 = tk.BooleanVar(value=False)
        ttk.Checkbutton(top_v2, text="цілі", variable=self.int_var_v2).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_v2, text="Згенерувати",
                   command=lambda: self._generate_random_vector(2)).pack(side=tk.LEFT, padx=3)
        ttk.Button(top_v2, text="Відкрити",
                   command=lambda: self._load_vector(2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_v2, text="Записати",
                   command=lambda: self._save_vector(2)).pack(side=tk.LEFT, padx=2)

        ops_frame = ttk.LabelFrame(parent, text="Виконати операцію")
        ops_frame.pack(fill=tk.X, padx=8, pady=3)

        ops_inner = ttk.Frame(ops_frame)
        ops_inner.pack(padx=5, pady=5)

        ttk.Button(ops_inner, text="V1 + V2", width=10,
                   command=self._add_vectors).grid(row=0, column=0, padx=4, pady=2)
        ttk.Button(ops_inner, text="V1 − V2", width=10,
                   command=self._sub_vectors).grid(row=0, column=1, padx=4, pady=2)
        ttk.Button(ops_inner, text="‖V1‖", width=10,
                   command=self._vector_norm).grid(row=0, column=2, padx=4, pady=2)

        scalar_v = ttk.Frame(ops_inner)
        scalar_v.grid(row=0, column=3, padx=10)
        ttk.Label(scalar_v, text="k=").pack(side=tk.LEFT)
        self.entry_vec_scalar = ttk.Entry(scalar_v, width=4)
        self.entry_vec_scalar.insert(0, "2")
        self.entry_vec_scalar.pack(side=tk.LEFT, padx=1)
        ttk.Button(scalar_v, text="V1·k",
                   command=self._mul_vector_scalar).pack(side=tk.LEFT, padx=3)

        # Результат
        res_frame = ttk.LabelFrame(parent, text="Результат")
        res_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(3, 8))

        self.text_vec_result = tk.Text(res_frame, height=8, font=("Courier New", 10))
        self.text_vec_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # слар
    def _build_slae_tab(self, parent):
        top_paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        top_paned.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        frame_sa = ttk.LabelFrame(top_paned, text="Коефіцієнти системи (матриця A)")
        top_paned.add(frame_sa, weight=3)

        self.text_slae_a = tk.Text(frame_sa, height=12, width=35, font=("Courier New", 10))
        self.text_slae_a.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 2))

        sa_ctrl = ttk.Frame(frame_sa)
        sa_ctrl.pack(fill=tk.X, padx=5, pady=3)
        ttk.Label(sa_ctrl, text="Розмірність n:").pack(side=tk.LEFT)
        self.entry_slae_n = ttk.Entry(sa_ctrl, width=3)
        self.entry_slae_n.insert(0, "3")
        self.entry_slae_n.pack(side=tk.LEFT, padx=3)
        ttk.Label(sa_ctrl, text="від:").pack(side=tk.LEFT, padx=(4, 0))
        self.entry_low_slae = ttk.Entry(sa_ctrl, width=4)
        self.entry_low_slae.insert(0, "-10")
        self.entry_low_slae.pack(side=tk.LEFT, padx=2)
        ttk.Label(sa_ctrl, text="до:").pack(side=tk.LEFT)
        self.entry_high_slae = ttk.Entry(sa_ctrl, width=4)
        self.entry_high_slae.insert(0, "10")
        self.entry_high_slae.pack(side=tk.LEFT, padx=2)
        self.int_var_slae = tk.BooleanVar(value=False)
        ttk.Checkbutton(sa_ctrl, text="цілі", variable=self.int_var_slae).pack(side=tk.LEFT, padx=2)
        ttk.Button(sa_ctrl, text="Згенерувати",
                   command=self._generate_slae_a).pack(side=tk.LEFT, padx=4)
        ttk.Button(sa_ctrl, text="Відкрити з файлу",
                   command=self._load_slae_a).pack(side=tk.RIGHT, padx=2)

        right_slae = ttk.Frame(top_paned)
        top_paned.add(right_slae, weight=2)

        frame_sb = ttk.LabelFrame(right_slae, text="Права частина (вектор b)")
        frame_sb.pack(fill=tk.X, padx=4, pady=(0, 3))

        ttk.Label(frame_sb, text="Числа через пробіл:").pack(anchor=tk.W, padx=5, pady=(4, 0))
        self.entry_slae_b = ttk.Entry(frame_sb, width=32, font=("Courier New", 10))
        self.entry_slae_b.pack(fill=tk.X, padx=5, pady=3)

        sb_ctrl = ttk.Frame(frame_sb)
        sb_ctrl.pack(fill=tk.X, padx=5, pady=(0, 5))
        ttk.Button(sb_ctrl, text="Згенерувати b",
                   command=self._generate_slae_b).pack(side=tk.LEFT, padx=2)
        ttk.Button(sb_ctrl, text="Відкрити з файлу",
                   command=self._load_slae_b).pack(side=tk.LEFT, padx=2)

        ttk.Separator(right_slae, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(right_slae, text="Розв'язати методом Гауса",
               command=self._solve_slae).pack(padx=10, pady=(5, 3), fill=tk.X)
        ttk.Button(right_slae, text="Знайти обернену матрицю A (метод Гауса)",
               command=self._inverse_slae_matrix).pack(padx=10, pady=(0, 5), fill=tk.X)

        demo_frame = ttk.LabelFrame(right_slae, text="Демо приклади")
        demo_frame.pack(fill=tk.X, padx=4, pady=(0, 4))
        ttk.Button(demo_frame, text="Тест 1: єдиний розв'язок",
               command=self._load_demo_unique_slae).pack(side=tk.LEFT, padx=4, pady=4)
        ttk.Button(demo_frame, text="Тест 2: погано обумовлена матриця",
               command=self._load_demo_ill_slae).pack(side=tk.LEFT, padx=4, pady=4)

        res_frame = ttk.LabelFrame(right_slae, text="Розв'язок системи")
        res_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(3, 4))

        self.text_slae_result = tk.Text(res_frame, height=10, font=("Courier New", 10))
        self.text_slae_result.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _parse_matrix_from_text(self, text_widget):
        content = text_widget.get("1.0", tk.END).strip()
        if not content:
            return None
        data = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                row = [float(x) for x in line.split()]
                data.append(row)
        return Matrix(data=data)

    def _display_matrix_in_text(self, text_widget, matrix):
        text_widget.delete("1.0", tk.END)
        for row in matrix.data:
            line = ' '.join(f"{x}" for x in row)
            text_widget.insert(tk.END, line + '\n')

    def _parse_vector_from_entry(self, entry_widget):
        content = entry_widget.get().strip()
        if not content:
            return None
        data = [float(x) for x in content.split()]
        return Vector(data=data)

    def _display_vector_in_entry(self, entry_widget, vector):
        entry_widget.delete(0, tk.END)
        values = ' '.join(f"{vector.get(i)}" for i in range(vector.size))
        entry_widget.insert(0, values)

    def _load_matrix(self, which):
        filename = filedialog.askopenfilename(
            title=f"Завантажити матрицю {which}",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filename:
            return
        try:
            m = Matrix.from_file(filename)
            if which == 'A':
                self.matrix_a = m
                self._display_matrix_in_text(self.text_matrix_a, m)
            else:
                self.matrix_b = m
                self._display_matrix_in_text(self.text_matrix_b, m)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати файл:\n{e}")

    def _save_matrix(self, which):
        try:
            if which == 'A':
                m = self._parse_matrix_from_text(self.text_matrix_a)
            else:
                m = self._parse_matrix_from_text(self.text_matrix_b)
            if m is None:
                messagebox.showwarning("Увага", "Матриця порожня.")
                return
        except Exception as e:
            messagebox.showerror("Помилка", f"Невірний формат матриці:\n{e}")
            return

        filename = filedialog.asksaveasfilename(
            title=f"Зберегти матрицю {which}",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if filename:
            try:
                m.to_file(filename)
                messagebox.showinfo("Успіх", f"Матриця збережена у {filename}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти:\n{e}")

    def _save_result(self):
        content = self.text_result.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Увага", "Немає результату для збереження.")
            return
        filename = filedialog.asksaveasfilename(
            title="Зберегти результат",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Успіх", f"Результат збережено у {filename}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти:\n{e}")

    def _generate_random_matrix(self, which):
        try:
            if which == 'A':
                rows = int(self.entry_rows_a.get())
                cols = int(self.entry_cols_a.get())
                low = float(self.entry_low_a.get())
                high = float(self.entry_high_a.get())
                use_int = self.int_var_a.get()
                m = Matrix.random_matrix(rows, cols, low, high, use_int)
                self.matrix_a = m
                self._display_matrix_in_text(self.text_matrix_a, m)
            else:
                rows = int(self.entry_rows_b.get())
                cols = int(self.entry_cols_b.get())
                low = float(self.entry_low_b.get())
                high = float(self.entry_high_b.get())
                use_int = self.int_var_b.get()
                m = Matrix.random_matrix(rows, cols, low, high, use_int)
                self.matrix_b = m
                self._display_matrix_in_text(self.text_matrix_b, m)
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректні числа для розміру та діапазону.")

    def _get_both_matrices(self):
        try:
            a = self._parse_matrix_from_text(self.text_matrix_a)
            b = self._parse_matrix_from_text(self.text_matrix_b)
            if a is None or b is None:
                messagebox.showwarning("Увага", "Обидві матриці повинні бути заповнені.")
                return None, None
            return a, b
        except Exception as e:
            messagebox.showerror("Помилка", f"Невірний формат:\n{e}")
            return None, None

    def _show_result(self, text):
        self.text_result.delete("1.0", tk.END)
        self.text_result.insert("1.0", text)

    def _add_matrices(self):
        a, b = self._get_both_matrices()
        if a is None:
            return
        try:
            result = a + b
            self._show_result(f"A + B =\n{result}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def _sub_matrices(self):
        a, b = self._get_both_matrices()
        if a is None:
            return
        try:
            result = a - b
            self._show_result(f"A - B =\n{result}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def _mul_matrices(self):
        a, b = self._get_both_matrices()
        if a is None:
            return
        try:
            result = a * b
            self._show_result(f"A × B =\n{result}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def _mul_scalar(self):
        try:
            a = self._parse_matrix_from_text(self.text_matrix_a)
            if a is None:
                messagebox.showwarning("Увага", "Матриця A порожня.")
                return
            k = float(self.entry_scalar.get())
            result = a * k
            self._show_result(f"A × {k} =\n{result}")
        except ValueError as e:
            messagebox.showerror("Помилка", f"Помилка:\n{e}")

    def _compute_norm(self, kind):
        try:
            a = self._parse_matrix_from_text(self.text_matrix_a)
            if a is None:
                messagebox.showwarning("Увага", "Матриця A порожня.")
                return
            if kind == "max":
                val = a.norm_max()
                self._show_result(f"Максимальна норма матриці A = {val:.6f}")
            else:
                val = a.norm_frobenius()
                self._show_result(f"Фробеніусова норма матриці A = {val:.6f}")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _generate_random_vector(self, num):
        try:
            if num == 1:
                size = int(self.entry_v1_size.get())
                low = float(self.entry_low_v1.get())
                high = float(self.entry_high_v1.get())
                use_int = self.int_var_v1.get()
                v = Vector.random_vector(size, low, high, use_int)
                self._display_vector_in_entry(self.entry_v1, v)
            else:
                size = int(self.entry_v2_size.get())
                low = float(self.entry_low_v2.get())
                high = float(self.entry_high_v2.get())
                use_int = self.int_var_v2.get()
                v = Vector.random_vector(size, low, high, use_int)
                self._display_vector_in_entry(self.entry_v2, v)
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректний розмір та діапазон.")

    def _load_vector(self, num):
        filename = filedialog.askopenfilename(
            title=f"Завантажити вектор V{num}",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filename:
            return
        try:
            v = Vector.from_file(filename)
            if num == 1:
                self._display_vector_in_entry(self.entry_v1, v)
            else:
                self._display_vector_in_entry(self.entry_v2, v)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати:\n{e}")

    def _save_vector(self, num):
        try:
            if num == 1:
                v = self._parse_vector_from_entry(self.entry_v1)
            else:
                v = self._parse_vector_from_entry(self.entry_v2)
            if v is None:
                messagebox.showwarning("Увага", "Вектор порожній.")
                return
        except Exception as e:
            messagebox.showerror("Помилка", f"Невірний формат:\n{e}")
            return

        filename = filedialog.asksaveasfilename(
            title=f"Зберегти вектор V{num}",
            defaultextension=".txt",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if filename:
            try:
                v.to_file(filename)
                messagebox.showinfo("Успіх", f"Вектор збережено у {filename}")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося зберегти:\n{e}")

    def _show_vec_result(self, text):
        self.text_vec_result.delete("1.0", tk.END)
        self.text_vec_result.insert("1.0", text)

    def _add_vectors(self):
        try:
            v1 = self._parse_vector_from_entry(self.entry_v1)
            v2 = self._parse_vector_from_entry(self.entry_v2)
            if v1 is None or v2 is None:
                messagebox.showwarning("Увага", "Обидва вектори повинні бути заповнені.")
                return
            result = v1 + v2
            self._show_vec_result(f"V1 + V2 = {result}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def _sub_vectors(self):
        try:
            v1 = self._parse_vector_from_entry(self.entry_v1)
            v2 = self._parse_vector_from_entry(self.entry_v2)
            if v1 is None or v2 is None:
                messagebox.showwarning("Увага", "Обидва вектори повинні бути заповнені.")
                return
            result = v1 - v2
            self._show_vec_result(f"V1 - V2 = {result}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def _mul_vector_scalar(self):
        try:
            v1 = self._parse_vector_from_entry(self.entry_v1)
            if v1 is None:
                messagebox.showwarning("Увага", "Вектор V1 порожній.")
                return
            k = float(self.entry_vec_scalar.get())
            result = v1 * k
            self._show_vec_result(f"V1 × {k} = {result}")
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))

    def _vector_norm(self):
        try:
            v1 = self._parse_vector_from_entry(self.entry_v1)
            if v1 is None:
                messagebox.showwarning("Увага", "Вектор V1 порожній.")
                return
            val = v1.norm()
            self._show_vec_result(f"Евклідова норма V1 = {val:.6f}")
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _load_slae_a(self):
        filename = filedialog.askopenfilename(
            title="Завантажити матрицю A для СЛАР",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filename:
            return
        try:
            m = Matrix.from_file(filename)
            self._display_matrix_in_text(self.text_slae_a, m)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати:\n{e}")

    def _load_slae_b(self):
        filename = filedialog.askopenfilename(
            title="Завантажити вектор b для СЛАР",
            filetypes=[("Текстові файли", "*.txt"), ("Усі файли", "*.*")]
        )
        if not filename:
            return
        try:
            v = Vector.from_file(filename)
            self._display_vector_in_entry(self.entry_slae_b, v)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати:\n{e}")

    def _generate_slae_a(self):
        try:
            n = int(self.entry_slae_n.get())
            low = float(self.entry_low_slae.get())
            high = float(self.entry_high_slae.get())
            use_int = self.int_var_slae.get()
            m = Matrix.random_matrix(n, n, low, high, use_int)
            self._display_matrix_in_text(self.text_slae_a, m)
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне n та діапазон.")

    def _generate_slae_b(self):
        try:
            n = int(self.entry_slae_n.get())
            low = float(self.entry_low_slae.get())
            high = float(self.entry_high_slae.get())
            use_int = self.int_var_slae.get()
            v = Vector.random_vector(n, low, high, use_int)
            self._display_vector_in_entry(self.entry_slae_b, v)
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректне n та діапазон.")

    def _solve_slae(self):
        try:
            a = self._parse_matrix_from_text(self.text_slae_a)
            b = self._parse_vector_from_entry(self.entry_slae_b)
            if a is None or b is None:
                messagebox.showwarning("Увага", "Заповніть матрицю A та вектор b.")
                return

            system = SLAE(A=a, b=b)
            info = system.solve_gauss_general()

            result_text = "Розв'язок СЛАР методом Гауса з вибором ведучого елемента:\n\n"
            result_text += f"Статус системи: {info['message']}\n"
            result_text += f"rank(A) = {info['rank_a']}, rank([A|b]) = {info['rank_ab']}\n\n"

            if info["status"] == "unique_solution":
                x = info["x"]
                r = system.residual()
                for i in range(x.size):
                    result_text += f"  x[{i + 1}] = {x.get(i):.6f}\n"
                result_text += f"\nВектор нев'язки r = Ax - b:\n  {r}\n"
                result_text += f"Норма нев'язки: {r.norm():.2e}\n\n"

            result_text += system.decomposition_text() + "\n"

            self.text_slae_result.delete("1.0", tk.END)
            self.text_slae_result.insert("1.0", result_text)

        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _inverse_slae_matrix(self):
        try:
            a = self._parse_matrix_from_text(self.text_slae_a)
            if a is None:
                messagebox.showwarning("Увага", "Заповніть матрицю A.")
                return
            system = SLAE(A=a, b=Vector(size=a.rows))
            inv = system.inverse_matrix_gauss()

            text = "Обернена матриця A:\n\n"
            text += f"{inv}\n\n"
            text += "Коротко про метод:\n"
            text += "1) Формуємо [A|I].\n"
            text += "2) Елементарними перетвореннями рядків приводимо ліву частину до I.\n"
            text += "3) Права частина стає A^(-1)."

            self.text_slae_result.delete("1.0", tk.END)
            self.text_slae_result.insert("1.0", text)
        except Exception as e:
            messagebox.showerror("Помилка", str(e))

    def _load_demo_unique_slae(self):
        self._load_demo_slae_files("matrix_A.txt", "vector_b.txt")

    def _load_demo_ill_slae(self):
        self._load_demo_slae_files("matrix_ill.txt", "vector_ill.txt")

    def _load_demo_slae_files(self, matrix_name, vector_name):
        try:
            base = os.path.join(os.path.dirname(__file__), "examples")
            matrix_path = os.path.join(base, matrix_name)
            vector_path = os.path.join(base, vector_name)

            a = Matrix.from_file(matrix_path)
            b = Vector.from_file(vector_path)
            self._display_matrix_in_text(self.text_slae_a, a)
            self._display_vector_in_entry(self.entry_slae_b, b)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити демо-приклад:\n{e}")
