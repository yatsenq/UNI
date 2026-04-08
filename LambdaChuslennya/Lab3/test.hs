myMaximum :: Ord a => [a] -> a
myMaximum [x] = x
myMaximum (x:xs)
    | x > maxRest = x
    | otherwise = maxRest
    where
        maxRest = myMaximum xs