""" Automated theorem prover for propositional logic, based on a modification
    of LK.
    
    Goals:
    - Write a robust theorem prover for propositional logic.
    - Figure out why first-order is only semi-determinable.

    Theorems are represented by two sets, ({}, {}), of assumptions and results.
    The theorem solver is assumed to preserve truth, and to always decrement
    the operator count.
    A term is a set (type, args*) where type is the operator or "term".

    Author: Alastair Hughes
    Date:   6-9-2016
"""

NOT     = '!'
AND     = '&'
OR      = '|'
IMPLY   = '>'
TERM    = ''

LEFT    = 0
RIGHT   = 1

NOT_SYM     = '¬'
AND_SYM     = '∧'
OR_SYM      = '∨'
IMPLY_SYM   = '→'
TURNSTYLE   = '⊢'


def render_theorem(theorem):
    """ Render the given theorem into a string """

    return ", ".join((render_formula(formula) for formula in theorem[0])) + \
            ' ' + TURNSTYLE + ' ' + \
            ", ".join((render_formula(formula) for formula in theorem[1]))


def render_formula(formula):
    """ Render the given formula into a string """

    if formula[0] == NOT:
        return NOT_SYM + render_formula(formula[1])
    elif formula[0] == AND:
        return '({} {} {})'.format(render_formula(formula[1]), AND_SYM, \
                render_formula(formula[2]))
    elif formula[0] == OR:
        return '({} {} {})'.format(render_formula(formula[1]), OR_SYM, \
                render_formula(formula[2]))
    elif formula[0] == IMPLY:
        return '({} {} {})'.format(render_formula(formula[1]), IMPLY_SYM, \
                render_formula(formula[2]))
    return formula[1]


def render_proof(proof):
    """ Render the given proof into a string in a top-down form """

    if len(proof) == 1:
        return render_theorem(proof[0])
    elif len(proof) == 2:
        return render_theorem(proof[0]) + '\n' + render_proof(proof[1])
    elif len(proof) == 3:
        # TODO: This does not work as intended.
        return render_theorem(proof[0]) + '\n' + \
                render_proof(proof[1]) + '\t\t' + render_proof(proof[2])


def parse_theorem(string):
    """ Parse a theorem from the given string """

    left, right = string.split(':')
    assump = {parse_formula(tokenise_formula(formula)) \
            for formula in left.split(',')}
    results = {parse_formula(tokenise_formula(formula)) \
            for formula in right.split(',')}
    return (assump, results)


def tokenise_formula(string):
    """ Tokenise the given formula """
    return [tok for tok in string \
        if tok in (NOT, OR, AND, IMPLY, '(', ')') or tok.isalpha()]


def parse_formula(tokens):
    """ Parse a formula from the given list of tokens """
    result, tokens = parse_subformula(tokens)
    if len(tokens) != 0:
        raise ValueError("Unexpected extra tokens {}".format(tokens))
    return result


def parse_subformula(tokens):
    """ Parse a formula from the given list of tokens, returning the result and
        any unused tokens.
    """

    # TODO: This is BROKEN!!!

    if len(tokens) == 0:
        raise ValueError("Expected a token, got nothing!")
    
    if tokens[0] == '(':
        result, tokens = parse_subformula(tokens[1:])
        if tokens[0] != ')':
            raise ValueError("Unmatched ')'!")
        return result, tokens[1:]
    elif len(tokens) > 1 and tokens[0] == NOT:
        # Special case !(); otherwise bind to !a for some term.
        if tokens[1] == '(':
            result, tokens = parse_subformula(tokens[1:])
            return (NOT, result), tokens
        else:
            return (NOT, (TERM, tokens[1])), tokens[2:]
    elif len(tokens) > 2 and tokens[1] in (OR, AND, IMPLY):
        first, op = tokens[:2]
        if not first.isalpha():
            raise ValueError("Expected term, got {}!", first)
        result, tokens = parse_subformula(tokens[2:])
        return (op, (TERM, first), result), tokens
    elif tokens[0].isalpha():
        return (TERM, tokens[0]), tokens[1:]
    else:
        raise ValueError("Unknown token {} at {}".format(tokens[0], tokens))


def opcount(formula):
    """ Count the number of operands in the given formula.
        
        >>> opcount((TERM, 'a'))
        0
        >>> opcount((NOT, (TERM, 'a')))
        1
        >>> opcount((AND, (NOT, (TERM, 'a')), (OR, (TERM, 'b'), (TERM, 'c'))))
        3
    """
    if formula[0] == NOT:
        return 1 + opcount(formula[1])
    elif formula[0] == TERM:
        return 0
    else:
        return 1 + opcount(formula[1]) + opcount(formula[2])


def solve(theorem):
    """ Generate a proof for the given theorem, if possible.
        An invalid theorem will result in a proof containing a contradiction,
        in the form of a theorem of two empty sets (set(), set()).
    
        >>> solve((set(), set()))
        [(set(), set())]
        >>> solve(({(TERM, 'a')}, {(TERM, 'b')}))
        [(set(), set())]
        >>> solve(({(TERM, 'a')}, {(TERM, 'a')}))
        [({('', 'a')}, {('', 'a')})]
        >>> solve(({(TERM, 'a')}, {(TERM, 'a')}))
        [({('', 'a')}, {('', 'a')})]
        >>> solve(({(NOT, (TERM, 'a'))}, {(TERM, 'a')}))
        (({('!', ('', 'a'))}, {('', 'a')}), [(set(), set())])
        >>> solve(({(AND, (TERM, 'a'), (TERM, 'b'))}, {(TERM, 'a')}))
        (({('&', ('', 'a'), ('', 'b'))}, {('', 'a')}), [({('', 'a')}, {('', 'a')})])

        # TODO: Add more tests...
    """

    # Find the candidate.
    candidate = None
    for side, contents in enumerate(theorem):
        for formula in contents:
            if formula[0] in (NOT, AND, OR, IMPLY):
                candidate = (side, formula)

    if candidate is None:
        # Contract - only terms remain.
        intersect = theorem[LEFT].intersection(theorem[RIGHT])
        return [(intersect, intersect)]

    # Make a copy of the theorem with the candidate removed.
    new = (theorem[0].copy(), theorem[1].copy())
    new[candidate[0]].remove(candidate[1])

    # Add the value back in.
    side, formula = candidate
    if formula[0] == NOT:
        new[(side + 1) % 2].add(formula[1])
        return (theorem, solve(new))
    elif formula[0] == AND:
        if side == LEFT:
            new[LEFT].add(formula[1])
            new[LEFT].add(formula[2])
            return (theorem, solve(new))
        else:
            new_2 = (new[0].copy(), new[1].copy())
            new[RIGHT].add(formula[1])
            new_2[RIGHT].add(formula[2])
            return (theorem, solve(new), solve(new_2))
    elif formula[0] == OR:
        if side == RIGHT:
            new[RIGHT].add(formula[1])
            new[RIGHT].add(formula[2])
            return (theorem, solve(new))
        else:
            new_2 = (new[0].copy(), new[1].copy())
            new[LEFT].add(formula[1])
            new_2[LEFT].add(formula[2])
            return (theorem, solve(new), solve(new_2))
    elif formula[0] == IMPLY:
        if side == RIGHT:
            new[LEFT].add(formula[1])
            new[RIGHT].add(formula[2])
            return (theorem, solve(new))
        else:
            new_2 = (new[0].copy(), new[1].copy())
            new[RIGHT].add(formula[1])
            new_2[LEFT].add(formula[2])
            return (theorem, solve(new), solve(new_2))
    
    return theorem


if __name__ == "__main__":
    import doctest
    doctest.testmod()
