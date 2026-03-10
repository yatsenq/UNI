from matrix import Matrix
import random
import math


class Vector:
    """
    Клас Вектор — обгортка над Matrix розміру n x 1.
    Вектор зберігається як матриця-стовпець.
    """

    def __init__(self, size=0, data=None):
        """
        Конструктор вектора.
        - Без параметрів: порожній вектор
        - З розміром: нульовий вектор
        - З даними: вектор з переданого списку
        """
        if data is not None:
            # data — це звичайний список чисел [1, 2, 3]
            matrix_data = [[x] for x in data]
            self.matrix = Matrix(data=matrix_data)
        else:
            self.matrix = Matrix(rows=size, cols=1)

    @property
    def size(self):
        """Розмір вектора (кількість елементів)."""
        return self.matrix.rows

    def get(self, i):
        """Повертає i-й елемент вектора."""
        return self.matrix.get(i, 0)

    def set(self, i, value):
        """Встановлює i-й елемент вектора."""
        self.matrix.set(i, 0, value)

    @classmethod
    def random_vector(cls, size, low=-10, high=10, use_int=False):
        """Створює вектор з випадковими числами у діапазоні [low, high]."""
        if use_int:
            data = [random.randint(int(low), int(high)) for _ in range(size)]
        else:
            data = [round(random.uniform(low, high), 2) for _ in range(size)]
        return cls(data=data)

    @classmethod
    def from_file(cls, filename):
        """
        Зчитує вектор з файлу.
        Формат: кожний рядок — один елемент вектора.
        """
        data = []
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    data.append(float(line))
        return cls(data=data)

    def to_file(self, filename):
        """Записує вектор у файл."""
        with open(filename, 'w') as f:
            for i in range(self.size):
                f.write(str(self.get(i)) + '\n')

    def __add__(self, other):
        """Додавання векторів."""
        result_matrix = self.matrix + other.matrix
        data = [result_matrix.get(i, 0) for i in range(result_matrix.rows)]
        return Vector(data=data)

    def __sub__(self, other):
        """Віднімання векторів."""
        result_matrix = self.matrix - other.matrix
        data = [result_matrix.get(i, 0) for i in range(result_matrix.rows)]
        return Vector(data=data)

    def __mul__(self, scalar):
        """Множення вектора на число."""
        result_matrix = self.matrix * scalar
        data = [result_matrix.get(i, 0) for i in range(result_matrix.rows)]
        return Vector(data=data)

    def __rmul__(self, scalar):
        """Множення числа на вектор."""
        return self.__mul__(scalar)

    def norm(self):
        """Евклідова норма вектора."""
        s = 0
        for i in range(self.size):
            s += self.get(i) ** 2
        return math.sqrt(s)

    def to_list(self):
        """Повертає вектор як звичайний список."""
        return [self.get(i) for i in range(self.size)]

    def copy(self):
        """Повертає копію вектора."""
        return Vector(data=self.to_list())

    def __str__(self):
        """Рядкове представлення вектора."""
        if self.size == 0:
            return "[порожній вектор]"
        values = [f"{self.get(i):.4f}" for i in range(self.size)]
        return "[ " + ", ".join(values) + " ]"

    def __repr__(self):
        return f"Vector(size={self.size})"
