from matrix import Matrix
from vector import Vector


class SLAE:
    def __init__(self, A=None, b=None):
        try:
            if A is not None:
                self.A = A.copy()
            else:
                self.A = Matrix()

            if b is not None:
                self.b = b.copy()
            else:
                self.b = Vector()
        except Exception as e:
            raise TypeError(f"Не вдалося ініціалізувати СЛАР: {e}")

        self.A_orig = self.A.copy()
        self.b_orig = self.b.copy()

        self.x = Vector()
        self.solution_status = "not_solved"
        self.dec_matrix = Matrix()
        self.dec_error = None

    def _validate_system(self):
        n = self.A.rows
        if n == 0:
            raise ValueError("Матриця порожня, нема чого розв'язувати.")
        if n != self.A.cols:
            raise ValueError("Матриця повинна бути квадратною для методу Гауса.")
        if n != self.b.size:
            raise ValueError("Розмір вектора b не відповідає розміру матриці A.")
        return n

    def _build_augmented(self):
        try:
            n = self.A.rows
            aug_data = []
            for i in range(n):
                row = []
                for j in range(n):
                    row.append(self.A.get(i, j))
                row.append(self.b.get(i))
                aug_data.append(row)
            return aug_data
        except Exception as e:
            raise ValueError(f"Не вдалося сформувати розширену матрицю [A|b]: {e}")

    # def _identity_list(self, n):
    #     return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    def _lu_decompose(self, eps=1e-12):
        # діагональ = 1 / pivot,
        # під діагоналлю = -(a_ik / pivot), (множники f)
        # над діагоналлю = елементи нормованого рядка після ділення на pivot. 
        try:
            n = self.A.rows
            u = [row[:] for row in self.A.data]
            dec_a = [[0.0] * n for _ in range(n)]

            for k in range(n):
                pivot = u[k][k]
                if abs(pivot) < eps:
                    raise ValueError("Нульовий ведучий елемент!")

                dec_a[k][k] = 1.0 / pivot

                for i in range(k + 1, n):
                    multiplier = -(u[i][k] / pivot)
                    dec_a[i][k] = multiplier

                    for j in range(k, n):
                        if j == k:
                            u[i][j] = 0.0
                        else:
                            u[i][j] += multiplier * u[k][j]

                for j in range(k, n):
                    u[k][j] /= pivot

                for j in range(k + 1, n):
                    dec_a[k][j] = u[k][j]

            self.dec_matrix = Matrix(data=dec_a)
            self.dec_error = None
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Помилка декомпозиції матриці: {e}")

    def _solve_core(self, eps=1e-12):
        n = self._validate_system()

        aug = self._build_augmented()
        pivot_cols = []
        row = 0

        for col in range(n):
            pivot_row = row
            max_val = abs(aug[row][col]) if row < n else 0.0
            for i in range(row + 1, n):
                val = abs(aug[i][col])
                if val > max_val:
                    max_val = val
                    pivot_row = i

            if max_val < eps:
                continue

            if pivot_row != row:
                aug[row], aug[pivot_row] = aug[pivot_row], aug[row]

            pivot_cols.append(col)
            for i in range(row + 1, n):
                factor = aug[i][col] / aug[row][col]
                for j in range(col, n + 1):
                    aug[i][j] -= factor * aug[row][j]
            row += 1
            if row == n:
                break

        rank_a = 0
        rank_ab = 0
        inconsistent = False
        for i in range(n):
            non_zero_a = any(abs(aug[i][j]) >= eps for j in range(n))
            non_zero_ab = non_zero_a or abs(aug[i][n]) >= eps
            if non_zero_a:
                rank_a += 1
            if non_zero_ab:
                rank_ab += 1
            if (not non_zero_a) and abs(aug[i][n]) >= eps:
                inconsistent = True #0 = 5

        if inconsistent or rank_a < rank_ab:
            self.x = Vector()
            self.solution_status = "no_solution"
            self.dec_matrix = Matrix()
            self.dec_error = None
            return {
                "status": "no_solution",
                "message": "Система несумісна: розв'язків немає.",
                "rank_a": rank_a,
                "rank_ab": rank_ab,
            }

        if rank_a < n:
            self.x = Vector()
            self.solution_status = "infinite_solutions"
            self.dec_matrix = Matrix()
            self.dec_error = None
            return {
                "status": "infinite_solutions",
                "message": "Система сумісна, але має безліч розв'язків.",
                "rank_a": rank_a,
                "rank_ab": rank_ab,
            }

        x_data = [0.0] * n
        for i in range(n - 1, -1, -1):
            s = aug[i][n]
            for j in range(i + 1, n):
                s -= aug[i][j] * x_data[j]
            if abs(aug[i][i]) < eps:
                raise ValueError("Неможливо завершити зворотний хід через нульовий півот.")
            x_data[i] = s / aug[i][i]

        try:
            self._lu_decompose(eps=eps)
        except Exception as e:
            self.dec_matrix = Matrix()
            self.dec_error = str(e)

        self.x = Vector(data=x_data)
        self.solution_status = "unique_solution"
        return {
            "status": "unique_solution",
            "message": "Система має єдиний розв'язок.",
            "rank_a": rank_a,
            "rank_ab": rank_ab,
            "x": self.x,
        }

    def solve_gauss_general(self, eps=1e-12):
        try:
            return self._solve_core(eps=eps)
        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Невідома помилка при розв'язуванні СЛАР: {e}")

    # def solve_gauss(self):
    #     try:
    #         result = self.solve_gauss_general()
    #         if result["status"] != "unique_solution":
    #             raise ValueError(result["message"])
    #         return result["x"]
    #     except ValueError:
    #         raise
    #     except Exception as e:
    #         raise RuntimeError(f"Помилка solve_gauss: {e}")

    def inverse_gauss_jordan(self):
        n = self.A_orig.rows
        if self.A_orig.cols != n:
            raise ValueError("Обернена матриця існує лише для квадратних матриць.")

        aug = [
            self.A_orig.data[i][:] + [1.0 if i == j else 0.0 for j in range(n)]
            for i in range(n)
        ]

        for k in range(n):
            max_row = max(range(k, n), key=lambda r: abs(aug[r][k]))
            if abs(aug[max_row][k]) < 1e-12:
                raise ValueError("Матриця вироджена - обернена не існує.")
            aug[k], aug[max_row] = aug[max_row], aug[k]

            pivot = aug[k][k]
            aug[k] = [v / pivot for v in aug[k]]

            for i in range(n):
                if i != k:
                    factor = aug[i][k]
                    aug[i] = [aug[i][j] - factor * aug[k][j] for j in range(2 * n)]

        inv_data = [aug[i][n:] for i in range(n)]
        return Matrix(data=inv_data)

    def decomposition_text(self):
        if self.dec_matrix.rows == 0:
            if self.dec_error:
                return f"Декомпозицію не обчислено: {self.dec_error}"
            return "Декомпонована матриця ще не обчислена."
        text = "Декомпонована матриця:\n"
        text += "  діагональ — 1/pivot\n"
        text += "  нижній трикутник — від'ємні множники занулення\n"
        text += "  верхній трикутник — нормовані рядки (ділені на pivot)\n\n"
        text += f"{self.dec_matrix}"
        return text

    def residual(self):
        if self.x.size == 0:
            raise ValueError("Спочатку потрібно розв'язати систему.")

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
        if self.dec_matrix.rows > 0:
            result += "Декомпонована матриця обчислена.\n"
        return result
