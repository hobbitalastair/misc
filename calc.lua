#!/usr/bin/env lua
-- Small stack based calculator, for learning a little bit of Lua

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

function calculate(expr)
    local tokens, err = tokenize(expr)
    if err then
        return err
    end

    local stack = {}
    for _, token in ipairs(tokens) do
        if type(token) == "number" then
            table.insert(stack, token)
        elseif token == "+" then
            local op1 = table.remove(stack)
            local op2 = table.remove(stack)
            table.insert(stack, op1 + op2)
        else
            return "Unknown token " .. token
        end
    end

    return tostring(stack[1])
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

repl()
