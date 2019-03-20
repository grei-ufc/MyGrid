#Auto-Transformador
Apenas o auto-transformador elevador do Tipo B, em conexão estrela-estrela,  está disponivel para uso. A sua modelagem segue a que foi dado por kersting no capítulo 7 do livro <a href="#[1]"> Distribution System Modeling and Analysis </a>:
```python

Definição dos parâmetros:

class Auto_TransformerModel(object):
    def __init__(self,
                 name,
                 step,
                 tap_max,
                 voltage,
                 vhold=122,
                 Npt = 20,
                 connection='YY',
                 tap_a=None,
                 tap_b=None,
                 tap_c=None,
                 CTP=None,
                 R=None,
                 X=None,
                 r=None,
                 x=None):
```
+ **name**:
    <p> Nome do auto-transdormador.
+ **step**:
    <p> Passo do comutador (V).
+ **tap_max**:
    <p> Quantidade máxima de comutações.
+ **voltage**:
    <p> Tensão de linha nominal do auto-transformador (V).
+ **vhold**:
    <p> Tensão alvo do compensador (V).
+ **Npt**:
    <p> Relação de transformação do TP.
+ **tap_a**:
    <p> TAP na fase *a* definido manualmente (p.u).
+ **tap_b**:
    <p> TAP na fase *b* definido manualmente (p.u).
+ **tap_c**:
    <p> TAP na fase *c* definido manualmente (p.u).
+ **CTP**:
    <p> Relação de transformação do TC.
+ **R**:
    <p> 'R' do compensador de linha (V).
+ **X**:
    <p> 'X' do compensador de linha (V).
+ **r**:
    <p> 'r' do compensador de linha (Ω).
+ **x**:
    <p> 'x' do compensador de linha (Ω).

Se **R** e **X** forem definidos **r** e **x** não seram considerados, caso nenhum desses pares seja definido o auto-transformador não funcionará com compensador de linha, ou seja, será manual.

#### Exemplo:
Auto-transformador presente na rede teste  <a href="#[2]">IEEE 13 Barras</a>. 
```python
from mygrid.grid import Auto_TransformerModel

auto_650 = Auto_TransformerModel(name="auto_t1_650",
                                step=0.75,
                                tap_max=32,
                                vhold=122,
                                voltage=4.16e3,
                                R=3,
                                X=9,
                                CTP=700,
                                Npt=20)
```

## Referências

<p id = "[1]">[1] - KERSTING, W. H.
Distribution System Modeling and Analysis
. 3. ed. [S.l.]: CRC Press,
2012. </p>

  <p id = "[2]">[2] - KERSTING, W. H. Radial distribution test feeders. v. 2, p. 908–912 vol.2, Jan 2001.
 </p>