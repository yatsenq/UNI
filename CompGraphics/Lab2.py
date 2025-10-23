import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk
from mpl_toolkits.mplot3d import Axes3D

class BilinearSurfaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Білінійна інтерполююча поверхня Q(u,v)")
        self.root.geometry("1400x900")
        
        # Початкові контрольні точки (P00, P10, P01, P11)
        self.points = [
            [0.0, 0.0, 0.0],  # P00
            [1.0, 0.0, 1.0],  # P10
            [0.0, 1.0, 1.0],  # P01
            [1.0, 1.0, 2.0]   # P11
        ]
        
        self.grid_size = 20
        
        self.setup_gui()
        self.update_plot()
    
    def setup_gui(self):
        # Головний контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Ліва панель - контроль точок
        control_frame = ttk.LabelFrame(main_frame, text="Контрольні точки", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Поля вводу для кожної точки
        self.entries = []
        labels = ["P₀₀ (u=0, v=0)", "P₁₀ (u=1, v=0)", "P₀₁ (u=0, v=1)", "P₁₁ (u=1, v=1)"]
        
        for i, label in enumerate(labels):
            ttk.Label(control_frame, text=label, font=('Arial', 10, 'bold')).grid(
                row=i*4, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
            )
            
            point_entries = []
            for j, coord in enumerate(['X:', 'Y:', 'Z:']):
                ttk.Label(control_frame, text=coord).grid(row=i*4+j+1, column=0, sticky=tk.W)
                entry = ttk.Entry(control_frame, width=10)
                entry.insert(0, str(self.points[i][j]))
                entry.grid(row=i*4+j+1, column=1, padx=5, pady=2)
                point_entries.append(entry)
            
            self.entries.append(point_entries)
        
        # Розмір сітки
        ttk.Label(control_frame, text="Розмір сітки:", font=('Arial', 10, 'bold')).grid(
            row=16, column=0, sticky=tk.W, pady=(20, 5)
        )
        self.grid_scale = tk.Scale(
            control_frame, from_=5, to=50, orient=tk.HORIZONTAL,
            command=self.on_grid_change, length=200
        )
        self.grid_scale.set(self.grid_size)
        self.grid_scale.grid(row=17, column=0, columnspan=3, pady=5)
        
        # Кнопка оновлення
        update_btn = ttk.Button(
            control_frame, text="Оновити поверхню",
            command=self.update_plot, style='Accent.TButton'
        )
        update_btn.grid(row=18, column=0, columnspan=3, pady=20)
        
        # Інформація
        info_frame = ttk.LabelFrame(control_frame, text="Формула", padding="10")
        info_frame.grid(row=19, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        info_text = "Q(u,v) = (1-u)(1-v)P₀₀ + \n         u(1-v)P₁₀ + \n         (1-u)vP₀₁ + \n         uvP₁₁\n\nде u,v ∈ [0,1]"
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()
        
        # Права панель - графіки
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Створення фігури matplotlib
        self.fig = Figure(figsize=(14, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Налаштування розміру
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def on_grid_change(self, value):
        self.grid_size = int(float(value))
    
    def bilinear_interpolation(self, u, v):
        """Білінійна інтерполяція для параметрів u, v"""
        p00, p10, p01, p11 = self.points
        
        x = (1-u)*(1-v)*p00[0] + u*(1-v)*p10[0] + (1-u)*v*p01[0] + u*v*p11[0]
        y = (1-u)*(1-v)*p00[1] + u*(1-v)*p10[1] + (1-u)*v*p01[1] + u*v*p11[1]
        z = (1-u)*(1-v)*p00[2] + u*(1-v)*p10[2] + (1-u)*v*p01[2] + u*v*p11[2]
        
        return x, y, z
    
    def generate_surface(self):
        """Генерація точок поверхні"""
        u = np.linspace(0, 1, self.grid_size)
        v = np.linspace(0, 1, self.grid_size)
        
        X = np.zeros((self.grid_size, self.grid_size))
        Y = np.zeros((self.grid_size, self.grid_size))
        Z = np.zeros((self.grid_size, self.grid_size))
        
        for i, u_val in enumerate(u):
            for j, v_val in enumerate(v):
                x, y, z = self.bilinear_interpolation(u_val, v_val)
                X[i, j] = x
                Y[i, j] = y
                Z[i, j] = z
        
        return X, Y, Z
    
    def update_plot(self):
        """Оновлення всіх графіків"""
        # Зчитування точок з GUI
        try:
            for i in range(4):
                for j in range(3):
                    self.points[i][j] = float(self.entries[i][j].get())
        except ValueError:
            return
        
        # Генерація поверхні
        X, Y, Z = self.generate_surface()
        
        # Очищення попередніх графіків
        self.fig.clear()
        
        # 3D поверхня
        ax1 = self.fig.add_subplot(2, 2, 1, projection='3d')
        ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, edgecolor='none')
        ax1.plot_wireframe(X, Y, Z, color='black', alpha=0.3, linewidth=0.5)
        
        # Контрольні точки
        points_array = np.array(self.points)
        ax1.scatter(points_array[:, 0], points_array[:, 1], points_array[:, 2],
                   color='red', s=100, marker='o', label='Контрольні точки')
        
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title('3D поверхня Q(u,v)', fontsize=12, fontweight='bold')
        ax1.legend()
        
        # Проекція на площину z=0 (XY)
        ax2 = self.fig.add_subplot(2, 2, 2)
        # Координатні криві u=const
        for i in range(0, self.grid_size, max(1, self.grid_size//10)):
            ax2.plot(X[i, :], Y[i, :], 'b-', alpha=0.5, linewidth=0.8)
        # Координатні криві v=const
        for j in range(0, self.grid_size, max(1, self.grid_size//10)):
            ax2.plot(X[:, j], Y[:, j], 'r-', alpha=0.5, linewidth=0.8)
        
        ax2.scatter(points_array[:, 0], points_array[:, 1], color='red', s=50, zorder=5)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title('Проекція на площину z=0', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_aspect('equal', adjustable='box')
        
        # Проекція на площину y=0 (XZ)
        ax3 = self.fig.add_subplot(2, 2, 3)
        for i in range(0, self.grid_size, max(1, self.grid_size//10)):
            ax3.plot(X[i, :], Z[i, :], 'b-', alpha=0.5, linewidth=0.8)
        for j in range(0, self.grid_size, max(1, self.grid_size//10)):
            ax3.plot(X[:, j], Z[:, j], 'r-', alpha=0.5, linewidth=0.8)
        
        ax3.scatter(points_array[:, 0], points_array[:, 2], color='red', s=50, zorder=5)
        ax3.set_xlabel('X')
        ax3.set_ylabel('Z')
        ax3.set_title('Проекція на площину y=0', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.set_aspect('equal', adjustable='box')
        
        # Проекція на площину x=0 (YZ)
        ax4 = self.fig.add_subplot(2, 2, 4)
        for i in range(0, self.grid_size, max(1, self.grid_size//10)):
            ax4.plot(Y[i, :], Z[i, :], 'b-', alpha=0.5, linewidth=0.8)
        for j in range(0, self.grid_size, max(1, self.grid_size//10)):
            ax4.plot(Y[:, j], Z[:, j], 'r-', alpha=0.5, linewidth=0.8)
        
        ax4.scatter(points_array[:, 1], points_array[:, 2], color='red', s=50, zorder=5)
        ax4.set_xlabel('Y')
        ax4.set_ylabel('Z')
        ax4.set_title('Проекція на площину x=0', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_aspect('equal', adjustable='box')
        
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = BilinearSurfaceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()