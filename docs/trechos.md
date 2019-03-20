# Trechos
Trechos são usados para representar linha elétrica, transformadores e reguladores de tensão, podendo conter também uma chave caso represente uma linha.

```python
class Section(Edge):
    def __init__(self,
                 name,
                 n1,
                 n2,
                 switch=None,
                 transformer=None,
                 line_model=None,
                 length=None):
```

Definição dos parâmetros:

+ **name**:
    <p> Nome do trecho. Obrigatório.
+ **n1**:
    <p> Nó de inicio do trecho.
+ **n2**:
    <p> Nó de término do trecho.
+ **switch**:
    <p>Chave do trecho, caso exista alguma.
+ **transformer**:
    <p> Transformador do trecho. Caso este argumento não seja ```None``` o trecho representará exclusivamente o transformador passado.
+ **line_model**:
    <p> Modelo de linha.
+ **length**: 
    <p> Comprimento da linha elétrica em milhas ou km (Depende da unidade usado no modelo de linha).

#### Exemplo:

```python
from mygrid.grid import Switch, LineModel, UnderGroundLine
from mygrid.grid import Under_Ground_Conductor
from mygrid.grid import Section, LoadNode, TransformerModel, Conductor
from mygrid.grid import Auto_TransformerModel
from mygrid.util import p2r, r2p

vll_mt = p2r(4.16e3, 0.0)

spacing500=[0.0 + 28.0j,
            2.5 + 28.0j,
            7.0 + 28.0j,
            4.0 + 24.0j]

conduct2 = Conductor(id=44)


line602 =  LineModel(loc=spacing500,
                     phasing=['c','a','b','n'],
                     conductor=conduct2,
                     neutral_conductor=conduct2)


Load_Node632 = LoadNode(name='632',
                        ppa=0.0e3 + 0.0e3j,
                        ppb=0.0e3 + 0.0e3j,
                        ppc=0.0e3 + 0.0e3j,
                        type_connection="wye",
                        zipmodel=[1.0, 0.0, 0.0],
                        voltage=vll_mt)

Load_Node633 = LoadNode(name='633',
                        voltage=vll_mt)

Load_Node632_to_Load_Node633 = Section(name='section4',
                                       n1=Load_Node632,
                                       n2=Load_Node633,
                                       line_model=line602,
                                       length=500/5280)
```

