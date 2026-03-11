import random
import math


class Matrix:
    def __init__(self, rows=0, cols=0, data=None):
        if data is not None:
            try:
                if not isinstance(data, list):
                    raise ValueError("Дані матриці повинні бути списком рядків.")
                self.rows = len(data)
                self.cols = len(data[0]) if self.rows > 0 else 0
                for row in data:
                    if len(row) != self.cols:
                        raise ValueError("Усі рядки матриці мають бути однакової довжини.")
                self.data = [row[:] for row in data]
            except Exception as e:
                raise ValueError(f"Помилка створення матриці: {e}")
        else:
            if rows < 0 or cols < 0:
                raise ValueError("Розміри матриці не можуть бути від'ємними.")
            self.rows = rows
            self.cols = cols
            self.data = [[0.0] * cols for _ in range(rows)]

    @classmethod
    def random_matrix(cls, rows, cols, low=-10, high=10, use_int=False):
        if rows < 0 or cols < 0:
            raise ValueError("Розміри матриці не можуть бути від'ємними.")
        if low > high:
            raise ValueError("Нижня межа діапазону не може бути більшою за верхню.")
        data = []
        for i in range(rows):
            row = []
            for j in range(cols):
                if use_int:
                    row.append(random.randint(int(low), int(high)))
                else:
                    row.append(round(random.uniform(low, high), 2))
            data.append(row)
        return cls(data=data)

    @classmethod
    def from_file(cls, filename):
        data = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        row = [float(x) for x in line.split()]
                        data.append(row)
        except OSError as e:
            raise OSError(f"Не вдалося відкрити файл '{filename}': {e}")
        except ValueError as e:
            raise ValueError(f"Невірний формат числа у файлі '{filename}': {e}")
        if not data:
            return cls()
        return cls(data=data)

    def to_file(self, filename):
        try:
            with open(filename, 'w') as f:
                for row in self.data:
                    line = ' '.join(str(x) for x in row)
                    f.write(line + '\n')
        except OSError as e:
            raise OSError(f"Не вдалося записати матрицю у файл '{filename}': {e}")

    def get(self, i, j):
        if i < 0 or j < 0 or i >= self.rows or j >= self.cols:
            raise IndexError("Індекс елемента матриці поза межами.")
        return self.data[i][j]

    def set(self, i, j, value):
        if i < 0 or j < 0 or i >= self.rows or j >= self.cols:
            raise IndexError("Індекс елемента матриці поза межами.")
        self.data[i][j] = value

    def __add__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Розміри матриць не збігаються для додавання.")
        result_data = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] + other.data[i][j])
            result_data.append(row)
        return Matrix(data=result_data)

    def __sub__(self, other):
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("Розміри матриць не збігаються для віднімання.")
        result_data = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] - other.data[i][j])
            result_data.append(row)
        return Matrix(data=result_data)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            result_data = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(self.data[i][j] * other)
                result_data.append(row)
            return Matrix(data=result_data)

        if isinstance(other, Matrix):
            if self.cols != other.rows:
                raise ValueError(
                    f"Неможливо перемножити: кількість стовпців A ({self.cols}) "
                    f"не дорівнює кількості рядків B ({other.rows})."
                )
            result_data = []
            for i in range(self.rows):
                row = []
                for j in range(other.cols):
                    s = 0
                    for k in range(self.cols):
                        s += self.data[i][k] * other.data[k][j]
                    row.append(s)
                result_data.append(row)
            return Matrix(data=result_data)

        raise TypeError("Множення підтримується лише на число або матрицю.")

    def __rmul__(self, other):
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        raise TypeError("Непідтримуваний тип для множення.")

    def norm_max(self):
        max_val = 0
        for i in range(self.rows):
            for j in range(self.cols):
                val = abs(self.data[i][j])
                if val > max_val:
                    max_val = val
        return max_val

    def norm_frobenius(self):
        s = 0
        for i in range(self.rows):
            for j in range(self.cols):
                s += self.data[i][j] ** 2
        return math.sqrt(s)

    def copy(self):
        copied_data = [row[:] for row in self.data]
        return Matrix(data=copied_data)

    def __str__(self):
        if self.rows == 0 or self.cols == 0:
            return "[порожня матриця]"
        lines = []
        for row in self.data:
            formatted = [f"{x:10.4f}" for x in row]
            lines.append("  ".join(formatted))
        return '\n'.join(lines)

    def __repr__(self):
        return f"Matrix({self.rows}x{self.cols})"
