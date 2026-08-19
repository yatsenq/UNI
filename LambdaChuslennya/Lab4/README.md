# Чат-бот з накопиченням знань — Завдання 6

## Структура файлів

```
Main.hs              — головний код програми
QnA.txt              — база знань (питання + відповіді)
OpenQuestions.txt    — відкриті питання (бот задасть їх користувачу)
README.md            — цей файл
```

## Запуск

### Базовий варіант (один бот)
```bash
runhaskell Main.hs QnA.txt OpenQuestions.txt
```

### Розширений варіант (декілька ботів)
```bash
runhaskell Main.hs QnA.txt OpenQuestions.txt QnA1.txt OpenQuestions1.txt QnA2.txt OpenQuestions2.txt
```

## Формат файлів

### QnA.txt — база знань
```
Q: Hello
A: Hi

Q: How are you?
A: I'm fine, thank you!
```

### OpenQuestions.txt — відкриті питання
```
What is lazy evaluation?
How to read a file in Haskell?
```

## Логіка роботи

1. При запуску виводиться: `This bot was created by [Ваше ім'я]`
2. Бот чекає питання від користувача
3. Шукає відповідь у **всіх** QnA-файлах (основному + чужих)
4. Якщо не знає — каже `I don't know. Please ask me later.`  
   і дописує питання у `OpenQuestions` файли **інших** ботів
5. Бот сам ставить питання з `OpenQuestions.txt`:
   - задає перше питання зі свого файлу
   - видаляє його (щоб не повторювати)
   - зберігає відповідь у `QnA.txt`
6. Введення `exit` — завершує програму

## Технічні особливості коду

| Функція | Що робить |
|---|---|
| `parseArgs` | Розбирає аргументи CLI у конфіг |
| `readQnA` | Зчитує та парсить файл QnA |
| `findAnswer` | Шукає відповідь (без урахування регістру) |
| `findAnswerInFiles` | Шукає у кількох QnA-файлах послідовно |
| `readOpenQuestions` | Зчитує список відкритих питань |
| `removeFirstQuestion` | Видаляє перше питання з файлу |
| `appendQnA` | Дописує нову пару Q–A у файл |
| `mainLoop` | Головний нескінченний цикл діалогу |
| `askFromOpenQuestions` | Бот ставить питання і запам'ятовує відповідь |

## Сценарій колективного навчання

```
Студент 1:
  Ви: What is functor?
  Бот: I don't know. Please ask me later.
  → питання додається в OpenQuestions1.txt, OpenQuestions2.txt…

Студент 2 (інший бот читає OpenQuestions1.txt):
  Бот: What is functor?
  Ви: It's a type class for containers mappable via fmap
  → відповідь зберігається в QnA1.txt

Студент 1 знову:
  Ви: What is functor?
  Бот: It's a type class for containers mappable via fmap  ✓
```
