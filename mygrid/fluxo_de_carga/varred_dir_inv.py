#! coding:utf-8

# Esta é a implementação do cálculo de fluxo de carga de varredura
# direta-inversa utilizando a estrutura de dados do pacote MyGrid

from mygrid.util import Fasor
from mygrid.rede import Trecho
import numpy as np


def calcular_fluxo_de_carga(subestacao):

        # atribui a tensão de fase da barra da subestação a todos
        # os nós de carga da subestação
        f1 = Fasor(mod=13.8e3 / np.sqrt(3), ang=0.0, tipo=Fasor.Tensao)
        _atribuir_tensao_a_subestacao(subestacao, f1)

        for alimentador in subestacao.alimentadores.values():
            max_iteracaoes = 50
            criterio_converg = 0.001
            converg = 1e6
            iter = 0

            print '============================'
            print 'Varredura no alimentador {al}'.format(al=alimentador.nome)
            converg_nos = dict()
            for no in alimentador.nos_de_carga.values():
                converg_nos[no.nome] = 1e6

            while iter <= max_iteracaoes and converg > criterio_converg:
                iter += 1
                print '-------------------------'
                print 'Iteração: {iter}'.format(iter=iter)

                tensao_nos = dict()
                for no in alimentador.nos_de_carga.values():
                    tensao_nos[no.nome] = Fasor(real=no.tensao.real,
                                                imag=no.tensao.imag,
                                                tipo=Fasor.Tensao)

                _varrer_alimentador(alimentador)

                for no in alimentador.nos_de_carga.values():
                    converg_nos[no.nome] = abs(tensao_nos[no.nome].mod -
                                               no.tensao.mod)

                converg = max(converg_nos.values())
                print 'Max. diferença de tensões: {conv}'.format(conv=converg)

        # for atualiza os valores das tensões dos nós de carga para valores
        # de tensão de linha
        subestacao.tensao.mod = subestacao.tensao.mod * np.sqrt(3)
        nos = list()
        for alimentador in subestacao.alimentadores.values():
            for no in alimentador.nos_de_carga.values():
                if no.nome not in nos:
                    no.tensao.mod = no.tensao.mod * np.sqrt(3)
                    nos.append(no.nome)


def _busca_trecho(alimentador, n1, n2):
        """Função que busca trechos em um alimendador entre os nós/chaves
          n1 e n2"""
        # for pecorre os nos de carga do alimentador
        for no in alimentador.nos_de_carga.keys():

            # cria conjuntos das chaves ligadas ao no
            chaves_n1 = set(alimentador.nos_de_carga[n1].chaves)
            chaves_n2 = set(alimentador.nos_de_carga[n2].chaves)

            # verifica se existem chaves comuns aos nos
            chaves_intersec = chaves_n1.intersection(chaves_n2)

            if chaves_intersec != set():
                # verifica quais trechos estão ligados a chave
                # comum as nós.
                chave = chaves_intersec.pop()
                trechos_ch = []
                # identificação dos trechos requeridos
                for trecho in alimentador.trechos.values():
                    if trecho.n1.nome == chave:
                        if trecho.n2.nome == n1 or trecho.n2.nome == n2:
                            trechos_ch.append(trecho)
                    elif trecho.n2.nome == chave:
                        if trecho.n1.nome == n1 or trecho.n1.nome == n2:
                            trechos_ch.append(trecho)
                # caso o comprimento da lista seja dois, ou seja, há chave
                # entre dois ós de carga, a função retorna os trechos.
                if len(trechos_ch) == 2:
                    return trechos_ch
            else:
                # se não existirem chaves comuns, verifica qual trecho
                # tem os nos n1 e n2 como extremidade
                for trecho in alimentador.trechos.values():
                    if trecho.n1.nome == n1:
                        if trecho.n2.nome == n2:
                            return trecho
                    elif trecho.n1.nome == n2:
                        if trecho.n2.nome == n1:
                            return trecho


def _atribuir_tensao_a_subestacao(subestacao, tensao):
    """ Função que atribui tensão à subestação
     e a define para todos os nós de carga"""
    subestacao.tensao = tensao
    for alimentador in subestacao.alimentadores.values():
        for no in alimentador.nos_de_carga.values():
            no.tensao = Fasor(real=tensao.real,
                              imag=tensao.imag,
                              tipo=Fasor.Tensao)
        for trecho in alimentador.trechos.values():
            trecho.fluxo = Fasor(real=0.0,
                                 imag=0.0,
                                 tipo=Fasor.Corrente)


def _varrer_alimentador(alimentador):
    """ Função que varre os alimentadores pelo
    método varredura direta/inversa"""

    # guarda os nós de carga na variável nos_alimentador
    nos_alimentador = alimentador.nos_de_carga.values()

    # guarda a rnp dos nós de carga na variável rnp_alimentador
    rnp_alimentador = alimentador.arvore_nos_de_carga.rnp

    # guarda a árvore de cada nós de carga
    arvore_nos_de_carga = alimentador.arvore_nos_de_carga.arvore

    # variáveis para o auxílio na determinação do nó mais profundo
    prof_max = 0

    # for percorre a rnp dos nós de carga tomando valores
    # em pares (profundidade, nó).
    for no_prof in rnp_alimentador.transpose():
        # pega os nomes dos nós de carga.
        nos_alimentador_nomes = [no.nome for no in nos_alimentador]

        # verifica se a profundidade do nó é maior do que a
        # profundidade máxima e se ele está na lista de nós do alimentador.
        if (int(no_prof[0]) > prof_max) \
           and (no_prof[1] in nos_alimentador_nomes):
            prof_max = int(no_prof[0])

    # prof recebe a profundidae máxima determinada
    prof = prof_max

    # seção do cálculo das potências partindo dos
    # nós com maiores profundidades até o nó raíz
    while prof >= 0:
        # guarda os nós com maiores profundidades.
        nos = [alimentador.nos_de_carga[no_prof[1]]
               for no_prof in rnp_alimentador.transpose() if
               int(no_prof[0]) == prof]

        # decrementodo da profundidade.
        prof -= 1

        # for que percorre os nós com a profundidade
        # armazenada na variável prof
        for no in nos:
            # zera as potências para que na próxima
            # iteração não ocorra acúmulo.
            no.potencia_eq.real = 0.0
            no.potencia_eq.imag = 0.0

            # armazena a árvore do nó de carga
            # armazenado na variável nó
            vizinhos = arvore_nos_de_carga[no.nome]

            # guarda os pares (profundidade, nó)
            no_prof = [no_prof for no_prof in rnp_alimentador.transpose()
                       if no_prof[1] == no.nome]
            vizinhos_jusante = list()

            # for que percorre a árvore de cada nó de carga
            for vizinho in vizinhos:
                # verifica quem é vizinho do nó desejado.
                vizinho_prof = [viz_prof for viz_prof in
                                rnp_alimentador.transpose()
                                if viz_prof[1] == vizinho]

                # verifica se a profundidade do vizinho é maior
                if int(vizinho_prof[0][0]) > int(no_prof[0][0]):
                    # armazena os vizinhos a jusante.
                    vizinhos_jusante.append(
                        alimentador.nos_de_carga[vizinho_prof[0][1]])

            # verifica se não há vizinho a jusante,
            # se não houverem o nó de carga analisado
            # é o último do ramo.
            if vizinhos_jusante == []:
                no.potencia_eq.real += no.potencia.real / 3.0
                no.potencia_eq.imag += no.potencia.imag / 3.0
            else:
                # soma a potencia da carga associada ao nó atual
                no.potencia_eq.real += no.potencia.real / 3.0
                no.potencia_eq.imag += no.potencia.imag / 3.0

                # acrescenta à potência do nó atual
                # as potências dos nós a jusante
                for no_jus in vizinhos_jusante:
                    no.potencia_eq.real += no_jus.potencia_eq.real
                    no.potencia_eq.imag += no_jus.potencia_eq.imag

                    # chama a função busca_trecho para definir
                    # quais trechos estão entre o nó atual e o nó a jusante
                    trecho = _busca_trecho(alimentador,
                                           no.nome,
                                           no_jus.nome)
                    # se o trecho não for uma instancia da classe
                    # Trecho(quando há chave entre nós de cargas)
                    # a impedância é calculada
                    if not isinstance(trecho, Trecho):

                        r1, x1 = trecho[0].calcula_impedancia()
                        r2, x2 = trecho[1].calcula_impedancia()
                        r, x = r1 + r2, x1 + x2
                    # se o trecho atual for uma instancia da classe trecho
                    else:
                        r, x = trecho.calcula_impedancia()
                        # calculo das potências dos nós de carga a jusante.
                    no.potencia_eq.real += r * (no_jus.potencia_eq.mod ** 2) / \
                        no_jus.tensao.mod ** 2
                    no.potencia_eq.imag += x * (no_jus.potencia_eq.mod ** 2) / \
                        no_jus.tensao.mod ** 2

    prof = 0
    # seção do cálculo de atualização das tensões
    while prof <= prof_max:
        # salva os nós de carga a montante
        nos = [alimentador.nos_de_carga[col_no_prof[1]]
               for col_no_prof in rnp_alimentador.transpose()
               if int(col_no_prof[0]) == prof + 1]
        # percorre os nós para guardar a árvore do nó requerido
        for no in nos:
            vizinhos = arvore_nos_de_carga[no.nome]
            # guarda os pares (profundidade,nó)
            no_prof = [col_no_prof
                       for col_no_prof in rnp_alimentador.transpose()
                       if col_no_prof[1] == no.nome]
            vizinhos_montante = list()
            # verifica quem é vizinho do nó desejado.
            for vizinho in vizinhos:
                vizinho_prof = [viz_prof
                                for viz_prof in rnp_alimentador.transpose()
                                if viz_prof[1] == vizinho]
                if int(vizinho_prof[0][0]) < int(no_prof[0][0]):
                    # armazena os vizinhos a montante.
                    vizinhos_montante.append(
                        alimentador.nos_de_carga[vizinho_prof[0][1]])
            # armazena o primeiro vizinho a montante
            no_mon = vizinhos_montante[0]
            trecho = _busca_trecho(alimentador, no.nome, no_mon.nome)
            # se existir chave, soma a resistência dos dois trechos
            if not isinstance(trecho, Trecho):

                r1, x1 = trecho[0].calcula_impedancia()
                r2, x2 = trecho[1].calcula_impedancia()
                r, x = r1 + r2, x1 + x2
            # caso não exista, a resistência é a do próprio trecho
            else:
                r, x = trecho.calcula_impedancia()

            v_mon = no_mon.tensao.mod

            p = no.potencia_eq.real
            q = no.potencia_eq.imag

            # parcela de perdas
            p += r * (no.potencia_eq.mod ** 2) / no.tensao.mod ** 2
            q += x * (no.potencia_eq.mod ** 2) / no.tensao.mod ** 2

            v_jus = v_mon ** 2 - 2 * (r * p + x * q) + \
                (r ** 2 + x ** 2) * (p ** 2 + q ** 2) / v_mon ** 2
            v_jus = np.sqrt(v_jus)

            k1 = (p * x - q * r) / v_mon
            k2 = v_mon - (p * r - q * x) / v_mon

            ang = no_mon.tensao.ang * np.pi / 180.0 - np.arctan(k1 / k2)

            no.tensao.mod = v_jus
            no.tensao.ang = ang * 180.0 / np.pi

            print 'Tensao do no {nome}: {tens}'.format(
                nome=no.nome,
                tens=no.tensao.mod * np.sqrt(3) / 1e3)

            # calcula o fluxo de corrente passante no trecho
            corrente = no.tensao.real - no_mon.tensao.real
            corrente += (no.tensao.imag - no_mon.tensao.imag) * 1.0j
            corrente /= (r + x * 1.0j)
            # se houver chaves, ou seja, há dois trechos a mesma corrente
            # é atribuida
            if not isinstance(trecho, Trecho):
                trecho[0].fluxo = Fasor(real=corrente.real,
                                        imag=corrente.imag,
                                        tipo=Fasor.Corrente)
                trecho[1].fluxo = Fasor(real=corrente.real,
                                        imag=corrente.imag,
                                        tipo=Fasor.Corrente)
            else:
                trecho.fluxo = Fasor(real=corrente.real,
                                     imag=corrente.imag,
                                     tipo=Fasor.Corrente)
        prof += 1
