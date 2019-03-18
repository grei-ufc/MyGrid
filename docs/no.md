# Generação Distribuída
```python
class Generation(object):
    def __init__(self,name,
                 Pa=0.0+0.0j,
                 Pb=0.0+0.0j,
                 Pc=0.0+0.0j,
                 P=None,
                 Qmin=0.0+0.0j,
                 Qmax=0.0+0.0j,
                 generation_type="PQ",
                 type_connection="wye",
                 Z=None)
```
Definição dos parâmetros:

+ **name**:
    <p>Nome do nó. Obrigatório. ```string```
+ **ppa**:
    <p>Potência da fase *a* (W+jVar). Usado somente quando **power** é do tipo ```None```. ```float```
+ **ppb**:
    <p>Potência da fase *b* (W+jVar). Usado somente quando **power** é do tipo ```None```. ```float```
+ **ppc**:
    <p>Potência da fase *c* (W+jVar). Usado somente quando **power** é do tipo ```None```. ```float```
+ **power**:
    <p>Potência trifásica (W+jVar). ```float```
+ **Qmin**:
    <p>Potência Reativa mínima (p.u.). ```float```
+ **Qmax**:
    <p>Potência Reativa máxima (p.u.). ```float```
+ **generation_type**:
    <p>Tipo de geração, ```"PQ``` ou ```"PV"```. ````string```
+ **type_connection**:
    <p>Define o tipo de conexão, ```"wye"``` para estrela e ```"delta"``` para conexão delta. ```string```
+ **Z**:
    <p>Impedância interna da geração. ```numpy.ndarray```

#### Exemplo:

```python
from mygrid.grid import Generation

Z = np.eye(3, dtype=complex)*(15+100j)

b2_PV = Generation(name="b2_PV",
                   P=0e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.0002,
                   generation_type="PV",
                   Z=Z)

aa1_PQ = Generation(name="aa1_PV",
                    Pa=4.0e3-2.62e3j,
                    Pb=4.0e3-2.62e3j,
                    Pc=4.0e3-2.62e3j,
                    generation_type="PQ",
                    Z=Z)
```


# Capacitores Shunt
```python
class Shunt_Capacitor(object):
    def __init__(self,
                 vll, 
                 Qa,
                 Qb,
                 Qc,
                 type_connection):
```
Definição dos parâmetros:

+ **vll**:
    <p> Tensão de linha. ```float```
+ **Qa**:
    <p> Potência reativa capacitiva na fase *a*. ```float```
+ **Qb**:
    <p> Potência reativa capacitiva na fase *b*. ```float```
+ **Qc**:
    <p> Potência reativa capacitiva na fase *c*. ```float```
+ **type_connection**:
    <p> Define o tipo de conexão, ```"wye"``` para estrela e ```"delta"``` para conexão delta. ```string```
#### Exemplo:

```python
from mygrid.grid import Shunt_Capacitor

capacitor_675 = Shunt_Capacitor(vll=4.16e3,
                                Qa=200e3, Qb=200e3, Qc=200e3,
                                type_connection="wye")

capacitor_611 = Shunt_Capacitor(vll=4.16e3,
                                Qa=0.0e3, Qb=0.0e3, Qc=100e3,
                                type_connection="wye")
```

# Nós de Carga/Passagem


```python
class LoadNode(object):
    def __init__(self,
                 name,
                 power=None,
                 ppa=0.0+0.0j,
                 ppb=0.0+0.0j,
                 ppc=0.0+0.0j,
                 voltage=0.0+0.0j,
                 Vmin=0.98,
                 Vmax=1.05,
                 Vspecified=1.0,
                 DV_presc=0.002,
                 generation=None,
                 type_connection="wye",
                 shunt_capacitor=None,
                 external_grid=None,
                 zipmodel=[1.0, 0.0, 0.0])
```
Definição dos parâmetros:

+ **name**:
    <p>Nome do nó. Obrigatório. ```string``` 
+ **power**:
    <p>Potência trifásica (W+jVar). ```float```
+ **ppa**:
    <p>Potência da fase *a* (W+jVar). Usado somente quando **power** é do tipo ```None```. ```float```
+ **ppb**:
    <p>Potência da fase *b* (W+jVar). Usado somente quando **power** é do tipo ```None```. ```float```
+ **ppc**:
    <p>Potência da fase *c* (W+jVar). Usado somente quando **power** é do tipo ```None```. ```float```
+ **voltage**:
    <p>Tensão no Nó (V). ```float```
+ **Vmin**:
    <p>Tensão mínima (p.u.). ```float```
+ **Vmax**:
    <p>Tensão máxima (p.u.). ```float```
+ **Vspecified**:
    <p>Tensão alvo para geração PV. ```float``
+ **DV_presc**:
    <p>Precisão mínima para convergência da geração PV. ```float`
+ **generation**:
    <p>Geração distribuída. ```Generation```
+ **type_connection**:
    <p>Define o tipo de conexão, ```"wye"``` para estrela e ```"delta"``` para conexão delta. ```string```
+ **shunt_capacitor**:
    <p>Capacitor shunt. ```Shunt_Capacitor```
+ **external_grid**:
    <p>Rede externa. Usada para o nó raíz. ```ExternalGrid```
+ **zipmodel**:
    <p>Modelo zip [Potência constante, Impedância constante, Corrente constante]. ```list```

#### Exemplo:

```python
from mygrid.grid import LoadNode
from mygrid.util import p2r, r2p

vll_mt = p2r(13.8e3, 0.0)
vll_bt = p2r(380.0, 0.0)

Load_Node675 = LoadNode(name='675',
                        ppa=485.0e3 + 190.0e3j,
                        ppb=68.0e3 + 60.0e3j,
                        ppc=290.0e3 + 212.0e3j,
                        type_connection="wye",
                        shunt_capacitor=capacitor_675,
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)

b2 = LoadNode(name='B2',
              generation = b2_PV,
              power=150.0e3 + 110.0e3j,
              voltage=vll_mt)

aa3 = LoadNode(name='AA3',
               generation=aa1_PQ,
               power=20.0e3 + 5.0e3j,
               voltage=vll_bt)
```