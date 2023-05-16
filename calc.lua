#!/usr/bin/env lua
-- Small stack based calculator, for learning a little bit of Lua



function tokenize(expr)
    local tokens = {}
    -- Note; tables are unordered! So I can't assume ordering here
    local patterns = {
        ["^%d+"] = function(m) table.insert(tokens, tonumber(m)) end,
        ["^%l+"] = function(m) table.insert(tokens, m) end,
        ["^[%+%-%*/]"] = function(m) table.insert(tokens, m) end,
        ["^%s+"] = function(m) end
    }

    local offset = 1
    while offset <= #expr do
        local matched = false
        for pattern, pattern_handler in pairs(patterns) do
            local match = string.match(expr, pattern, offset)
            if match ~= nil then
                matched = true
                pattern_handler(match)
                offset = offset + #match
                break
            end
        end

        if not matched then
            return tokens, "Invalid expression at offset " .. offset
        end
    end
    return tokens, false
end

function evaluate(tokens, start, count)
    if count == 1 and type(tokens[start]) == "number" then
        return tokens[start]
    elseif count == 2 then
        if tokens[start] == "-" and type(tokens[start + 1]) == "number" then
            return 0 - tokens[start + 1]
        else
            return "Invalid fragment"
        end
    elseif count >= 3 then
        local op = tokens[start + count - 2]
        local end_is_num = type(tokens[start + count - 1]) == "number"
        if op == "+" and end_is_num then
            return evaluate(tokens, start, count - 2) + tokens[start + count - 1]
        elseif op == "-" and end_is_num then
            return evaluate(tokens, start, count - 2) - tokens[start + count - 1]
        else
            return "Invalid fragment"
        end
    else
        return "Invalid fragment"
    end
end

function calculate(expr)
    local tokens, err = tokenize(expr)
    if err then
        return err
    end
    if #tokens == 0 then
        return ""
    end

    return tostring(evaluate(tokens, 1, #tokens))
end

function repl ()
    while true do
        io.write("> ")
        local func = io.read()
        if func == "exit" then
            break
        else
            io.write(calculate(func))
            io.write("\n")
        end
    end
end

function run_tests()
    check_expr = function(a, b)
        io.write(a .. " => ")
        io.flush()
        local result = calculate(a)
        local expected = tostring(b)
        if result ~= expected then
            io.write(result .. " != " .. expected .. "\n")
        else
            io.write(expected .. "\n")
        end
    end
    check_expr("5", 5)
    check_expr("5 - 3 + 9", 11)
    check_expr("5 + 3 - 9", -1)
    check_expr("-3 + -4", -7)
    check_expr("0 - -7", 7)
end

if #arg == 0 then
    repl()
elseif arg[1] == "--test" then
    run_tests()
else
    io.write("Unknown arguments\n")
end
