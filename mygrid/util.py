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
                raise Exception('O parâmetro i esta vazio!')
        elif m is not None:
            if a is not None:
                self.__m = m
                self.__a = a
                self.__r = self.__m * np.cos(np.pi / 180.0 * self.__a)
                self.__i = self.__m * np.sin(np.pi / 180.0 * self.__a)
            else:
                raise Exception('O parâmetro a esta vazio!')
        else:
            raise Exception('O parâmetro r ou o parâmetro m prescisam \
                ser passados!')

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
            raise Exception('O parâmetro nome deve ser do tipo string')
        else:
            self.__nome = value

    @property
    def polar(self):
        return self.__polar

    @polar.setter
    def polar(self, value):
        if type(value) is not bool:
            raise Exception('O parâmetro polar deve ser do tipo bool')
        else:
            self.__polar = value

    @property
    def base(self):
        if self.__base is None:
            raise Exception('Nenhuma Base está associada ao Phasor!')
        else:
            return self.__base

    @base.setter
    def base(self, valor):
        if not isinstance(valor, float) and not isinstance(valor, int):
            raise TypeError('O parâmetro base deve ser do tipo float ou int!')
        else:
            self.__base = valor

    @property
    def pu(self):
        if self.__base is None:
            raise Exception('Uma base deve estar associada ao Phasor!')
        else:
            f = Phasor(m=self.m / self.base, a=self.a)
            f.polar = True
            return f

    @pu.setter
    def pu(self, valor):
        raise Exception('Esse valor não pode ser alterado!')

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
            raise TypeError('O objeto deve ser do tipo Phasor \
                para proceder a soma!')
        else:
            return Phasor(r=self.r + other.r,
                     i=self.i + other.i)

    def __sub__(self, other):
        if not isinstance(other, Phasor):
            raise TypeError('O objeto deve ser do tipo Phasor \
                para proceder a subtracao!')
        else:
            return Phasor(r=self.r - other.r,
                     i=self.i - other.i)

    def __mul__(self, other):
        if not isinstance(other, Phasor):
            raise TypeError('O objeto deve ser do tipo Phasor \
                para proceder a multiplicacao!')
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
            raise TypeError('O objeto deve ser do tipo Phasor \
                para proceder a divisao!')
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
            raise Exception('Os parâmetros r e i precisam ser passados!')
        else:
            super(R, self).__init__(r=r, i=i, nom=nom)


class P(Phasor):
    def __init__(self, m=None, a=None, nom=None):
        if m is None or a is None:
            raise Exception('Os parâmetros m e a precisam ser passados!')
        else:
            super(P, self).__init__(m=m, a=a, nom=nom)
            self.polar = True


class Base(object):
    def __init__(self, tensao, potencia):
        self.tensao = tensao
        self.potencia = potencia
        self.corrente = self.potencia / (np.sqrt(3) * self.tensao)
        self.impedancia = self.tensao ** 2 / self.potencia

    def __repr__(self):
        return 'Base de {tensao} V e potencia {potencia} VA'.format(
            tensao=self.tensao, potencia=self.potencia)
