import math
import random
import fractions

try:
    import gmpy
except ImportError:
    gmpy = None

from primes import get_prime, DEFAULT_ITERATION
import exceptions


'''Primitive functions extracted from the PKCS1 RFC'''

def _pow(a, b, mod):
    if gmpy:
        return long(pow(gmpy.mpz(a), gmpy.mpz(b), gmpy.mpz(mod)))
    else:
        return pow(a, b, mod)

class RsaPublicKey(object):
    __slots__ = ('n', 'e', 'k')

    def __init__(self, n, e):
        self.k = integer_byte_size(n)
        self.n = n
        self.e = e

    def __repr__(self):
        return '<RsaPublicKey n: %d e: %d k: %d>' % (self.n, self.e, self.k)

class RsaPrivateKey(object):
    __slots__ = ('n', 'd', 'k')

    def __init__(self, n, d):
        self.k = integer_byte_size(n)
        self.n = n
        self.d = d

    def __repr__(self):
        return '<RsaPrivateKey n: %d d: %d k: %d>' % (self.n, self.d, self.k)


def integer_ceil(a, b):
    quanta, mod = divmod(a, b)
    if mod:
        quanta += 1
    return int(math.ceil(float(a) / float(b)))

def integer_byte_size(n):
    quanta, mod = divmod(integer_bit_size(n), 8)
    if mod or n == 0:
        quanta += 1
    return quanta

def integer_bit_size(n):
    if n == 0:
        return 1
    s = 0
    while n:
        s += 1
        n >>= 1
    return s

def euclide_gcd(a,b):
    if a > b:
        x, y, h = euclide_gcd(b, a)
        return y, x, h
    c = b // a
    b = b % a
    if b == 0:
        return 1, 0, a
    x, y, h = euclide_gcd(a, b)
    return x-c*y, y, h


def i2osp(x, x_len):
    if x > 256**x_len:
        raise exceptions.IntegerTooLarge
    h = hex(x)[2:]
    if h[-1] == 'L':
        h = h[:-1]
    if len(h) & 1 == 1:
        h = '0%s' % h
    x = h.decode('hex')
    return '\x00' * int(x_len-len(x)) + x

def os2ip(x):
    h = x.encode('hex')
    return int(h, 16)

def rsaep(public_key, m):
    if not (0 <= m <= public_key.n-1):
        raise exceptions.MessageRepresentativeOutOfRange
    return _pow(m, public_key.e, public_key.n)

def rsadp(private_key, c):
    if not (0 <= c <= private_key.n-1):
        raise exceptions.CiphertextRepresentativeOutOfRange
    return _pow(c, private_key.d, private_key.n)

def rsasp1(private_key, m):
    if not (0 <= m <= private_key.n-1):
        raise exceptions.MessageRepresentativeOutOfRange
    return rsadp(private_key, m)

def rsavp1(public_key, s):
    if not (0 <= s <= public_key.n-1):
        raise exceptions.SignatureRepresentativeOutOfRange
    return rsaep(public_key, s)

def string_xor(a, b):
    return ''.join((chr(ord(x) ^ ord(y)) for (x,y) in zip(a,b)))

def generate_key_pair(size=512, rnd=random.SystemRandom, k=DEFAULT_ITERATION,
        primality_algorithm=None):
    '''Generates a key pair'''
    p = get_prime(size >> 1, rnd, k, algorithm=primality_algorithm)
    q = get_prime(size >> 1, rnd, k, algorithm=primality_algorithm)
    n = p*q
    lbda = (p-1)*(q-1)
    e = 0x10001
    while e < lbda:
        if fractions.gcd(e, lbda) == 1:
            break
        e += 2
    d, y, z = euclide_gcd(e, lbda)
    assert z == 1
    if d < 0:
        d += lbda
    assert (d*e) % lbda == 1
    public, private = RsaPublicKey(n, e), RsaPrivateKey(n, d)
    assert check_rsa_keys_coherency(public, private)
    return public, private

def check_rsa_keys_coherency(public_key, private_key):
    '''Check that the public and private key match each other'''
    return public_key.n == private_key.n

def get_nonzero_random_bytes(length, rnd=random.SystemRandom):
    result = []
    i = 0
    if callable(rnd):
        rnd = rnd()
    while i < length:
        l = rnd.getrandbits(12*length)
        s = i2osp(l, 3*length)
        s = s.replace('\x00', '')
        result.append(s)
        i += len(s)
    return (''.join(result))[:length]

def constant_time_cmp(a, b):
    '''Compare two strings using constant time'''
    result = True
    for x, y in zip(a,b):
        result &= (x == y)
    return result
import textwrap

def dump_hex(data):
    if isinstance(data, basestring):
        print 'length', len(data)
        print textwrap.fill(''.join(['%s ' % x.encode('hex') for x in data]), 72)
