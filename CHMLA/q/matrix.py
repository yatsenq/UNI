import random
import math


class Matrix:
    """Клас для представлення прямокутної матриці розміру n x m."""

    def __init__(self, rows=0, cols=0, data=None):
        """
        Конструктор матриці.
        - Без параметрів: порожня матриця 0x0
        - З розмірами: нульова матриця rows x cols
        - З даними: матриця з переданих даних (список списків)
        """
        if data is not None:
            self.rows = len(data)
            self.cols = len(data[0]) if self.rows > 0 else 0
            # Копіюємо дані, щоб не було спільних посилань
            self.data = [row[:] for row in data]
        else:
            self.rows = rows
            self.cols = cols
            self.data = [[0.0] * cols for _ in range(rows)]

    @classmethod
    def random_matrix(cls, rows, cols, low=-10, high=10, use_int=False):
        """Створює матрицю з випадковими числами у діапазоні [low, high]."""
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
        """
        Зчитує матрицю з файлу.
        Формат файлу: кожний рядок — рядок матриці, елементи через пробіл.
        """
        data = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    row = [float(x) for x in line.split()]
                    data.append(row)
        if not data:
            return cls()
        return cls(data=data)

    def to_file(self, filename):
        """Записує матрицю у файл з вказаним ім'ям."""
        with open(filename, 'w') as f:
            for row in self.data:
                line = ' '.join(str(x) for x in row)
                f.write(line + '\n')

    def get(self, i, j):
        """Повертає елемент матриці [i][j]."""
        return self.data[i][j]

    def set(self, i, j, value):
        """Встановлює значення елемента матриці [i][j]."""
        self.data[i][j] = value

    def __add__(self, other):
        """Додавання матриць: A + B."""
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
        """Віднімання матриць: A - B."""
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
        """
        Множення:
        - Матриця * число (скаляр)
        - Матриця * Матриця
        """
        # Множення на число
        if isinstance(other, (int, float)):
            result_data = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(self.data[i][j] * other)
                result_data.append(row)
            return Matrix(data=result_data)

        # Множення матриць
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
        """Множення числа на матрицю: k * A."""
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        raise TypeError("Непідтримуваний тип для множення.")

    def norm_max(self):
        """Максимальна норма — максимум модулів усіх елементів."""
        max_val = 0
        for i in range(self.rows):
            for j in range(self.cols):
                val = abs(self.data[i][j])
                if val > max_val:
                    max_val = val
        return max_val

    def norm_frobenius(self):
        """Евклідова (Фробеніусова) норма матриці."""
        s = 0
        for i in range(self.rows):
            for j in range(self.cols):
                s += self.data[i][j] ** 2
        return math.sqrt(s)

    def copy(self):
        """Повертає копію матриці."""
        return Matrix(data=self.data)

    def __str__(self):
        """Рядкове представлення матриці для виводу."""
        if self.rows == 0 or self.cols == 0:
            return "[порожня матриця]"
        lines = []
        for row in self.data:
            formatted = [f"{x:10.4f}" for x in row]
            lines.append("  ".join(formatted))
        return '\n'.join(lines)

    def __repr__(self):
        return f"Matrix({self.rows}x{self.cols})"
