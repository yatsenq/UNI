"""
ЧМЛА — Завдання 1: Класи Матриця, Вектор, СЛАР
Запуск графічного інтерфейсу.
"""
import tkinter as tk
from gui import App


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
