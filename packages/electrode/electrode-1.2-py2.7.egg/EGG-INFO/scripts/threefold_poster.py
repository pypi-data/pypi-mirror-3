# -*- coding: utf-8 -*-
# <nbformat>3</nbformat>

# <codecell>

from numpy import *
from matplotlib import pyplot as plt
from scipy import constants
from electrode.transformations import euler_matrix
from electrode.system import System
from electrode.electrode import PointPixelElectrode, PolygonPixelElectrode
from electrode.pattern_constraints import (PatternValueConstraint,
    PatternRangeConstraint)
set_printoptions(precision=2)

# <codecell>

def hextess(n, points):
    x = vstack(array([[i+j*.5, j*3**.5*.5, 0]
        for j in range(-n-min(0, i), n-max(0, i)+1)])
        for i in range(-n, n+1))/(n+.5)
    if points:
        a = ones((len(x),))*3**.5/(n+.5)**2/2
        return PointPixelElectrode(points=x, areas=a)
    else:
        a = 1/(3**.5*(n+.5))
        p = x[:, None, :] + [[[a*cos(phi), a*sin(phi), 0] for phi in
            arange(pi/6, 2*pi, pi/3)]]
        return PolygonPixelElectrode(paths=list(p))
    

# <codecell>

def threefold(n, h, d, points=True):
    s = System()
    rf = hextess(n, points)
    rf.voltage_rf = 1.
    rf.name = "rf"
    s.electrodes.append(rf)
    ct = [PatternRangeConstraint(min=0, max=1.)]
    for p in 0, 4*pi/3, 2*pi/3:
        x = array([d/3**.5*cos(p), d/3**.5*sin(p), h])
        r = euler_matrix(p, pi/2, pi/4, "rzyz")[:3, :3]
        ct.append(PatternValueConstraint(d=1, x=x, r=r, v=[0, 0, 0]))
        ct.append(PatternValueConstraint(d=2, x=x, r=r,
            v=2**(-1/3.)*eye(3)*[1, 1, -2]))
    rf.pixel_factors, c = rf.optimize(ct, verbose=False)
    return s, c

# <codecell>

points=True; n=50; h=1/8.; d=1/4.
s, c = threefold(n, h, d, points=points)
x0 = array([d/3**.5, 0, h])
print "c*h**2*c:", h**2
print "rf'/c:", s.electrode("rf").potential(x0, 1)[0][:, 0]/c
print "rf''/c:", diag(s.electrode("rf").potential(x0, 2)[0][:, :, 0])/c

# <codecell>

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, aspect="equal")
s.plot_voltages(ax, u=array([1.]))
ax.autoscale()

# <codecell>

xs1, ps1 = s.saddle(x0+1e-2)
xs0, ps0 = s.saddle([0, 0, .8])
print "main saddle:", xs0, ps0
n = 50
xyz = mgrid[-d:d:1j*n, 0:1, .7*h:3*h:1j*n]
xyzt = xyz.transpose((1, 2, 3, 0)).reshape((-1, 3))
p = s.potential(xyzt)
xx, zz = xyz[0].reshape((n,n)), xyz[2].reshape((n,n))
pp = log(p).reshape((n,n))
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, aspect="equal")
ax.contour(xx, zz, pp, 20, cmap=plt.cm.hot)
ax.contour(xx, zz, pp, [log(ps0), log(ps1)], color="black")
ax.autoscale()

