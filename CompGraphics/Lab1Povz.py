import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

fig = plt.figure(figsize=(8, 8), facecolor='#1a1a1a')
ax = fig.add_subplot(111, facecolor='#2a2a2a')
ax.set_aspect('equal')

n = 4
for k in range(n + 1):
    ax.axvline(k, color='gray', linewidth=0.3, alpha=0.5)
    ax.axhline(k, color='gray', linewidth=0.3, alpha=0.5)

colors = [
    ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'],
    ['#FFEEAD', '#D4A5A5', '#9B59B6', '#3498DB'],
    ['#E74C3C', '#2ECC71', '#F1C40F', '#E67E22'],
    ['#1ABC9C', '#C0392B', '#8E44AD', '#F39C12']
]
patches = []
for i in range(n):
    for j in range(n):
        patch = Polygon([[0, 0], [0, 0], [0, 0], [0, 0]], closed=True, fill=True, 
                        facecolor=colors[i][j], edgecolor='white', linewidth=1, alpha=0.7)
        ax.add_patch(patch)
        patches.append(patch)
ax_slider = plt.axes([0.15, 0.02, 0.65, 0.03], facecolor='#2a2a2a')
slider = Slider(ax_slider, 'Alpha (°/s)', -180, 180, valinit=30, valstep=1, 
                color='#FF6B6B', initcolor='white')
slider.label.set_color('white')
slider.valtext.set_color('white')  

current_alpha = [slider.val] 

def update_alpha(val):
    current_alpha[0] = val

slider.on_changed(update_alpha)
def update(t):
    idx = 0
    for i in range(n):
        for j in range(n):
            cx = i + 0.5
            cy = j + 0.5
            beta = (current_alpha[0] * t) if (i + j) % 2 == 0 else -(current_alpha[0] * t)
            theta = beta + 45
            theta_rad = np.deg2rad(theta)
            cos_th = np.cos(theta_rad)
            sin_th = np.sin(theta_rad)
            max_cs = max(abs(cos_th), abs(sin_th))
            a = 0.5  
            r = a / max_cs if max_cs > 0 else a
            thetas = [theta + k * 90 for k in range(4)]
            verts = []
            for th in thetas:
                th_rad = np.deg2rad(th)
                x = cx + r * np.cos(th_rad)
                y = cy + r * np.sin(th_rad)
                verts.append([x, y])
            patches[idx].set_xy(verts)
            patches[idx].set_alpha(0.7 + 0.2 * np.sin(t * 2 * np.pi)) 
            idx += 1
    return patches

fps = 90
ani = FuncAnimation(fig, update, frames=np.linspace(0, 20, 20 * fps), interval=1000/fps, blit=True)

ax.set_xlim(-0.1, n + 0.1)
ax.set_ylim(-0.1, n + 0.1)

ax.set_xticks([])
ax.set_yticks([])

plt.subplots_adjust(bottom=0.1)

plt.show()