from matrix import Matrix
from vector import Vector


class BandMatrixVector:
    def __init__(self, n, lower_bw, upper_bw, values):
        if n <= 0:
            raise ValueError("Розмір матриці n має бути додатним.")
        if lower_bw < 0 or upper_bw < 0:
            raise ValueError("Ширини стрічки мають бути невід'ємними.")

        self.n = n
        self.lower_bw = lower_bw
        self.upper_bw = upper_bw

        self.row_offsets = []
        expected = 0
        for i in range(n):
            self.row_offsets.append(expected)
            left = max(0, i - lower_bw)
            right = min(n - 1, i + upper_bw)
            expected += right - left + 1

        if len(values) != expected:
            raise ValueError(
                f"Невірна довжина вектора стрічкової матриці: очікується {expected}, отримано {len(values)}."
            )

        self.values = [float(v) for v in values]

    @classmethod
    def from_dense(cls, matrix, lower_bw, upper_bw):
        if matrix.rows != matrix.cols:
            raise ValueError("Матриця для стрічкового методу має бути квадратною.")

        n = matrix.rows
        values = []
        tol = 1e-12

        for i in range(n):
            for j in range(n):
                val = matrix.get(i, j)
                in_band = (i - lower_bw) <= j <= (i + upper_bw)
                if not in_band and abs(val) > tol:
                    raise ValueError(
                        "Матриця містить ненульові елементи поза заданою стрічкою. "
                        "Перевірте lower/upper bandwidth."
                    )

            left = max(0, i - lower_bw)
            right = min(n - 1, i + upper_bw)
            for j in range(left, right + 1):
                values.append(matrix.get(i, j))

        return cls(n=n, lower_bw=lower_bw, upper_bw=upper_bw, values=values)

    def _row_start(self, i):
        return max(0, i - self.lower_bw)

    def _row_end(self, i):
        return min(self.n - 1, i + self.upper_bw)

    def _index(self, i, j):
        left = self._row_start(i)
        right = self._row_end(i)
        if j < left or j > right:
            raise IndexError("Індекс поза стрічкою.")
        return self.row_offsets[i] + (j - left)

    def get(self, i, j):
        if i < 0 or i >= self.n or j < 0 or j >= self.n:
            raise IndexError("Індекс елемента матриці поза межами.")
        left = self._row_start(i)
        right = self._row_end(i)
        if j < left or j > right:
            return 0.0
        return self.values[self._index(i, j)]

    def set(self, i, j, value):
        if i < 0 or i >= self.n or j < 0 or j >= self.n:
            raise IndexError("Індекс елемента матриці поза межами.")
        left = self._row_start(i)
        right = self._row_end(i)
        if j < left or j > right:
            if abs(value) > 1e-12:
                raise ValueError("Неможливо записати ненульовий елемент поза стрічкою.")
            return
        self.values[self._index(i, j)] = float(value)

    def to_dense_matrix(self):
        data = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            left = self._row_start(i)
            right = self._row_end(i)
            for j in range(left, right + 1):
                data[i][j] = self.get(i, j)
        return Matrix(data=data)


class BandGaussianSolver:
    def __init__(self, band_matrix, b):
        if band_matrix.n != b.size:
            raise ValueError("Розмір вектора b не відповідає матриці A.")
        self.A = band_matrix
        self.b = b.copy()

    def solve(self, eps=1e-12):
        n = self.A.n
        A = BandMatrixVector(
            n=self.A.n,
            lower_bw=self.A.lower_bw,
            upper_bw=self.A.upper_bw,
            values=self.A.values[:],
        )
        rhs = self.b.to_list()

        for k in range(n):
            pivot = A.get(k, k)
            if abs(pivot) < eps:
                raise ValueError(
                    "Нульовий або занадто малий півот. "
                    "Для цього варіанта стрічкового Гауса потрібна невироджена матриця з ненульовою діагоналлю."
                )

            i_end = min(n - 1, k + A.lower_bw)
            for i in range(k + 1, i_end + 1):
                aik = A.get(i, k)
                if abs(aik) < eps:
                    continue

                factor = aik / pivot
                A.set(i, k, 0.0)

                j_end = min(n - 1, k + A.upper_bw)
                for j in range(k + 1, j_end + 1):
                    new_val = A.get(i, j) - factor * A.get(k, j)
                    A.set(i, j, new_val)

                rhs[i] -= factor * rhs[k]

        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            j_end = min(n - 1, i + A.upper_bw)
            s = rhs[i]
            for j in range(i + 1, j_end + 1):
                s -= A.get(i, j) * x[j]

            diag = A.get(i, i)
            if abs(diag) < eps:
                raise ValueError("Нульовий діагональний елемент під час зворотного ходу.")
            x[i] = s / diag

        x_vec = Vector(data=x)
        dense_a = self.A.to_dense_matrix()
        ax_matrix = dense_a * x_vec.matrix
        ax_vec = Vector(data=[ax_matrix.get(i, 0) for i in range(ax_matrix.rows)])
        residual = ax_vec - self.b

        return {
            "x": x_vec,
            "residual": residual,
            "residual_norm": residual.norm(),
            "storage_vector": self.A.values[:],
        }
