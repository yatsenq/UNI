import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation

def create_animation(alpha, fig_title):
    fig = plt.figure(figsize=(6, 6), facecolor='#1a1a1a')
    ax = fig.add_subplot(111, facecolor='#2a2a2a')
    ax.set_aspect('equal')
    ax.set_title(f'Alpha = {alpha}°/s', color='white')

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

    def update(t):
        idx = 0
        for i in range(n):
            for j in range(n):
                cx = i + 0.5
                cy = j + 0.5
                beta = (alpha * t) if (i + j) % 2 == 0 else -(alpha * t)
                theta = beta + 45
                theta_rad = np.deg2rad(theta)
                cos_th = np.cos(theta_rad)
                sin_th = np.sin(theta_rad)
                max_cs = max(abs(cos_th), abs(sin_th))
                a = 0.5
                r = a / max_cs if max_cs > 0 else a
                thetas = [theta + k * 90 for k in range(4)]
                verts = [[cx + r * np.cos(np.deg2rad(th)), cy + r * np.sin(np.deg2rad(th))] for th in thetas]
                patches[idx].set_xy(verts)
                patches[idx].set_alpha(0.7 + 0.2 * np.sin(t * 2 * np.pi))
                idx += 1
        return patches

    fps = 30
    ani = FuncAnimation(fig, update, frames=np.linspace(0, 20, 20 * fps), interval=1000/fps, blit=True)

    ax.set_xlim(-0.1, n + 0.1)
    ax.set_ylim(-0.1, n + 0.1)
    ax.set_xticks([])
    ax.set_yticks([])

    return fig, ani

while True:
    try:
        alpha1 = float(input("Введіть першу кутову швидкість (alpha1): "))
        alpha2 = float(input("Введіть другу кутову швидкість (alpha2): "))
        break
    except ValueError:
        print("Будь ласка, введіть числові значення для кутових швидкостей.")

fig1, ani1 = create_animation(alpha1, f'Animation with Alpha = {alpha1}°')
fig2, ani2 = create_animation(alpha2, f'Animation with Alpha = {alpha2}°')

plt.show()