#!/usr/bin/python
# .+
#
# .context    : Algebra
# .title      : Quaternion Algebra
# .kind	      : python source
# .author     : Marco Abrate
# .site	      : Torino - Italy
# .creation   :	15-Nov-2011
# .copyright  :	(c) 2011 Marco Abrate
# .license    : GNU General Public License
#
# qmath is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# qmath is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qmath. If not, see <http://www.gnu.org/licenses/>.
#
# .-


# import required modules

import math
import cmath
import numpy as np

## module information
## qmath - a Python module to manipulate quaternions

__author__ = 'Marco Abrate <abrate.m@gmail.com>'
__license__ = '>= GPL v3'
__version__ = '0.1.1'


class AlgebraicError(Exception):
  "Algebraic error exception"
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class quaternion:
    "Quaternion algebra"
    
    def __init__(self, q, vector = None):
        """
        Initializes the quaternion.
        The following types can be converted to quaternion:
        - Numbers (real or complex);
        - lists or numpy arrays of the components with respect to 1,i,j and k; 
        - strings of the form 'a+bi+cj+dk';
        - pairs (rotation angle, axis of rotation);
        - lists whose components are Euler angles;
        - 3X3 orthogonal matrices representing rotations

        >>> import qmath
        >>> qmath.quaternion([1,2,3,4])
        (1.0+2.0i+3.0j+4.0k)
        >>> qmath.quaternion(np.array([1,2,3,4]))
        (1.0+2.0i+3.0j+4.0k)
        >>> qmath.quaternion(1)
        (1.0)
        >>> qmath.quaternion(1+1j)
        (1.0+1.0i)
        >>> qmath.quaternion('1+1i+3j-2k')
        (1.0+1.0i+3.0j-2.0k)
        """
        
        if q.__class__ == quaternion:
            self.q = q.value()

        elif type(q) == type(np.array([])) and q.shape == (3, 3):
            self.euler = MatrixToEuler(q)
            self.q = EulerToQuaternion(self.euler)
            
        elif type(q) == list or type(q) == type(np.array([])):
            if len(q) == 4:
                self.q = 1.0 * np.array(q)
            elif len(q) == 3:
                self.q = EulerToQuaternion(q)
                
            else:
                pass
            
        elif (type(q) == int or type(q) == float or type(q) == type(1.0 * np.array([1])[0])) and vector == None:
            self.q = 1.0 * np.array([q,0.,0.,0.])
            
        elif type(q) == complex:
            self.q = 1.0 * np.array([q.real,q.imag,0,0])
        
        elif type(q) == str:
            self.q = StringToQuaternion(q).value()

        elif vector:
            try:
                self.q = RotationToQuaternion(q, vector)
            except:
                pass
    
        else:
            pass
        return

    
    def __repr__(self):
        "Algebraic representation of a quaternion"
        
        try:
            self.string = ''
            self.basis = ['','i','j','k']
            if self.norm() != 0:
                for self.count in range(4):
                    if self.q[self.count] > 0:
                        self.string = self.string + '+' + str(abs(self.q[self.count])) + self.basis[self.count]
                    elif self.q[self.count] < 0:
                        self.string = self.string + '-' + str(abs(self.q[self.count])) + self.basis[self.count]
            else:
                self.string = str(0.0)

            if self.string[0] == '+':
                self.string = self.string[1:]
            return '(' + self.string + ')'
        except:
            raise AlgebraicError, 'can not convert' + str(q) + ' to quaternion'

    def __getitem__(self, key):
        """
        >>> import qmath
        >>> a = qmath.quaternion('1+2i-2k')
        >>> a[1]
        2.0
        """
        return self.q[key]
        
    def __setitem__(self,key,value):
        """
        >>> import qmath
        >>> a = qmath.quaternion('1+2i-2k')
        >>> a[1] = 7
        >>> a
        (1.0+7.0i-2.0k)
        """
        self.q[key] = value
        return quaternion(self.q)
        

    def __delitem__(self,key):
        """
        >>> import qmath
        >>> q = qmath.quaternion([1,2,3,4])
        >>> del q[1]
        >>> q
        (1.0+3.0j+4.0k)
        """
        if 0 <= key <= 3:
            self[key] = 0
            return self
        else:
            raise IndexError, 'list index out of range'

    def __delslice__(self, n, m):
        """
        >>> import qmath
        >>> q = qmath.quaternion([1,2,3,4])
        >>> del q[1:3]
        >>> q
        (1.0)
        """
        if n >= 0 and m <=3:
            if n <= m:
                for self.count in range(n,m + 1):
                    del self[self.count]
            else:
                for self.count in range(m,n + 1):
                    del self[self.count]
        else:
            raise IndexError, 'quaternion index out of range'

    def __contains__(self, item):
        """
        >>> import qmath
        >>> q = qmath.quaternion('1+1i+5k')
        >>> 'j' in q
        False
        >>> 'i' in q
        True
        """
        
        if item == 'i':
            return self.q[1] != 0
        elif item == 'j':
            return self.q[2] != 0
        elif item == 'k':
            return self.q[3] != 0
        else:
            return False

    def __or__(self,other):
        """
        >>> import qmath
        >>> qmath.quaternion(1)|3
        ((1.0), 3)
        """
        return (self, other)

    def __lt__(self, other):
        """
        >>> import qmath
        >>> a = qmath.quaternion('1i')
        >>> a < 0
        Traceback (most recent call last):
        TypeError: no ordering relation is defined for quaternion numbers
        """
        raise TypeError, 'no ordering relation is defined for quaternion numbers'

    def __le__(self, other):
        """
        >>> import qmath
        >>> a = qmath.quaternion('1i')
        >>> a <= 0
        Traceback (most recent call last):
        TypeError: no ordering relation is defined for quaternion numbers
        """
        raise TypeError, 'no ordering relation is defined for quaternion numbers'
    
    def __eq__(self, other):
        """
        >>> import qmath
        >>> q = qmath.quaternion('1+1k')
        >>> q == 0
        False
        >>> q == '1+1k'
        True
        >>> q == qmath.quaternion([1,0,1e-15,1])|1e-9
        True
        >>> q == [1,1,1e-15,0]
        False
        
        """
        if type(other) == tuple:
            try:
                return self.equal(other[0],other[1])
            except:
                raise TypeError, str(self) + ' and ' + str(other[0]) + ' can not be compared'
        else:
            return self.equal(other)
    
    def __ne__(self, other):
        """
        >>> import qmath
        >>> q = qmath.quaternion('1+1k')
        >>> q != 0
        True
        >>> q != '1+1k'
        False
        """
        return not self == other

    def __gt__(self, other):
        """
        >>> import qmath
        >>> a = qmath.quaternion('1i')
        >>> a > 0
        Traceback (most recent call last):
        TypeError: no ordering relation is defined for quaternion numbers
        """
        raise TypeError, 'no ordering relation is defined for quaternion numbers'
    
    def __ge__(self, other):
        """
        >>> import qmath
        >>> a = qmath.quaternion('1i')
        >>> a >= 0
        Traceback (most recent call last):
        TypeError: no ordering relation is defined for quaternion numbers
        """
        raise TypeError, 'no ordering relation is defined for quaternion numbers'

    def __iadd__(self, other):
        """
        >>> import qmath
        >>> q = qmath.quaternion([1,2,0,3])
        >>> q += qmath.quaternion([2,1,3,0])
        >>> q
        (3.0+3.0i+3.0j+3.0k)
        """
        self.other = quaternion(other)
        return quaternion(self.q + self.other.value())
        
    def __isub__(self, other):
        """
        >>> import qmath
        >>> q = qmath.quaternion([1,2,0,3])
        >>> q -= qmath.quaternion([2,1,3,0])
        >>> q
        (-1.0+1.0i-3.0j+3.0k)
        """
        self.other = quaternion(other)
        self += - self.other
        return self

    def __imul__(self, other):
        """
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> b = qmath.quaternion(3-4j)
        >>> a *= b
        >>> a
        (11.0+2.0i-7.0j+24.0k)
        """
        self.p = quaternion(other)
        try:
            self.vect = self.q[0] * self.p.value()[1:] + self.p.value()[0] * self.q[1:] + np.cross(self.q[1:],self.p.value()[1:])
            return quaternion(np.array([self.q[0] * self.p.value()[0] - np.dot(self.q[1:],self.p.value()[1:])] + self.vect.tolist()))
        except:
            return quaternion(other)

    def __idiv__(self, other):
        """
        Right multiplication by the inverse of p, if p is invertible

        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> b = qmath.quaternion(3-4j)
        >>> a /= b
        >>> a
        (-0.2+0.4i+1.0j)
        >>> a /= qmath.quaternion(0)
        Traceback (most recent call last):
        AlgebraicError: '(0.0) is not invertible'
        """
        self.p = quaternion(other)
        try:
            return self * self.p.inverse()
        except:
            raise AlgebraicError, str(quaternion(other)) + ' is not invertible'


    def __add__(self, other):
        "Quaternion addiction"
        """
        >>> import qmath
        >>> qmath.quaternion([1,2,0,3]) + quaternion.quaternion([2,1,3,0])
        (3.0+3.0i+3.0j+3.0k)
        """
        self += other
        return self


    def __sub__(self,other):
        "Quaternion subtraction"
        """
        >>> import qmath
        >>> qmath.quaternion([1,2,0,3]) - qmath.quaternion([2,1,3,0])
        (-1.0+1.0i-3.0j+3.0k)
        """
        self -= other
        return self

    def __mul__(self, other):
        """
        Quaternion right multiplication by p:
        i**2 = j**2 = k**2 = -1, i*j = k

        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> b = qmath.quaternion(3-4j)
        >>> a * b
        (11.0+2.0i-7.0j+24.0k)
        """
        self *= other
        return self
    
    def __div__(self, other):
        """
        Right multiplication by the inverse of p, if p is invertible

        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> b = qmath.quaternion(3-4j)
        >>> a / b
        (-0.2+0.4i+1.0j)
        >>> a / qmath.quaternion(0)
        Traceback (most recent call last):
        AlgebraicError: '(0.0) is not invertible'
        """
        self /= other
        return self 

    def __rmul__(self, other):
        """
        Quaternion left multiplication by p.

        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> b = qmath.quaternion(3-4j)
        >>> a.__rmul__(b)
        (11.0+2.0i+25.0j)
        >>> 3 * a
        (3.0+6.0i+9.0j+12.0k)
        """
        return quaternion(other) * self

    def __rdiv__(self, other):
        """
        Left multiplication by the inverse of p, if p is invertible
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> b = qmath.quaternion(3-4j)
        >>> a.__rdiv__(b)
        (-0.2+0.4i-0.28j+0.96k)
        """
        return quaternion(other).inverse() * self
        
    def __neg__(self):
        """
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> -a
        (-1.0-2.0i-3.0j-4.0k)
        """
        return quaternion(-1 * self.q)
    
    def __pow__(self,e):
        """
        Returns the integer power of a quaternion.
        If the basis is invertible exponent can be negative.

        >>> import qmath
        >>> base = qmath.quaternion('1+1i+2j-2k')
        >>> base ** 3
        (-26.0-6.0i-12.0j+12.0k)
        >>> base ** (-2)
        (-0.08-0.02i-0.04j+0.04k)
        >>> qmath.quaternion([-5,1,0,1]) ** (1.0/3)
        (1.0+1.0i+1.0k)
        >>> qmath.quaternion([-5,1,0,1]) ** (2.0/3)
        (-1.0+2.0i+2.0k)
        >>> qmath.quaternion('1.0+1.0i+1.0k') ** 2
        (-1.0+2.0i+2.0k)
        """
        if math.floor(e) == e:
            self.e = int(e)
            if self.e > 0:
                self.u = quaternion(self.q)
                self.pow = quaternion(1)
                while self.e > 0:
                    if self.e % 2 == 1:
                        self.pow = self.pow * self.u
                    self.u = self.u * self.u
                    self.e = self.e / 2
                return self.pow
            elif self.e == 0:
                self.pow = quaternion(1)
                return self.pow
            else:
                try:
                    self.pow = self.inverse() ** (-e)
                    return self.pow
                except:
                    raise AlgebraicError, str(self) + ' is not invertible'

        elif math.floor(2 * e) == 2 * e:
            return self ** int(math.floor(e)) * self.sqrt()

        elif math.floor(3 * e) == 3 * e:
            if int(math.floor(3 * e)) % 3 == 1:
                return self ** int(math.floor(e)) * self.croot()
            elif int(math.floor(3 * e)) % 3 == 2:
                return self ** int(math.floor(e)) * (self.croot()) ** 2
                          
        else:
            raise AlgebraicError, 'a quaternion power can be computed only for integer powers or half of an integer'

    def __abs__(self):
        """
        Returns the modulus of the quaternion
        >>> import qmath
        >>> a = qmath.quaternion([0,0,-3,4])
        >>> abs(a)
        5.0
        """
        
        self.abs = math.sqrt(self.norm())
        return self.abs

    def equal(self, other, tolerance = 0):
        """
        Quarternion equality with arbitrary tolerance
        >>> import qmath
        >>> a = qmath.quaternion([1,1,1e-15,0])
        >>> b = qmath.quaternion(1+1j)
        >>> a.equal(b,1e-9)
        True
        >>> a.equal(b)
        False
        """
        for self.count in range(4):
            if abs(self.q[self.count] - quaternion(other).value()[self.count]) <= tolerance:
                pass
            else:
                return False
        return True

           
    def value(self):
        try:
            return self.q
        except:
            raise AlgebraicError, str(q) + ' is not a quaternion'

    def real(self):
        """
        Returns the real part of the quaternion
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> a.real()
        (1.0)
        """
        return quaternion(self.q.dot([1,0,0,0]))

    def imag(self):
        """
        Returns the imaginary part of the quaternion
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> a.imag()
        (2.0i+3.0j+4.0k)
        """
        return self - self.real()      

    def trace(self):
        """
        Returns the trace of the quaternion
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> a.trace()
        2.0
        """
        return 2 * self.q[0]
        
    def conj(self):
        """
        Returns the conjugate of the quaternion
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> a.conj()
        (1.0-2.0i-3.0j-4.0k)
        """
        return self.real() - self.imag()

    def norm(self):
        """
        Returns the norm of the quaternion (the square of the modulus)
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> a.norm()
        30.0
        """
        return self.q[0] ** 2 + self.q[1] ** 2 + self.q[2] ** 2 + self.q[3] ** 2

    def delta(self):
        """
        >>> import qmath
        >>> a = qmath.quaternion([1,2,3,4])
        >>> a.delta()
        -29.0
        """
        return self.q[0] ** 2 - self.norm()

    def inverse(self):
        """
        Quaternionic inverse, if it exists
        >>> import qmath
        >>> a = qmath.quaternion([2,-2,-4,-1])
        >>> a.inverse()
        (0.08+0.08i+0.16j+0.04k)
        >>> zero = qmath.quaternion(0)
        >>> zero.inverse()
        Traceback (most recent call last):
        AlgebraicError: '(0.0) is not invertible'
        """
        if self == 0:
            raise AlgebraicError, str(self) + ' is not invertible'
        else:
            return self.conj() * (1 / self.norm())
            
    def unitary(self):
        """
        Returns the normalized quaternion.
        >>> import qmath
        >>> a = qmath.quaternion('1+1i+1j-1k')
        >>> a.unitary()
        (0.5+0.5i+0.5j-0.5k)
        >>> zero = qmath.quaternion(0)
        >>> zero.unitary()
        Traceback (most recent call last):
        AlgebraicError: '(0.0) has no direction'
        """
        if self != 0:
            return self / abs(self)
        else:
            raise AlgebraicError, str(quaternion(self.q)) + ' has no direction'

    def sqrt(self):
        """
        Computes the square root of a quaternion.
        If q has only two roots, the one with positive trace is given.
        If this method returns r, also -r is a root.
        >>> import qmath
        >>> qmath.quaternion([3,5,0,-4]).sqrt()
        (2.24399953341+1.11408222808i-0.891265782468k)
        """
        self.nu = math.sqrt(self.norm())
        self.tau = math.sqrt(2 * self.nu + self.trace())
        if self.tau != 0:
            self.solution = (self.q + np.array([self.nu,0,0,0])) / self.tau
            return quaternion(self.solution)
        else:
            return str(self) + ' has infinitely many square roots:\n every (a i+b j+c k) such that\n a ** 2 + b ** 2 + c ** 2 = ' + str(self.nu)

    def croot(self):
        """
        Computes the cube root of a quaternion.
        >>> import qmath
        >>> qmath.quaternion([-5,1,0,1]).croot()
        (1.0+1.0i+1.0k)
        """
        self.nu = math.pow(self.norm(), 1.0/3)
        self.tau = (self.q[0] + cmath.sqrt(self.delta())).__pow__(1.0/3) + (self.q[0] - cmath.sqrt(self.delta())).__pow__(1.0/3)
        if self.tau ** 2 - self.nu != 0:
            self.solution = (self.q + np.array([self.nu * self.tau,0,0,0])) / (self.tau ** 2 - self.nu)
            return quaternion(self.solution)
        else:
            return str(self) + ' has infinitely many cubic roots'

    def QuaternionToRotation(self):
        """
        Converts the quaternion, if unitary, into a rotation matrix
        >>> import qmath
        >>> q = qmath.quaternion(3-4j)
        >>> q.QuaternionToRotation()
        Traceback (most recent call last):
        AlgebraicError: 'the quaternion must be unitary'
        >>> M = q.unitary().QuaternionToRotation()
        >>> M
        array([[ 1.  , -0.  ,  0.  ],
               [ 0.  , -0.28,  0.96],
               [-0.  , -0.96, -0.28]])
        >>> qmath.quaternion(M).equal(q.unitary(),1e-12)
        True
        """
        if quaternion(self.norm()) == quaternion(1.0)|1e-9:
            return np.array([[self.q[0] ** 2 + self.q[1] ** 2 - self.q[2] ** 2 - self.q[3] ** 2, 2 * (self.q[1] * self.q[2] - self.q[0] * self.q[3]), 2 * (self.q[0] * self.q[2] + self.q[1] * self.q[3]) ],
                             [2 * (self.q[1] * self.q[2] + self.q[0] * self.q[3]), self.q[0] ** 2 - self.q[1] ** 2 + self.q[2] ** 2 - self.q[3] ** 2, 2 * (self.q[3] * self.q[2] - self.q[0] * self.q[1])],
                             [2 * (self.q[1] * self.q[3] - self.q[0] * self.q[2]), 2 * (self.q[1] * self.q[0] + self.q[2] * self.q[3]), self.q[0] ** 2 - self.q[1] ** 2 - self.q[2] ** 2 + self.q[3] ** 2]]) / self.__abs__()
        else:
            raise AlgebraicError, 'the quaternion must be unitary'

def real(quat):
    """
    >>> import qmath
    >>> qmath.real(1+3j)
    (1.0)
    """
    q = quaternion(quat)
    return q.real()

def imag(quat):
    """
    >>> import qmath
    >>> qmath.imag([1,2,3,4])
    (2.0i+3.0j+4.0k)
    """
    q = quaternion(quat)
    return q.imag()      

def trace(quat):
    """
    >>> import qmath
    >>> qmath.trace([1,2,3,4])
    2.0
    """
    q = quaternion(quat)
    return q.trace()
        
def conj(quat):
    """
    >>> import qmath
    >>> qmath.conj([1,2,3,4])
    (1.0-2.0i-3.0j-4.0k)
    """
    q = quaternion(quat)
    return q.conj()

def norm(quat):
    """
    >>> import qmath
    >>> qmath.norm([1,2,3,4])
    30.0
    """
    q = quaternion(quat)
    return q.norm()

def delta(quat):
    """
    >>> import qmath
    >>> qmath.delta([1,2,3,4])
    -29.0
    """
    q = quaternion(quat)
    return q.delta()

def inverse(quat):
    """
    >>> import qmath
    >>> qmath.inverse([2,-2,-4,-1])
    (0.08+0.08i+0.16j+0.04k)
    """
    q = quaternion(quat)
    return q.inverse()
            
def unitary(quat):
    """
    >>> import qmath
    >>> qmath.unitary('1+1i+1j-1k')
    (0.5+0.5i+0.5j-0.5k)
    """ 
    q = quaternion(quat)
    return q.unitary()

def sqrt(quat):
    """
    >>> import qmath
    >>> qmath.sqrt([3,5,0,-4])
    (2.24399953341+1.11408222808i-0.891265782468k)
    """
    q = quaternion(quat)
    return q.sqrt()

def croot(quat):
    """
    >>> import qmath
    >>> qmath.croot([-5,1,0,1])
    (1.0+1.0i+1.0k)
    """
    q = quaternion(quat)
    return q.croot()

def StringToQuaternion(string):
    """
    Converts a string into a quaternion
    """
    if string[0] == '+' or string[0] == '-':
        a = string
    else:
        a = '+' + string           
    components = ['','','','']
    count = 0
    while max(a.rfind('-'),a.rfind('+')) != -1:
        components[count]=a[max(a.rfind('-'),a.rfind('+')):]
        a = a[:max(a.rfind('-'),a.rfind('+'))]
        count = count + 1
    q = np.array([0.,0.,0.,0.])
    try:
        for component in components:
            if len(component) > 0:
                if component[len(component) - 1] == 'k':
                    q[3] = float(component[:len(component) - 1])
                elif component[len(component) - 1] == 'j':
                    q[2] = float(component[:len(component) - 1])
                elif component[len(component) - 1] == 'i':
                    q[1] = float(component[:len(component) - 1])
                else:
                    q[0] = float(component[:len(component)])
        return quaternion(q)
    except:
        raise AlgebraicError, string + ' can not be converted to quaternion'

def MatrixToEuler(matrix):
    """
    Converts a 3X3 matrix into a vector having Euler angles as components
    """
    if matrix.shape == (3, 3):
        try:
            theta = math.asin(- matrix[2][0])
            if math.cos(theta) != 0:
                try:
                    psi = math.atan2(matrix[2][1] / math.cos(theta), matrix[2][2] / math.cos(theta))
                except:
                    psi = math.atan(matrix[2][1])
                try:
                    phi = math.atan2(matrix[1][0] / math.cos(theta), matrix[0][0] / math.cos(theta))
                except:
                    phi = math.atan(matrix[1][0])
            else:
                phi = theta
                psi = math.arcsin(matrix[1][1])
            return [phi, theta, psi]
        except:
            raise AlgebraicError, 'the matrix is not orthogonal'
                      
def EulerToQuaternion(angles):
    """
    Converts a vector whose components are Euler angles into a quaternion
    """
    if len(angles) == 3:
        return quaternion(np.array([math.cos(angles[0] / 2.) * math.cos(angles[1] / 2.) * math.cos(angles[2] / 2.) + math.sin(angles[0] / 2.) * math.sin(angles[1] / 2.) * math.sin(angles[2] / 2.),
                                    math.cos(angles[0] / 2.) * math.cos(angles[1] / 2.) * math.sin(angles[2] / 2.) - math.sin(angles[0] / 2.) * math.sin(angles[1] / 2.) * math.cos(angles[2] / 2.),
                                    math.cos(angles[0] / 2.) * math.sin(angles[1] / 2.) * math.cos(angles[2] / 2.) + math.sin(angles[0] / 2.) * math.cos(angles[1] / 2.) * math.sin(angles[2] / 2.),
                                    math.sin(angles[0] / 2.) * math.cos(angles[1] / 2.) * math.cos(angles[2] / 2.) - math.cos(angles[0] / 2.) * math.sin(angles[1] / 2.) * math.sin(angles[2] / 2.)]))
    else:
        raise AlgebraicError, str(angles) + ' can not be converted to quaternion'
    
def RotationToQuaternion(angle, vector):
    """
    Converts a pair angle-vector into a quaternion
    """
    if len(vector) == 3:
        quat = np.array([math.cos(angle/2.0), vector[0]*(math.sin(angle/2.0)), vector[1]*(math.sin(angle/2.0)), vector[2]*(math.sin(angle/2.0))])
    else:
        raise AlgebraicError, 'the pair ' + str(angle) + str(vector) + ' can not be converted to quaternion'
    return quaternion(quat)

def identity():
    """
    >>> import qmath
    >>> qmath.identity()
    (1.0)
    """
    return quaternion(1)

def zero():
    """
    >>> import qmath
    >>> qmath.zero()
    (0.0)
    """
    return quaternion(0)

def dot(q1,q2):
    """
    Dot product of two quaternions
    >>> import qmath
    >>> a = qmath.quaternion('1+2i-2k')
    >>> b = qmath.quaternion('3-2i+8j')
    >>> qmath.dot(a,b)
    -1.0
    """
    Q1 = quaternion(q1)
    Q2 = quaternion(q2)
    dot = np.dot(Q1.value(),Q2.value())
    return dot


def CrossRatio(q1,q2=None,q3=None,q4=None):
    """
    Cross ratio of four quaternions
    >>> import qmath
    >>> a = qmath.quaternion([1,0,1,0])
    >>> b = qmath.quaternion([0,1,0,1])
    >>> c = qmath.quaternion([-1,0,-1,0])
    >>> d = qmath.quaternion([0,-1,0,-1])
    >>> qmath.CrossRatio(a,b,c,d)
    (2.0)
    >>> tpl = a,b,c,d
    >>> qmath.CrossRatio(tpl)
    (2.0)
    >>> qmath.CrossRatio(a,b,b,d)
    'Infinity'
    >>> qmath.CrossRatio(a,a,a,d)
    (1.0)
    >>> qmath.CrossRatio(a,b,a,b)
    (0.0)
    """
    if type(q1) == tuple:
        return CrossRatio(q1[0],q1[1],q1[2],q1[3])

    else:
        Q1 = quaternion(q1)
        Q2 = quaternion(q2)
        Q3 = quaternion(q3)
        Q4 = quaternion(q4)
        if (Q1 - Q4) * (Q2 - Q3) != 0:
            return (Q1 - Q3) * (quaternion.inverse(Q1 - Q4))*(Q2 - Q4)*(quaternion.inverse(Q2 - Q3))
        elif (Q1 - Q3) * (Q2 - Q4) != 0:
            return 'Infinity'
        else:
            return identity()
            
def Moebius(quaternion_or_infinity, a,b=None,c=None,d=None):
    """
    The Moebius transformation of a quaternion (z)
    with parameters a,b,c and d
    >>> import qmath
    >>> a = qmath.quaternion([1,1,1,0])
    >>> b = qmath.quaternion([-2,1,0,1])
    >>> c = qmath.quaternion([1,0,0,0])
    >>> d = qmath.quaternion([0,-1,-3,-4])
    >>> z = qmath.quaternion([1,1,3,4])
    >>> qmath.Moebius(z,a,b,c,d)
    (-5.0+7.0i+7.0k)
    >>> d = - z
    >>> z = qmath.Moebius(z,a,b,c,d)
    >>> z
    'Infinity'
    >>> qmath.Moebius(z,a,b,c,d)
    (1.0+1.0i+1.0j)
    """
    if type(a) == tuple:
        return Moebius(quaternion_or_infinity,a[0],a[1],a[2],a[3])
    else:
        A = quaternion(a)
        B = quaternion(b)
        C = quaternion(c)
        D = quaternion(d)
        if A * D - B * C == 0:
            raise AlgebraicError, ' this is not a Moebius transformation'
        elif quaternion_or_infinity == 'Infinity':
            return A / C
        else:
            Z = quaternion(quaternion_or_infinity)
            try:
                return (A * Z + B) * quaternion.inverse(C * Z + D)
            except:
                return 'Infinity'
        
if __name__ == "__main__":
    print '*** running doctest ***'
    import doctest,qmath
    doctest.testmod(qmath)


#### END
