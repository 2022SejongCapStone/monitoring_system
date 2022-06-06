import Crypto.PublicKey.ElGamal as elg
from Crypto.Util.number import getRandomRange
from os import urandom
from Crypto import Random
from Crypto.Math.Primality import ( generate_probable_safe_prime, test_probable_prime, COMPOSITE )
from Crypto.Math.Numbers import Integer
import json


class AdditiveElgamalKey(elg.ElGamalKey):
    """Sub Class"""
    def __init__(self,randfunc=None,N=64): # N: max bit of msg  # added for additive HE
        super().__init__(randfunc)
        self.N=N

    def _encrypt(self, M, K):
        a=pow(self.g, K, self.p)
        b=( pow(self.y, K, self.p) * pow(self.g, M, self.p) ) % self.p   # added for additive HE
        return [int(a), int(b)]

    def _decrypt(self, M):
        if (not hasattr(self,'lookup')):
            self.lookup = {}
            for i in range(self.N):
                self.lookup[int(pow(self.g,i,self.p))] = i

        if (not hasattr(self, 'x')):
            raise TypeError('Private key not available in this object')

        r = Integer.random_range(min_inclusive=2,
                                 max_exclusive=self.p-1,
                                 randfunc=self._randfunc)
        a_blind = (pow(self.g, r, self.p) * M[0]) % self.p
        ax=pow(a_blind, self.x, self.p)
        plaintext_blind = (ax.inverse(self.p) * M[1] ) % self.p
        plaintext = (plaintext_blind * pow(self.y, r, self.p)) % self.p
        plaintext = self.lookup[int(plaintext)]  # added for additive HE
        return plaintext

def construct_additive(tup):
    r"""Construct an ElGamal key from a tuple of valid ElGamal components.
    The modulus *p* must be a prime.
    The following conditions must apply:
    .. math::
        \begin{align}
        &1 < g < p-1 \\
        &g^{p-1} = 1 \text{ mod } 1 \\
        &1 < x < p-1 \\
        &g^x = y \text{ mod } p
        \end{align}
    Args:
      tup (tuple):
        A tuple with either 3 or 4 integers,
        in the following order:
        1. Modulus (*p*).
        2. Generator (*g*).
        3. Public key (*y*).
        4. Private key (*x*). Optional.
    Raises:
        ValueError: when the key being imported fails the most basic ElGamal validity checks.
    Returns:
        an :class:`ElGamalKey` object
    """

    obj=AdditiveElgamalKey()
    if len(tup) not in [3,4]:
        raise ValueError('argument for construct() wrong length')
    for i in range(len(tup)):
        field = obj._keydata[i]
        setattr(obj, field, Integer(tup[i]))

    fmt_error = test_probable_prime(obj.p) == COMPOSITE
    fmt_error |= obj.g<=1 or obj.g>=obj.p
    fmt_error |= pow(obj.g, obj.p-1, obj.p)!=1
    fmt_error |= obj.y<1 or obj.y>=obj.p
    if len(tup)==4:
        fmt_error |= obj.x<=1 or obj.x>=obj.p
        fmt_error |= pow(obj.g, obj.x, obj.p)!=obj.y

    if fmt_error:
        raise ValueError("Invalid ElGamal key components")

    return obj
