# Linhas de Distribuição

O MyGrid possui modelagem para linhas aéreas até 4 fios, 3 fases + neutro, e linhas subterrâneas até 3 fases + Neutro. Modelagem e cálculo dos parâmetros das linhas elétricas estão baseados nos capítulos 4, 5 e 6 do livro <a href="#[1]">Distribution System Modeling and Analysis</a>.
## Condutores para linhas aéreas

Definição dos parâmetros dos condutores aéreos:
```python
class Conductor(object):
    def __init__(self,
                 id=None):
```
+ **id**:
    <p> Chave de indentificação do condutor no arquivo <a href="../conductors/">```conductor.json```</a>. Neste arquivo, o usuário tem acesso a diversos  dados de condutores de linhas aéreas, como também pode acrescentar novas informações conforme a sua necessidade.

####Exemplo:
```python
from mygrid.grid import Conductor
conduct1 = Conductor(id=75)
conduct2 = Conductor(id=44)
conduct3 = Conductor(id=31)
conduct6 = Conductor(id=32)
```

## Linhas Aéreas

```python
 class LineModel(object):
    def __init__(self,
                 loc=[],
                 neutral=False,
                 conductor=None,
                 neutral_conductor=None,
                 phasing=['a','b','c','n'],
                 Transpose=False,
                 units='Imperial',
                 f=60,
                 pg=100):
```
Definição dos parâmetros:

+ **loc**:
    <p>Posições dos condutores presentes na linha. ```list```
+ **neutral**:
    <p>Indica a existência de neutro. ```boolean```
+ **conductor**:
    <p>Instância do condutor Fase. ```Conductor```
+ **neutral_conductor**:
    <p>Instância do condutor Neutro. ```Conductor```
+ **phasing**:
    <p>Indica a que fase ou neutro, pertence as posições dadas em **loc**. ```list```
+ **units**:
    <p>Define em  qual unidade, ```'Imperial'``` ou ```'SI'```, deve se calcular a impedância série e admitância shunt da linha. ```string```
+ **f**:
    <p>Frequência da linha (Hz).```float```
+ **pg**:
    <p>Resistividade do solo (Ω.m).```float```
####Exemplo:
Os modelos de linha a seguir foram retirados da rede teste <a href="#[2]"> 13 Barras </a>:
```python 
from mygrid.grid import LineModel
```
Espaçamentos dos cabos:
```python
spacing500=[0.0 + 28.0j,
            2.5 + 28.0j,
            7.0 + 28.0j,
            4.0 + 24.0j]

spacing505=[0.0 + 28.0j,
            7.0 + 28.0j,
            4.0 + 24.0j]
```
Criando os modelos de linhas aérea:

```python
line601 =  LineModel(loc=spacing500,
                     phasing=['b','a','c','n'],
                     conductor=conduct1,
                     neutral_conductor=conduct2)

line602 =  LineModel(loc=spacing500,
                     phasing=['c','a','b','n'],
                     conductor=conduct2,
                     neutral_conductor=conduct2)

line603 =  LineModel(loc=spacing505,
                     phasing=['c','b','n'],
                     conductor=conduct3,
                     neutral_conductor=conduct3)
```
## Condutores para linhas subterrâneas
```python
class Under_Ground_Conductor(object):
    def __init__(self,
                name = None,
                type="concentric",
                outsider_diameter = None,
                rp = None,
                GMRp = None,
                dp = None,
                k = None,
                rs = None,
                GMRs = None,
                ds = None,
                T=None,
                ampacity = None):
```
Definição dos parâmetros:


+ **name**:
    <p> Nome do condutor. Opcional. ```string```
+ **type**:
    <p> Indica se o cabo a ser modelado é do tipo blindado, ```"tapeshield"```, ou de neutro concentrico, ```"concentric"```. ```string```
+ **outsider_diameter**:
    <p> Diâmetro externo do cabo (in). 
+ **rp**:
    <p>Resistividade do condutor fase (Ω/mi).
+ **GMRp**:
    <p>Raio médio geométrico do condutor fase (ft).
+ **dp**:
    <p>Diâmetro do condutor fase (in)
+ **k**:
    <p>Número de neutros concêntricos.
+ **rs**:
    <p>Resistividade do neutro concêntrico (Ω/mi).
+ **GMRs**: 
   <p>Raio médio geométrico do condutor fase (ft).
+ **ds**:
    <p>Diâmetro do neutro concêntrico (in).
+ **T**:
    <p>É a espessura da blindagem (mil)

####Exemplos:


```python
from mygrid.grid import Under_Ground_Conductor

conduct4 = Under_Ground_Conductor(outsider_diameter=1.29,
                                rp=0.4100,
                                GMRp=0.0171,
                                dp=0.567,
                                k=13,
                                rs=14.87,
                                GMRs=0.00208,
                                ds=0.0641,
                                ampacity=None)

conduct5 = Under_Ground_Conductor(type="tapeshield",
                                rp=0.97,
                                GMRp=0.0111,
                                dp=0.368,
                                ds=0.88,
                                T=5)
```

## Linhas Subterrâneas
No MyGrid é possível modelos linhas subterrâneas com cabo blindado ou de neutro concêntrico.
```python
class UnderGroundLine(LineModel):
    def __init__(self,
                 loc=[],
                 conductor=None,
                 phasing=['a','b','c'],
                 neutral_conductor=None,
                 Transpose=False,
                 units='Imperial',
                 f=60,
                 pg=100):
```

Definição dos parâmetros:

+ **loc**:
    <p>Posições dos condutores presentes na linha. ```list```
+ **neutral**:
    <p>Indica a existência de neutro. ```boolean```
+ **conductor**:
    <p>Instância do condutor Fase. ```UnderGroundLine```
+ **neutral_conductor**:
    <p>Instância do condutor Neutro. ```Conductor```
+ **phasing**:
    <p>Indica a que fase ou neutro, pertence as posições dadas em **loc**. ```list```
+ **units**:
    <p>Define em  qual unidade, ```'Imperial'``` ou ```'SI'```, deve se calcular a impedância série e admitância shunt da linha. ```string```
+ **f**:
    <p>Frequência da linha (Hz).```float```
+ **pg**:
    <p>Resistividade do solo (Ω.m).```float```

####Exemplos:
```python
line606 =  UnderGroundLine(loc=spacing515,
                           phasing=['a','b','c'],
                           conductor=conduct4)

line607 =  UnderGroundLine(loc=spacing520,
                           phasing=['a', 'n'],
                           conductor=conduct5,
                           neutral_conductor=conduct6)
```

##Referências
<p id = "[1]">[1] - KERSTING, W. H.
Distribution System Modeling and Analysis. 3. ed. [S.l.]: CRC Press, 2012.</p>
<p id = "[2]">[2] - KERSTING, W. H. Radial distribution test feeders. v. 2, p. 908–912 vol.2, Jan 2001.</p>


