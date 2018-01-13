""" MathJam helper functions """

# Number facts.
def prod_digits(n):
    i = 1
    for d in str(n):
        i *= int(d)
    return i
sum_digits = lambda n: sum(int(d) for d in str(n))
ith_digit = lambda i, n: (("0" * i) + str(n))[i] #ith digit of n, where i=0 is the lsb.
i_digits = lambda i, n: len(str(n)) == i # is i digits long

factors = lambda n: (i for i in range(1,n+1) if n % i == 0) # Factors of n
tri_num = lambda n: n*(n + 1)//2 # nth triangle number

def q13a():
    parts = 2
    for i in range(35):
        parts += tri_num(i+1)+1
    print(parts)

def q18a():
    tri = {tri_num(i) for i in range(2*100) if tri_num(i) < 2*100}
    for a in tri:
        for b in tri:
            if i_digits(2, a) and i_digits(2, b) \
                and abs(a - b) in tri and a + b in tri:
                print(a, b)

def q43a():
    tri = {tri_num(i) for i in range(2*1000) if tri_num(i) < 2*1000}
    for a in tri:
        for b in tri:
            if i_digits(3, a) and i_digits(3, b) \
                and abs(a - b) in tri and a + b in tri:
                print(a, b)


def q23a():
    i = 77
    while i < 10000:
        if sum_digits(i) == 7 and i_digits(4, i):
            print(i)
        i += 7


def q9d():
    i = 100
    while i < 175: # <= 172.
        print(list(factors(i)))
        i += 5

q13a()
