import math
import random

import numpy as np

from ._prime import PRIMES


def _prev_prime_index(x):
    assert PRIMES[0] <= x < PRIMES[-1]
    return np.where(PRIMES - x <= 0)[0][-1]


def prev_prime(x):
    """
    Returns the nearest prime :math:`p`, such that :math:`p \\le x`.

    Parameters
    ----------
    x : int
        A positive integer.

    Returns
    -------
    int
        The nearest prime :math:`p \\le x`.

    Examples
    --------
    .. ipython:: python

        galois.prev_prime(13)
        galois.prev_prime(15)
    """
    prev_idx = _prev_prime_index(x)
    return PRIMES[prev_idx]


def next_prime(x):
    """
    Returns the nearest prime :math:`p`, such that :math:`p > x`.

    Parameters
    ----------
    x : int
        A positive integer.

    Returns
    -------
    int
        The nearest prime :math:`p > x`.

    Examples
    --------
    .. ipython:: python

        galois.next_prime(13)
        galois.next_prime(15)
    """
    prev_idx = _prev_prime_index(x)
    return PRIMES[prev_idx + 1]


def prime_factors(x):
    """
    Computes the prime factors of the positive integer :math:`x`.

    The integer :math:`x` can be factored into :math:`x = p_1^{k_1} p_2^{k_2} \\dots p_{n-1}^{k_{n-1}}`.

    Parameters
    ----------
    x : int
        The positive integer to be factored.

    Returns
    -------
    list
        Sorted list of prime factors :math:`p = [p_1, p_2, \\dots, p_{n-1}]` with :math:`p_1 < p_2 < \\dots < p_{n-1}`.
    list
        List of corresponding prime powers :math:`k = [k_1, k_2, \\dots, k_{n-1}]`.

    Examples
    --------
    .. ipython:: python

        p, k = galois.prime_factors(120)
        p, k

        # The product of the prime powers is the factored integer
        np.multiply.reduce(np.array(p) ** np.array(k))

    Prime factorization of 1 less than a large prime.

    .. ipython:: python

        prime =1000000000000000035000061
        galois.is_prime(prime)
        p, k = galois.prime_factors(prime - 1)
        p, k
        np.multiply.reduce(np.array(p) ** np.array(k))
    """
    if not isinstance(x, (int, np.integer)):
        raise TypeError(f"Argument `x` must be an integer, not {type(x)}.")
    if not x > 0:
        raise ValueError(f"Argument `x` must be a positive integer, not {x}.")

    if x == 1:
        return [1], [1]

    max_factor = int(math.ceil(math.sqrt(x)))
    max_prime_idx = np.where(PRIMES - max_factor <= 0)[0][-1]

    p = []
    k = []
    for prime in PRIMES[0:max_prime_idx+1]:
        degree = 0
        while x % prime == 0:
            degree += 1
            x = x // prime
        if degree > 0:
            p.append(int(prime))  # TODO: Needed until PRIMES is a list of python ints
            k.append(degree)
        if x == 1:
            break

    if x > 2:
        p.append(int(x))  # TODO: Needed until PRIMES is a list of python ints
        k.append(1)

    return p, k


def is_prime(n):
    """
    Determines if :math:`n` is prime.

    This algorithm will first run Fermat's primality test to check :math:`n` for compositeness. If
    it determines :math:`n` is composite, the function will quickly return. If Fermat's primality test
    returns `True`, then :math:`n` could be prime or pseudoprime. If so, then this function will run seven
    rounds of Miller-Rabin's primality test. With this many rounds, a result of `True` should have high
    probability of being a true prime, not a pseudoprime.

    Parameters
    ----------
    n : int
        A positive integer.

    Returns
    -------
    bool:
        `True` if the integer :math:`n` is prime.

    Examples
    --------
    .. ipython:: python

        galois.is_prime(13)
        galois.is_prime(15)

    The algorithm is also efficient on very large :math:`n`.

    .. ipython:: python

        galois.is_prime(1000000000000000035000061)
    """
    if not isinstance(n, (int, np.integer)):
        raise TypeError(f"Argument `n` must be an integer, not {type(n)}.")
    if not n > 0:
        raise ValueError(f"Argument `n` must be a positive integer, not {n}.")

    if n == 1:
        return False
    if n == 2:
        return True

    if not fermat_primality_test(n):
        # If the test returns False, then n is definitely composite
        return False

    if not miller_rabin_primality_test(n, rounds=7):
        # If the test returns False, then n is definitely composite
        return False

    return True


def fermat_primality_test(n):
    """
    Probabilistic primality test of :math:`n`.

    This function implements Fermat's primality test. The test says that for an integer :math:`n`, select an integer
    :math:`a` coprime with :math:`n`. If :math:`a^{n-1} \\equiv 1 (\\textrm{mod}\\ n)`, then :math:`n` is prime or pseudoprime.

    Parameters
    ----------
    n : int
        A positive integer.

    Returns
    -------
    bool
        `False` if :math:`n` is known to be composite. `True` if :math:`n` is prime or pseudoprime.

    Examples
    --------
    .. ipython:: python

        # List of some primes
        primes = [257, 24841, 65497]

        for prime in primes:
            is_prime = galois.fermat_primality_test(prime)
            p, k = galois.prime_factors(prime)
            print("Prime = {:5d}, Fermat's Prime Test = {}, Prime factors = {}".format(prime, is_prime, list(p)))

        # List of some strong pseudoprimes with base 2
        pseudoprimes = [2047, 29341, 65281]

        for pseudoprime in pseudoprimes:
            is_prime = galois.fermat_primality_test(pseudoprime)
            p, k = galois.prime_factors(pseudoprime)
            print("Pseudoprime = {:5d}, Fermat's Prime Test = {}, Prime factors = {}".format(pseudoprime, is_prime, list(p)))
    """
    if not isinstance(n, (int, np.integer)):
        raise TypeError(f"Argument `n` must be an integer, not {type(n)}.")
    if not n > 2:
        raise ValueError(f"Argument `n` must be greater than 2, not {n}.")

    n = int(n)  # TODO: Needed until primes is a list of python ints
    a = 2  # A value coprime with n

    if pow(a, n - 1, n) != 1:
        # n is definitely composite
        return False

    # n is a pseudoprime, but still may be composite
    return True


def miller_rabin_primality_test(n, a=None, rounds=1):
    """
    Probabilistic primality test of :math:`n`.

    This function implements the Miller-Rabin primality test. The test says that for an integer :math:`n`, select an integer
    :math:`a` such that :math:`a < n`. Factor :math:`n - 1` such that :math:`2^s d = n - 1`. Then, :math:`n` is composite,
    if :math:`a^d \\not\\equiv 1 (\\textrm{mod}\\ n)` and :math:`a^{2^r d} \\not\\equiv n - 1 (\\textrm{mod}\\ n)` for
    :math:`1 \\le r < s`.

    Parameters
    ----------
    n : int
        A positive integer.
    a : int, optional
        Initial composite witness value, :math:`1 \\le a < n`. On subsequent rounds, :math:`a` will
        be a different value. The default is a random value.
    rounds : int, optional
        The number of iterations attempting to detect :math:`n` as composite. Additional rounds will choose
        new :math:`a`. Sufficient rounds have arbitrarily-high probability of detecting a composite.

    Returns
    -------
    bool
        `False` if :math:`n` is known to be composite. `True` if :math:`n` is prime or pseudoprime.

    References
    ----------
    * https://math.dartmouth.edu/~carlp/PDF/paper25.pdf

    Examples
    --------
    .. ipython:: python

        # List of some primes
        primes = [257, 24841, 65497]

        for prime in primes:
            is_prime = galois.miller_rabin_primality_test(prime)
            p, k = galois.prime_factors(prime)
            print("Prime = {:5d}, Miller-Rabin Prime Test = {}, Prime factors = {}".format(prime, is_prime, list(p)))

        # List of some strong pseudoprimes with base 2
        pseudoprimes = [2047, 29341, 65281]

        # Single round of Miller-Rabin, sometimes fooled by pseudoprimes
        for pseudoprime in pseudoprimes:
            is_prime = galois.miller_rabin_primality_test(pseudoprime)
            p, k = galois.prime_factors(pseudoprime)
            print("Pseudoprime = {:5d}, Miller-Rabin Prime Test = {}, Prime factors = {}".format(pseudoprime, is_prime, list(p)))

        # 7 rounds of Miller-Rabin, never fooled by pseudoprimes
        for pseudoprime in pseudoprimes:
            is_prime = galois.miller_rabin_primality_test(pseudoprime, rounds=7)
            p, k = galois.prime_factors(pseudoprime)
            print("Pseudoprime = {:5d}, Miller-Rabin Prime Test = {}, Prime factors = {}".format(pseudoprime, is_prime, list(p)))
    """
    a = random.randint(1, n - 1) if a is None else a
    if not isinstance(n, (int, np.integer)):
        raise TypeError(f"Argument `n` must be an integer, not {type(n)}.")
    if not n > 1:
        raise ValueError(f"Argument `n` must be greater than 1, not {n}.")
    if not 1 <= a < n:
        raise ValueError(f"Arguments must satisfy `1 <= a < n`, not `1 <= {a} < {n}`.")

    n = int(n)  # TODO: Needed until primes is a list of python ints

    # Factor (n - 1) by 2
    x = n -1
    s = 0
    while x % 2 == 0:
        s += 1
        x //= 2

    d = (n - 1) // 2**s
    assert d % 2 != 0

    # Write (n - 1) = 2^s * d
    assert 2**s * d == n - 1

    composite_tests = []
    composite_tests.append(pow(a, d, n) != 1)
    for r in range(0, s):
        composite_tests.append(pow(a, 2**r * d, n) != n - 1)
    composite_test = all(composite_tests)

    if composite_test:
        # n is definitely composite
        return False
    else:
        # Optionally iterate tests
        rounds -= 1
        if rounds > 0:
            # On subsequent rounds, don't specify a -- we want new, different a's
            return miller_rabin_primality_test(n, rounds=rounds)
        else:
            # n might be a prime
            return True
