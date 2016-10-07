""" Landau's Function implementation.

    This is an experiment to see whether a naive algorithm matches up with the
    expected results for some set of n.

    Author: Alastair Hughes
    Date:   7-10-2016
"""

from fractions import gcd
from math import sqrt, ceil, floor


def product(factors):
    """ Return the product of the given set of numbers """
    product = 1
    for i in factors:
        product *= i
    return product


def add_factor(i, n, factors):
    """ Try to add the given factor to the list of factors.
    
        This removes elements, starting with the largest and working down to
        the smallest, until the new element can fit.
        It only actually adds the element if it will be beneficial.

        TODO: The choice of factors to remove is arbitary and broken; for
              example, see landau(9) (should be 20)
    """

    new_factors = factors.copy()
    while sum(new_factors) + i > n:
        try:
            new_factors.remove(max(new_factors))
        except ValueError: # Nothing left to remove; abandon ship.
            break
    if product(factors.difference(new_factors)) <= i:
        new_factors.add(i)
        return new_factors

    return factors


def primish(n):
    """ Return a set of numbers which are either primes or powers of a prime,
        up to and including the value of n.
    """

    factors = set()
    for i in range(n, 1, -1):

        # Find the smallest divisor of i.
        smallest = 2
        while (i % smallest) != 0:
            smallest += 1

        # Divide by that divisor until we have 1 or something else.
        remainder = i
        while (remainder % smallest) == 0:
            remainder /= smallest

        # Keep it if needed.
        if remainder == 1:
            factors.add(i)

    return factors


def landau1(n):
    """ Return the landau function for the given value of n.
    
        We increment a counter. Whenever we increment the counter, we decide
        whether to add it to the set.
    """

    i = 2
    sum_factors = 1
    factors = set()

    while i <= n: 
        common = {j for j in factors if gcd(j, i) != 1}
        if len(common) == 0:
            factors = add_factor(i, n, factors)
            sum_factors = sum(factors)
        elif product(common) <= i:
            difference = factors.difference(common)
            new_factors = add_factor(i, n, difference)
            if product(new_factors) > product(factors):
                factors = new_factors
                sum_factors = sum(factors)
        i += 1

    print(n, product(factors), factors)
    return product(factors)


def landau2(n):
    """ Return the landau function for the given value of n.

        We begin with the set of all values up to and including n, then reduce
        that until we have a set with a sum less than n.
    """

    factors = primish(n)

    # TODO: I have no idea here...

    #assert sum(factors) <= n
    return product(factors)


if __name__ == "__main__":
    for i in range(30):
        print("{}: {} {}".format(i, landau1(i), landau2(i)))
