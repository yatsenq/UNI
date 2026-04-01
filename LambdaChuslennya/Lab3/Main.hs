module Main where

import Lab3

assertEq :: (Eq a, Show a) => String -> a -> a -> IO Bool
assertEq name expected actual = do
  let ok = expected == actual
  putStrLn $ (if ok then "[PASS] " else "[FAIL] ") ++ name
  if ok
    then pure ()
    else do
      putStrLn $ "  expected: " ++ show expected
      putStrLn $ "  actual:   " ++ show actual
  pure ok

main :: IO ()
main = do
  putStrLn "Running Lab3 tests..."

  r1 <- assertEq "myRemoveAt basic" "acd" (myRemoveAt 2 "abcd")
  r2 <- assertEq "myRemoveAt out-of-range" "abcd" (myRemoveAt 10 "abcd")

  r3 <- assertEq "myInsertAt basic" "aXbcd" (myInsertAt 'X' "abcd" 2)
  r4 <- assertEq "myInsertAt prepend" "Xabcd" (myInsertAt 'X' "abcd" 1)
  r5 <- assertEq "myInsertAt append" "abcdX" (myInsertAt 'X' "abcd" 10)

  r6 <- assertEq "myDuplicate basic" [1, 1, 2, 2, 3, 3] (myDuplicate [1, 2, 3])
  r7 <- assertEq "myDuplicate empty" ([] :: [Int]) (myDuplicate [])

  r8 <- assertEq "myCompress basic" "abcade" (myCompress "aaaabccaadeeee")
  r9 <- assertEq "myCompress no-consecutive" "abac" (myCompress "abac")

  r10 <- assertEq "myMap basic" [2, 4, 6, 8] (myMap (*2) [1, 2, 3, 4])
  r11 <- assertEq "myMap empty" ([] :: [Int]) (myMap (*2) [])

  let total = 11
      passed = length (filter id [r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11])

  putStrLn ""
  putStrLn $ "Summary: " ++ show passed ++ "/" ++ show total ++ " tests passed."
  if passed == total
    then putStrLn "All tests passed."
    else putStrLn "Some tests failed."
