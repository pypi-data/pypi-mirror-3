"""iterative.py

Iterative fibonacci number calculation.
"""

def fib_iterative(n):
    """Calculate the n'th fibonacci number using a reasonably
    efficient iterative algorithm.
    """
    if n < 0:
        raise ValueError('cannot calculate negative fibonacci numbers')
    elif not isinstance(n, (int, long)):
        raise TypeError('"n" must be an integer')
    elif n <= 1:
        return n

    penultimate, ultimate = 0, 1

    # we're account for n=1 with "ultimate"
    n -= 1

    while n > 0:
        penultimate, ultimate = ultimate, penultimate + ultimate
        n -= 1

    return ultimate

try:
    import _cmultifib
    c_fib_iterative = _cmultifib.fib_iterative
except ImportError:
    def c_fib_iterative(n):
        raise Exception('C extension module could not be imported')

