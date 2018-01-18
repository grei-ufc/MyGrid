# coding=utf-8

import numpy as np

HEAD_WIDTH = 5.0
HEAD_LENGTH = 8.0
WIDTH = 2.0

class Phasor(object):

    def __init__(self,
                 r=None,
                 i=None,
                 m=None,
                 a=None,
                 nom=None):

        self.__base = None
        self.__pu = None
        self.__polar = False
        self.__nome = nom

        if r is not None:
            if i is not None:
                self.__r = r
                self.__i = i
                self.__m = np.absolute(self.__r + self.__i * 1.0j)
                self.__a = np.angle(self.__r + self.__i * 1.0j, deg=1)
            else:
                raise Exception('The parameter i is empty!')
        elif m is not None:
            if a is not None:
                self.__m = m
                self.__a = a
                self.__r = self.__m * np.cos(np.pi / 180.0 * self.__a)
                self.__i = self.__m * np.sin(np.pi / 180.0 * self.__a)
            else:
                raise Exception('The parameter a is empty!')
        else:
            raise Exception('The parameters r or m need to be given!)

    def conj(self):
        f = Phasor(r=self.__r, i=-self.__i)
        if self.polar:
            f.polar = True
        return f

    @property
    def nome(self):
        return self.__nome

    @nome.setter
    def nome(self, value):
        if type(value) is not str:
            raise Exception('The parameter name need to be String')
        else:
            self.__nome = value

    @property
    def polar(self):
        return self.__polar

    @polar.setter
    def polar(self, value):
        if type(value) is not bool:
            raise Exception('The parameter polar need to be bool')
        else:
            self.__polar = value

    @property
    def base(self):
        if self.__base is None:
            raise Exception('No Base is associated to Phasor!')
        else:
            return self.__base

    @base.setter
    def base(self, valor):
        if not isinstance(valor, float) and not isinstance(valor, int):
            raise TypeError('The parameter base need to be float or int!')
        else:
            self.__base = valor

    @property
    def pu(self):
        if self.__base is None:
            raise Exception('A base must be associated with a Phasor!')
        else:
            f = Phasor(m=self.m / self.base, a=self.a)
            f.polar = True
            return f

    @pu.setter
    def pu(self, valor):
        raise Exception('This value can not be changed!')

    @property
    def r(self):
        return self.__r

    @r.setter
    def r(self, valor):
        self.__r = valor
        self.__m = np.absolute(self.__r + self.__i * 1.0j)
        self.__a = np.angle(self.__r + self.__i * 1.0j, deg=1)

    @property
    def i(self):
        return self.__i

    @i.setter
    def i(self, valor):
        self.__i = valor
        self.__m = np.absolute(self.__r + self.__i * 1.0j)
        self.__a = np.angle(self.__r + self.__i * 1.0j, deg=1)

    @property
    def m(self):
        return self.__m

    @m.setter
    def m(self, valor):
        self.__m = abs(valor)
        self.__r = self.__m * np.cos(np.pi / 180.0 * self.__a)
        self.__i = self.__m * np.sin(np.pi / 180.0 * self.__a)

    @property
    def a(self):
        return self.__a

    @a.setter
    def a(self, valor):
        self.__a = valor
        self.__r = self.__m * np.cos(np.pi / 180.0 * self.__a)
        self.__i = self.__m * np.sin(np.pi / 180.0 * self.__a)

    def __add__(self, other):
        if not isinstance(other, Phasor):
            raise TypeError('The object needs to be Phasor to sum!')
        else:
            return Phasor(r=self.r + other.r,
                     i=self.i + other.i)

    def __sub__(self, other):
        if not isinstance(other, Phasor):
            raise TypeError('The object needs to be Phasor to subtract!')
        else:
            return Phasor(r=self.r - other.r,
                     i=self.i - other.i)

    def __mul__(self, other):
        if not isinstance(other, Phasor):
            raise TypeError('The object needs to be Phasor to multiply!')
        else:
            f = Phasor(m=self.m * other.m, a=self.a + other.a)

            if self.polar is True and other.polar is True:
                f.polar = True

            return f

    def __rmul__(self, other):
        return Phasor(m=self.m * other,
                 a=self.a)

    def __truediv__(self, other):
        if not isinstance(other, Phasor):
            raise TypeError('The object need to be a Phasor to divide!')
        else:
            return Phasor(m=self.m / other.m,
                     a=self.a - other.a)

    def __repr__(self):
        if self.__polar:
            return '{r} ∠ {i}º'.format(r=round(self.m, 2),
                                          i=round(self.a, 2))
        else:
            return '{r} + {i}j'.format(r=round(self.r, 2),
                                       i=round(self.i, 2))


class R(Phasor):
    def __init__(self, r=None, i=None, nom=None):
        if r is None or i is None:
            raise Exception('The parameters r and i need to be given!')
        else:
            super(R, self).__init__(r=r, i=i, nom=nom)


class P(Phasor):
    def __init__(self, m=None, a=None, nom=None):
        if m is None or a is None:
            raise Exception('The parameters m and a need to be given!')
        else:
            super(P, self).__init__(m=m, a=a, nom=nom)
            self.polar = True


class Base(object):
    def __init__(self, voltage, power):
        self.voltage = voltage
        self.power = power
        self.current = self.power / (np.sqrt(3) * self.voltage)
        self.impedance = self.voltage ** 2 / self.power

    def __repr__(self):
        return 'Voltage Base {voltage} V and Power Base {power} VA'.format(
            voltage=self.voltage, power=self.power)
