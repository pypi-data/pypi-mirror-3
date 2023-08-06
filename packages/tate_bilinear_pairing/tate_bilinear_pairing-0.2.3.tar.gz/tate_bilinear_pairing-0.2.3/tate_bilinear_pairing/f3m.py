"""
This module provides operations over the Galois Field $GF(3^m)$, where $m$ is 97.
$GF(3^m)$ is an extension field of $GF(3)$, and the degree of the extension is $m$.
In this module, an element of $GF(3^m)$ is a list of length $m$, where each element is in $GF(3)$. 
"""

from . import it
from . import f3

'''degree of the irreducible polynomial'''
m = 97

def E(value = None):
    '''returning an element in $GF(3^m)$ with a given value, that is a list of length $m$.
    the optional argument value should be a list no longer than $m$.
    Usage:
        E() == [0]*m
        E([1]) == [1] + [0]*(m-1)
    '''
    if value is not None:
        p2 = [0]*(m-len(value))
        return value + p2
    else:
        return [0]*m

def zero():
    'returning the zero element in $GF(3^m)$, which is $[0]*m$'
    return [0]*m

def one():
    'returning the element with value of one in $GF(3^m)$, which is $[1]+[0]*(m-1)$'
    a = [0]*m
    a[0] = 1
    return a

def two():
    'returning the element with value of two in $GF(3^m)$, which is $[2]+[0]*(m-1)$'
    a = [0]*m
    a[0] = 2
    return a

def random():
    'returning a random element in $GF(3^m)$'
    a = [0] * m
    for i in range(m):
        a[i] = f3.random()
    return a

def add(a, b, c):
    '''doing addition
    The function sets the value of $c$ as $a+b$, and returns nothing.'''
    l = max(len(a), len(b), len(c))
    for i in range(l):
        c[i] = f3.add(a[i], b[i])

def neg(a, c):
    '''doing negation
    The functions sets the value of $c$ as $-a$ and returns nothing.'''
    for i in range(max(len(a), len(c))):
        c[i] = f3.neg(a[i])

def sub(a, b, c):
    '''doing substraction
    note that $add$, $neg$, $sub$ are performed element-wisely.
    The function sets the value of $c$ as $a-b$, and returns nothing.'''
    l = max(len(a), len(b), len(c))
    for exp in range(l):
        c[exp] = f3.sub(a[exp], b[exp])

def reduct(a):
    '''doing reduction
    The function returns the value of $a$ modulo $the irreducible trinomial$.'''
    if len(a) >= m:
        p_m = m
        p_t = it.table[p_m]
        for exp in range(len(a)-1, p_m-1, -1):
            if a[exp] != 0:
                v = a[exp]
                dest_exp = exp - p_m + p_t
                a[dest_exp] = f3.sub(a[dest_exp], v)
                dest_exp = exp - p_m
                a[dest_exp] = f3.add(a[dest_exp], v)
        del a[p_m:] # a[:] = a[:p_m]

def _f1(number, a, c):
    '''doing multiplication of a constant $number$ and an element $a$ in GF(3^m)
    The function setts $c == number * a$ and returns nothing.'''
    for i in range(max(len(a), len(c))):
        c[i] = f3.mult(number, a[i])
    return c

def _f2(a):
    '''right-shifting $a$ by one element then doing a reduction'''    
    a.insert(0, 0)
    reduct(a)

def mult(a, b):
    '''doing multiplication in GF(3^m)
    The function returns $a*b \in GF(3^m)$'''
    a = E(a) # clone
    c = E()
    t = E()
    for i in range(len(b)):
        _f1(b[i], a, t) # t == b[i]*a in GF(3^m)
        add(c, t, c) # c += b[i]*a in GF(3^m)
        a.insert(0, 0)
        reduct(a) # a == a*x
    return c

def cubic(a):
    '''computing the cubic of an element $a$ in GF(3^m), and returning $a^3$
    '''
    b = [0] * (3*len(a)-2)
    for i in range(len(a)):
        b[3*i] = a[i]
    reduct(b)
    return b

def inverse(a):
    '''computing the inversion of an element $a$ in GF(3^m).
    The algorithm is by Tim Kerins, Emanuel Popovici and William Marnane
    in the paper of "Algorithms and Architectures for use in FPGA",
    Lecture Notes in Computer Science, 2004, Volume 3203/2004, 74-83.'''
    p_t = it.table[m]
    S = [0] * (m+1) # S = p(x)
    S[m] = 1; S[p_t] = 1; S[0] = 2
    R = E(a) # clone
    R.append(0) 
    t = [0] * (m+1)
    U = one()
    V = zero()
    t2 = E()
    d = 0
    for _ in range(2*m):
        r_m = R[m]
        s_m = S[m]
        if r_m == 0:
            R.insert(0, 0) # R = xR
            S.append(0)
            t.append(0)
            _f2(U) # U = xU mod p
            d += 1
        else:
            q = f3.mult(r_m, s_m)
            _f1(q, R, t)
            sub(S, t, S) # S = S-qR
            _f1(q, U, t2)
            sub(V, t2, V) # V = V-qU
            S.insert(0, 0) # S = xS
            R.append(0)
            t.append(0)
            if d == 0:
                R, S = S, R
                U, V = V, U
                _f2(U) # U = xU mod p
                d += 1
            else:
                U.append(0)
                while U[0] != 0:
                    # U += P
                    U[m] = f3.add(U[m], 1)
                    U[p_t] = f3.add(U[p_t], 1)
                    U[0] = f3.add(U[0], 2)
                del U[0] # divide U by $x$
                d -= 1
    r_m = R[m]
    _f1(r_m, U, U)
    return U[:m]
