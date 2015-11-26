# coding=utf-8

import numpy as np


class Fasor(object):

    Tensao, Corrente, Impedancia, Potencia = range(4)

    def __init__(self,
                 real=None,
                 imag=None,
                 mod=None,
                 ang=None,
                 tipo=None):
        if tipo is None:
            raise Exception('Um tipo precisa ser associado ao Fasor!')
        else:
            self.__tipo = tipo

        self.__base = None
        self.__pu = None

        if not real == None:
            if not imag == None:
                self.__real = real
                self.__imag = imag
                self.__mod = np.absolute(self.__real + self.__imag * 1.0j)
                self.__ang = np.angle(self.__real + self.__imag * 1.0j, deg=1)
            else:
                raise Exception('O parâmetro imag esta vazio!')
        elif not mod == None:
            if not ang == None:
                self.__mod = mod
                self.__ang = ang
                self.__real = self.__mod * np.cos(np.pi / 180.0 * self.__ang)
                self.__imag = self.__mod * np.sin(np.pi / 180.0 * self.__ang)
            else:
                raise Exception('O parâmetro ang esta vazio!')
        else:
            raise Exception('O parâmetro real ou o parâmetro mod prescisam ser passados!')

    @property
    def tipo(self):
        if self.__tipo == 0:
            return 'Tensao'
        elif self.__tipo == 1:
            return 'Corrente'
        elif self.__tipo == 2:
            return 'Impedancia'
        elif self.__tipo == 3:
            return 'Potencia'

    @tipo.setter
    def tipo(self, valor):
        raise Exception('O tipo de um fasor não pode ser alterado!')

    @property
    def base(self):
        if self.__base is None:
            raise Exception('Nenhuma Base está associada ao Fasor!')
        else:
            return self.__base

    @base.setter
    def base(self, valor):
        if not isinstance(valor, Base):
            raise TypeError('O parâmetro base deve ser do tipo Base!')
        else:
            self.__base = valor
    @property
    def pu(self):
        if self.__base is None:
            raise Exception('Uma base deve estar associada ao Fasor!')
        else:
            if self.__tipo == 0:
                return self.mod / self.__base.tensao
            elif self.__tipo == 1:
                return self.mod / self.__base.corrente
            elif self.__tipo == 2:
                return self.mod / self.__base.impedancia
            elif self.__tipo == 3:
                return self.mod / self.__base.potencia

    @pu.setter
    def pu(self, valor):
        raise Exception('Esse valor não pode ser alterado!')

    @property
    def real(self):
        return self.__real

    @real.setter
    def real(self, valor):
        self.__real = valor
        self.__mod = np.absolute(self.__real + self.__imag * 1.0j)
        self.__ang = np.angle(self.__real + self.__imag * 1.0j, deg=1)

    @property
    def imag(self):
        return self.__imag

    @imag.setter
    def imag(self, valor):
        self.__imag = valor
        self.__mod = np.absolute(self.__real + self.__imag * 1.0j)
        self.__ang = np.angle(self.__real + self.__imag * 1.0j, deg=1)

    @property
    def mod(self):
        return self.__mod

    @mod.setter
    def mod(self, valor):
        self.__mod = abs(valor)
        self.__real = self.__mod * np.cos(np.pi / 180.0 * self.__ang)
        self.__imag = self.__mod * np.sin(np.pi / 180.0 * self.__ang)

    @property
    def ang(self):
        return self.__ang

    @ang.setter
    def ang(self, valor):
        self.__ang = valor
        self.__real = self.__mod * np.cos(np.pi / 180.0 * self.__ang)
        self.__imag = self.__mod * np.sin(np.pi / 180.0 * self.__ang)

    def __add__(self, other):
        if not isinstance(other, Fasor):
            raise TypeError('O objeto deve ser do tipo Fasor para proceder a soma!')
        elif not self.tipo == other.tipo:
            raise TypeError('Os fasores devem ser do mesmo tipo para proceder a soma!')
        else:
            return Fasor(real=self.real + other.real,
                         imag=self.imag + other.imag,
                         tipo=self.__tipo)

    def __sub__(self, other):
        if not isinstance(other, Fasor):
            raise TypeError('O objeto deve ser do tipo Fasor para proceder a subtracao!')
        elif not self.tipo == other.tipo:
            raise TypeError('Os fasores devem ser do mesmo tipo para proceder a subtracao!')
        else:
            return Fasor(real=self.real - other.real,
                         imag=self.imag - other.imag,
                         tipo=self.__tipo)

    def __mul__(self, other):
        if not isinstance(other, Fasor):
            raise TypeError('O objeto deve ser do tipo Fasor para proceder a multiplicacao!')
        elif not self.tipo == other.tipo:
            raise TypeError('Os fasores devem ser do mesmo tipo para proceder a multiplicacao!')
        else:
            return Fasor(mod=self.mod * other.mod,
                         ang=self.ang + other.ang,
                         tipo=self.__tipo)

    def __div__(self, other):
        if not isinstance(other, Fasor):
            raise TypeError('O objeto deve ser do tipo Fasor para proceder a divisao!')
        elif not self.tipo == other.tipo:
            raise TypeError('Os fasores devem ser do mesmo tipo para proceder a divisao!')
        else:
            return Fasor(mod=self.mod / other.mod,
                         ang=self.ang - other.ang,
                         tipo=self.__tipo)

    def __str__(self):
        return 'Fasor de {tipo}: {real} + {imag}j'.format(tipo=self.tipo, real=self.real, imag=self.imag)


class Base(object):
    def __init__(self, tensao, potencia):
        self.tensao = tensao
        self.potencia = potencia
        self.corrente = self.potencia / (np.sqrt(3) * self.tensao)
        self.impedancia = self.tensao ** 2 / self.potencia

    def __str__(self):
        return 'Base de {tensao} V e potencia {} VA'.format(tensao=self.tensao, potencia=self.potencia)

#
# class Tensao(Fasor):
#     def __init__(self, mod, ang, mult=None):
#         super(Tensao, self).__init__(mod=mod, ang=ang, mult=mult)
#
#     def __str__(self):
#         if self.mult == 1e3:
#             return 'Tensão: {mod}/_{ang} kV'.format(mod=self.mod, ang=self.ang)
#         elif self.mult == 1e6:
#             return 'Tensão: {mod}/_{ang} MV'.format(mod=self.mod, ang=self.ang)
#         else:
#             return 'Tensão: {mod}/_{ang} V'.format(mod=self.mod, ang=self.ang)
#
#
# class Corrente(Fasor):
#     def __init__(self, mod, ang, mult=None):
#         super(Corrente, self).__init__(mod=mod, ang=ang, mult=mult)
#
#     def __str__(self):
#         if self.mult == 1e3:
#             return 'Corrente: {mod}/_{ang} MA'.format(mod=self.mod, ang=self.ang)
#         elif self.mult == 1e6:
#             return 'Corrente: {mod}/_{ang} MA'.format(mod=self.mod, ang=self.ang)
#         else:
#             return 'Corrente: {mod}/_{ang} A'.format(mod=self.mod, ang=self.ang)
#
#
# class Potencia(Fasor):
#     def __init__(self, ativa, reativa, mult=None):
#         super(Potencia, self).__init__(real=ativa, imag=reativa, mult=mult)
#
#     def __str__(self):
#         if self.mult == 1e3:
#             return 'Potencia {mod} kVA'.format(mod=self.mod)
#         elif self.mult == 1e6:
#             return 'Potencia: {mod} MVA'.format(mod=self.mod)
#         else:
#             return 'Potencia {mod} VA'.format(mod=self.mod)


if __name__ == '__main__':
    fasor_1 = Fasor(real=1.0, imag=0.5)
    print fasor_1.real
    print fasor_1.imag
