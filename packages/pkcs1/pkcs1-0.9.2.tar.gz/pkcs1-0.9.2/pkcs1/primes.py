import random
import math
import fractions
import primitives

PRIME_ALGO = 'miller-rabin'
try:
    import gmpy
    PRIME_ALGO = 'gmpy-miller-rabin'
except ImportError:
    gmpy = None

DEFAULT_ITERATION = 1000

USE_MILLER_RABIN = True

def is_prime(n, rnd=random.SystemRandom, k=DEFAULT_ITERATION, algorithm=None):
    if algorithm is None:
        algorithm = PRIME_ALGO
    if algorithm == 'gmpy-miller-rabin':
        if not gmpy:
            raise NotImplemented
        return gmpy.is_prime(n, k)
    elif algorithm == 'miller-rabin':
        # miller rabin probability of primality is 1/4**k
        return miller_rabin(n, k, rnd=rnd)
    elif algorithm == 'solovay-strassen':
        # for jacobi it's 1/2**k
        return randomized_primality_testing(n, rnd=rnd, k=k*2)
    else:
        raise NotImplemented


def get_prime(size=128, rnd=random.SystemRandom, k=DEFAULT_ITERATION, algorithm=None):
    if callable(rnd):
        rnd = rnd()
    while True:
        n = rnd.getrandbits(size-2)
        n = 2 ** (size-1) + n * 2 + 1
        if is_prime(n, rnd=rnd, k=k, algorithm=algorithm):
            return n
        if algorithm == 'gmpy-miller-rabin':
            return gmpy.next_prime(n)

def jacobi(a, b):
    '''Calculates the value of the Jacobi symbol (a/b) where both a and b are
    positive integers, and b is odd

    :returns: -1, 0 or 1
    '''

    assert a > 0
    assert b > 0

    if a == 0: return 0
    result = 1
    while a > 1:
        if a & 1:
            if ((a-1)*(b-1) >> 2) & 1:
                result = -result
            a, b = b % a, a
        else:
            if (((b * b) - 1) >> 3) & 1:
                result = -result
            a >>= 1
    if a == 0: return 0
    return result

def jacobi_witness(x, n):
    '''Returns False if n is an Euler pseudo-prime with base x, and
    True otherwise.
    '''

    j = jacobi(x, n) % n

    f = pow(x, n >> 1, n)

    if j == f: return False
    return True

def randomized_primality_testing(n, rnd=random.SystemRandom, k=DEFAULT_ITERATION):
    '''Calculates whether n is composite (which is always correct) or
    prime (which is incorrect with error probability 2**-k)

    Returns False if the number is composite, and True if it's
    probably prime.
    '''

    # 50% of Jacobi-witnesses can report compositness of non-prime numbers

    # The implemented algorithm using the Jacobi witness function has error
    # probability q <= 0.5, according to Goodrich et. al
    #
    # q = 0.5
    # t = int(math.ceil(k / log(1 / q, 2)))
    # So t = k / log(2, 2) = k / 1 = k
    # this means we can use range(k) rather than range(t)

    for _ in range(k):
        x = random.randint(0, n-1)
        if jacobi_witness(x, n): return False
    
    return True

def miller_rabin(n, k, rnd=random.SystemRandom):
    s = 0
    d = n-1
    # Find nearest power of 2
    s = primitives.integer_bit_size(n)
    # Find greatest factor which is a power of 2
    s = fractions.gcd(2**s, n-1)
    d = (n-1) // s
    s = primitives.integer_bit_size(s) - 1
    if callable(rnd):
        rnd = rnd()
    while k:
        k = k - 1
        a = random.randint(2, n-2)
        x = pow(a,d,n)
        if x == 1 or x == n - 1:
            continue
        for r in xrange(1,s-1):
            x = pow(x,2,n)
            if x == 1:
                return False
            if x == n - 1:
                break
        else:
            return False
    return True

