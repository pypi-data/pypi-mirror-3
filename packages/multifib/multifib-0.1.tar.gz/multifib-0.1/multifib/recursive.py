"""recursive.py

Recursive fibonacci number calculation.
"""

def fib_recursive(n):
    """Calculate the n'th fibonacci number using a straight-
    forward but inefficient recursive algorithm.
    """
    if n < 0:
        raise ValueError('cannot calculate negative fibonacci numbers')
    elif not isinstance(n, (int, long)):
        raise TypeError('"n" must be an integer')
    elif n <= 1:
        return n

    return fib_recursive(n - 1) + fib_recursive(n - 2)

try:
    import _cmultifib
    c_fib_recursive = _cmultifib.fib_recursive
except ImportError:
    import traceback
    traceback.print_exc()
    def c_fib_recursive(n):
        raise Exception('C extension module could not be imported')

