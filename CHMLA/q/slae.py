from matrix import Matrix
from vector import Vector


class SLAE:
    """
    Клас СЛАР (Система Лінійних Алгебраїчних Рівнянь).
    Представляє систему Ax = b, де:
      A — матриця коефіцієнтів (n x m)
      x — вектор розв'язку (n x 1)
      b — вектор правої частини (n x 1)
    """

    def __init__(self, A=None, b=None):
        """
        Конструктор СЛАР.
        A — об'єкт Matrix (матриця коефіцієнтів)
        b — об'єкт Vector (вектор правої частини)
        """
        if A is not None:
            self.A = A.copy()
        else:
            self.A = Matrix()

        if b is not None:
            self.b = b.copy()
        else:
            self.b = Vector()

        # Вектор розв'язку — спочатку порожній
        self.x = Vector()

    def solve_gauss(self):
        """
        Розв'язує СЛАР методом Гауса з вибором головного елемента по стовпцю.
        Повертає вектор розв'язку x.
        """
        n = self.A.rows

        if n == 0:
            raise ValueError("Матриця порожня, нема чого розв'язувати.")
        if n != self.A.cols:
            raise ValueError("Матриця повинна бути квадратною для методу Гауса.")
        if n != self.b.size:
            raise ValueError("Розмір вектора b не відповідає розміру матриці A.")

        # Створюємо розширену матрицю [A | b]
        aug_data = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append(self.A.get(i, j))
            row.append(self.b.get(i))
            aug_data.append(row)

        # Прямий хід з вибором головного елемента
        for k in range(n):
            # Пошук максимального елемента у стовпці k (від рядка k до n)
            max_val = abs(aug_data[k][k])
            max_row = k
            for i in range(k + 1, n):
                if abs(aug_data[i][k]) > max_val:
                    max_val = abs(aug_data[i][k])
                    max_row = i

            # Перестановка рядків
            if max_row != k:
                aug_data[k], aug_data[max_row] = aug_data[max_row], aug_data[k]

            # Перевірка на вироджену матрицю
            if abs(aug_data[k][k]) < 1e-12:
                raise ValueError("Матриця вироджена — система не має єдиного розв'язку.")

            # Елімінація
            for i in range(k + 1, n):
                factor = aug_data[i][k] / aug_data[k][k]
                for j in range(k, n + 1):
                    aug_data[i][j] -= factor * aug_data[k][j]

        # Зворотний хід
        x_data = [0.0] * n
        for i in range(n - 1, -1, -1):
            s = aug_data[i][n]
            for j in range(i + 1, n):
                s -= aug_data[i][j] * x_data[j]
            x_data[i] = s / aug_data[i][i]

        self.x = Vector(data=x_data)
        return self.x

    def residual(self):
        """
        Обчислює вектор нев'язки r = Ax - b.
        Використовується для перевірки точності розв'язку.
        """
        if self.x.size == 0:
            raise ValueError("Спочатку потрібно розв'язати систему.")

        # A * x — використовуємо множення матриці на вектор (як матрицю n×1)
        ax_matrix = self.A * self.x.matrix
        ax_data = [ax_matrix.get(i, 0) for i in range(ax_matrix.rows)]
        ax_vector = Vector(data=ax_data)

        r = ax_vector - self.b
        return r

    def __str__(self):
        result = "=== СЛАР: Ax = b ===\n"
        result += f"Матриця A ({self.A.rows}x{self.A.cols}):\n{self.A}\n"
        result += f"Вектор b: {self.b}\n"
        if self.x.size > 0:
            result += f"Розв'язок x: {self.x}\n"
        else:
            result += "Розв'язок: ще не обчислено\n"
        return result
