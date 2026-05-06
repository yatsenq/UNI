import numpy as np

def f(x):
    return 2*x**2 + 4*x + 2

def df(x):
    return 4*x + 4

a, b = -3, 1
L = 8

points = [a, b]

for iteration in range(1, 6):
    def piecewise(x_val):
        return max(f(p) - L * abs(x_val - p) for p in points)
    
    xs = np.linspace(a, b, 1000000)
    ys = np.array([piecewise(x) for x in xs])
    min_idx = np.argmin(ys)
    x_new = round(xs[min_idx], 4)
    S = round(ys[min_idx], 4)
    f_new = round(f(x_new), 4)
    
    print(f"Ітерація {iteration}:")
    print(f"  x_new = {x_new}")
    print(f"  x_new^2 = {round(x_new**2, 4)}")
    print(f"  f(x_new) = 2·{round(x_new**2,4)} + 4·({x_new}) + 2 = {round(2*x_new**2,4)} + ({round(4*x_new,4)}) + 2 = {f_new}")
    print(f"  S = {S}")
    print(f"  f - S = {round(f_new - S, 4)}")
    print()
    
    points.append(x_new)