"""
This module computes the Tate bilinear pairing.
"""

from . import f3m
from . import f33m
from . import f36m

def _algo4a(t, u):
    '''computing of $(-t^2 +u*s -t*p -p^2)^3$
    The algorithm is by J.Beuchat et.al, in the paper of "Algorithms and Arithmetic Operators for Computing
    the $eta_T$ Pairing in Characteristic Three", algorithm 4 in the appendix
    '''
    c0 = f3m.cubic(t) # c0 == t^3
    c1 = f3m.cubic(u)
    f3m.neg(c1, c1) # c1 == -u^3
    m0 = f3m.mult(c0, c0) # m0 == c0^2
    v0 = f3m.zero()
    f3m.neg(m0, v0) # v0 == -c0^2
    f3m.sub(v0, c0, v0) # v0 == -c0^2 -c0
    f3m._add2(v0) # v0 == -c0^2 -c0 -1
    v1 = c1
    v2 = f3m.one()
    f3m.sub(v2, c0, v2) # v2 == 1 -c0
    return [[v0, v1], [v2, f3m.zero()], [f3m.two(), f3m.zero()]]

def _algo4(xp, yp, xq, yq):
    re = f3m._m % 12
    xp = f3m._clone(xp)
    f3m._add1(xp) # xp == xp + b
    yp = f3m._clone(yp)
    if re == 1 or re == 11: 
        f3m.neg(yp, yp) # yp == -\mu*b*yp, \mu == 1 when re==1, or 11
    xq = f3m.cubic(xq) # xq == xq^3
    yq = f3m.cubic(yq) # yq == yq^3
    t = f3m.zero(); f3m.add(xp, xq, t) # t == xp+xq
    nt = f3m.zero()
    f3m.neg(t, nt) # nt == -t
    nt2 = f3m.mult(t, nt) # nt2 == -t^2
    v2 = f3m.mult(yp, yq) # v2 == yp*yq
    v1 = f3m.mult(yp, t) # v1 == yp*t
    if re == 7 or re == 11: # \lambda == 1
        nyp = f3m.zero(); f3m.neg(yp, nyp) # nyp == -yp
        nyq = f3m.zero(); f3m.neg(yq, nyq) # nyq == -yq
        a1 = [[v1, nyq], [nyp, f3m.zero()], [f3m.zero(), f3m.zero()]]
        # a1 == \lambda*yp*t -\lambda*yq*s -\lambda*yp*p
    else: # \lambda == -1
        f3m.neg(v1, v1) # v1 == -yp*t
        a1 = [[v1, yq], [yp, f3m.zero()], [f3m.zero(), f3m.zero()]]
    a2 = [[nt2, v2], [nt, f3m.zero()], [f3m.two(), f3m.zero()]] 
    # a2 == -t^2 +yp*yq*s -t*p -p^2
    R = f36m.mult(a1, a2)
    for _ in range((f3m._m - 1) // 2):
        R = f36m.cubic(R)
        xq = f3m.cubic(xq)
        xq = f3m.cubic(xq)
        f3m._add2(xq) # xq <= xq^9-b
        yq = f3m.cubic(yq)
        yq = f3m.cubic(yq)
        f3m.neg(yq, yq) # yq <= -yq^9
        f3m.add(xp, xq, t) # t == xp+xq
        f3m.neg(t, nt) # nt == -t
        nt2 = f3m.mult(t, nt) # nt2 == -t^2
        u = f3m.mult(yp, yq) # u == yp*yq
        S = [[nt2, u], [nt, f3m.zero()], [f3m.two(), f3m.zero()]]
        R = f36m.mult(R, S)
    return R

def _algo5(xp, yp, xq, yq):
    '''computing the $\eta_T$ pairing
    This is the algorithm 5 in the paper above. 
    
    :param xp: the x coordinate of element $P=[xp, yp]$
    :type xp: list
    :param yp: the y coordinate of element $P=[xp, yp]$
    :type yp: list
    :param xq: the x coordinate of element $R=[xq, yq]$
    :type xq: list
    :param yq: the y coordinate of element $R=[xq, yq]$
    :type yq: list
    :returns: \eta_T(P,Q)
    '''
    re = f3m._m % 12
    xp = f3m._clone(xp)
    f3m._add1(xp) # xp == xp + b
    yp = f3m._clone(yp)
    if re == 1 or re == 11: 
        f3m.neg(yp, yp) # yp == -\mu*b*yp, \mu == 1 when re==1, or 11
    xq = f3m.cubic(xq) # xq == xq^3
    yq = f3m.cubic(yq) # yq == yq^3
    t = f3m.zero(); f3m.add(xp, xq, t) # t == xp+xq
    nt = f3m.zero()
    f3m.neg(t, nt) # nt == -t
    nt2 = f3m.mult(t, nt) # nt2 == -t^2
    v2 = f3m.mult(yp, yq) # v2 == yp*yq
    v1 = f3m.mult(yp, t) # v1 == yp*t
    if re == 7 or re == 11: # \lambda == 1
        nyp = f3m.zero(); f3m.neg(yp, nyp) # nyp == -yp
        nyq = f3m.zero(); f3m.neg(yq, nyq) # nyq == -yq
        a1 = [[v1, nyq], [nyp, f3m.zero()], [f3m.zero(), f3m.zero()]]
        # a1 == \lambda*yp*t -\lambda*yq*s -\lambda*yp*p
    else: # \lambda == -1
        f3m.neg(v1, v1) # v1 == -yp*t
        a1 = [[v1, yq], [yp, f3m.zero()], [f3m.zero(), f3m.zero()]]
    a2 = [[nt2, v2], [nt, f3m.zero()], [f3m.two(), f3m.zero()]] 
    # a2 == -t^2 +yp*yq*s -t*p -p^2
    R = f36m.mult(a1, a2)
    nu = f3m.zero()
    for _ in range((f3m._m - 1) // 4):
        R = f36m.cubic(R)
        R = f36m.cubic(R) # R <= R^9
        xq = f3m.cubic(xq)
        xq = f3m.cubic(xq)
        f3m._add2(xq) # xq <= xq^9-b
        yq = f3m.cubic(yq)
        yq = f3m.cubic(yq) # yq <= yq^9
        f3m.add(xp, xq, t) # t == xp+xq
        u = f3m.mult(yp, yq) # u == yp*yq
        f3m.neg(u, nu) # nu == -yp*yq
        S = _algo4a(t, nu) # S == (-t^2 -u*s -t*p -p^2)^3
        xq = f3m.cubic(xq)
        xq = f3m.cubic(xq)
        f3m._add2(xq) # xq <= xq^9-b
        yq = f3m.cubic(yq)
        yq = f3m.cubic(yq) # yq <= yq^9
        f3m.add(xp, xq, t) # t == xp+xq
        u = f3m.mult(yp, yq) # u == yp*yq
        f3m.neg(t, nt) # nt == -t
        nt2 = f3m.mult(t, nt) # nt2 == -t^2
        S2 = [[nt2, u], [nt, f3m.zero()], [f3m.two(), f3m.zero()]] # S2 == -t^2 +u*s -t*p -p^2
        S = f36m.mult(S, S2)
        R = f36m.mult(R, S)
    return R

def _algo6(u):
    '''computation of $U ^ {3^{3m} - 1}$
    This is the algorithm 6 in the paper above. '''
    u0, u1 = u[0]
    u2, u3 = u[1]
    u4, u5 = u[2]
    v0 = [u0, u2, u4]
    v1 = [u1, u3, u5]
    m0 = f33m.mult(v0, v0)
    m1 = f33m.mult(v1, v1)
    m2 = f33m.mult(v0, v1)
    a0 = f33m.zero()
    f33m.sub(m0, m1, a0)
    a1 = f33m.zero()
    f33m.add(m0, m1, a1)
    i = f33m.inverse(a1)
    v0 = f33m.mult(a0, i)
    v1 = f33m.mult(m2, i)
    a0, a1, a2 = v0
    a3, a4, a5 = v1
    return [[a0, a3], [a1, a4], [a2, a5]]

def _algo7(u):
    '''computation of $U ^ {3^m+1}$, $U \in T_2(F_{3^3M})$
    This is the algorithm 7 in the paper above.'''
    u0, u1 = u[0]
    u2, u3 = u[1]
    u4, u5 = u[2]
    a0, a1, a2, a3, a4, a5, a6 = f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero()
    f3m.add(u0, u1, a0)
    f3m.add(u2, u3, a1)
    f3m.sub(u4, u5, a2)
    m0 = f3m.mult(u0, u4)
    m1 = f3m.mult(u1, u5)
    m2 = f3m.mult(u2, u4)
    m3 = f3m.mult(u3, u5)
    m4 = f3m.mult(a0, a2)
    m5 = f3m.mult(u1, u2)
    m6 = f3m.mult(u0, u3)
    m7 = f3m.mult(a0, a1)
    m8 = f3m.mult(a1, a2)
    f3m.add(m5, m6, a3)
    f3m.sub(a3, m7, a3)
    f3m.neg(m2, a4)
    f3m.sub(a4, m3, a4)
    f3m.sub(m3, m2, a5)
    f3m.sub(m1, m0, a6)
    f3m.add(a6, m4, a6)
    v0, v1, v2, v3, v4, v5 = f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero(), f3m.zero()
    if f3m._m % 6 == 1:
        f3m.add(m0, m1, v0)
        f3m.add(v0, a4, v0)
        f3m._add1(v0)
        f3m.sub(m5, m6, v1)
        f3m.add(v1, a6, v1)
        f3m.sub(a4, a3, v2)
        f3m.add(m8, a5, v3)
        f3m.sub(v3, a6, v3)
        f3m.add(a3, a4, v4)
        f3m.neg(v4, v4)
        f3m.add(m8, a5, v5)
    else: # f3m._m % 6 == 5
        f3m.add(m0, m1, v0)
        f3m.sub(v0, a4, v0)
        f3m._add1(v0)
        f3m.sub(m6, m5, v1)
        f3m.add(v1, a6, v1)
        v2 = a3
        f3m.add(m8, a5, v3)
        f3m.add(v3, a6, v3)
        f3m.add(a3, a4, v4)
        f3m.neg(v4, v4)
        f3m.add(m8, a5, v5)
        f3m.neg(v5, v5)
    return [[v0, v1], [v2, v3], [v4, v5]]

def _algo8(u):
    '''computing U^M, M=(3^{3m}-1)*(3^m+1)*(3^m+1-\mu*b*3^{(m+1)//2})
    This is the algorithm 8 in the paper above. '''
    v = _algo6(u)
    v = _algo7(v)
    w = v
    for _ in range((f3m._m + 1) // 2):
        w = f36m.cubic(w)
    v = _algo7(v)
    m = f3m._m
    if m % 12 in [1, 11]:
        w0, w1 = w[0]
        w2, w3 = w[1]
        w4, w5 = w[2]
        f3m.neg(w1, w1)
        f3m.neg(w3, w3)
        f3m.neg(w5, w5)
        w = [[w0, w1], [w2, w3], [w4, w5]]
    return f36m.mult(v, w)

def pairing(x1, y1, x2, y2):
    '''computing the Tate bilinear pairing
    
    :param x1: the x coordinate of element $P=[x1, y1]$
    :type x1: list
    :param y1: the y coordinate of element $P=[x1, y1]$
    :type y1: list
    :param x2: the x coordinate of element $R=[x2, y2]$
    :type x2: list
    :param y2: the y coordinate of element $R=[x2, y2]$
    :type y2: list
    :returns: the result
    '''
    v = _algo5(x1, y1, x2, y2)
    return _algo8(v)
