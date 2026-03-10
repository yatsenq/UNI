from matrix import Matrix
import random
import math


class Vector:
    def __init__(self, size=0, data=None):
        if data is not None:
            try:
                matrix_data = [[x] for x in data]
                self.matrix = Matrix(data=matrix_data)
            except Exception as e:
                raise ValueError(f"Помилка створення вектора з даних: {e}")
        else:
            if size < 0:
                raise ValueError("Розмір вектора не може бути від'ємним.")
            self.matrix = Matrix(rows=size, cols=1)

    @property
    def size(self): 
        return self.matrix.rows

    def get(self, i):
        if i < 0 or i >= self.size:
            raise IndexError("Індекс елемента вектора поза межами.")
        return self.matrix.get(i, 0)

    def set(self, i, value):
        if i < 0 or i >= self.size:
            raise IndexError("Індекс елемента вектора поза межами.")
        self.matrix.set(i, 0, value)

    @classmethod
    def random_vector(cls, size, low=-10, high=10, use_int=False):
        if size < 0:
            raise ValueError("Розмір вектора не може бути від'ємним.")
        if low > high:
            raise ValueError("Нижня межа діапазону не може бути більшою за верхню.")
        if use_int:
            data = [random.randint(int(low), int(high)) for _ in range(size)]
        else:
            data = [round(random.uniform(low, high), 2) for _ in range(size)]
        return cls(data=data)

    @classmethod
    def from_file(cls, filename):
        data = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data.append(float(line))
        except OSError as e:
            raise OSError(f"Не вдалося відкрити файл '{filename}': {e}")
        except ValueError as e:
            raise ValueError(f"Невірний формат числа у файлі '{filename}': {e}")
        return cls(data=data)

    def to_file(self, filename):
        try:
            with open(filename, 'w') as f:
                for i in range(self.size):
                    f.write(str(self.get(i)) + '\n')
        except OSError as e:
            raise OSError(f"Не вдалося записати вектор у файл '{filename}': {e}")

    def __add__(self, other):
        result_matrix = self.matrix + other.matrix
        data = [result_matrix.get(i, 0) for i in range(result_matrix.rows)]
        return Vector(data=data)

    def __sub__(self, other):
        result_matrix = self.matrix - other.matrix
        data = [result_matrix.get(i, 0) for i in range(result_matrix.rows)]
        return Vector(data=data)

    def __mul__(self, scalar): # vector * a
        result_matrix = self.matrix * scalar
        data = [result_matrix.get(i, 0) for i in range(result_matrix.rows)]
        return Vector(data=data)

    def __rmul__(self, scalar): # a * vector
        return self.__mul__(scalar)

    def norm(self):
        s = 0
        for i in range(self.size):
            s += self.get(i) ** 2
        return math.sqrt(s)

    def to_list(self):
        return [self.get(i) for i in range(self.size)]

    def copy(self):
        return Vector(data=self.to_list())

    def __str__(self):
        if self.size == 0:
            return "[порожній вектор]"
        values = [f"{self.get(i):.4f}" for i in range(self.size)]
        return "[ " + ", ".join(values) + " ]"

    def __repr__(self):
        return f"Vector(size={self.size})"
