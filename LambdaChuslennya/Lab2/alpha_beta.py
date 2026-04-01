"""
Альфа-конгруентність та бета-редукція у безтиповому лямбда-численні.

Реалізовано дві функції:
  - alpha_congruent(t1, t2) — перевіряє альфа-конгруентність двох термів
  - simplify(t)             — виконує один крок бета-редукції редексу

Класи лямбда-виразів (Var, Term, Atm, App, Abs) з властивостями
var_map, rename, substitute взяті з файлу typeless_lambda_2.ipynb.
"""

import typing
import re


# Клас змінних

class Var(str):
    """Змінна (ім'я) лямбда-виразу.
    Зберігається у внутрішньому реєстрі, щоб гарантувати
    унікальність: одне ім'я — один об'єкт у пам'яті.
    """

    __registry: dict[str, 'Var'] = {}
    __pattern = re.compile(r"[a-z][a-zA-Z0-9_]*")

    @classmethod
    def checkname(cls, name: object) -> str:
        """Перевіряє, чи name є коректним ім'ям змінної."""
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

    @classmethod
    def _show_registry(cls) -> dict[str, 'Var']:
        return cls.__registry

    @classmethod
    def fresh(cls, base: str = "x") -> 'Var':
        """Генерує свіжу змінну, якої ще немає в реєстрі."""
        try:
            cls.checkname(base)
        except (TypeError, ValueError):
            base = "x"
        if base not in cls.__registry:
            return cls(base)
        i = 1
        while True:
            candidate = f"{base}_{i}"
            if candidate not in cls.__registry:
                return cls(candidate)
            i += 1


# Абстрактний клас терму

class Term:
    """Абстрактний клас — спільний предок для всіх видів термів."""
    __slots__ = ()

    def __str__(self) -> str:
        raise NotImplementedError

    @property
    def var_map(self) -> dict[str, int]:
        """Словник змінних терму: 1 — лише вільні, 2 — лише зв'язані, 3 — обидва."""
        raise NotImplementedError

    def rename(self, old_name: str, new_name: str) -> 'Term':
        """Перейменування вільних входжень old_name на new_name."""
        raise NotImplementedError

    def substitute(self, name: str, term: typing.Self) -> 'Term':
        """Підстановка term замість вільних входжень змінної name."""
        raise NotImplementedError


# Терм-атом

class Atm(Term):
    """Атомарний терм — відповідає одній змінній."""
    __slots__ = ('_name',)

    def __init__(self, name: str):
        self._name = Var.checkname(name)

    def __str__(self) -> str:
        return self._name

    @property
    def var_map(self) -> dict[str, int]:
        # Атом містить лише одне вільне входження своєї змінної
        return {self._name: 1}

    def rename(self, old_name: str, new_name: str) -> 'Atm':
        old_name = Var.checkname(old_name)
        new_name = Var.checkname(new_name)
        return Atm(new_name) if old_name == self._name else self

    def substitute(self, name: str, term: typing.Self) -> 'Atm':
        name = Var.checkname(name)
        if not isinstance(term, Term):
            raise TypeError("A variable can be substituted only with a term.")
        return term if name == self._name else self


# Терм-застосування

class App(Term):
    """Застосування: App(f, v) відповідає (f v)."""
    __slots__ = ('_fun', '_val')

    def __init__(self, f: Term, v: Term):
        if not (isinstance(f, Term) and isinstance(v, Term)):
            raise TypeError("Both arguments must be 'Term'")
        self._fun = f
        self._val = v

    def __str__(self) -> str:
        return f"({str(self._fun)} {str(self._val)})"

    @property
    def var_map(self) -> dict[str, int]:
        # Об'єднуємо словники піддерев; якщо статуси різні — ставимо 3
        temp = self._fun.var_map.copy()
        for x, status in self._val.var_map.items():
            temp[x] = 3 if x in temp and temp[x] != status else status
        return temp

    def rename(self, old_name: str, new_name: str) -> 'App':
        old_name = Var.checkname(old_name)
        new_name = Var.checkname(new_name)
        new_fun = self._fun.rename(old_name, new_name)
        new_val = self._val.rename(old_name, new_name)
        return App(new_fun, new_val)

    def substitute(self, name: str, term: typing.Self) -> typing.Self | None:
        name = Var.checkname(name)
        if not isinstance(term, Term):
            raise TypeError("A variable can be substituted only with a term.")
        new_fun = self._fun.substitute(name, term)
        new_val = self._val.substitute(name, term)
        return App(new_fun, new_val)


# Терм-абстракція

class Abs(Term):
    """Абстракція: Abs(x, t) відповідає (λ x. t)."""
    __slots__ = ('_name', '_body')

    def __init__(self, x: str, t: Term):
        if not isinstance(t, Term):
            raise TypeError("Type of 'body' must be 'Term'")
        self._body = t
        self._name = Var(x)

    def __str__(self) -> str:
        return f"(λ {self._name}. {self._body})"

    @property
    def var_map(self) -> dict[str, int]:
        # Змінна-аргумент абстракції завжди зв'язана (статус 2)
        temp = self._body.var_map.copy()
        if self._name in temp:
            temp[self._name] = 2
        return temp

    def rename(self, old_name: str, new_name: str) -> 'Abs':
        old_name = Var.checkname(old_name)
        new_name = Var.checkname(new_name)
        # Не перейменовуємо, якщо old_name або new_name збігається з іменем
        # зв'язаної змінної — це запобігає захопленню
        return (self if self._name in (old_name, new_name) else
                Abs(self._name, self._body.rename(old_name, new_name)))

    def substitute(self, name: str, term: typing.Self) -> 'Abs':
        name = Var.checkname(name)
        if not isinstance(term, Term):
            raise TypeError("A variable can be substituted only with a term.")
        status = self.var_map.get(name)
        # Якщо name не входить у терм або name — сама зв'язана змінна
        if status is None or name == self._name:
            return self
        status = term.var_map.get(self._name)
        # Якщо змінна self._name не входить вільно у term — підстановка безпечна
        if status is None or status & 1 == 0:
            return Abs(self._name, self._body.substitute(name, term))
        # Інакше — потрібна альфа-конверсія перед підстановкою
        new_name = Var.fresh(self._name)
        new_body = self._body.rename(self._name, new_name)
        new_body = self._body if new_body is None else new_body
        return Abs(new_name, new_body.substitute(name, term))


# Альфа-конгруентність

def alpha_congruent(t1: Term, t2: Term) -> bool:
    """Перевіряє, чи два терми є альфа-конгруентними.

    Два терми альфа-конгруентні, якщо вони відрізняються лише
    іменами зв'язаних змінних. Наприклад:
        λx.x  ≡α  λy.y      (True)
        λx.λy.x  ≡α  λa.λb.a  (True)
        λx.y  ≡α  λx.z      (False — y та z вільні й різні)

    Реалізація: порівнюємо структуру термів рекурсивно,
    відстежуючи глибину зв'язування кожної змінної.
    Якщо дві зв'язані змінні були введені на однаковій
    глибині — вони відповідають одна одній.
    """

    def helper(t1: Term, t2: Term,
               env1: dict[str, int], env2: dict[str, int],
               depth: int) -> bool:
        """Рекурсивне порівняння з контекстами зв'язування.
        env1, env2 — словники, що відображають ім'я змінної
        на глибину, де вона була зв'язана (для t1 та t2 відповідно).
        depth — поточна глибина вкладеності абстракцій.
        """

        # Атом ↔ Атом
        if isinstance(t1, Atm) and isinstance(t2, Atm):
            bound1 = env1.get(t1._name)
            bound2 = env2.get(t2._name)
            if bound1 is not None and bound2 is not None:
                # Обидві зв'язані — порівнюємо глибини зв'язування
                return bound1 == bound2
            if bound1 is None and bound2 is None:
                # Обидві вільні — порівнюємо імена напряму
                return t1._name == t2._name
            # Одна зв'язана, інша вільна — не конгруентні
            return False

        # Застосування ↔ Застосування
        if isinstance(t1, App) and isinstance(t2, App):
            return (helper(t1._fun, t2._fun, env1, env2, depth) and
                    helper(t1._val, t2._val, env1, env2, depth))

        # Абстракція ↔ Абстракція
        if isinstance(t1, Abs) and isinstance(t2, Abs):
            # Зв'язані змінні отримують однакову глибину
            new_env1 = {**env1, t1._name: depth}
            new_env2 = {**env2, t2._name: depth}
            return helper(t1._body, t2._body, new_env1, new_env2, depth + 1)

        # Різні види термів — не конгруентні
        return False

    return helper(t1, t2, {}, {}, 0)


# Бета-редукція (один крок)

def simplify(t: App) -> Term:
    """Виконує один крок бета-редукції, якщо t є редексом.

    Редекс — це терм виду (λ x. body) val.
    Бета-редукція: (λ x. body) val  →β  body[x := val]
    тобто підставляємо val замість усіх вільних входжень x у body.

    Якщо t не є редексом (його _fun не є абстракцією),
    повертається сам t без змін.
    """
    # Перевіряємо, що t — це застосування
    if not isinstance(t, App):
        raise TypeError("Аргумент має бути термом-застосуванням (App)")

    # Перевіряємо, чи ліва частина є абстракцією (λ x. body)
    if isinstance(t._fun, Abs):
        # t = (λ x. body) val — це редекс
        # Виконуємо підстановку: body[x := val]
        x = t._fun._name       # ім'я зв'язаної змінної
        body = t._fun._body    # тіло абстракції
        val = t._val            # аргумент застосування
        return body.substitute(x, val)

    # Не редекс — повертаємо без змін
    return t


# Демонстрація

if __name__ == "__main__":

    # Альфа-конгруентність 
    print("Альфа-конгруентність\n")

    # λx.x та λy.y — конгруентні (відрізняються лише ім'ям зв'язаної змінної)
    t1 = Abs('x', Atm('x'))
    t2 = Abs('y', Atm('y'))
    print(f"t1 = {t1}")
    print(f"t2 = {t2}")
    print(f"alpha_congruent(t1, t2) = {alpha_congruent(t1, t2)}")  # True
    print()

    # λx.λy.x та λa.λb.a — конгруентні
    t3 = Abs('x', Abs('y', Atm('x')))
    t4 = Abs('a', Abs('b', Atm('a')))
    print(f"t3 = {t3}")
    print(f"t4 = {t4}")
    print(f"alpha_congruent(t3, t4) = {alpha_congruent(t3, t4)}")  # True
    print()

    # λx.y та λx.z — НЕ конгруентні (y та z — різні вільні змінні)
    t5 = Abs('x', Atm('y'))
    t6 = Abs('x', Atm('z'))
    print(f"t5 = {t5}")
    print(f"t6 = {t6}")
    print(f"alpha_congruent(t5, t6) = {alpha_congruent(t5, t6)}")  # False
    print()

    # λx.λy.x та λx.λy.y — НЕ конгруентні (різна структура зв'язування)
    t7 = Abs('x', Abs('y', Atm('x')))
    t8 = Abs('x', Abs('y', Atm('y')))
    print(f"t7 = {t7}")
    print(f"t8 = {t8}")
    print(f"alpha_congruent(t7, t8) = {alpha_congruent(t7, t8)}")  # False
    print()

    # Бета-редукція
    print("=== Бета-редукція (simplify) ===\n")

    # Редекс: (λx.x) y  →β  y
    redex1 = App(Abs('x', Atm('x')), Atm('y'))
    print(f"t = {redex1}")
    print(f"simplify(t) = {simplify(redex1)}")  # y
    print()

    # Редекс: (λx.(x z)) y  →β  (y z)
    redex2 = App(Abs('x', App(Atm('x'), Atm('z'))), Atm('y'))
    print(f"t = {redex2}")
    print(f"simplify(t) = {simplify(redex2)}")  # (y z)
    print()

    # Не редекс: (x y) — fun не є абстракцією
    non_redex = App(Atm('x'), Atm('y'))
    print(f"t = {non_redex}")
    print(f"simplify(t) = {simplify(non_redex)}")  # (x y) без змін
    print()

    # Редекс з підстановкою: (λx.λy.x) z  →β  λy.z
    redex3 = App(Abs('x', Abs('y', Atm('x'))), Atm('z'))
    print(f"t = {redex3}")
    print(f"simplify(t) = {simplify(redex3)}")  # (λ y. z)
