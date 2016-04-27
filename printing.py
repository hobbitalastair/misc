

import random
import time

CONT = None
DIE = 0
MULT = 1

class char:

    count = 0

    def __init__(self):
        self.pos = random.randint(0, 99)
        char.count += 1
        self.age = 0
        self.col = 3

    def update(self):
        self.age += 1
        self.pos += random.randint(-3, 3)
        self.pos = max(min(self.pos, 99), 0)
        if self.age > 3 and random.randint(0, 1) == 0:
            return MULT
        elif self.pos % int((20 / char.count) + 1) == 0 or \
                self.age > random.randint(15, 20):
            char.count -= 1
            return DIE
        elif self.age > 10 and random.randint(0, 5) == 0:
            self.col = random.randint(1, 5)

    def render(self):
        return '\x1b[3' + str(self.col) + 'm+\x1b[0m'

    def mult(self):
        c = char()
        c.col = self.col
        c.pos = min(max(random.randint(self.pos - 4, self.pos + 4), 0), 99)
        return c

chars = [char()]

while True:

    new_chars = []
    for ch in chars:
        state = ch.update()
        if state == CONT or state == MULT:
            new_chars.append(ch)
        if state == MULT:
            new_chars.append(ch.mult())
    chars = new_chars

    i = 0
    for ch in sorted(chars, key=lambda c: c.pos):
        if i - 1 == ch.pos:
            # Ignore more than one on a spot.
            continue
        if not 0 <= ch.pos <= 99:
            # Ignore invalid positions.
            continue
        print(' ' * (ch.pos - i) + ch.render(), end='')
        i = ch.pos + 1

    print(' ' * (100 - i) + '|' + ''.join([c.render() for c in sorted(chars, key=lambda c: c.col)]))
    time.sleep(.00)
    if char.count == 0:
        exit()
