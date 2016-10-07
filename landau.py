""" Landau's Function implementation.

    This is an experiment to see whether a naive algorithm matches up with the
    expected results for some set of n.

    Author: Alastair Hughes
    Date:   7-10-2016
"""

from fractions import gcd

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


def landau(n):
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

    print(n, sum(factors), factors)
    return product(factors)


if __name__ == "__main__":
    for i in range(20):
        print("{}: {}".format(i, landau(i)))
