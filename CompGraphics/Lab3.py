import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Toplevel
import math

class CircleDrawer:
    def __init__(self, root):
        self.root = root
        self.root.title("Креслення кола - Брезенхем vs Многокутник")
        self.root.geometry("1450x850")
        self.root.configure(bg='#ecf0f1')
        
        self.width = 32
        self.height = 32
        self.pixel_size = 15
        
        self.framebuffer = [0] * (self.width * self.height)
        
        self.colors = {
            'bg': '#ecf0f1',
            'frame_bg': '#ffffff',
            'accent1': '#3498db',
            'accent2': '#e74c3c',
            'accent3': '#2ecc71',
            'header': '#34495e',
            'button': '#3498db'
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        params_frame = tk.LabelFrame(self.root, text="Параметри креслення", 
                                     font=('Arial', 11, 'bold'), bg='#ffffff', 
                                     fg='#2c3e50', relief=tk.GROOVE, bd=2)
        params_frame.grid(row=0, column=0, columnspan=3, padx=15, pady=15, sticky="ew")
        
        inner_params = tk.Frame(params_frame, bg='#ffffff')
        inner_params.pack(padx=20, pady=15)
        
        tk.Label(inner_params, text="Центр X:", font=('Arial', 10), 
                bg='#ffffff', fg='#34495e').grid(row=0, column=0, padx=5, pady=5)
        self.center_x = tk.Entry(inner_params, width=12, font=('Arial', 10), 
                                relief=tk.SOLID, bd=1)
        self.center_x.insert(0, "16")
        self.center_x.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(inner_params, text="Центр Y:", font=('Arial', 10), 
                bg='#ffffff', fg='#34495e').grid(row=0, column=2, padx=5, pady=5)
        self.center_y = tk.Entry(inner_params, width=12, font=('Arial', 10), 
                                relief=tk.SOLID, bd=1)
        self.center_y.insert(0, "16")
        self.center_y.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(inner_params, text="Радіус:", font=('Arial', 10), 
                bg='#ffffff', fg='#34495e').grid(row=0, column=4, padx=5, pady=5)
        self.radius = tk.Entry(inner_params, width=12, font=('Arial', 10), 
                              relief=tk.SOLID, bd=1)
        self.radius.insert(0, "10")
        self.radius.grid(row=0, column=5, padx=5, pady=5)
        
        tk.Label(inner_params, text="Сторін многокутника:", font=('Arial', 10), 
                bg='#ffffff', fg='#34495e').grid(row=0, column=6, padx=5, pady=5)
        self.polygon_sides = tk.Entry(inner_params, width=12, font=('Arial', 10), 
                                     relief=tk.SOLID, bd=1)
        self.polygon_sides.insert(0, "12")
        self.polygon_sides.grid(row=0, column=7, padx=5, pady=5)
        
        button_frame = tk.Frame(params_frame, bg='#ffffff')
        button_frame.pack(pady=10)
        
        draw_btn = tk.Button(button_frame, text="Намалювати", 
                            command=self.draw_circles,
                            font=('Arial', 10, 'bold'), bg="#34495e", fg='white',
                            relief=tk.RAISED, bd=2, padx=20, pady=8,
                            cursor='hand2')
        draw_btn.grid(row=0, column=0, padx=5)
        draw_btn.bind('<Enter>', lambda e: draw_btn.config(bg="#34495e"))
        draw_btn.bind('<Leave>', lambda e: draw_btn.config(bg="#34495e"))
        
        clear_btn = tk.Button(button_frame, text="Очистити", 
                             command=self.clear_all,
                             font=('Arial', 10, 'bold'), bg="#34495e", fg='white',
                             relief=tk.RAISED, bd=2, padx=20, pady=8,
                             cursor='hand2')
        clear_btn.grid(row=0, column=1, padx=5)
        clear_btn.bind('<Enter>', lambda e: clear_btn.config(bg="#34495e"))
        clear_btn.bind('<Leave>', lambda e: clear_btn.config(bg="#34495e"))
        
        random_btn = tk.Button(button_frame, text="Випадково", 
                              command=self.random_params,
                              font=('Arial', 10, 'bold'), bg="#34495e", fg='white',
                              relief=tk.RAISED, bd=2, padx=20, pady=8,
                              cursor='hand2')
        random_btn.grid(row=0, column=2, padx=5)
        random_btn.bind('<Enter>', lambda e: random_btn.config(bg='#34495e'))
        random_btn.bind('<Leave>', lambda e: random_btn.config(bg='#34495e'))
        
        canvas_frame = tk.Frame(self.root, bg='#ecf0f1')
        canvas_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        
        bresenham_frame = tk.LabelFrame(canvas_frame, text="Алгоритм Брезенхема", 
                                       font=('Arial', 10, 'bold'), bg='#ffffff',
                                       fg='#3498db', relief=tk.GROOVE, bd=2)
        bresenham_frame.grid(row=0, column=0, padx=8)
        self.canvas_bresenham = tk.Canvas(bresenham_frame, width=self.width*self.pixel_size, 
                                         height=self.height*self.pixel_size, bg='#fafafa',
                                         relief=tk.SUNKEN, bd=1)
        self.canvas_bresenham.pack(padx=5, pady=5)
        
        polygon_frame = tk.LabelFrame(canvas_frame, text="Апроксимація многокутником", 
                                     font=('Arial', 10, 'bold'), bg='#ffffff',
                                     fg='#e74c3c', relief=tk.GROOVE, bd=2)
        polygon_frame.grid(row=0, column=1, padx=8)
        self.canvas_polygon = tk.Canvas(polygon_frame, width=self.width*self.pixel_size, 
                                       height=self.height*self.pixel_size, bg='#fafafa',
                                       relief=tk.SUNKEN, bd=1)
        self.canvas_polygon.pack(padx=5, pady=5)
        
        comparison_frame = tk.LabelFrame(canvas_frame, text="Порівняння (накладення)", 
                                        font=('Arial', 10, 'bold'), bg='#ffffff',
                                        fg='#2ecc71', relief=tk.GROOVE, bd=2)
        comparison_frame.grid(row=0, column=2, padx=8)
        self.canvas_comparison = tk.Canvas(comparison_frame, width=self.width*self.pixel_size, 
                                          height=self.height*self.pixel_size, bg='#fafafa',
                                          relief=tk.SUNKEN, bd=1)
        self.canvas_comparison.pack(padx=5, pady=5)
        
        output_frame = tk.Frame(self.root, bg='#ecf0f1')
        output_frame.grid(row=2, column=0, columnspan=3, padx=15, pady=10, sticky="nsew")
        
        bresenham_list_frame = tk.LabelFrame(output_frame, text="Пікселі Брезенхема", 
                                            font=('Arial', 10, 'bold'), bg='#ffffff',
                                            fg="#34495e", relief=tk.GROOVE, bd=2)
        bresenham_list_frame.grid(row=0, column=0, padx=5, sticky="nsew")
        
        scroll_frame1 = tk.Frame(bresenham_list_frame, bg='#ffffff')
        scroll_frame1.pack(padx=5, pady=5)
        
        self.bresenham_text = scrolledtext.ScrolledText(scroll_frame1, width=32, height=10,
                                                       font=('Courier', 9), bg='#f8f9fa',
                                                       relief=tk.SUNKEN, bd=1)
        self.bresenham_text.pack()
        
        open_btn1 = tk.Button(bresenham_list_frame, text="Відкрити повний список", 
                             command=lambda: self.open_pixel_window("Брезенхем", self.bresenham_pixels_cache),
                             font=('Arial', 9), bg="#34495e", fg='white',
                             relief=tk.RAISED, bd=1, padx=10, pady=5,
                             cursor='hand2')
        open_btn1.pack(pady=5)
        open_btn1.bind('<Enter>', lambda e: open_btn1.config(bg="#34495e"))
        open_btn1.bind('<Leave>', lambda e: open_btn1.config(bg="#34495e"))
        
        polygon_list_frame = tk.LabelFrame(output_frame, text="Пікселі многокутника", 
                                          font=('Arial', 10, 'bold'), bg='#ffffff',
                                          fg="#34495e", relief=tk.GROOVE, bd=2)
        polygon_list_frame.grid(row=0, column=1, padx=5, sticky="nsew")
        
        scroll_frame2 = tk.Frame(polygon_list_frame, bg='#ffffff')
        scroll_frame2.pack(padx=5, pady=5)
        
        self.polygon_text = scrolledtext.ScrolledText(scroll_frame2, width=32, height=10,
                                                     font=('Courier', 9), bg='#f8f9fa',
                                                     relief=tk.SUNKEN, bd=1)
        self.polygon_text.pack()
        
        open_btn2 = tk.Button(polygon_list_frame, text="Відкрити повний список", 
                             command=lambda: self.open_pixel_window("Многокутник", self.polygon_pixels_cache),
                             font=('Arial', 9), bg="#34495e", fg='white',
                             relief=tk.RAISED, bd=1, padx=10, pady=5,
                             cursor='hand2')
        open_btn2.pack(pady=5)
        open_btn2.bind('<Enter>', lambda e: open_btn2.config(bg='#c0392b'))
        open_btn2.bind('<Leave>', lambda e: open_btn2.config(bg='#e74c3c'))
        
        stats_frame = tk.LabelFrame(output_frame, text="Статистика порівняння", 
                                   font=('Arial', 10, 'bold'), bg='#ffffff',
                                   fg="#34495e", relief=tk.GROOVE, bd=2)
        stats_frame.grid(row=0, column=2, padx=5, sticky="nsew")
        self.stats_text = scrolledtext.ScrolledText(stats_frame, width=40, height=12,
                                                   font=('Courier', 9), bg='#f8f9fa',
                                                   relief=tk.SUNKEN, bd=1)
        self.stats_text.pack(padx=5, pady=5)
        
        footer_frame = tk.Frame(self.root, bg='#34495e', height=35)
        footer_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        footer_frame.grid_propagate(False)
        
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(2, weight=1)
        output_frame.columnconfigure(0, weight=1)
        output_frame.columnconfigure(1, weight=1)
        output_frame.columnconfigure(2, weight=1)
        
        self.bresenham_pixels_cache = []
        self.polygon_pixels_cache = []
    
    def open_pixel_window(self, title, pixels):
        if not pixels:
            messagebox.showinfo("Інформація", "Спочатку намалюйте коло!")
            return
            
        window = Toplevel(self.root)
        window.title(f"Повний список пікселів - {title}")
        window.geometry("500x600")
        window.configure(bg='#ecf0f1')
        
        frame = tk.LabelFrame(window, text=f"Метод: {title}", 
                             font=('Arial', 11, 'bold'), bg='#ffffff',
                             relief=tk.GROOVE, bd=2)
        frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        text_widget = scrolledtext.ScrolledText(frame, width=50, height=30,
                                               font=('Courier', 10), bg='#f8f9fa',
                                               relief=tk.SUNKEN, bd=1)
        text_widget.pack(padx=10, pady=10, fill='both', expand=True)
        
        text_widget.insert(tk.END, f"Метод: {title}\n")
        text_widget.insert(tk.END, f"Всього пікселів: {len(pixels)}\n")
        text_widget.insert(tk.END, "=" * 40 + "\n")
        text_widget.insert(tk.END, "Формат: (рядок, колонка)\n")
        text_widget.insert(tk.END, "Пікселі з псевдобуфера кадра\n")
        text_widget.insert(tk.END, "(одновимірний масив 32×32)\n")
        text_widget.insert(tk.END, "=" * 40 + "\n\n")
        
        for i, (x, y) in enumerate(pixels, 1):
            text_widget.insert(tk.END, f"{i:3d}. ({y:2d}, {x:2d})\n")
        
        text_widget.config(state='disabled')
        
        close_btn = tk.Button(window, text="Закрити", 
                             command=window.destroy,
                             font=('Arial', 10, 'bold'), bg='#95a5a6', fg='white',
                             relief=tk.RAISED, bd=2, padx=20, pady=8,
                             cursor='hand2')
        close_btn.pack(pady=10)
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#7f8c8d'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='#95a5a6'))
    
    def clear_all(self):
        self.canvas_bresenham.delete('all')
        self.canvas_polygon.delete('all')
        self.canvas_comparison.delete('all')
        self.bresenham_text.delete(1.0, tk.END)
        self.polygon_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.draw_grid(self.canvas_bresenham)
        self.draw_grid(self.canvas_polygon)
        self.draw_grid(self.canvas_comparison)
        self.bresenham_pixels_cache = []
        self.polygon_pixels_cache = []
    
    def random_params(self):
        import random
        self.center_x.delete(0, tk.END)
        self.center_x.insert(0, str(random.randint(10, 22)))
        self.center_y.delete(0, tk.END)
        self.center_y.insert(0, str(random.randint(10, 22)))
        self.radius.delete(0, tk.END)
        self.radius.insert(0, str(random.randint(5, 12)))
        self.polygon_sides.delete(0, tk.END)
        self.polygon_sides.insert(0, str(random.randint(6, 20)))
    
    def clear_framebuffer(self):
        self.framebuffer = [0] * (self.width * self.height)
    
    def set_pixel_in_buffer(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            index = y * self.width + x
            self.framebuffer[index] = 1
    
    def get_pixels_from_buffer(self):
        pixels = []
        for i in range(len(self.framebuffer)):
            if self.framebuffer[i] == 1:
                x = i % self.width
                y = i // self.width
                pixels.append((x, y))
        return pixels
    
    def render_buffer_to_canvas(self, canvas, color='blue'):
        for i in range(len(self.framebuffer)):
            if self.framebuffer[i] == 1:
                x = i % self.width
                y = i // self.width
                self.draw_pixel(canvas, x, y, color)
        
    def draw_grid(self, canvas):
        for i in range(self.width + 1):
            x = i * self.pixel_size
            canvas.create_line(x, 0, x, self.height * self.pixel_size, fill='#d0d0d0', width=1)
        for i in range(self.height + 1):
            y = i * self.pixel_size
            canvas.create_line(0, y, self.width * self.pixel_size, y, fill='#d0d0d0', width=1)
    
    def draw_pixel(self, canvas, x, y, color='blue'):
        if 0 <= x < self.width and 0 <= y < self.height:
            x1 = x * self.pixel_size + 1
            y1 = y * self.pixel_size + 1
            x2 = (x + 1) * self.pixel_size - 1
            y2 = (y + 1) * self.pixel_size - 1
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
    
    def bresenham_circle(self, xc, yc, r):
        pixels = []
        x = 0
        y = r
        d = 3 - 2 * r
        
        def add_symmetric_points(xc, yc, x, y):
            points = [
                (xc + x, yc + y),
                (xc - x, yc + y),
                (xc + x, yc - y),
                (xc - x, yc - y),
                (xc + y, yc + x),
                (xc - y, yc + x),
                (xc + y, yc - x),
                (xc - y, yc - x)
            ]
            return points
        
        while y >= x:
            pixels.extend(add_symmetric_points(xc, yc, x, y))
            x += 1
            
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
        
        pixels = list(set(pixels))
        pixels.sort()
        return pixels
    
    def polygon_circle(self, xc, yc, r, n_sides):
        pixels = set()
        angle_step = 2 * math.pi / n_sides
        
        vertices = []
        for i in range(n_sides):
            angle = i * angle_step
            x = xc + r * math.cos(angle)
            y = yc + r * math.sin(angle)
            vertices.append((x, y))
        
        for i in range(n_sides):
            x0, y0 = vertices[i]
            x1, y1 = vertices[(i + 1) % n_sides]
            pixels.update(self.bresenham_line(x0, y0, x1, y1))
        
        pixels = list(pixels)
        pixels.sort()
        return pixels
    
    def bresenham_line(self, x0, y0, x1, y1):
        pixels = []
        
        x0, y0 = round(x0), round(y0)
        x1, y1 = round(x1), round(y1)
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            if 0 <= x0 < self.width and 0 <= y0 < self.height:
                pixels.append((x0, y0))
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        return pixels
    
    def draw_circles(self):
        try:
            xc = int(self.center_x.get())
            yc = int(self.center_y.get())
            r = int(self.radius.get())
            n_sides = int(self.polygon_sides.get())
            
            if not (0 <= xc < self.width and 0 <= yc < self.height):
                raise ValueError("Центр повинен бути в межах 0-31")
            if r <= 0 or r > 20:
                raise ValueError("Радіус повинен бути від 1 до 20")
            if n_sides < 3:
                raise ValueError("Кількість сторін повинна бути >= 3")
            
            self.canvas_bresenham.delete('all')
            self.canvas_polygon.delete('all')
            self.canvas_comparison.delete('all')
            
            self.draw_grid(self.canvas_bresenham)
            self.draw_grid(self.canvas_polygon)
            self.draw_grid(self.canvas_comparison)
            
            self.clear_framebuffer()
            bresenham_pixels = self.bresenham_circle(xc, yc, r)
            
            for x, y in bresenham_pixels:
                self.set_pixel_in_buffer(x, y)
            
            self.render_buffer_to_canvas(self.canvas_bresenham, '#3498db')
            self.render_buffer_to_canvas(self.canvas_comparison, '#3498db')
            
            bresenham_pixels_from_buffer = self.get_pixels_from_buffer()
            self.bresenham_pixels_cache = bresenham_pixels_from_buffer
            
            self.clear_framebuffer()
            polygon_pixels = self.polygon_circle(xc, yc, r, n_sides)
            
            for x, y in polygon_pixels:
                self.set_pixel_in_buffer(x, y)
            
            self.render_buffer_to_canvas(self.canvas_polygon, '#e74c3c')
            
            polygon_pixels_from_buffer = self.get_pixels_from_buffer()
            self.polygon_pixels_cache = polygon_pixels_from_buffer
            
            bresenham_set = set(bresenham_pixels)
            polygon_set = set(polygon_pixels)
            common_pixels = bresenham_set.intersection(polygon_set)
            only_polygon = polygon_set - bresenham_set
            
            for x, y in only_polygon:
                self.draw_pixel(self.canvas_comparison, x, y, '#e74c3c')
            for x, y in common_pixels:
                self.draw_pixel(self.canvas_comparison, x, y, '#2ecc71')
            
            self.draw_pixel(self.canvas_bresenham, xc, yc, '#f39c12')
            self.draw_pixel(self.canvas_polygon, xc, yc, '#f39c12')
            self.draw_pixel(self.canvas_comparison, xc, yc, '#f39c12')
            
            self.display_pixel_list(bresenham_pixels_from_buffer, self.bresenham_text, "Брезенхема")
            self.display_pixel_list(polygon_pixels_from_buffer, self.polygon_text, "многокутника")
            
            self.display_statistics(bresenham_pixels, polygon_pixels, common_pixels)
            
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, f"Помилка: {e}")
    
    def display_pixel_list(self, pixels, text_widget, method_name):
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"Метод: {method_name}\n")
        text_widget.insert(tk.END, f"Всього пікселів: {len(pixels)}\n")
        text_widget.insert(tk.END, "=" * 30 + "\n")
        text_widget.insert(tk.END, "Формат: (рядок, колонка)\n\n")
        
        display_count = min(len(pixels), 50)
        for i, (x, y) in enumerate(pixels[:display_count], 1):
            text_widget.insert(tk.END, f"{i:3d}. ({y:2d}, {x:2d})\n")
        
        if len(pixels) > display_count:
            text_widget.insert(tk.END, f"\n... та ще {len(pixels) - display_count} пікселів\n")
            text_widget.insert(tk.END, "Натисніть 'Відкрити повний список'\n")
    
    def display_statistics(self, bresenham_pixels, polygon_pixels, common_pixels):
        self.stats_text.delete(1.0, tk.END)
        
        bresenham_set = set(bresenham_pixels)
        polygon_set = set(polygon_pixels)
        
        only_bresenham = bresenham_set - polygon_set
        only_polygon = polygon_set - bresenham_set
        
        total_unique = len(bresenham_set.union(polygon_set))
        
        self.stats_text.insert(tk.END, "СТАТИСТИКА ПОРІВНЯННЯ\n")
        self.stats_text.insert(tk.END, "=" * 38 + "\n\n")
        
        self.stats_text.insert(tk.END, "ПСЕВДОБУФЕР КАДРА:\n")
        self.stats_text.insert(tk.END, f"  Розмір: {self.width}x{self.height}\n")
        self.stats_text.insert(tk.END, f"  Елементів: {len(self.framebuffer)}\n")
        self.stats_text.insert(tk.END, f"  Тип: одновимірний масив\n\n")
        
        self.stats_text.insert(tk.END, "КІЛЬКІСТЬ ПІКСЕЛІВ:\n")
        self.stats_text.insert(tk.END, f"  Брезенхем: {len(bresenham_pixels)}\n")
        self.stats_text.insert(tk.END, f"  Многокутник: {len(polygon_pixels)}\n\n")
        
        self.stats_text.insert(tk.END, "АНАЛІЗ ЗБІГУ:\n")
        self.stats_text.insert(tk.END, f"  Спільні: {len(common_pixels)}\n")
        self.stats_text.insert(tk.END, f"  Тільки Брезенхем: {len(only_bresenham)}\n")
        self.stats_text.insert(tk.END, f"  Тільки многокутник: {len(only_polygon)}\n")
        self.stats_text.insert(tk.END, f"  Всього унікальних: {total_unique}\n\n")
        
        if len(bresenham_pixels) > 0:
            match_percentage = (len(common_pixels) / len(bresenham_pixels)) * 100
            self.stats_text.insert(tk.END, f"  Збіг з Брезенхемом: {match_percentage:.1f}%\n")
        
        if len(polygon_pixels) > 0:
            match_percentage_poly = (len(common_pixels) / len(polygon_pixels)) * 100
            self.stats_text.insert(tk.END, f"  Збіг з многокутником: {match_percentage_poly:.1f}%\n")

def main():
    root = tk.Tk()
    app = CircleDrawer(root)
    root.mainloop()

if __name__ == "__main__":
    main()