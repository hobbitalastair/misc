#!/usr/bin/env lua
-- Small calculator, for learning a little bit of Lua

function tokenize(expr)
    local tokens = {}
    -- Note; tables are unordered! So I can't assume ordering here
    local patterns = {
        ["^%d+"] = function(m) table.insert(tokens, tonumber(m)) end,
        ["^%l+"] = function(m) table.insert(tokens, m) end,
        ["^[%+%-%*/()]"] = function(m) table.insert(tokens, m) end,
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

function consume_number(tokens, start, count)
    if count >= 1 and type(tokens[start]) == "number" then
        return tokens[start], 1
    elseif count >= 2 and tokens[start] == "-" and type(tokens[start + 1]) == "number" then
        return 0 - tokens[start + 1], 2
    else
        return "Invalid number", 0
    end
end

function subexpression(tokens, start, count)
    if count >= 1 and tokens[start] == "(" then
        start = start + 1
        count = count - 1

        result, consumed = expression(tokens, start, count)
        if consumed == 0 then
            return result, 0
        end

        if tokens[start + consumed] == ")" then
            return result, consumed + 2
        else
            return "Unterminated parenthesis", 0
        end
    else
        return consume_number(tokens, start, count)
    end
end

function multiply_or_divide(tokens, start, count)
    local sum, consumed = subexpression(tokens, start, count)
    if consumed == 0 then
        return sum, 0
    end
    start = start + consumed
    count = count - consumed
    local total_consumed = consumed

    while count >= 2 and (tokens[start] == '*' or tokens[start] == '/') do
        local operator = tokens[start]
        start = start + 1
        count = count - 1
        total_consumed = total_consumed + 1

        local new_number, consumed = subexpression(tokens, start, count)
        if consumed == 0 then
            return new_number, 0
        end
        start = start + consumed
        count = count - consumed
        total_consumed = total_consumed + consumed

        if operator == "*" then
            sum = sum * new_number
        elseif operator == "/" then
            sum = sum / new_number
        end
    end

    return sum, total_consumed
end

function plus_or_minus(tokens, start, count)
    local sum, consumed = multiply_or_divide(tokens, start, count)
    if consumed == 0 then
        return sum, 0
    end
    start = start + consumed
    count = count - consumed
    local total_consumed = consumed

    while count >= 2 and (tokens[start] == '+' or tokens[start] == '-') do
        local operator = tokens[start]
        start = start + 1
        count = count - 1
        total_consumed = total_consumed + 1

        local new_number, consumed = multiply_or_divide(tokens, start, count)
        if consumed == 0 then
            return new_number, 0
        end
        start = start + consumed
        count = count - consumed
        total_consumed = total_consumed + consumed

        if operator == "+" then
            sum = sum + new_number
        elseif operator == "-" then
            sum = sum - new_number
        end
    end

    return sum, total_consumed
end

function expression(tokens, start, count)
    return plus_or_minus(tokens, start, count)
end

function calculate(expr)
    local tokens, err = tokenize(expr)
    if err then
        return err
    end
    if #tokens == 0 then
        return ""
    end

    result, consumed = expression(tokens, 1, #tokens)
    if consumed == #tokens then
        return tostring(result)
    else
        -- Error; return the error string
        return "Invalid input"
    end
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
            io.write(result .. " != " .. expected .. "!!!!!\n")
        else
            io.write(expected .. "\n")
        end
    end
    check_expr("5", 5)
    check_expr("-13", -13)
    check_expr("5 - 3 + 9", 11)
    check_expr("5 + 3 - 9", -1)
    check_expr("-3 + -4", -7)
    check_expr("0 - -7", 7)
    check_expr("5 * 6", 30)
    check_expr("5 * 6 + 3", 33)
    check_expr("3 - 5 * 6", -27)
    check_expr("4 * 2 + 3 - 5 * 6", -19)
    check_expr("4 * 4 * 6", 96)
    check_expr("5 * 4 / 4", 5.0)
    check_expr("16 / 4 / 4", 1.0)
    check_expr("16 / 4 / 4 + 9", 10.0)
    check_expr("(4)", 4)
    check_expr("(-204)", -204)
    check_expr("5 * (3 - 2)", 5)
    check_expr("(3 + 2) * 4", 20)
    check_expr("(3 + (2 / 2)) * 4", 16.0)
    check_expr("((200)) / ((15 * 4) / ((3 * 5 + 5) - 5))", 50.0)
end

if #arg == 0 then
    repl()
elseif arg[1] == "--test" then
    run_tests()
else
    io.write("Unknown arguments\n")
end
