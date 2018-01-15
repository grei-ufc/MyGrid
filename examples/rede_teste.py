from mygrid.rede import Subestacao, Alimentador, Setor, Chave
from mygrid.rede import Trecho, NoDeCarga, Transformador, Condutor
from mygrid.util import R, P

from mygrid.fluxo_de_carga.varred_dir_inv import calcular_fluxo_de_carga
from mygrid.curto_circuito.componentes_simetricas import config_objects, calculaimpedanciaeq, calculacurto


from terminaltables import AsciiTable

# Este trecho do módulo faz parte de sua documentacao e serve
# como exemplo de como utiliza-lo. Uma pequena rede com duas
# subestações é representada.

# Na Subestação S1 existem três setores de carga: A, B, C.
# O setor A possui três nós de carga: A1, A2, e A3
# O setor B possui três nós de carga: B1, B2, e B3
# O setor C possui três nós de carga: C1, C2, e C3
# O nó de carga S1 alimenta o setor A por A2 através da chave 1
# O nó de carga A3 alimenta o setor B por B1 através da chave 2
# O nó de carga A2 alimenta o setor C por C1 através da chave 3

# Na Subestação S2 existem dois setores de carga: D e E.
# O setor D possui três nós de carga: D1, D2, e D3
# O setor E possui três nós de carga: E1, E2, e E3
# O nó de carga S2 alimenta o setor D por D1 através da chave 6
# O nó de carga D1 alimenta o setor E por E1 através da chave 7

# A chave 4 interliga os setores B e E respectivamente por B2 e E2
# A chave 5 interliga os setores B e C respectivamente por B3 e C3
# A chave 8 interliga os setores C e E respectivamente por C3 e E3

# Para representar a rede são criados então os seguintes objetos:
# _chaves : dicionario contendo objetos do tipo chave que representam
# as chaves do sistema;
# _seotores_1 : dicionario contendo objetos setor que representam
# os setores da Subestação S1;
# _seotores_2 : dicionario contendo objetos setor que representam
# os setores da Subestação S2;
# _nos : dicionarios contendo objetos nos_de_carga que representam
# os nós de carga dos setores em cada um dos trechos das
# subestações;
# _subestacoes : dicionario contendo objetos Subestacao que herdam
# a classe Arvore e contém todos os elementos que
# representam um ramo da rede elétrica, como chaves, setores,
# nós de carga e trechos;

# chaves do alimentador de S1
ch1 = Chave(nome='1', estado=1)
ch2 = Chave(nome='2', estado=1)
ch3 = Chave(nome='3', estado=1)

# chaves de Fronteira
ch4 = Chave(nome='4', estado=0)
ch5 = Chave(nome='5', estado=0)
ch8 = Chave(nome='8', estado=0)

# chaves do alimentador de S2
ch6 = Chave(nome='6', estado=1)
ch7 = Chave(nome='7', estado=1)

# Nos de carga do alimentador S1_AL1
s1 = NoDeCarga(nome='S1',
               vizinhos=['A2'],
               potencia=R(0.0, 0.0),
               chaves=['1'])
a1 = NoDeCarga(nome='A1',
               vizinhos=['A2'],
               potencia=R(160.0e3, 120.0e3))
a2 = NoDeCarga(nome='A2',
               vizinhos=['S1', 'A1', 'A3', 'C1'],
               potencia=R(150.0e3, 110.0e3),
               chaves=['1', '3'])
a3 = NoDeCarga(nome='A3',
               vizinhos=['A2', 'B1'],
               potencia=R(100.0e3, 80.0e3),
               chaves=['2'])
b1 = NoDeCarga(nome='B1',
               vizinhos=['B2', 'A3'],
               potencia=R(200.0e3, 140.0e3),
               chaves=['2'])
b2 = NoDeCarga(nome='B2',
               vizinhos=['B1', 'B3', 'E2'],
               potencia=R(150.0e3, 110.0e3),
               chaves=['4'])
b3 = NoDeCarga(nome='B3',
               vizinhos=['B2', 'C3'],
               potencia=R(100.0e3, 80.0e3),
               chaves=['5'])
c1 = NoDeCarga(nome='C1',
               vizinhos=['C2', 'C3', 'A2'],
               potencia=R(200.0e3, 140.0e3),
               chaves=['3'])
c2 = NoDeCarga(nome='C2',
               vizinhos=['C1'],
               potencia=R(150.0e3, 110.0e3))
c3 = NoDeCarga(nome=  'C3',
               vizinhos=['C1', 'E3', 'B3'],
               potencia=R(100.0e3, 80.0e3),
               chaves=['5', '8'])

# Nos de carga do alimentador S2_AL1
s2 = NoDeCarga(nome='S2',
               vizinhos=['D1'],
               potencia=R(0.0, 0.0),
               chaves=['6'])
d1 = NoDeCarga(nome='D1',
               vizinhos=['S2', 'D2', 'D3', 'E1'],
               potencia=R(200.0e3, 160.0e3),
               chaves=['6', '7'])
d2 = NoDeCarga(nome='D2',
               vizinhos=['D1'],
               potencia=R(90.0e3, 40.0e3))
d3 = NoDeCarga(nome=  'D3',
               vizinhos=['D1'],
               potencia=R(100.0e3, 80.0e3))
e1 = NoDeCarga(nome=  'E1',
               vizinhos=['E3', 'E2', 'D1'],
               potencia=R(100.0e3, 40.0e3),
               chaves=['7'])
e2 = NoDeCarga(nome='E2',
               vizinhos=['E1', 'B2'],
               potencia=R(110.0e3, 70.0e3),
               chaves=['4'])
e3 = NoDeCarga(nome='E3',
               vizinhos=['E1', 'C3'],
               potencia=R(150.0e3, 80.0e3),
               chaves = ['8'])

cond_1 = Condutor(nome='CAA 266R',
                  rp=0.2391,
                  xp=0.37895,
                  rz=0.41693,
                  xz=1.55591,
                  ampacidade=301)

# Trechos do alimentador S1_AL1
s1_ch1 = Trecho(nome='S1CH1', n1=s1, n2=ch1, condutor=cond_1, comprimento=0.01)

ch1_a2 = Trecho(nome='CH1A2', n1=ch1, n2=a2, condutor=cond_1, comprimento=1.0)
a2_a1 = Trecho(nome='A2A1', n1=a2, n2=a1, condutor=cond_1, comprimento=1.0)
a2_a3 = Trecho(nome='A2A3', n1=a2, n2=a3, condutor=cond_1, comprimento=1.0)
a2_ch3 = Trecho(nome='A2CH3', n1=a2, n2=ch3, condutor=cond_1, comprimento=0.5)
a3_ch2 = Trecho(nome='A3CH2', n1=a3, n2=ch2, condutor=cond_1, comprimento=0.5)

ch3_c1 = Trecho(nome='CH3C1', n1=ch3, n2=c1, condutor=cond_1, comprimento=0.5)
c1_c2 = Trecho(nome='C1C2', n1=c1, n2=c2, condutor=cond_1, comprimento=1.0)
c1_c3 = Trecho(nome='C1C3', n1=c1, n2=c3, condutor=cond_1, comprimento=1.0)
c3_ch8 = Trecho(nome='C3CH8', n1=c3, n2=ch8, condutor=cond_1, comprimento=0.5)
c3_ch5 = Trecho(nome='C3CH5', n1=c3, n2=ch5, condutor=cond_1, comprimento=0.5)

ch2_b1 = Trecho(nome='CH2B1', n1=ch2, n2=b1, condutor=cond_1, comprimento=0.5)
b1_b2 = Trecho(nome='B1B2', n1=b1, n2=b2, condutor=cond_1, comprimento=1.0)
b2_ch4 = Trecho(nome='B2CH4', n1=b2, n2=ch4, condutor=cond_1, comprimento=0.5)
b2_b3 = Trecho(nome='B2B3', n1=b2, n2=b3, condutor=cond_1, comprimento=1.0)
b3_ch5 = Trecho(nome='B3CH5', n1=b3, n2=ch5, condutor=cond_1, comprimento=0.5)

# Trechos do alimentador S2_AL1
s2_ch6 = Trecho(nome='S2CH6', n1=s2, n2=ch6, condutor=cond_1, comprimento=0.01)

ch6_d1 = Trecho(nome='CH6D1', n1=ch6, n2=d1, condutor=cond_1, comprimento=1.0)
d1_d2 = Trecho(nome='D1D2', n1=d1, n2=d2, condutor=cond_1, comprimento=1.0)
d1_d3 = Trecho(nome='D1D3', n1=d1, n2=d3, condutor=cond_1, comprimento=1.0)
d1_ch7 = Trecho(nome='D1CH7', n1=d1, n2=ch7, condutor=cond_1, comprimento=0.5)

ch7_e1 = Trecho(nome='CH7E1', n1=ch7, n2=e1, condutor=cond_1, comprimento=0.5)
e1_e2 = Trecho(nome='E1E2', n1=e1, n2=e2, condutor=cond_1, comprimento=1.0)
e2_ch4 = Trecho(nome='E2CH4', n1=e2, n2=ch4, condutor=cond_1, comprimento=0.5)
e1_e3 = Trecho(nome='E1E3', n1=e1, n2=e3, condutor=cond_1, comprimento=1.0)
e3_ch8 = Trecho(nome='E3CH8', n1=e3, n2=ch8, condutor=cond_1, comprimento=0.5)

# Setor S1
st1 = Setor(nome='S1',
            vizinhos=['A'],
            nos_de_carga=[s1])

# setor A
stA = Setor(nome='A',
            vizinhos=['S1', 'B', 'C'],
            nos_de_carga=[a1, a2, a3])

# Setor B
stB = Setor(nome='B',
            vizinhos=['A', 'C', 'E'],
            nos_de_carga=[b1, b2, b3])

# Setor C
stC = Setor(nome='C',
            vizinhos=['A', 'B', 'E'],
            nos_de_carga=[c1, c2, c3])

# Setor S2
st2 = Setor(nome='S2',
            vizinhos=['D'],
            nos_de_carga=[s2])

# Setor D
stD = Setor(nome='D',
            vizinhos=['S2', 'E'],
            nos_de_carga=[d1, d2, d3])

# Setor E
stE = Setor(nome='E',
            vizinhos=['D', 'B', 'C'],
            nos_de_carga=[e1, e2, e3])

# ligação das chaves com os respectivos setores
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

# Alimentador 1 de S1
taux = [s1_ch1, ch1_a2, a2_a1, a2_a3, a2_ch3, ch3_c1, c1_c2, c1_c3, c3_ch5,
         c3_ch8, a3_ch2, ch2_b1, b1_b2, b2_ch4, b2_b3, b3_ch5]
sub_1_al_1 = Alimentador(nome='S1_AL1',
                         setores=[st1, stA, stB, stC],
                         trechos=taux,
                         chaves=[ch1, ch2, ch3, ch4, ch5, ch8])

# Alimentador 1 de S2
taux = [s2_ch6, ch6_d1, d1_d2, d1_d3, d1_ch7, ch7_e1, e1_e2, e2_ch4, e1_e3, e3_ch8]
sub_2_al_1 = Alimentador(nome='S2_AL1',
                         setores=[st2, stD, stE],
                         trechos=taux,
                         chaves=[ch6, ch7, ch4, ch8])

t1 = Transformador(nome='S1_T1',
                   tensao_primario=P(69e3, 0.0),
                   tensao_secundario=P(13.8e3, 0.0),
                   potencia=P(10e6, 0.0),
                   impedancia=R(0.5, 0.2))

t2 = Transformador(nome='S2_T1',
                   tensao_primario=P(69e3, 0.0),
                   tensao_secundario=P(13.8e3, 0.0),
                   potencia=P(10e6, 0.0),
                   impedancia=R(0.5, 0.2))

sub_1 = Subestacao(nome='S1', alimentadores=[sub_1_al_1], transformadores=[t1])

sub_2 = Subestacao(nome='S2', alimentadores=[sub_2_al_1], transformadores=[t2])

_subestacoes = {sub_1_al_1.nome: sub_1_al_1, sub_2_al_1.nome: sub_2_al_1}

sub_1_al_1.ordenar(raiz='S1')
sub_2_al_1.ordenar(raiz='S2')

sub_1_al_1.gerar_arvore_nos_de_carga()
sub_2_al_1.gerar_arvore_nos_de_carga()

# calculos com a subestacao 1

# calculo de fluxo de carga

calcular_fluxo_de_carga(sub_1)

# calculo de curto circuito

config_objects(sub_1)

curto_trifasico = calculacurto(sub_1, 'trifasico')
tabela = AsciiTable(curto_trifasico)
print(tabela.table)

calculacurto(sub_1, 'monofasico')
calculacurto(sub_1, 'bifasico')
calculacurto(sub_1, 'monofasico_minimo')
