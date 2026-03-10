import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, messagebox
from mpl_toolkits.mplot3d import Axes3D

class CubicSurfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Інтерполяцій кубічна поверхня Q(u,v). Варіант №20")
        self.root.geometry("1550x950")
        
        self.points = [
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.333, 0.0, 1.0, 0.0, 0.0],
            [0.667, 0.0, 2.0, 0.0, 0.0],
            [1.0, 0.0, 3.0, 0.0, 0.0],
            
            [0.0, 0.333, 0.0, 1.0, 0.5],
            [0.333, 0.333, 1.0, 1.0, 1.0],
            [0.667, 0.333, 2.0, 1.0, 1.5],
            [1.0, 0.333, 3.0, 1.0, 2.0],
            
            [0.0, 0.667, 0.0, 2.0, 1.0],
            [0.333, 0.667, 1.0, 2.0, 1.5],
            [0.667, 0.667, 2.0, 2.0, 2.0],
            [1.0, 0.667, 3.0, 2.0, 2.5],
            
            [0.0, 1.0, 0.0, 3.0, 1.5],
            [0.333, 1.0, 1.0, 3.0, 2.0],
            [0.667, 1.0, 2.0, 3.0, 2.5],
            [1.0, 1.0, 3.0, 3.0, 3.0]
        ]
        
        self.examples = {
            "Площина (початкова)": [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.333, 0.0, 1.0, 0.0, 0.0],
                [0.667, 0.0, 2.0, 0.0, 0.0],
                [1.0, 0.0, 3.0, 0.0, 0.0],
                [0.0, 0.333, 0.0, 1.0, 0.0],
                [0.333, 0.333, 1.0, 1.0, 0.0],
                [0.667, 0.333, 2.0, 1.0, 0.0],
                [1.0, 0.333, 3.0, 1.0, 0.0],
                [0.0, 0.667, 0.0, 2.0, 0.0],
                [0.333, 0.667, 1.0, 2.0, 0.0],
                [0.667, 0.667, 2.0, 2.0, 0.0],
                [1.0, 0.667, 3.0, 2.0, 0.0],
                [0.0, 1.0, 0.0, 3.0, 0.0],
                [0.333, 1.0, 1.0, 3.0, 0.0],
                [0.667, 1.0, 2.0, 3.0, 0.0],
                [1.0, 1.0, 3.0, 3.0, 0.0]
            ],
            "Параболоїд": [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.333, 0.0, 1.0, 0.0, 0.11],
                [0.667, 0.0, 2.0, 0.0, 0.44],
                [1.0, 0.0, 3.0, 0.0, 1.0],
                [0.0, 0.333, 0.0, 1.0, 0.11],
                [0.333, 0.333, 1.0, 1.0, 0.22],
                [0.667, 0.333, 2.0, 1.0, 0.55],
                [1.0, 0.333, 3.0, 1.0, 1.11],
                [0.0, 0.667, 0.0, 2.0, 0.44],
                [0.333, 0.667, 1.0, 2.0, 0.55],
                [0.667, 0.667, 2.0, 2.0, 0.88],
                [1.0, 0.667, 3.0, 2.0, 1.44],
                [0.0, 1.0, 0.0, 3.0, 1.0],
                [0.333, 1.0, 1.0, 3.0, 1.11],
                [0.667, 1.0, 2.0, 3.0, 1.44],
                [1.0, 1.0, 3.0, 3.0, 2.0]
            ],
            "Хвиля": [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.333, 0.0, 1.0, 0.0, 1.0],
                [0.667, 0.0, 2.0, 0.0, 0.5],
                [1.0, 0.0, 3.0, 0.0, 0.0],
                [0.0, 0.333, 0.0, 1.0, 1.0],
                [0.333, 0.333, 1.0, 1.0, 0.5],
                [0.667, 0.333, 2.0, 1.0, 1.0],
                [1.0, 0.333, 3.0, 1.0, 1.5],
                [0.0, 0.667, 0.0, 2.0, 0.5],
                [0.333, 0.667, 1.0, 2.0, 1.0],
                [0.667, 0.667, 2.0, 2.0, 0.5],
                [1.0, 0.667, 3.0, 2.0, 1.0],
                [0.0, 1.0, 0.0, 3.0, 0.0],
                [0.333, 1.0, 1.0, 3.0, 1.0],
                [0.667, 1.0, 2.0, 3.0, 0.5],
                [1.0, 1.0, 3.0, 3.0, 0.0]
            ],
            "Сідлова поверхня": [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.333, 0.0, 1.0, 0.0, -0.5],
                [0.667, 0.0, 2.0, 0.0, -1.0],
                [1.0, 0.0, 3.0, 0.0, -1.5],
                [0.0, 0.333, 0.0, 1.0, 0.5],
                [0.333, 0.333, 1.0, 1.0, 0.0],
                [0.667, 0.333, 2.0, 1.0, -0.5],
                [1.0, 0.333, 3.0, 1.0, -1.0],
                [0.0, 0.667, 0.0, 2.0, 1.0],
                [0.333, 0.667, 1.0, 2.0, 0.5],
                [0.667, 0.667, 2.0, 2.0, 0.0],
                [1.0, 0.667, 3.0, 2.0, -0.5],
                [0.0, 1.0, 0.0, 3.0, 1.5],
                [0.333, 1.0, 1.0, 3.0, 1.0],
                [0.667, 1.0, 2.0, 3.0, 0.5],
                [1.0, 1.0, 3.0, 3.0, 0.0]
            ],
            "Пагорб": [
                [0.0, 0.0, 0.0, 0.0, 0.5],
                [0.333, 0.0, 1.0, 0.0, 1.0],
                [0.667, 0.0, 2.0, 0.0, 0.8],
                [1.0, 0.0, 3.0, 0.0, 0.5],
                [0.0, 0.333, 0.0, 1.0, 1.0],
                [0.333, 0.333, 1.0, 1.0, 2.5],
                [0.667, 0.333, 2.0, 1.0, 2.0],
                [1.0, 0.333, 3.0, 1.0, 1.0],
                [0.0, 0.667, 0.0, 2.0, 0.8],
                [0.333, 0.667, 1.0, 2.0, 2.0],
                [0.667, 0.667, 2.0, 2.0, 1.8],
                [1.0, 0.667, 3.0, 2.0, 0.8],
                [0.0, 1.0, 0.0, 3.0, 0.5],
                [0.333, 1.0, 1.0, 3.0, 1.0],
                [0.667, 1.0, 2.0, 3.0, 0.8],
                [1.0, 1.0, 3.0, 3.0, 0.5]
            ]
        }
        
        self.grid_size = 30
        self.selected_point = 0
        self.coeffs_x = None
        self.coeffs_y = None
        self.coeffs_z = None
        
        self.setup_gui()
        self.update_plot()
    
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        control_frame = ttk.LabelFrame(main_frame, text="Контрольні точки (16 точок для інтерполяції)", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        canvas_frame = tk.Canvas(control_frame, width=380)
        scrollbar = ttk.Scrollbar(control_frame, orient="vertical", command=canvas_frame.yview)
        scrollable_frame = ttk.Frame(canvas_frame)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_frame.configure(scrollregion=canvas_frame.bbox("all"))
        )
        
        canvas_frame.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_frame.configure(yscrollcommand=scrollbar.set)
        
        canvas_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ttk.Label(scrollable_frame, text="Виберіть точку:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=5
        )
        
        self.point_selector = ttk.Combobox(scrollable_frame, width=28, state='readonly')
        self.point_selector['values'] = [f"Точка {i+1} (u={p[0]:.2f}, v={p[1]:.2f})" for i, p in enumerate(self.points)]
        self.point_selector.current(0)
        self.point_selector.bind('<<ComboboxSelected>>', self.on_point_select)
        self.point_selector.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Label(scrollable_frame, text="Параметри (u, v):", font=('Arial', 9, 'bold'), foreground='darkblue').grid(
            row=3, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        
        self.u_entry = ttk.Entry(scrollable_frame, width=12)
        self.v_entry = ttk.Entry(scrollable_frame, width=12)
        
        ttk.Label(scrollable_frame, text="u:").grid(row=4, column=0, sticky=tk.W)
        self.u_entry.grid(row=4, column=1, padx=5, pady=2)
        
        ttk.Label(scrollable_frame, text="v:").grid(row=5, column=0, sticky=tk.W)
        self.v_entry.grid(row=5, column=1, padx=5, pady=2)
        
        ttk.Label(scrollable_frame, text="Координати (x, y, z):", font=('Arial', 9, 'bold'), foreground='darkgreen').grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        
        self.x_entry = ttk.Entry(scrollable_frame, width=12)
        self.y_entry = ttk.Entry(scrollable_frame, width=12)
        self.z_entry = ttk.Entry(scrollable_frame, width=12)
        
        ttk.Label(scrollable_frame, text="x:").grid(row=7, column=0, sticky=tk.W)
        self.x_entry.grid(row=7, column=1, padx=5, pady=2)
        
        ttk.Label(scrollable_frame, text="y:").grid(row=8, column=0, sticky=tk.W)
        self.y_entry.grid(row=8, column=1, padx=5, pady=2)
        
        ttk.Label(scrollable_frame, text="z:").grid(row=9, column=0, sticky=tk.W)
        self.z_entry.grid(row=9, column=1, padx=5, pady=2)
        
        self.update_entry_fields()
        
        btn_frame = ttk.Frame(scrollable_frame)
        btn_frame.grid(row=10, column=0, columnspan=3, pady=10)
        
        apply_btn = ttk.Button(btn_frame, text="Застосувати зміни", command=self.update_point, width=22)
        apply_btn.pack(pady=3)
        
        examples_frame = ttk.LabelFrame(scrollable_frame, text="Готові приклади", padding="10")
        examples_frame.grid(row=11, column=0, columnspan=3, pady=(15, 5), sticky=(tk.W, tk.E))
        
        ttk.Label(examples_frame, text="Виберіть приклад поверхні:", font=('Arial', 9)).pack(pady=5)
        
        self.example_selector = ttk.Combobox(examples_frame, width=25, state='readonly')
        self.example_selector['values'] = list(self.examples.keys())
        self.example_selector.current(0)
        self.example_selector.pack(pady=5)
        
        ttk.Button(examples_frame, text="Обрати приклад", command=self.load_example, width=28).pack(pady=5)
        
        info_frame = ttk.LabelFrame(scrollable_frame, text="", padding="10")
        info_frame.grid(row=12, column=0, columnspan=3, pady=(15, 5), sticky=(tk.W, tk.E))
        
        self.info_label = tk.Label(info_frame, text="", 
                                   font=('Arial', 9), justify=tk.LEFT, wraplength=350)
        self.info_label.pack(pady=5)
        
        ttk.Label(scrollable_frame, text="Розмір сітки:", font=('Arial', 10, 'bold')).grid(
            row=13, column=0, sticky=tk.W, pady=(20, 5)
        )
        self.grid_scale = tk.Scale(
            scrollable_frame, from_=10, to=50, orient=tk.HORIZONTAL,
            length=250
        )
        self.grid_scale.set(self.grid_size)
        self.grid_scale.grid(row=14, column=0, columnspan=3, pady=5)
        
        self.grid_scale.config(command=lambda v: self.on_grid_change(v))
        
        update_btn = ttk.Button(
            scrollable_frame, text="Оновити поверхню",
            command=self.update_plot
        )
        update_btn.grid(row=15, column=0, columnspan=3, pady=15)        
        
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.fig = Figure(figsize=(14, 11))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def update_entry_fields(self):
        point = self.points[self.selected_point]
        self.u_entry.delete(0, tk.END)
        self.u_entry.insert(0, f"{point[0]:.3f}")
        self.v_entry.delete(0, tk.END)
        self.v_entry.insert(0, f"{point[1]:.3f}")
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, f"{point[2]:.3f}")
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, f"{point[3]:.3f}")
        self.z_entry.delete(0, tk.END)
        self.z_entry.insert(0, f"{point[4]:.3f}")
    
    def on_point_select(self, event):
        self.selected_point = self.point_selector.current()
        self.update_entry_fields()
    
    def update_point(self):
        try:
            self.points[self.selected_point] = [
                float(self.u_entry.get()),
                float(self.v_entry.get()),
                float(self.x_entry.get()),
                float(self.y_entry.get()),
                float(self.z_entry.get())
            ]
            self.point_selector['values'] = [f"Точка {i+1} (u={p[0]:.2f}, v={p[1]:.2f})" for i, p in enumerate(self.points)]
            self.update_plot()
        except ValueError:
            messagebox.showerror("Помилка", "Введіть коректні числові значення!")
    
    def load_example(self):
        example_name = self.example_selector.get()
        if example_name in self.examples:
            self.points = [point[:] for point in self.examples[example_name]]
            self.point_selector['values'] = [f"Точка {i+1} (u={p[0]:.2f}, v={p[1]:.2f})" for i, p in enumerate(self.points)]
            self.selected_point = 0
            self.point_selector.current(0)
            self.update_entry_fields()
            self.update_plot()
            
    def on_grid_change(self, value):
        self.grid_size = int(float(value))
    
    def cubic_interpolation_coefficients(self, u_points, v_points, coord_points):
        n = len(u_points)
        
        A = np.zeros((n, 16))
        for k in range(n):
            u = u_points[k]
            v = v_points[k]
            idx = 0
            for i in range(4):
                for j in range(4):
                    A[k, idx] = (u ** i) * (v ** j)
                    idx += 1
        
        try:
            if n == 16:
                coeffs = np.linalg.solve(A, coord_points)
            else:
                coeffs = np.linalg.lstsq(A, coord_points, rcond=None)[0]
        except Exception as e:
            print(f"Помилка обчислення коефіцієнтів: {e}")
            coeffs = np.zeros(16)
        
        return coeffs
    
    def evaluate_cubic_surface(self, coeffs, u, v):
        result = 0.0
        idx = 0
        for i in range(4):
            for j in range(4):
                result += coeffs[idx] * (u ** i) * (v ** j)
                idx += 1
        return result
    
    def cubic_interpolation(self):
        points_array = np.array(self.points)
        
        u_points = points_array[:, 0]
        v_points = points_array[:, 1]
        x_points = points_array[:, 2]
        y_points = points_array[:, 3]
        z_points = points_array[:, 4]
        
        self.coeffs_x = self.cubic_interpolation_coefficients(u_points, v_points, x_points)
        self.coeffs_y = self.cubic_interpolation_coefficients(u_points, v_points, y_points)
        self.coeffs_z = self.cubic_interpolation_coefficients(u_points, v_points, z_points)
        
        u_grid = np.linspace(0, 1, self.grid_size)
        v_grid = np.linspace(0, 1, self.grid_size)
        U, V = np.meshgrid(u_grid, v_grid)
        
        X = np.zeros_like(U)
        Y = np.zeros_like(U)
        Z = np.zeros_like(U)
        
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                X[i, j] = self.evaluate_cubic_surface(self.coeffs_x, U[i, j], V[i, j])
                Y[i, j] = self.evaluate_cubic_surface(self.coeffs_y, U[i, j], V[i, j])
                Z[i, j] = self.evaluate_cubic_surface(self.coeffs_z, U[i, j], V[i, j])
        
        errors = []
        for point in self.points:
            u, v, x_real, y_real, z_real = point
            x_interp = self.evaluate_cubic_surface(self.coeffs_x, u, v)
            y_interp = self.evaluate_cubic_surface(self.coeffs_y, u, v)
            z_interp = self.evaluate_cubic_surface(self.coeffs_z, u, v)
            
            error = np.sqrt((x_real - x_interp)**2 + (y_real - y_interp)**2 + (z_real - z_interp)**2)
            errors.append(error)
        
        max_error = np.max(errors) if errors else 0
        
        #info_text = f"помилка: {max_error:.6f}\n"
        #self.info_label.config(text=info_text)
        return X, Y, Z
    
    def update_plot(self):
        X, Y, Z = self.cubic_interpolation()
        
        self.fig.clear()
        
        points_array = np.array(self.points)
        
        ax1 = self.fig.add_subplot(2, 2, 1, projection='3d')
        surf = ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.7, 
                                edgecolor='none', antialiased=True)
        ax1.plot_wireframe(X, Y, Z, color='black', alpha=0.2, linewidth=0.5)
        
        ax1.scatter(points_array[:, 2], points_array[:, 3], points_array[:, 4],
                   color='red', s=80, marker='o', label='Контрольні точки', 
                   edgecolors='darkred', linewidth=1.5)
        
        for i, p in enumerate(points_array):
            ax1.text(p[2], p[3], p[4], f'  {i+1}', fontsize=8, 
                    color='darkred', fontweight='bold')
        
        ax1.set_xlabel('X', fontsize=10, fontweight='bold')
        ax1.set_ylabel('Y', fontsize=10, fontweight='bold')
        ax1.set_zlabel('Z', fontsize=10, fontweight='bold')
        ax1.set_title('3D інтерполююча кубічна поверхня Q(u,v)', fontsize=12, fontweight='bold')
        ax1.legend(loc='upper left')
        self.fig.colorbar(surf, ax=ax1, shrink=0.5, aspect=5)
        ax2 = self.fig.add_subplot(2, 2, 2)
        
        for i in range(0, self.grid_size, max(1, self.grid_size//8)):
            ax2.plot(X[:, i], Y[:, i], 'b-', alpha=0.6, linewidth=1.2, label='u=const' if i == 0 else '')
        for j in range(0, self.grid_size, max(1, self.grid_size//8)):
            ax2.plot(X[j, :], Y[j, :], 'r-', alpha=0.6, linewidth=1.2, label='v=const' if j == 0 else '')
        
        ax2.scatter(points_array[:, 2], points_array[:, 3], color='red', s=60, 
                   zorder=5, edgecolors='darkred', linewidth=1.5)
        
        for i, p in enumerate(points_array):
            ax2.annotate(f'{i+1}', (p[2], p[3]), fontsize=8, 
                        xytext=(3, 3), textcoords='offset points',
                        fontweight='bold', color='darkred')
        
        ax2.set_xlabel('X', fontsize=10, fontweight='bold')
        ax2.set_ylabel('Y', fontsize=10, fontweight='bold')
        ax2.set_title('Проекція на площину z=0\n(синій: u=const, червоний: v=const)', 
                     fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_aspect('equal', adjustable='box')
        
        ax3 = self.fig.add_subplot(2, 2, 3)
        for i in range(0, self.grid_size, max(1, self.grid_size//8)):
            ax3.plot(X[:, i], Z[:, i], 'b-', alpha=0.6, linewidth=1.2)
        for j in range(0, self.grid_size, max(1, self.grid_size//8)):
            ax3.plot(X[j, :], Z[j, :], 'r-', alpha=0.6, linewidth=1.2)
        
        ax3.scatter(points_array[:, 2], points_array[:, 4], color='red', s=60, 
                   zorder=5, edgecolors='darkred', linewidth=1.5)
        
        for i, p in enumerate(points_array):
            ax3.annotate(f'{i+1}', (p[2], p[4]), fontsize=8, 
                        xytext=(3, 3), textcoords='offset points',
                        fontweight='bold', color='darkred')
        
        ax3.set_xlabel('X', fontsize=10, fontweight='bold')
        ax3.set_ylabel('Z', fontsize=10, fontweight='bold')
        ax3.set_title('Проекція на площину y=0\n(синій: u=const, червоний: v=const)', 
                     fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3, linestyle='--')
        ax3.set_aspect('equal', adjustable='box')
        
        ax4 = self.fig.add_subplot(2, 2, 4)
        for i in range(0, self.grid_size, max(1, self.grid_size//8)):
            ax4.plot(Y[:, i], Z[:, i], 'b-', alpha=0.6, linewidth=1.2)
        for j in range(0, self.grid_size, max(1, self.grid_size//8)):
            ax4.plot(Y[j, :], Z[j, :], 'r-', alpha=0.6, linewidth=1.2)
        
        ax4.scatter(points_array[:, 3], points_array[:, 4], color='red', s=60, 
                   zorder=5, edgecolors='darkred', linewidth=1.5)
        
        for i, p in enumerate(points_array):
            ax4.annotate(f'{i+1}', (p[3], p[4]), fontsize=8, 
                        xytext=(3, 3), textcoords='offset points',
                        fontweight='bold', color='darkred')
        
        ax4.set_xlabel('Y', fontsize=10, fontweight='bold')
        ax4.set_ylabel('Z', fontsize=10, fontweight='bold')
        ax4.set_title('Проекція на площину x=0\n(синій: u=const, червоний: v=const)', 
                     fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3, linestyle='--')
        ax4.set_aspect('equal', adjustable='box')
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = CubicSurfaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()