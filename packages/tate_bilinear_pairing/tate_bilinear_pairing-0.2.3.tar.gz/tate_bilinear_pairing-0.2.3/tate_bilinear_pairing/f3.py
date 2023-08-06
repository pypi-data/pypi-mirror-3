"""
This module provides operations over the Galois Field $GF(3)$.
An element in $GF(3)$ is in the set of $\{0,1,2\}$, where arithmetic is performed modulo 3.
"""

_list1 = (0,1,2,0,1)
_list2 = (0,2,1)
_list3 = (0,1,2)
import random as _r

def add(a, b):
    '''addition modulo 3 of two elements in GF(3)
    for example, $add(2,2) == 1$, and $add(1,2) == 0$'''
    return _list1[a+b]

def neg(a):
    '''negation modulo 3 of one elements in GF(3)
    for example, $neg(2) == 1$, and $neg(1) == 2$'''
    return _list2[a]

def sub(a, b):
    '''substraction modulo 3 of two elements in GF(3)
    for example, $sub(2,2) == 0$, and $sub(1,2) == 2$'''
    return _list3[a-b]

def mult(a, b):
    '''multiplication modulo 3 of two elements in GF(3)
    for example, $mult(2,2) == 1$, and $mult(1,2) == 2$'''
    return _list1[a*b]

def random():
    '''returning a random element in GF(3)'''
    return _r.randint(0,2)
