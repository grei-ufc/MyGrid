
<div style="text-align:center">
    <img src="my_grid_logo_2.png" width="300">    
</div>
<br>

# Bem vindo à documentação do projeto MyGrid

O projeto MyGrid tem o objetivo de oferecer uma ferramenta computacional para **representação topológica e descritiva dos componentes da rede elétrica de distribuição**, permitindo em contrapartida a realização de estudos da rede definida, tais como:

- análise de fluxo de carga;
- ajuste de reguladores de tensão;
- cálculo de curto-circuito;
- estudos de impactos causados pela inserção de micro-geração distribuída.

A representação que o MyGrid faz de todos os componentes da rede elétrica é trifásica o que permite uma representação mais fiel à realidade, permitindo o estudo de desequilíbrios no sistema e a conexão de cargas e gerações monofásica e bifásicas.

O MyGrid é desenvolvido em linguagem de programação python e mantido pelo Grupo de Redes Elétricas Inteligentes da Universidade Federal do Ceará - [GREI-UFC](https://grei-master.github.io/site/).

## Começando do começo

Para começar a utilizar o MyGrid existem duas opções. A primeira é utilizar o repositório padrão de pacotes python (PYPI), simplesmente digitando o comando:

    $ pip install mygrid

Inicie uma seção Jupyter e digite:

    In [1]: import mygrid

Pronto, o mygrid já está pronto para ser utilizado.

A segunda opção é fazer o download do código fonte no seu computador, para fazer isso é muito simples, basta abrir o terminal e digitar o seguinte comando:

    $ git clone https://github.com/grei-ufc/MyGrid

Após executar esse comando uma pasta com o nome MyGrid será criada no diretório em que você se encontra.

Digite:

    $ cd MyGrid

Inicie uma seção Jupyter:

    $ jupyter qtconsole

 No console Jupyter digite:


    In [1]: import mygrid

Para instalar o código no seu ambiente Python padrão ou no virtual enviroment que estiver utilizando, basta digitar no diretório raiz do mygrid:

    $ python setup.py install

Se tudo tiver corrido bem nenhum erro ocorrerá e você estará pronto para utilizar o MyGrid.

## Princípios Gerais

O MyGrid é a implementação computacional do conceito de RNP, ou Representação Nó Profundidade, para a representação da rede elétrica de distribuição. Ou seja, no MyGrid os conceitos de nó, profundidade, árvore de grafo, entre outros estão mesclados aos conceitos de rede elétrica, chave, trecho de condutor, setor elétrico, e assim por diante. Isso foi realizado por meio de duas camadas de implementação computacional.

Na primeira camada o MyGrid implementa dos conceitos relacionados à RNP por meio da classe Árvore. Em uma segunda camada as classes implementadas representam os elementos da rede elétrica, como mencionados anteriormente, tendo alguns destes elementos as classes que representam a RNP como super-classes.

Os conceitos aqui mencionados serão mais bem compreendidos por meio da montagem e utilização dos métodos computacionais disponibilizados pelas classes afim de realizar operações na rede elétrica.

Além de disponibilizar uma representação computacionalmente eficiente da rede elétrica o MyGrid disponibiliza algoritmos de análise tais como cálculo de fluxo de carga e de curto-circuito.

## Representação de Grafos

Para que seja possível a representação da rede elétrica por meio de grafos no modelo nó profundidade primeiro é necessário ter ferramentas que permitam a representação genérica de grafos. Quem implementa essas funções no MyGrid é o módulo principal chamado de `rnp.py`.

A principal classe desse módulo se chama `Tree()` e possui todos os métodos e atributos necessários para a manipulação de uma árvore de grafo.

No exemplo abaixo é mostrado o instanciamento de duas árvores de grafo, `tree_1` e `tree_2`. Para que a estrutura rnp possa ser montada duas ações precisam ser realizadas, a primeira é a passagem da estrutura da rede, isso é feito por meio de um dicionário em que cada chave é o nome de um dos nós da árvore e os valores são listas contendo os vizinhos desse nó, sem considerar orientação, ainda. A segunda ação é indicar qual a o nó será considerado o nó de referência da árvore, ou seja, qual o nó será o nó raiz, isso implica que este nó terá profundidade zero.

```python
nodes1 = {3: [1],
          1: [3, 2, 7],
          7: [1, 8, 9, 4, 10],
          10: [7],
          4: [7, 5, 6],
          5: [4],
          6: [4],
          9: [7],
          8: [7],
          2: [1, 11, 12, 13],
          11: [2],
          12: [2, 13],
          13: [12]}

nodes2 = {14: [15],
          15: [14, 16, 19],
          16: [15, 17, 18],
          17: [16],
          18: [16],
          19: [15]}

# definição da tree a1
tree_1 = Tree(nodes1)

# ordenação da tree a1
tree_1.order(root=3)
print(tree_1.rnp)

# definição da tree a2
tree_2 = Tree(nodes2)

# ordenação da tree a2
tree_2.order(root=14)
print(tree_2.rnp)
```

Após a definição das árvores de grafo e instanciados os objetos é possível relizar as operações de poda e de inserção sobre as árvores de grafos, e dessa forma modificar suas estruturas. No código abaixo é feita uma operação de poda em `tree_1` na altura do nó 7 e em seguida o ramo podado é inserido em `tree_2` na altura do nó 19.

```python
# operação de poda
prune = tree_1.prune(7, change_rnp=True)
print(prune)
print(tree_1.rnp)

# operação de inserção
tree_2.insert_branch(19, prune, 7)
print(tree_2.rnp)
```

Os resultados são mostrados abaixo:


## Instanciando uma rede elétrica

O principal objetivo do MyGrid é a representação da rede elétrica em uma estrtura de grafos mas ao mesmo tempo com recursos de orientação a objetos. Isso é feito definindo classes que representam os elementos da rede elétrica mas que também herdam das classes definidas no módulo `rnp.py` para que seja possível uma representação topológica da rede.

Para exemplificar o processo de representação da rede elétrica iremos considerar a rede mostrada na Figura abaixo.

![Rede Elétrica](rede.png "Rede Elétrica")


Nesta rede é possível observar alguns componentes básicos de uma rede elétrica de média/baixa tensão:

- Transformadores;
- Chaves Elétricas;
- Trechos de Linahs;
- Pontos de derivação e de carga;

Os primeiros elementos que podem ser instanciados para a composição da rede elétrica são as chaves existentes no sistema, para a rede exemplo temos:

```python

from mygrid.grid import Switch

# switchs do alimentador 1 de S1
ch1 = Switch(name='1', state=1)
ch2 = Switch(name='2', state=1)
ch3 = Switch(name='3', state=1)

# Switchs do alimentador 2 de S1
ch9 = Switch(name='9', state=1)
ch10 = Switch(name='10', state=1)

# switchs de Fronteira
ch4 = Switch(name='4', state=0)
ch5 = Switch(name='5', state=0)
ch8 = Switch(name='8', state=0)
ch11 = Switch(name='11', state=0)

# switchs do alimentador de S2
ch6 = Switch(name='6', state=1)
ch7 = Switch(name='7', state=1)
```

Em seguinda podemos instanciar os transformadores de distribuição, ou seja, os transformadores que baixam o nível de tensão de linha de 13,8kV para 380V. Para isso é necessário também instanciar os níveis de tensão primário e secundário:

```python

from mygrid.grid import TransformerModel
# tensao nominal

vll_mt = p2r(13.8e3, 0.0)
vll_bt = p2r(380.0, 0.0)

# transformers
t1 = TransformerModel(name="T1",
                      primary_voltage=vll_mt,
                      secondary_voltage=vll_bt,
                      power=225e3,
                      impedance=0.01 + 0.2j)
```

Após instanciar chaves e transformadores de distribuição o próximo passo é instanciar os nós de carga presentes no sistema, tanto os de média quanto os de baixa tensão, isso é feito especificando um *nome*, um *nível de tensão*, e um *valor de carga*.

Também se o nó de carga possuir interface com uma rede elétrica externa isso deve ser informador no parâmetro `external_grid`.


```python
# Nos de carga do alimentador S1_AL1
s1 = LoadNode(name='S1',
              voltage=vll_mt,
              external_grid=eg1)
a1 = LoadNode(name='A1',
              power=120 + 160j,
              voltage=vll_mt)
a2 = LoadNode(name='A2',
              power=150.0e3 + 110.0e3j,
              voltage=vll_mt)

a3 = LoadNode(name='A3',
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt)
b1 = LoadNode(name='B1',
              power=200.0e3 + 140.0e3j,
              # generation=b1_PQ,
              voltage=vll_mt)
b2 = LoadNode(name='B2',
              power=150.0e3 + 110.0e3j,
              # generation=b2_PV,
              voltage=vll_mt)

b3 = LoadNode(name='B3',
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt)
c1 = LoadNode(name='C1',
              power=200.0e3 + 140.0e3j,
              # shunt_capacitor=SC_C1,
              voltage=vll_mt)
c2 = LoadNode(name='C2',
              power=150.0e3 + 110.0e3j,
              # generation=c2_PV,
              voltage=vll_mt)
c3 = LoadNode(name='C3',
              ppa=400.0e3 + 0.0j,
              ppb=0.0e3 + 0.0j,
              ppc=0.0e3 + 0.0j,
              # generation=c3_PV,
              voltage=vll_mt)

# Nos de carga do alimentador S1_AL1
f1 = LoadNode(name='F1',
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt)
g1 = LoadNode(name='G1',
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt)

# Nos de carga do alimentador S2_AL1
s2 = LoadNode(name='S2',
              voltage=vll_mt,
              external_grid=eg1)
d1 = LoadNode(name='D1',
              power=200.0e3 + 160.0e3j,
              voltage=vll_mt)
d2 = LoadNode(name='D2',
              power=900.0e3 + 40.0e3j,
              voltage=vll_mt)
d3 = LoadNode(name='D3',
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt,)
e1 = LoadNode(name='E1',
              power=100.0e3 + 40.0e3j,
              voltage=vll_mt)
e2 = LoadNode(name='E2',
              power=110.0e3 + 70.0e3j,
              voltage=vll_mt)
e3 = LoadNode(name='E3',
              power=150.0e3 + 80.0e3j,
              voltage=vll_mt)

# Subgrid load-nodes connecteds to A1
aa1 = LoadNode(name='AA1',
               power=0.0 + 0.0j,
               voltage=vll_bt)
aa2 = LoadNode(name='AA2',
               power=20.0e3 + 5.0e3j,
               voltage=vll_bt)
aa3 = LoadNode(name='AA3',
               power=20.0e3 + 5.0e3j,
               voltage=vll_bt)
```

Após serem definidos os nós de carga da rede elétrica, é preciso especificar os seguimentos de linha ou transformadores que estão entre dois nós, definindo assim a topologia da rede. O primeiro procedimento para isso é a definição dos condutores que serão utilizados nos seguimentos de linha. Para isso o MyGrid possui uma tabela de condutores pré-definidos conforme especificado nos apêndices do livro **Distribution System Modeling and Analysis de William H. Kersting**. A lista dos condutores com seus respectivos códigos pode ser visualizada abaixo:

```json
[
    {
        "id": 0,
        "size": "1",
        "stranding": "None",
        "material": "ACSR",
    },
    {
        "id": 1,
        "size": "1",
        "stranding": "7 STRD",
        "material": "Copper",
    },
    {
        "id": 2,
        "size": "1",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 3,
        "size": "2",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 4,
        "size": "2",
        "stranding": "7 STRD",
        "material": "Copper",
    },
    {
        "id": 5,
        "size": "2",
        "stranding": "7/1",
        "material": "ACSR",
    },
    {
        "id": 6,
        "size": "2",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 7,
        "size": "2",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 8,
        "size": "3",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 9,
        "size": "3",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 10,
        "size": "4",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 11,
        "size": "4",
        "stranding": "7/1",
        "material": "ACSR",
    },
    {
        "id": 12,
        "size": "4",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 13,
        "size": "4",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 14,
        "size": "5",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 15,
        "size": "5",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 16,
        "size": "6",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 17,
        "size": "6",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 18,
        "size": "6",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 19,
        "size": "7",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 20,
        "size": "8",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 21,
        "size": "9",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 22,
        "size": "10",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 23,
        "size": "12",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 24,
        "size": "14",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 25,
        "size": "16",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 26,
        "size": "18",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 27,
        "size": "19",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 28,
        "size": "20",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 29,
        "size": "22",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 30,
        "size": "24",
        "stranding": "AWG SLD",
        "material": "Copper",
    },
    {
        "id": 31,
        "size": "1/0",
        "stranding": "None",
        "material": "ACSR",
    },
    {
        "id": 32,
        "size": "1/0",
        "stranding": "7 STRD",
        "material": "Copper",
    },
    {
        "id": 33,
        "size": "1/0",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 34,
        "size": "2/0",
        "stranding": "None",
        "material": "ACSR",
    },
    {
        "id": 35,
        "size": "2/0",
        "stranding": "7 STRD",
        "material": "Copper",
    },
    {
        "id": 36,
        "size": "2/0",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 37,
        "size": "3/0",
        "stranding": "12 STRD",
        "material": "Copper",
    },
    {
        "id": 38,
        "size": "3/0",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 39,
        "size": "3/0",
        "stranding": "7 STRD",
        "material": "Copper",
    },
    {
        "id": 40,
        "size": "3/0",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 41,
        "size": "3/8",
        "stranding": "INCH STE",
        "material": "Steel",
    },
    {
        "id": 42,
        "size": "4/0",
        "stranding": "12 STRD",
        "material": "Copper",
    },
    {
        "id": 43,
        "size": "4/0",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 44,
        "size": "4/0",
        "stranding": "6/1",
        "material": "ACSR",
    },
    {
        "id": 45,
        "size": "4/0",
        "stranding": "7 STRD",
        "material": "Copper",
    },
    {
        "id": 46,
        "size": "4/0",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 47,
        "size": "250000",
        "stranding": "12 STRD",
        "material": "Copper",
    },
    {
        "id": 48,
        "size": "250000",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 49,
        "size": "250000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 50,
        "size": "266800",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 51,
        "size": "266800",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 52,
        "size": "300000",
        "stranding": "12 STRD",
        "material": "Copper",
    },
    {
        "id": 53,
        "size": "300000",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 54,
        "size": "300000",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 55,
        "size": "300000",
        "stranding": "30/7",
        "material": "ACSR",
    },
    {
        "id": 56,
        "size": "300000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 57,
        "size": "336400",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 58,
        "size": "336400",
        "stranding": "30/7",
        "material": "ACSR",
    },
    {
        "id": 59,
        "size": "336400",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 60,
        "size": "350000",
        "stranding": "12 STRD",
        "material": "Copper",
    },
    {
        "id": 61,
        "size": "350000",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 62,
        "size": "350000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 63,
        "size": "397500",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 64,
        "size": "397500",
        "stranding": "30/7",
        "material": "ACSR",
    },
    {
        "id": 65,
        "size": "397500",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 66,
        "size": "400000",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 67,
        "size": "450000",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 68,
        "size": "450000",
        "stranding": "CON LAG",
        "material": "AA",
    },
    {
        "id": 69,
        "size": "477000",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 70,
        "size": "477000",
        "stranding": "30/7",
        "material": "ACSR",
    },
    {
        "id": 71,
        "size": "477000",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 72,
        "size": "500000",
        "stranding": "19 STRD",
        "material": "Copper",
    },
    {
        "id": 73,
        "size": "500000",
        "stranding": "37 STRD",
        "material": "Copper",
    },
    {
        "id": 74,
        "size": "500000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 75,
        "size": "556500",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 76,
        "size": "556500",
        "stranding": "30/7",
        "material": "ACSR",
    },
    {
        "id": 77,
        "size": "556500",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 78,
        "size": "600000",
        "stranding": "37 STRD",
        "material": "Copper",
    },
    {
        "id": 79,
        "size": "600000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 80,
        "size": "605000",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 81,
        "size": "605000",
        "stranding": "54/7",
        "material": "ACSR",
    },
    {
        "id": 82,
        "size": "636000",
        "stranding": "27/7",
        "material": "ACSR",
    },
    {
        "id": 83,
        "size": "636000",
        "stranding": "30/19",
        "material": "ACSR",
    },
    {
        "id": 84,
        "size": "636000",
        "stranding": "54/7",
        "material": "ACSR",
    },
    {
        "id": 85,
        "size": "636000",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 86,
        "size": "666600",
        "stranding": "54/7",
        "material": "ACSR",
    },
    {
        "id": 87,
        "size": "700000",
        "stranding": "37 STRD",
        "material": "Copper",
    },
    {
        "id": 88,
        "size": "700000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 89,
        "size": "715500",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 90,
        "size": "715500",
        "stranding": "30/19",
        "material": "ACSR",
    },
    {
        "id": 91,
        "size": "715500",
        "stranding": "54/7",
        "material": "ACSR",
    },
    {
        "id": 92,
        "size": "715500",
        "stranding": "CLASS A",
        "material": "AA",
    },
    {
        "id": 93,
        "size": "750000",
        "stranding": "37 STRD",
        "material": "AA",
    },
    {
        "id": 94,
        "size": "750000",
        "stranding": "CON LAY",
        "material": "AA",
    },
    {
        "id": 95,
        "size": "795000",
        "stranding": "26/7",
        "material": "ACSR",
    },
    {
        "id": 96,
        "size": "795000",
        "stranding": "30/19",
        "material": "ACSR",
    },
    {
        "id": 97,
        "size": "795000",
        "stranding": "54/7",
        "material": "ACSR",
    }
]
```

Também é necessário definir um modelo de linha especificando os condutores da linha e sua configuração geométrica na estrutura utilizada. Para este exemplo são utilizados dois tipos de modelos de linha, um para a rede de média tensão e outro para a rede de baixa tensão. Também são especificados os condutores ids dos condutires de fase e de neutro para a média e a baixa tensão:

```python
phase_conduct = Conductor(id=57)
neutral_conduct = Conductor(id=44)

line_model_a = LineModel(loc_a=0.0 + 29.0j,
                         loc_b=2.5 + 29.0j,
                         loc_c=7.0 + 29.0j,
                         loc_n=4.0 + 25.0j,
                         conductor=phase_conduct,
                         neutral_conductor=neutral_conduct,
                         neutral=False)

phase_conduct_bt = Conductor(id=32)

line_model_b = LineModel(loc_a=0.0 + 29.0j,
                         loc_b=2.5 + 29.0j,
                         loc_c=7.0 + 29.0j,
                         loc_n=4.0 + 25.0j,
                         conductor=phase_conduct_bt,
                         neutral_conductor=neutral_conduct,
                         neutral=True)
```

Especificados os modelos de linha é possível passá-los como parâmetro da classe que irá especificar a ligação entre os nós, no MyGrid essa classe tem o nome de `Section()` e recebe como parâmetros um nome, os nós que estão em seus extremos, caso haja chave no seguimento esta é informada, o modelo de linha ou de transformador, e caso seja linha, o comprimento do seguimento de linha:

```python
# Trechos do alimentador S1_AL1
s1_a2 = Section(name='S1A2',
                n1=s1,
                n2=a2,
                switch=ch1,
                line_model=line_model_a,
                length=4)

a2_a1 = Section(name='A2A1',
                n1=a2,
                n2=a1,
                line_model=line_model_a,
                length=4)
a2_a3 = Section(name='A2A3',
                n1=a2,
                n2=a3,
                line_model=line_model_a,
                length=4)
a2_c1 = Section(name='A2C1',
                n1=a2,
                n2=c1,
                switch=ch3,
                line_model=line_model_a,
                length=4)

c1_c2 = Section(name='C1C2',
                n1=c1,
                n2=c2,
                line_model=line_model_a,
                length=4)
c1_c3 = Section(name='C1C3',
                n1=c1,
                n2=c3,
                line_model=line_model_a,
                length=4)

a3_b1 = Section(name='A3B1',
                n1=a3,
                n2=b1,
                switch=ch2,
                line_model=line_model_a,
                length=4)

b1_b2 = Section(name='B1B2',
                n1=b1,
                n2=b2,
                line_model=line_model_a,
                length=4)
b2_b3 = Section(name='B2B3',
                n1=b2,
                n2=b3,
                line_model=line_model_a,
                length=4)

# Trechos do alimentador S1_AL2
s1_f1 = Section(name='S1F1',
                n1=s1,
                n2=f1,
                switch=ch9,
                line_model=line_model_a,
                length=1.0)
f1_g1 = Section(name='F1G1',
                n1=f1,
                n2=g1,
                switch=ch10,
                line_model=line_model_a,
                length=1.0)
g1_d2 = Section(name='G1D2',
                n1=g1,
                n2=d2,
                switch=ch11,
                line_model=line_model_a,
                length=1.0)

# Trechos do alimentador S2_AL1
s2_d1 = Section(name='S2D1',
                n1=s2,
                n2=d1,
                switch=ch6,
                line_model=line_model_a,
                length=1.0)

d1_d2 = Section(name='D1D2',
                n1=d1,
                n2=d2,
                line_model=line_model_a,
                length=1.0)
d1_d3 = Section(name='D1D3',
                n1=d1,
                n2=d3,
                line_model=line_model_a,
                length=1.0)
d1_e1 = Section(name='D1E1',
                n1=d1,
                n2=e1,
                switch=ch7,
                line_model=line_model_a,
                length=1.0)
e1_e2 = Section(name='E1E2',
                n1=e1,
                n2=e2,
                line_model=line_model_a,
                length=1.0)
e1_e3 = Section(name='E1E3',
                n1=e1,
                n2=e3,
                line_model=line_model_a,
                length=1.0)

# Sections de encontro de alimentador
c3_e3 = Section(name='C3E3',
                n1=c3,
                n2=e3,
                switch=ch8,
                line_model=line_model_a,
                length=1.0)
b2_e2 = Section(name='B2E2',
                n1=b2,
                n2=e2,
                switch=ch4,
                line_model=line_model_a,
                length=1.0)

b3_c3 = Section(name='B3C3',
                n1=b3,
                n2=c3,
                switch=ch5,
                line_model=line_model_a,
                length=0.5)


# subgrid sections connecteds to A1
a1_aa1 = Section(name='A1AA1',
                 n1=a1,
                 n2=aa1,
                 transformer=t1,
                 length=3.0e-2)
aa1_aa2 = Section(name='AA1AA2',
                  n1=aa1,
                  n2=aa2,
                  line_model=line_model_b,
                  length=3.0e-2)
aa1_aa3 = Section(name='AA2AA3',
                  n1=aa1,
                  n2=aa3,
                  line_model=line_model_b,
                  length=3.0e-2)
```

