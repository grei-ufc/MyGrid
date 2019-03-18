#Transformadores Abaixadores

 Atualmente o MyGrid possui dois tipos de transformadores modelados conforme o capítulo 8 do livro <a href="#[1]"> Distribution System Modeling and Analysis </a>:

 - Delta - Estrela aterrado;
 - Estrela aterrado - Estrela aterrado.

Definição dos parâmetros:


```python
 class TransformerModel(object):
     def __init__(self,
                  name,
                  primary_voltage,
                  secondary_voltage,
                  power,
                  impedance=None,
                  R=5,
                  X=5,
                  connection='Dyn'):
```
- **name**:
<p>Nome do objeto transformador. Todos os transformadores devem possuir nomes diferentes.
+  **primary_voltage**:
<p>Tensão primária do transformador (V).
+ **secondary_voltage**:
<p>Tensão secundária do transformador (V):  
+ **power**:
<p> Potência do transformador (V.A).
+ **impedance**:
<p> Impendância complexa do transformador (Ω).
+ **R** e **X**:
<p> São, respectivamente, resistência e reatância em % (p.u x 100). Caso o valor de **impedance** seja *None*  os valores de **R** e **X** serão usados para computar a impedância do transformador.
+ **connection**:
<p> Define o tipo de conexão do transformador. Conexões disponíveis:
<ul>
    <li>``` Dyn``` - Delta-Estrela Aterrado</li>
    <li>``` nyyn``` - Estrela Aterrado-Estrela Aterrado</li>
</ul>

#### Exemplos:
<p> A seguir segue dois exemplos de transformadores modelados no MyGrid. Ambos são usados na rede teste 
    <a href="#[2]">IEEE 13 Barras</a>. 

Importando bibliotecas:
```python
from mygrid.util import p2r, r2p
from mygrid.grid import TransformerModel
```

Tensões:
```python
vll_ht = p2r(115e3, 0.0)
vll_mt = p2r(4.16e3, 0.0)
vll_bt = p2r(480.0, 0.0)
```
Criando instâncias dos transformadores:
```python
tf_Substation_t1 = TransformerModel(name="Substation_T1",
                      primary_voltage=vll_ht,
                      secondary_voltage=vll_mt,
                      power=5000e3,
                      connection='Dyn',
                      R=1,
                      X=8)

tf_XFM_1t1 = TransformerModel(name="XMF_1",
                      primary_voltage=vll_mt,
                      secondary_voltage=vll_bt,
                      connection='nyyn',
                      power=500e3,
                      R=1.1,
                      X=2)
```

<h2> Referências</h2>

  <p id = "[1]">[1] - KERSTING, W. H.
Distribution System Modeling and Analysis
. 3. ed. [S.l.]: CRC Press,
2012. </p>
  <p id = "[2]">[2] - KERSTING, W. H. Radial distribution test feeders. v. 2, p. 908–912 vol.2, Jan 2001.
 </p>
