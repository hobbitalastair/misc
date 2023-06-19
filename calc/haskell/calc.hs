import System.IO

evaluate :: String -> String
evaluate input = do
    "You entered: " ++ input

repl :: IO()
repl = do
    putStr "> "
    input <- getLine
    if input /= "quit" && input /= "exit"
    then
        putStrLn (evaluate input) >>
        repl
    else putStr ""

main = do
    hSetBuffering stdout NoBuffering
    repl
