from matrix import Matrix
from vector import Vector
import math


class SeidelSolver:
    def __init__(self, A=None, b=None):
        self.A = A.copy() if A is not None else Matrix()
        self.b = b.copy() if b is not None else Vector()

    def _validate(self):
        n = self.A.rows
        if n == 0:
            raise ValueError("Матриця порожня.")
        if n != self.A.cols:
            raise ValueError("Матриця A повинна бути квадратною.")
        if self.b.size != n:
            raise ValueError("Розмір вектора b не відповідає матриці A.")
        for i in range(n):
            if abs(self.A.get(i, i)) < 1e-12:
                raise ValueError("На головній діагоналі є нуль. Метод Зейделя неможливий.")
        return n

    def is_strictly_diagonally_dominant(self):
        n = self._validate()
        for i in range(n):
            diag = abs(self.A.get(i, i))
            off_sum = 0.0
            for j in range(n):
                if i != j:
                    off_sum += abs(self.A.get(i, j))
            if diag <= off_sum:
                return False
        return True

    def solve(self, eps=1e-6, max_iterations=1000, initial_x=None):
        if eps <= 0:
            raise ValueError("Точність eps повинна бути додатною.")
        if max_iterations <= 0:
            raise ValueError("Кількість ітерацій повинна бути додатною.")

        n = self._validate()
        if initial_x is not None:
            if initial_x.size != n:
                raise ValueError("Розмір початкового наближення не відповідає матриці A.")
            x_old = initial_x.to_list()
        else:
            x_old = [0.0] * n

        converged = False
        iterations = 0
        last_diff = 0.0
        overflow_detected = False

        for k in range(1, max_iterations + 1):
            x_new = x_old[:]
            for i in range(n):
                sum_left = 0.0
                for j in range(i):
                    sum_left += self.A.get(i, j) * x_new[j]

                sum_right = 0.0
                for j in range(i + 1, n):
                    sum_right += self.A.get(i, j) * x_old[j]

                x_new[i] = (self.b.get(i) - sum_left - sum_right) / self.A.get(i, i)

            if any((not math.isfinite(v)) or abs(v) > 1e100 for v in x_new):
                overflow_detected = True
                x_old = x_new
                iterations = k
                break

            last_diff = max(abs(x_new[i] - x_old[i]) for i in range(n))
            x_old = x_new
            iterations = k
            if last_diff < eps:
                converged = True
                break

        x_vector = Vector(data=x_old)

        ax_matrix = self.A * x_vector.matrix
        ax_vector = Vector(data=[ax_matrix.get(i, 0) for i in range(ax_matrix.rows)])
        residual = ax_vector - self.b

        residual_norm = 0.0
        for i in range(residual.size):
            residual_norm = math.hypot(residual_norm, residual.get(i))

        return {
            "converged": converged,
            "iterations": iterations,
            "x": x_vector,
            "last_diff": last_diff,
            "residual": residual,
            "residual_norm": residual_norm,
            "dominance": self.is_strictly_diagonally_dominant(),
            "overflow_detected": overflow_detected,
        }
