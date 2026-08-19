-- ============================================================
-- Модуль: Main
-- Опис: Інтерактивний чат-бот з накопиченням знань
--
-- Запуск (базовий):
--   runhaskell Main.hs QnA.txt OpenQuestions.txt
--
-- Запуск (розширений, декілька ботів):
--   runhaskell Main.hs QnA.txt OpenQuestions.txt QnA1.txt OpenQuestions1.txt ...
--
-- Автор: [Vladyslav Yatsenko]
-- ============================================================

module Main where

-- Імпорт стандартних бібліотек
import System.Environment  (getArgs)          -- для читання аргументів командного рядка
import System.IO           (hSetBuffering, hSetEncoding, stdout, stdin, stderr,
                            BufferMode(..), utf8)
                            -- utf8 потрібен для коректного відображення
                            -- кирилиці на Windows (PowerShell/cmd)
import System.Directory    (doesFileExist)     -- перевірка існування файлу
import Data.List           (isPrefixOf, intercalate, find)
import Data.Char           (toLower, isSpace)  -- для нормалізації тексту
import Control.Monad       (when, unless)      -- умовне виконання IO-дій
import System.Exit         (exitSuccess)       -- для завершення програми

-- ============================================================
-- ТИПИ ДАНИХ
-- ============================================================

-- | Пара «питання – відповідь» для зберігання знань бота
data QnAPair = QnAPair
  { question :: String   -- питання
  , answer   :: String   -- відповідь
  } deriving (Show)

-- | Конфігурація: шляхи до файлів поточного бота і «чужих» ботів
data Config = Config
  { mainQnA        :: FilePath    -- головний файл знань (QnA.txt)
  , mainOpenQ      :: FilePath    -- головний файл відкритих питань (OpenQuestions.txt)
  , otherQnAs      :: [FilePath]  -- файли знань інших ботів (QnA1.txt, QnA2.txt …)
  , otherOpenQs    :: [FilePath]  -- файли відкритих питань інших ботів
  } deriving (Show)

-- ============================================================
-- ТОЧКА ВХОДУ
-- ============================================================

main :: IO ()
main = do
  -- Встановлюємо UTF-8 для всіх потоків вводу/виводу.
  -- Це критично на Windows, де PowerShell/cmd за замовчуванням
  -- використовують кодування CP1251 або CP866, які не підтримують
  -- кирилицю в Haskell-рядках. Без цього програма падає з помилкою
  -- "cannot encode character".
  hSetEncoding stdout utf8
  hSetEncoding stdin  utf8
  hSetEncoding stderr utf8

  -- Вимикаємо буферизацію виводу, щоб відповідь з'являлась одразу
  hSetBuffering stdout NoBuffering

  -- Отримуємо аргументи командного рядка
  args <- getArgs

  -- Перевіряємо мінімальну кількість аргументів
  if length args < 2
    then putStrLn "Usage: runhaskell Main.hs QnA.txt OpenQuestions.txt [QnA1.txt OpenQuestions1.txt ...]"
    else do
      -- Розбираємо аргументи на конфігурацію
      let cfg = parseArgs args

      -- Перевіряємо/створюємо всі необхідні файли
      ensureFilesExist cfg

      -- Виводимо привітання від бота
      putStrLn "This bot was created by [Vladyslav Yatsenko]"
      putStrLn "Type your question or 'exit' to quit."
      putStrLn (replicate 50 '-')

      -- Запускаємо головний цикл діалогу
      mainLoop cfg

-- ============================================================
-- РОЗБІР АРГУМЕНТІВ
-- ============================================================

-- | Перетворює список аргументів на конфігурацію.
--   Перші два аргументи — файли поточного бота.
--   Далі йдуть пари (QnAn.txt, OpenQuestionsN.txt) для інших ботів.
parseArgs :: [String] -> Config
parseArgs (qna:oq:rest) = Config
  { mainQnA    = qna
  , mainOpenQ  = oq
  , otherQnAs  = extractEvens rest   -- парні індекси (0, 2, 4…) — QnA-файли
  , otherOpenQs = extractOdds rest   -- непарні індекси (1, 3, 5…) — OpenQ-файли
  }
  where
    -- Беремо елементи з парними позиціями (0, 2, 4…)
    extractEvens []       = []
    extractEvens (x:_:xs) = x : extractEvens xs
    extractEvens [x]      = [x]   -- якщо файл без пари — ігноруємо

    -- Беремо елементи з непарними позиціями (1, 3, 5…)
    extractOdds []       = []
    extractOdds (_:y:xs) = y : extractOdds xs
    extractOdds [_]      = []
parseArgs _ = Config "" "" [] []   -- не повинно трапитись через перевірку вище

-- ============================================================
-- РОБОТА З ФАЙЛАМИ
-- ============================================================

-- | Перевіряє існування кожного файлу і створює порожній, якщо його немає.
ensureFilesExist :: Config -> IO ()
ensureFilesExist cfg = do
  let allFiles = mainQnA cfg : mainOpenQ cfg
                 : otherQnAs cfg ++ otherOpenQs cfg
  mapM_ createIfMissing allFiles
  where
    createIfMissing path = do
      exists <- doesFileExist path
      unless exists $ do
        writeFile path ""   -- створюємо порожній файл
        putStrLn $ "Created new file: " ++ path

-- ============================================================
-- ПАРСИНГ ФАЙЛУ QnA
-- ============================================================

-- | Зчитує файл QnA.txt і повертає список пар QnAPair.
--   Формат файлу:
--     Q: питання
--     A: відповідь
--   ВАЖЛИВО: Примусуємо строге читання через length, щоб уникнути
--   "resource busy" помилки на Windows з ленивим readFile
readQnA :: FilePath -> IO [QnAPair]
readQnA path = do
  exists <- doesFileExist path
  if not exists
    then return []
    else do
      content <- readFile path
      let result = parseQnA (lines content)
      -- Примусуємо оцінювання всього списку, щоб закрити файловий дескриптор
      _ <- return $! length result
      return result

-- | Розбирає рядки файлу QnA на список пар «питання – відповідь».
--   Ігнорує порожні рядки.
parseQnA :: [String] -> [QnAPair]
parseQnA [] = []
parseQnA (q:a:rest)
  -- Рядок питання починається з "Q: ", рядок відповіді — з "A: "
  | "Q: " `isPrefixOf` q && "A: " `isPrefixOf` a =
      QnAPair
        { question = drop 3 q   -- відкидаємо префікс "Q: "
        , answer   = drop 3 a   -- відкидаємо префікс "A: "
        } : parseQnA rest
  | otherwise = parseQnA (a:rest)   -- пропускаємо «сміттєвий» рядок
parseQnA [_] = []   -- одинокий рядок без пари — ігнорується

-- ============================================================
-- ПОШУК ВІДПОВІДІ
-- ============================================================

-- | Шукає відповідь у файлі QnA за питанням користувача.
--   Порівнює без урахування регістру і пробілів на краях.
findAnswer :: String -> [QnAPair] -> Maybe String
findAnswer q pairs =
  answer <$> find (\p -> normalize (question p) == normalize q) pairs
  where
    -- Нормалізація: нижній регістр + видалення зайвих пробілів
    normalize = map toLower . trim

-- | Видаляє пробіли на початку та в кінці рядка.
trim :: String -> String
trim = reverse . dropWhile isSpace . reverse . dropWhile isSpace

-- ============================================================
-- РОЗШИРЕНИЙ ПОШУК: у кількох QnA-файлах
-- ============================================================

-- | Шукає відповідь послідовно у списку QnA-файлів.
--   Повертає першу знайдену відповідь або Nothing.
findAnswerInFiles :: String -> [FilePath] -> IO (Maybe String)
findAnswerInFiles _ [] = return Nothing
findAnswerInFiles q (f:fs) = do
  pairs <- readQnA f
  case findAnswer q pairs of
    Just ans -> return (Just ans)   -- знайшли — повертаємо
    Nothing  -> findAnswerInFiles q fs   -- шукаємо далі

-- ============================================================
-- РОБОТА З ВІДКРИТИМИ ПИТАННЯМИ
-- ============================================================

-- | Зчитує файл OpenQuestions.txt і повертає список питань.
--   ВАЖЛИВО: Примусуємо строге читання, щоб уникнути
--   "resource busy" помилки на Windows
readOpenQuestions :: FilePath -> IO [String]
readOpenQuestions path = do
  exists <- doesFileExist path
  if not exists
    then return []
    else do
      content <- readFile path
      let result = filter (not . null . trim) (lines content)
      -- Примусуємо оцінювання всього списку, щоб закрити файловий дескриптор
      _ <- return $! length result
      return result

-- | Видаляє перше питання з файлу OpenQuestions.txt
--   (бот «задав» його користувачу).
removeFirstQuestion :: FilePath -> IO ()
removeFirstQuestion path = do
  qs <- readOpenQuestions path
  case qs of
    []     -> return ()          -- файл порожній — нічого видаляти
    (_:rest) -> writeFile path (unlines rest)   -- перезаписуємо без першого питання

-- | Додає нове питання до файлу OpenQuestions.txt.
appendOpenQuestion :: FilePath -> String -> IO ()
appendOpenQuestion path q = appendFile path (q ++ "\n")

-- ============================================================
-- ЗБЕРЕЖЕННЯ НОВОЇ ПАРИ ЗНАНЬ
-- ============================================================

-- | Дописує нову пару Q–A у файл QnA.txt.
appendQnA :: FilePath -> String -> String -> IO ()
appendQnA path q a = appendFile path $
  "\nQ: " ++ q ++ "\nA: " ++ a ++ "\n"

-- ============================================================
-- ГОЛОВНИЙ ЦИКЛ
-- ============================================================

-- | Основний нескінченний цикл діалогу.
--   Кожна ітерація:
--     1. Бот очікує питання від користувача
--     2. Бот відповідає (або зізнається, що не знає)
--     3. Бот сам ставить питання з OpenQuestions.txt
mainLoop :: Config -> IO ()
mainLoop cfg = do
  -- Крок 1: зчитуємо питання користувача
  putStr "You: "
  userInput <- getLine

  -- Перевіряємо команду виходу
  if trim (map toLower userInput) == "exit"
    then putStrLn "Bot: Goodbye!"
    else do

      -- -------------------------------------------------------
      -- Крок 2: шукаємо відповідь
      -- -------------------------------------------------------

      -- Спершу шукаємо у власному QnA-файлі
      mainPairs <- readQnA (mainQnA cfg)
      let localAnswer = findAnswer userInput mainPairs

      -- Якщо не знайшли — шукаємо у файлах інших ботів
      answer' <- case localAnswer of
        Just a  -> return (Just a)
        Nothing -> findAnswerInFiles userInput (otherQnAs cfg)

      -- Виводимо відповідь
      case answer' of
        Just a -> putStrLn $ "Bot: " ++ a

        Nothing -> do
          -- Бот не знає відповіді
          putStrLn "Bot: I don't know. Please ask me later."

          -- Додаємо питання у файли OpenQuestions інших ботів,
          -- щоб вони спитали своїх користувачів
          let targets = otherOpenQs cfg
          if null targets
            then return ()   -- немає інших ботів — нікуди «кидати» питання
            else do
              mapM_ (`appendOpenQuestion` userInput) targets
              putStrLn $ "(Question forwarded to " ++ show (length targets)
                       ++ " other bot(s))"

      -- -------------------------------------------------------
      -- Крок 3: бот сам ставить питання з OpenQuestions.txt
      -- Передаємо останнє питання користувача, щоб уникнути дублювання
      -- відповіді, якщо топ-питання в OpenQuestions збігається з ним.
      askFromOpenQuestions cfg userInput

      -- Повторюємо цикл
      mainLoop cfg

-- | Бот зчитує перше питання з OpenQuestions.txt, виводить його
--   і чекає на відповідь користувача, яку зберігає у QnA.txt.
askFromOpenQuestions :: Config -> String -> IO ()
askFromOpenQuestions cfg lastUserQuestion = do
  qs <- readOpenQuestions (mainOpenQ cfg)
  case qs of
    [] -> putStrLn "Bot: What else would you like to ask me?"

    (q:_) -> do
      -- Якщо перше питання збігається з тим, що користувач тільки що
      -- задав, уникаємо дублювання: видаляємо його і не питаємо знову.
      let normalizeQ s = map toLower (trim s)
      if normalizeQ q == normalizeQ lastUserQuestion
        then do
          -- Якщо питання співпадає з тим, що тільки що задав користувач,
          -- видаляємо його і переходимо до наступного питання (якщо є).
          removeFirstQuestion (mainOpenQ cfg)
          askFromOpenQuestions cfg lastUserQuestion
        else do
          -- Перевіряємо, чи вже знаємо відповідь на це питання
          mainPairs <- readQnA (mainQnA cfg)
          let localAnswer = findAnswer q mainPairs

          case localAnswer of
            Just _ans -> do
                -- Бот вже знає відповідь — просто видаляємо питання з черги
                removeFirstQuestion (mainOpenQ cfg)
            -- Не знаємо локально — шукаємо у файлах інших ботів
            Nothing -> do
              answer' <- findAnswerInFiles q (otherQnAs cfg)
              case answer' of
                -- Знайшли у файлі іншого бота — відповідаємо
                Just ans -> do
                  putStrLn $ "Bot: " ++ ans
                  removeFirstQuestion (mainOpenQ cfg)

                -- Не знаємо ніде — запитуємо користувача
                Nothing -> do
                  putStrLn $ "Bot: " ++ q
                  removeFirstQuestion (mainOpenQ cfg)

                  -- Зчитуємо відповідь користувача
                  putStr "You: "
                  userAnswer <- getLine

                  -- Якщо користувач не хоче виходити — зберігаємо знання
                  if trim (map toLower userAnswer) == "exit"
                    then do
                      putStrLn "Bot: Goodbye!"
                      exitSuccess
                    else do
                      appendQnA (mainQnA cfg) q userAnswer
                      putStrLn "Bot: Thank you! I will remember that."

