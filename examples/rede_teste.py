from mygrid.grid import Substation, Feeder, Sector, Switch
from mygrid.grid import Section, LoadNode, Transformer, Conductor
from mygrid.util import R, P

from mygrid.power_flow.backward_forward_sweep import calc_power_flow
from mygrid.short_circuit.symmetrical_components import config_objects, calc_equivalent_impedance, calc_short_circuit

from terminaltables import AsciiTable

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

# switchs do alimentador de S1
ch1 = Switch(name='1', state=1)
ch2 = Switch(name='2', state=1)
ch3 = Switch(name='3', state=1)

# switchs de Fronteira
ch4 = Switch(name='4', state=0)
ch5 = Switch(name='5', state=0)
ch8 = Switch(name='8', state=0)

# switchs do alimentador de S2
ch6 = Switch(name='6', state=1)
ch7 = Switch(name='7', state=1)

# Nos de carga do alimentador S1_AL1
s1 = LoadNode(name='S1',
              neighbors=['A2'],
              power=R(0.0, 0.0),
              switchs=['1'])
a1 = LoadNode(name='A1',
              neighbors=['A2'],
              power=R(160.0e3, 120.0e3))
a2 = LoadNode(name='A2',
              neighbors=['S1', 'A1', 'A3', 'C1'],
              power=R(150.0e3, 110.0e3),
              switchs=['1', '3'])
a3 = LoadNode(name='A3',
              neighbors=['A2', 'B1'],
              power=R(100.0e3, 80.0e3),
              switchs=['2'])
b1 = LoadNode(name='B1',
              neighbors=['B2', 'A3'],
              power=R(200.0e3, 140.0e3),
              switchs=['2'])
b2 = LoadNode(name='B2',
              neighbors=['B1', 'B3', 'E2'],
              power=R(150.0e3, 110.0e3),
              switchs=['4'])
b3 = LoadNode(name='B3',
              neighbors=['B2', 'C3'],
              power=R(100.0e3, 80.0e3),
              switchs=['5'])
c1 = LoadNode(name='C1',
              neighbors=['C2', 'C3', 'A2'],
              power=R(200.0e3, 140.0e3),
              switchs=['3'])
c2 = LoadNode(name='C2',
              neighbors=['C1'],
              power=R(150.0e3, 110.0e3))
c3 = LoadNode(name=  'C3',
              neighbors=['C1', 'E3', 'B3'],
              power=R(100.0e3, 80.0e3),
              switchs=['5', '8'])

# Nos de carga do alimentador S2_AL1
s2 = LoadNode(name='S2',
              neighbors=['D1'],
              power=R(0.0, 0.0),
              switchs=['6'])
d1 = LoadNode(name='D1',
              neighbors=['S2', 'D2', 'D3', 'E1'],
              power=R(200.0e3, 160.0e3),
              switchs=['6', '7'])
d2 = LoadNode(name='D2',
              neighbors=['D1'],
              power=R(90.0e3, 40.0e3))
d3 = LoadNode(name=  'D3',
              neighbors=['D1'],
              power=R(100.0e3, 80.0e3))
e1 = LoadNode(name=  'E1',
              neighbors=['E3', 'E2', 'D1'],
              power=R(100.0e3, 40.0e3),
              switchs=['7'])
e2 = LoadNode(name='E2',
              neighbors=['E1', 'B2'],
              power=R(110.0e3, 70.0e3),
              switchs=['4'])
e3 = LoadNode(name='E3',
              neighbors=['E1', 'C3'],
              power=R(150.0e3, 80.0e3),
              switchs = ['8'])

cond_1 = Conductor(name='CAA 266R',
                   rp=0.2391,
                   xp=0.37895,
                   rz=0.41693,
                   xz=1.55591,
                   ampacity=301)

# Trechos do alimentador S1_AL1
s1_ch1 = Section(name='S1CH1', n1=s1, n2=ch1, conductor=cond_1, length=0.01)

ch1_a2 = Section(name='CH1A2', n1=ch1, n2=a2, conductor=cond_1, length=1.0)
a2_a1 = Section(name='A2A1', n1=a2, n2=a1, conductor=cond_1, length=1.0)
a2_a3 = Section(name='A2A3', n1=a2, n2=a3, conductor=cond_1, length=1.0)
a2_ch3 = Section(name='A2CH3', n1=a2, n2=ch3, conductor=cond_1, length=0.5)
a3_ch2 = Section(name='A3CH2', n1=a3, n2=ch2, conductor=cond_1, length=0.5)

ch3_c1 = Section(name='CH3C1', n1=ch3, n2=c1, conductor=cond_1, length=0.5)
c1_c2 = Section(name='C1C2', n1=c1, n2=c2, conductor=cond_1, length=1.0)
c1_c3 = Section(name='C1C3', n1=c1, n2=c3, conductor=cond_1, length=1.0)
c3_ch8 = Section(name='C3CH8', n1=c3, n2=ch8, conductor=cond_1, length=0.5)
c3_ch5 = Section(name='C3CH5', n1=c3, n2=ch5, conductor=cond_1, length=0.5)

ch2_b1 = Section(name='CH2B1', n1=ch2, n2=b1, conductor=cond_1, length=0.5)
b1_b2 = Section(name='B1B2', n1=b1, n2=b2, conductor=cond_1, length=1.0)
b2_ch4 = Section(name='B2CH4', n1=b2, n2=ch4, conductor=cond_1, length=0.5)
b2_b3 = Section(name='B2B3', n1=b2, n2=b3, conductor=cond_1, length=1.0)
b3_ch5 = Section(name='B3CH5', n1=b3, n2=ch5, conductor=cond_1, length=0.5)

# Trechos do alimentador S2_AL1
s2_ch6 = Section(name='S2CH6', n1=s2, n2=ch6, conductor=cond_1, length=0.01)

ch6_d1 = Section(name='CH6D1', n1=ch6, n2=d1, conductor=cond_1, length=1.0)
d1_d2 = Section(name='D1D2', n1=d1, n2=d2, conductor=cond_1, length=1.0)
d1_d3 = Section(name='D1D3', n1=d1, n2=d3, conductor=cond_1, length=1.0)
d1_ch7 = Section(name='D1CH7', n1=d1, n2=ch7, conductor=cond_1, length=0.5)

ch7_e1 = Section(name='CH7E1', n1=ch7, n2=e1, conductor=cond_1, length=0.5)
e1_e2 = Section(name='E1E2', n1=e1, n2=e2, conductor=cond_1, length=1.0)
e2_ch4 = Section(name='E2CH4', n1=e2, n2=ch4, conductor=cond_1, length=0.5)
e1_e3 = Section(name='E1E3', n1=e1, n2=e3, conductor=cond_1, length=1.0)
e3_ch8 = Section(name='E3CH8', n1=e3, n2=ch8, conductor=cond_1, length=0.5)

# Sector S1
st1 = Sector(name='S1',
             neighbors=['A'],
             load_nodes=[s1])

# setor A
stA = Sector(name='A',
             neighbors=['S1', 'B', 'C'],
             load_nodes=[a1, a2, a3])

# Sector B
stB = Sector(name='B',
             neighbors=['A', 'C', 'E'],
             load_nodes=[b1, b2, b3])

# Sector C
stC = Sector(name='C',
             neighbors=['A', 'B', 'E'],
             load_nodes=[c1, c2, c3])

# Sector S2
st2 = Sector(name='S2',
             neighbors=['D'],
             load_nodes=[s2])

# Sector D
stD = Sector(name='D',
             neighbors=['S2', 'E'],
             load_nodes=[d1, d2, d3])

# Sector E
stE = Sector(name='E',
             neighbors=['D', 'B', 'C'],
             load_nodes=[e1, e2, e3])

# ligação das switchs com os respectivos sectors
ch1.n1 = st1
ch1.n2 = stA

ch2.n1 = stA
ch2.n2 = stB

ch3.n1 = stA
ch3.n2 = stC

ch4.n1 = stB
ch4.n2 = stE

ch5.n1 = stB
ch5.n2 = stC

ch6.n1 = st2
ch6.n2 = stD

ch7.n1 = stD
ch7.n2 = stE

ch8.n1 = stC
ch8.n2 = stE

# Feeder 1 de S1
taux = [s1_ch1, ch1_a2, a2_a1, a2_a3, a2_ch3, ch3_c1, c1_c2, c1_c3, c3_ch5,
         c3_ch8, a3_ch2, ch2_b1, b1_b2, b2_ch4, b2_b3, b3_ch5]
sub_1_al_1 = Feeder(name='S1_AL1',
                         sectors=[st1, stA, stB, stC],
                         sections=taux,
                         switchs=[ch1, ch2, ch3, ch4, ch5, ch8])

# Feeder 1 de S2
taux = [s2_ch6, ch6_d1, d1_d2, d1_d3, d1_ch7, ch7_e1, e1_e2, e2_ch4, e1_e3, e3_ch8]
sub_2_al_1 = Feeder(name='S2_AL1',
                         sectors=[st2, stD, stE],
                         sections=taux,
                         switchs=[ch6, ch7, ch4, ch8])

t1 = Transformer(name='S1_T1',
                   primary_voltage=P(69e3, 0.0),
                   secondary_voltage=P(13.8e3, 0.0),
                   power=P(10e6, 0.0),
                   impedance=R(0.5, 0.2))

t2 = Transformer(name='S2_T1',
                   primary_voltage=P(69e3, 0.0),
                   secondary_voltage=P(13.8e3, 0.0),
                   power=P(10e6, 0.0),
                   impedance=R(0.5, 0.2))

sub_1 = Substation(name='S1', feeders=[sub_1_al_1], transformers=[t1])

sub_2 = Substation(name='S2', feeders=[sub_2_al_1], transformers=[t2])

_substations = {sub_1_al_1.name: sub_1_al_1, sub_2_al_1.name: sub_2_al_1}

sub_1_al_1.order(root='S1')
sub_2_al_1.order(root='S2')

sub_1_al_1.generate_load_nodes_tree()
sub_2_al_1.generate_load_nodes_tree()

# calculos com a subestacao 1

# calculo de fluxo de carga

calc_power_flow(sub_1)

# calculo de curto circuito

config_objects(sub_1)

three_phase_sc = calc_short_circuit(sub_1, 'three-phase')
tabela = AsciiTable(three_phase_sc)
print(tabela.table)

calc_short_circuit(sub_1, 'line-to-ground')
calc_short_circuit(sub_1, 'line-to-line')
calc_short_circuit(sub_1, 'line-to-ground-min')
