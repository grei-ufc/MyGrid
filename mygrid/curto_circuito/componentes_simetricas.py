#! coding: utf-8

from mygrid.util import P, R, Base
from mygrid.rede import Chave

def config_objects(subestacao,
                   impedancia_eq_positiva=0.0,
                   impedancia_eq_zero=0.0):
    """conifg_objects: configura os objetos da substecao para calculo 
    de curto-circuito."""
    subestacao.impedancia_positiva = impedancia_eq_positiva
    subestacao.impedancia_zero = impedancia_eq_zero
    subestacao.impedancia_equivalente_positiva = impedancia_eq_positiva
    subestacao.impedancia_equivalente_zero = impedancia_eq_zero

    for transformador in subestacao.transformadores.values():
        subestacao.base_sub = Base(transformador.tensao_secundario.m,
                                   transformador.potencia.m)
        break

    for alimentador in subestacao.alimentadores.values():
        for trecho in alimentador.trechos.values():
            trecho.impedancia_positiva = (trecho.condutor.rp + trecho.condutor.xp * 1j) * trecho.comprimento
            trecho.impedancia_zero = (trecho.condutor.rz + trecho.condutor.xz * 1j) * trecho.comprimento

            trecho.resistencia_contato = 100.0

            trecho.base = subestacao.base_sub

            trecho.impedancia_equivalente_positiva = trecho.impedancia_positiva / trecho.base.impedancia
            trecho.impedancia_equivalente_zero = trecho.impedancia_zero / trecho.base.impedancia

            trecho.fluxo = R(r=0.0, i=0.0)

    calculaimpedanciaeq(subestacao)


def calculacurto(subestacao, tipo):

    if tipo == 'trifasico':
        curto_trifasico = [['Trecho 3fasico', 'Curto pu', 'Curto A']]
        for alimentador_atual, r in subestacao.alimentadores.iteritems():
            for trecho in subestacao.alimentadores[alimentador_atual].trechos.values():
                curto = _calcula_curto_trifasico(trecho)
                curto_trifasico.append([trecho.nome,
                                        str(curto.pu),
                                        str(curto.m)])

        return curto_trifasico

    elif tipo == 'monofasico':
        curto_monofasico = [['Trecho 1fasico', 'Curto pu', 'Curto A']]
        for alimentador_atual, r in subestacao.alimentadores.iteritems():
            for trecho in subestacao.alimentadores[alimentador_atual].trechos.values():
                curto = _calcula_curto_monofasico(trecho)
                curto_monofasico.append([trecho.nome,
                                         str(curto.pu),
                                         str(curto.m)])

        return curto_monofasico

    elif tipo == 'bifasico':
        curto_bifasico = [['Trecho 2fasico', 'Curto pu', 'Curto A']]
        for alimentador_atual, r in subestacao.alimentadores.iteritems():
            for trecho in subestacao.alimentadores[alimentador_atual].trechos.values():
                curto = _calcula_curto_bifasico(trecho)
                curto_bifasico.append([trecho.nome,
                                       str(curto.pu),
                                       str(curto.m)])

        return curto_bifasico

    elif tipo == 'monofasico_minimo':
        curto_monofasico_minimo = [['Trecho 1fasico min', 'Curto pu', 'Curto A']]
        for alimentador_atual, r in subestacao.alimentadores.iteritems():
            for trecho in subestacao.alimentadores[alimentador_atual].trechos.values():
                curto = _calcula_curto_monofasico_minimo(trecho)
                curto_monofasico_minimo.append([trecho.nome,
                                                str(curto.pu),
                                                str(curto.m)])

        return curto_monofasico_minimo


def calculaimpedanciaeq(subestacao):

    trechosvisitados = []  # guarda os trechos em que já foram calculados a impedância equivalente

    for alimentador_atual, r in subestacao.alimentadores.iteritems():  # procura o nó inicial(raiz) do alimentador
        for i in subestacao.alimentadores[alimentador_atual].trechos.values():
            for j in subestacao.alimentadores[alimentador_atual].setores[r.arvore_nos_de_carga.raiz].nos_de_carga.keys():
                prox_no = subestacao.alimentadores[alimentador_atual].setores[r.arvore_nos_de_carga.raiz].nos_de_carga[j]  # nó a partir do qual será procurado trechos conectados a ele
                trechoatual = subestacao  # último trecho que foi calculado a impedância equivalente
                break
            break
        break

    _calculaimpedanciaeq(subestacao, trechoatual, prox_no, alimentador_atual, trechosvisitados)


def _calculaimpedanciaeq(subestacao, trecho_anterior, no_atual, alimentador_atual, trechosvisitados):
    for i in subestacao.alimentadores[alimentador_atual].trechos.values():
        if i not in trechosvisitados and (i.n1 or i.n2) == no_atual:  # procura trechos conectados ao no_atual (prox_no da execução anterior)
            if type(no_atual) == Chave:  # verifica se a ligação é feita por meio de chave, verificando-se o estado da chave
                if no_atual.estado == 0:
                    continue
                else:
                    pass
            else:
                pass

            # calcula impedância equivalente do trecho
            i.impedancia_equivalente_positiva = i.impedancia_equivalente_positiva + trecho_anterior.impedancia_equivalente_positiva
            i.impedancia_equivalente_zero = i.impedancia_equivalente_zero + trecho_anterior.impedancia_equivalente_zero
            trechosvisitados.append(i)
            trecho_atual = i

            # procura o pro_no para calcular as proximas impedancias equivalentes
            if no_atual == i.n1:
                prox_no = i.n2
            else:
                prox_no = i.n1

            _calculaimpedanciaeq(subestacao, trecho_atual, prox_no, alimentador_atual, trechosvisitados)
        else:
            pass
    return


def _calcula_impedancia(trecho):
    return (trecho.comprimento * trecho.condutor.rp,
            trecho.comprimento * trecho.condutor.xp)


def _calcula_curto_monofasico(trecho):
    curto1 = (3.0) * trecho.base.corrente / (2 * trecho.impedancia_equivalente_positiva + trecho.impedancia_equivalente_zero)
    correntecc = R(curto1.real, curto1.imag)
    correntecc.base = trecho.base.corrente
    return correntecc


def _calcula_curto_bifasico(trecho):
    curto2 = (3 ** 0.5) * trecho.base.corrente / (2 * trecho.impedancia_equivalente_positiva)
    correntecc = R(curto2.real, curto2.imag)
    correntecc.base = trecho.base.corrente
    return correntecc


def _calcula_curto_trifasico(trecho):
    curto3 = 1.0 * trecho.base.corrente / (trecho.impedancia_equivalente_positiva)
    correntecc = R(curto3.real, curto3.imag)
    correntecc.base = trecho.base.corrente
    return correntecc


def _calcula_curto_monofasico_minimo(trecho):
    curto1m = 3.0 * trecho.base.corrente / (2 * trecho.impedancia_equivalente_positiva + trecho.impedancia_equivalente_zero+3*trecho.resistencia_contato/trecho.base.impedancia)
    correntecc = R(curto1m.real, curto1m.imag)
    correntecc.base = trecho.base.corrente
    return correntecc
