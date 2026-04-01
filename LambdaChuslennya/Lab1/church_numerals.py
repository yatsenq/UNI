"""
Побудова нумералів Черча у безтиповому лямбда-численні.

Нумерали Черча — це спосіб кодування натуральних чисел
як лямбда-виразів. Число n представляється функцією двох
аргументів (x, y), яка застосовує x до y рівно n разів.

Визначення:
    [0]   = λ x. λ y. y
    [n+1] = λ x. λ y. x ([n] x y)

Класами лямбда-виразів (Var, Term, Atm, App, Abs) скористався
з файлу typeless_lambda_1.ipynb.
"""

import re


# Класи лямбда-виразів

class Var(str):
    """Клас змінних (імен).
    Кожна змінна — це рядок спеціального формату,
    що зберігається у внутрішньому реєстрі для унікальності.
    """

    __registry: dict[str, 'Var'] = {}              # реєстр використаних імен
    __pattern = re.compile(r"[a-z][a-zA-Z0-9_]*")  # шаблон імені змінної

    @classmethod
    def checkname(cls, name: object) -> str:
        """Перевіряє, чи може name бути ім'ям змінної."""
        if not isinstance(name, str):
            raise TypeError(
                f"Type of 'name' must be 'str' but obtained {type(name)}")
        if not cls.__pattern.fullmatch(name):
            raise ValueError("Invalid 'name' format")
        return name

    def __new__(cls, name: str) -> 'Var':
        """Створює або повертає з реєстру змінну з ім'ям name."""
        if cls.checkname(name) not in cls.__registry:
            cls.__registry[name] = super().__new__(cls, name)
        return cls.__registry[name]


class Term:
    """Абстрактний клас — спільний предок для всіх видів термів."""
    __slots__ = ()

    def __str__(self) -> str:
        raise NotImplementedError


class Atm(Term):
    """Терм-атом: найпростіший лямбда-вираз, що відповідає змінній."""
    __slots__ = ('_name',)

    def __init__(self, name: str):
        self._name = Var.checkname(name)

    def __str__(self) -> str:
        return self._name


class App(Term):
    """Терм-застосування: результат застосування одного терму до іншого."""
    __slots__ = ('_fun', '_val')

    def __init__(self, f: Term, v: Term):
        if not (isinstance(f, Term) and isinstance(v, Term)):
            raise TypeError("Both arguments must be 'Term'")
        self._fun = f
        self._val = v

    def __str__(self) -> str:
        return f"({str(self._fun)} {str(self._val)})"


class Abs(Term):
    """Терм-абстракція: лямбда-функція з аргументом та тілом."""
    __slots__ = ('_name', '_body')

    def __init__(self, x: str, t: Term):
        if not isinstance(t, Term):
            raise TypeError("Type of 'body' must be 'Term'")
        self._body = t
        self._name = Var(x)

    def __str__(self) -> str:
        return f"(λ {self._name}. {self._body})"


# Побудова нумералів Черча

def church(n: int) -> Term:
    """Повертає n-ий нумерал Черча як лямбда-вираз.

    Нумерали Черча кодують натуральні числа в лямбда-численні.
    Число n представляється функцією двох аргументів (x, y),
    яка застосовує x до y рівно n разів:
        [0]   = λ x. λ y. y
        [n+1] = λ x. λ y. x ([n] x y)

    Аргумент n — невід'ємне ціле число.
    """
    # Захист від некоректного вводу: від'ємні числа не мають нумералів
    if n < 0:
        raise ValueError("n must be a non-negative integer")

    # Базовий випадок: [0] = λ x. λ y. y
    # Нуль — це функція, яка ігнорує x і просто повертає y,
    # тобто x застосовується 0 разів
    if n == 0:
        return Abs('x', Abs('y', Atm('y')))
    else:
        # Рекурсивний крок: будуємо попередній нумерал [n-1]
        prev = church(n - 1)

        # Конструюємо аплікацію ([n-1] x y):
        # prev застосовується спочатку до x, потім результат — до y
        applied_prev = App(App(prev, Atm('x')), Atm('y'))

        # Огортаємо ще одним застосуванням x зовні:
        # x ([n-1] x y) — це додає одне застосування x
        body = App(Atm('x'), applied_prev)

        # Фінальна абстракція: λ x. λ y. body
        return Abs('x', Abs('y', body))


# Головна частина: друк перших 10 нумералів

if __name__ == "__main__":
    # Побудова та друк нумералів Черча [0], [1], ..., [9]
    for i in range(10):
        print(f"[{i}] = {church(i)}")
