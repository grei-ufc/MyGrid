# Primeira Rede Teste:

#### Importando bibliotecas
```python
from mygrid.grid import GridElements, ExternalGrid, Generation
from mygrid.grid import Shunt_Capacitor
from mygrid.grid import Substation, Sector, Switch, LineModel, UnderGroundLine
from mygrid.grid import Under_Ground_Conductor
from mygrid.grid import Section, LoadNode, TransformerModel, Conductor
from mygrid.grid import Auto_TransformerModel
from mygrid.util import R, P
from mygrid.util import p2r, r2p

from terminaltables import AsciiTable
import time
import numpy as np
``` 
#### Definindo chaves, espaçamento dos cabos de uma linha elétrica e as impendâncias internas de uma geração distribuida
```python
spacing500=[0.0 + 29.0j,
            2.5 + 29.0j,
            7.0 + 29.0j,
            4.0 + 25.0j]

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

Z = np.eye(3, dtype=complex)*(15+100j)
Z1 = np.eye(3, dtype=complex)
Z2 = np.eye(3, dtype=complex)*(1.5+5j)

```

#### Definindo as tensões nominais da rede
```python
# tensao nominal

vll_mt = p2r(13.8e3, 0.0)
vll_bt = p2r(380.0, 0.0)
```

#### Transformador
```python
t1 = TransformerModel(name="T1",
                      primary_voltage=vll_mt,
                      secondary_voltage=vll_bt,
                      power=225e3,
                      impedance=0.01 + 0.2j)
```
#### Rede externa
```python
eg1 = ExternalGrid(name='extern grid 1', vll=vll_mt)
```

#### Definição de GD's
```python
C2_PV = Generation(name="C2_PV",
                   P=0e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV",
                   Z=Z)

A3_PV = Generation(name="A3_PV",
                   P=0e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV",
                   Z=Z)

B3_PV = Generation(name="B3_PV",
                   P=0e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV",
                   Z=Z)

B1_PV = Generation(name="B1_PV",
                   P=0e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV",
                   Z=Z)

C3_PV = Generation(name="C3_PV",
                   P=10e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=1.0,
                   DV_presc=0.002,
                   generation_type="PV",
                   Z=Z)

G1_PV = Generation(name="G1_PV",
                   P=10e3+0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=1.0,
                   DV_presc=0.002,
                   generation_type="PV",
                   Z=Z2)
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
                    Pa=-2.62e3j,
                    Pb=-2.62e3j,
                    Pc=-2.62e3j,
                    generation_type="PQ",
                    Z=Z)

aa2_PQ = Generation(name="aa2_PV",
                    Pa=8.12e3j,
                    Pb=8.12e3j,
                    Pc=8.12e3j,
                    generation_type="PQ",
                    Z=Z)
```
#### Capacitor shunt
```python
SC_C1 = Shunt_Capacitor(vll=13.8e3,
                        Qa=1000e3, Qb=1000e3, Qc=1000e3,
                        type_connection="wye")
```

#### Nos de carga do alimentador S1_AL1
```python
s1 = LoadNode(name='S1',
              voltage=vll_mt,
              external_grid=eg1)
a1 = LoadNode(name='A1',
              power=120+160j,
              voltage=vll_mt)
a2 = LoadNode(name='A2',
              power=150.0e3 + 110.0e3j,
              voltage=vll_mt)
a3 = LoadNode(name='A3',
              generation=A3_PV,
              ppa=100.0e3 + 36.670e3j,
              ppb=100.0e3 + 36.670e3j,
              ppc=100.0e3 + 36.670e3j,
              voltage=vll_mt)
b1 = LoadNode(name='B1',
              generation=B1_PV,
              ppa=100.0e3 + 36.670e3j,
              ppb=100.0e3 + 36.670e3j,
              ppc=100.0e3 + 36.670e3j,
              voltage=vll_mt)
b2 = LoadNode(name='B2',
              generation = b2_PV,
              power=150.0e3 + 110.0e3j,
              voltage=vll_mt)
b3 = LoadNode(name='B3',
              generation=B3_PV,
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt)
c1 = LoadNode(name='C1',
              power=200.0e3 + 140.0e3j,
              voltage=vll_mt)
c2 = LoadNode(name='C2',
              generation=C2_PV,
              power=150.0e3 + 110.0e3j,
              voltage=vll_mt)
c3 = LoadNode(name='C3',
              #generation=C3_PV,
              ppa=20.0e3 + 36.670e3j,
              ppb=150.0e3 + 36.670e3j,
              ppc=100.0e3 + 36.670e3j,
              voltage=vll_mt)
```
#### Nos de carga do alimentador S1_AL2
```python
f1 = LoadNode(name='F1',
              power=100.0e3 + 80.0e3j,
              voltage=vll_mt)
g1 = LoadNode(name='G1',
              power=100.0e3 + 80.0e3j,
              # generation=G1_PV,
              voltage=vll_mt)
```
#### Nos de carga do alimentador S2_AL1
```python
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
```

#### Rede de baixa tensão conectada em  A1
```python
aa1 = LoadNode(name='AA1',
               power=0.0 + 0.0j,

               voltage=vll_bt)
aa2 = LoadNode(name='AA2',
               # generation=aa2_PQ,
               power=20.0e3 + 5.0e3j,
               voltage=vll_bt)
aa3 = LoadNode(name='AA3',
               # generation=aa1_PQ,
               power=20.0e3 + 5.0e3j,
               voltage=vll_bt)
```
#### Definição das linhas elétricas
```python
phase_conduct = Conductor(id=57)
neutral_conduct = Conductor(id=44)

line_model_a  =  LineModel(loc=spacing500,
                     phasing=['a','b','c','n'],
                     conductor=phase_conduct,
                     neutral_conductor=neutral_conduct)

phase_conduct_bt = Conductor(id=32)
line_model_b  =  LineModel(loc=spacing500,
                     phasing=['a','b','c','n'],
                     conductor=phase_conduct_bt,
                     neutral_conductor=neutral_conduct)
```
#### Trechos do alimentador S1_AL1
```python
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
```
#### Trechos do alimentador S1_AL2
```python
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
```
#### Trechos do alimentador S2_AL1
```python
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
```
#### Trechos de encontro de alimentador
```python
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
```

#### Trechos em baixa tensão a montante de  A1
```python
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
aa1_aa3 = Section(name='AA1AA3',
                  n1=aa1,
                  n2=aa3,
                  line_model=line_model_b,
                  length=3.0e-2)
```
#### Listando nós, trechos e chaves:
```python
load_nodes = [s1, a1, a2, a3, b1, b2, b3, c1, c2, c3,
              s2, d1, d2, d3, e1, e2, e3, f1, g1, aa1, aa2, aa3]

sections = [s1_a2, a2_a1, a2_a3, a2_c1, c1_c2, c1_c3, c3_e3, a3_b1, b1_b2,
            b2_b3, b2_e2, b3_c3, s2_d1, d1_d2, d1_d3, d1_e1, e1_e2, e1_e3,
            s1_f1, f1_g1, g1_d2, a1_aa1, aa1_aa2, aa1_aa3]

switchs = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11]
```

#Criando o objeto rede:
```python
grid_elements = GridElements(name='my_grid_elements')
```
####Adicionando os elementos constituintes da rede.
```python
grid_elements.add_switch(switchs)
grid_elements.add_load_node(load_nodes)
grid_elements.add_section(sections)
```
#### Criando a rede:
```python
grid_elements.create_grid()
```
# Fluxo de Carga
```python
from mygrid.power_flow.backward_forward_sweep_3p import calc_power_flow

inicio = time.time()
calc_power_flow(grid_elements.dist_grids['F0'])
fim = time.time()
print(fim - inicio)
grid_elements.nodes_table_voltage(Df=False)  
```
```grid_elements.dist_grids``` retorna, em lista, objetos contidos em alimentadores que pertecem a uma mesma subestação.

```grid_elements.nodes_table_voltage```. Retorna em tela uma tabela que contém as principais informações do fluxo de carga para toda a rede. Caso ```Df = True```, retorna um objeto no formato DataFrame.
# Curto-Circuito
Curto circuito em componentes de fase:
```python
from mygrid.short_circuit import phase_components
```


```phase_components``` possui os seguintes métodos para o cálculo do curto-circuito.

+ *```phase_components.biphasic```* para curto bifásico.

+ *```phase_components.biphasic_to_ground```* para curto bifásico com contato para terra.

+ *```phase_components.three_phase_to_ground```* para curto trifásico com contato para terra.

+ *```phase_components.three_phase```* para curto trifásico.

+ *```phase_components.mono_phase```* para curto monofásico.

+ *```phase_components.min_mono_phase```* para curto monofásico mínimo.

Esses métodos possuem os seguintes argumentos:

+ ```distgrid``` objeto rede.

+ ```node_name``` nome do nó em falta.

+ ```fs='Higher'``` Indica que fases considerar na execução do cálculo do curto-circuito. 
    - ```Higher``` indica que será considerado a combinação de fases que gere o maior nível de curto.
    - Para curto bifásico  três combinações são aceitas: ```Fab```, ```Fac``` e ```Fbc```
    - Para curto bifásico com contato para terra três combinações são aceitas: ```Fab_g```, ```Fac_g``` e ```Fbc_g```
    - Para curto monofásico  três combinações são aceitas: ```Fag```, ```Fcg``` e ```Fbg```.
    - Para curto monofásico mínimo três combinações são aceitas: ```Fag_min```, ```Fcg_min``` e ```Fbg_min```

+ ```Df``` Indica se o resultado retornado será no formato de dicionário ou de dataframe.

+ ```zc=0+0j``` Impedância de contato.

+ ```zt``` Impedância do solo. Usada somente em *```phase_components.min_mono_phase```*.


#### Exemplo
```python
from mygrid.short_circuit.phase_components import biphasic
from mygrid.short_circuit.phase_components import biphasic_to_ground
from mygrid.short_circuit.phase_components import three_phase, mono_phase
from mygrid.short_circuit.phase_components import min_mono_phase
from mygrid.short_circuit.phase_components import  three_phase_to_ground

distgrid=grid_elements.dist_grids['F0']

Iftg=three_phase_to_ground(distgrid, 'C1')
Ifb=biphasic(distgrid, 'C1')
Ifbg=biphasic_to_ground(distgrid, 'A2', fs='Fab_g')
ft= three_phase(distgrid, 'C1')
```