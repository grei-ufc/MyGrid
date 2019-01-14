import sys
sys.path.append('../')
from mygrid.grid import GridElements, ExternalGrid, Generation, Shunt_Capacitor
from mygrid.grid import Substation, Sector, Switch, LineModel
from mygrid.grid import Section, LoadNode, TransformerModel, Conductor, Auto_TransformerModel
from mygrid.util import R, P
from mygrid.util import p2r, r2p

from mygrid.power_flow.backward_forward_sweep_3p import calc_power_flow
from mygrid.short_circuit.symmetrical_components import config_objects, calc_equivalent_impedance, calc_short_circuit

from terminaltables import AsciiTable
import time

# Este trecho do módulo faz parte de sua documentacao e serve
# como exemplo de como utiliza-lo. Uma pequena rede com duas
# subestações é representada.

# Na Subestação S1 existem três sectors de carga: A, B, C.
# O setor A possui três nós de carga: A1, A2, e A3
# O setor B possui três nós de carga: B1, B2, e B3
# O setor C possui três nós de carga: C1, C2, e C3
# O nó de carga S1 alimenta o setor A por A2 através da chave 1
# O nó de carga A3 alimenta o setor B por B1 através da chave 2
# O nó de carga A2 alimenta o setor C por C1 através da chave 3

# Na Subestação S2 existem dois sectors de carga: D e E.
# O setor D possui três nós de carga: D1, D2, e D3
# O setor E possui três nós de carga: E1, E2, e E3
# O nó de carga S2 alimenta o setor D por D1 através da chave 6
# O nó de carga D1 alimenta o setor E por E1 através da chave 7

# A chave 4 interliga os sectors B e E respectivamente por B2 e E2
# A chave 5 interliga os sectors B e C respectivamente por B3 e C3
# A chave 8 interliga os sectors C e E respectivamente por C3 e E3

# Para representar a rede são criados então os seguintes objetos:
# _chaves : dicionario contendo objetos do tipo chave que representam
# as switchs do sistema;
# _seotores_1 : dicionario contendo objetos setor que representam
# os sectors da Subestação S1;
# _seotores_2 : dicionario contendo objetos setor que representam
# os sectors da Subestação S2;
# _nos : dicionarios contendo objetos load_nodes que representam
# os nós de carga dos sectors em cada um dos sections das
# subestações;
# _substations : dicionario contendo objetos Substation que herdam
# a classe Arvore e contém todos os elementos que
# representam um ramo da rede elétrica, como switchs, sectors,
# nós de carga e sections;


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

# tensao nominal

vll_mt = p2r(13.8e3, 0.0)
vll_bt = p2r(380.0, 0.0)

# transformers
t1 = TransformerModel(name="T1",
                      primary_voltage=vll_mt,
                      secondary_voltage=vll_bt,
                      power=225e3,
                      impedance=0.01 + 0.2j)

eg1 = ExternalGrid(name='extern grid 1', vll=vll_mt)

# Definição GD's

c2_PV = Generation(name="c2_PV",
                   P=10e3 + 0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV")
c3_PV = Generation(name="c3_PV",
                   P=10e3 + 0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV")
b2_PV = Generation(name="b2_PV",
                   P=10e3 + 0j,
                   Qmin=-200.0e3j,
                   Qmax=200.0e3j,
                   Vmin=0.975,
                   Vmax=1.05,
                   Vspecified=0.98,
                   DV_presc=0.002,
                   generation_type="PV")
b1_PQ = Generation(name="b2_PV",
                   Pa=100e3 + 300e3j,
                   Pb=0.0e3 + 200.0e3j,
                   Pc=0.0e3 + 0.0e3j,
                   generation_type="PQ")
SC_C1 = Shunt_Capacitor(vll=13.8e3,
                        Qa=100e3, Qb=100e3, Qc=100e3,
                        type_connection="wye")

auto_t1 = Auto_TransformerModel(name="auto_t1",
                                step=0.75,
                                tap_max=15,
				vhold=120,
                                voltage=12.47e3,
                                R=5,
                                X=11,
                                CTP=600,
                                Npt=20,
				Z=(1+1J)*1e-6)

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

spacing500=[0.0 + 28.0j,
            2.5 + 28.0j,
            7.0 + 28.0j,
            4.0 + 28.0j]

phase_conduct = Conductor(id=57)
neutral_conduct = Conductor(id=44)

line_model_a  =  LineModel(loc=spacing500,
                     phasing=['b','a','c','n'],
                     conductor=phase_conduct,
                     neutral_conductor=neutral_conduct)

phase_conduct_bt = Conductor(id=32)
line_model_b  =  LineModel(loc=spacing500,
                     phasing=['b','a','c','n'],
                     conductor=phase_conduct_bt,
                     neutral_conductor=neutral_conduct)

# # Trechos do alimentador S1_AL1
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

load_nodes = [s1, a1, a2, a3, b1, b2, b3, c1, c2, c3,
              s2, d1, d2, d3, e1, e2, e3, f1, g1, aa1, aa2, aa3]
sections = [s1_a2, a2_a1, a2_a3, a2_c1, c1_c2, c1_c3, c3_e3, a3_b1, b1_b2, b2_b3, b2_e2,
            b3_c3, s2_d1, d1_d2, d1_d3, d1_e1, e1_e2, e1_e3, s1_f1, f1_g1, g1_d2,
            a1_aa1, aa1_aa2, aa1_aa3]

switchs = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11]

grid_elements = GridElements(name='my_grid_elements')

grid_elements.add_switch(switchs)
grid_elements.add_load_node(load_nodes)
grid_elements.add_section(sections)

grid_elements.create_grid()

# calculo de fluxo de carga
inicio = time.time()
calc_power_flow(grid_elements.dist_grids['F0'])
fim = time.time()
print(fim - inicio)
grid_elements.nodes_table_voltage(Df=False)

# calculo de curto-circuito

from mygrid.short_circuit.phase_components import biphasic
from mygrid.short_circuit.phase_components import biphasic_to_ground
from mygrid.short_circuit.phase_components import three_phase, mono_phase
from mygrid.short_circuit.phase_components import min_mono_phase
from mygrid.short_circuit.phase_components import  three_phase_to_ground

distgrid=grid_elements.dist_grids['F0']
inicio = time.time()
Iftg=three_phase_to_ground(distgrid, 'C1')
Ifb=biphasic(distgrid, 'C1')
Ifbg=biphasic_to_ground(distgrid, 'A2')
ft= three_phase(distgrid, 'C1')
fim = time.time()
print(fim - inicio)
