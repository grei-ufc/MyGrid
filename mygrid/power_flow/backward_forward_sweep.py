#! coding:utf-8

# Esta é a implementação do cálculo de flow de carga de varredura
# direta-inversa utilizando a estrutura de dados do pacote MyGrid

from mygrid.util import Phasor, R, P
from mygrid.grid import Section
import numpy as np


def calc_power_flow(substation):

        # atribui a tensão de fase da barra da subestação a todos
        # os nós de carga da subestação
        f1 = P(13.8e3 / np.sqrt(3), 0.0)
        _assign_substation_voltage(substation, f1)

        for feeder in substation.feeders.values():
            max_iterations = 50
            converg_crt = 0.001
            converg = 1e6
            iter = 0

            print('============================')
            print('Feeder {al} Sweep'.format(al=feeder.name))
            nodes_converg = dict()
            for node in feeder.load_nodes.values():
                nodes_converg[node.name] = 1e6

            while iter <= max_iterations and converg > converg_crt:
                iter += 1
                print('-------------------------')
                print('Iteration: {iter}'.format(iter=iter))

                voltage_nodes = dict()
                for node in feeder.load_nodes.values():
                    voltage_nodes[node.name] = R(node.voltage.r, node.voltage.i)

                _feeder_sweep(feeder)

                for node in feeder.load_nodes.values():
                    nodes_converg[node.name] = abs(voltage_nodes[node.name].m -
                                               node.voltage.m)

                converg = max(nodes_converg.values())
                print('Max. diferença de tensões: {conv}'.format(conv=converg))

        # for atualiza os valores das tensões dos nós de carga para valores
        # de tensão de linha
        substation.voltage.m = substation.voltage.m * np.sqrt(3)
        nodes = list()
        for feeder in substation.feeders.values():
            for node in feeder.load_nodes.values():
                if node.name not in nodes:
                    node.voltage.m = node.voltage.m * np.sqrt(3)
                    nodes.append(node.name)


def _search_section(feeder, n1, n2):
        """Função que busca sections em um alimendador entre os nós/switchs
          n1 e n2"""
        # for pecorre os nodes de carga do feeder
        for node in feeder.load_nodes.keys():

            # cria conjuntos das switchs ligadas ao node
            switchs_n1 = set(feeder.load_nodes[n1].switchs)
            switchs_n2 = set(feeder.load_nodes[n2].switchs)

            # verifica se existem switchs comuns aos nodes
            intersection_switchs = switchs_n1.intersection(switchs_n2)

            if intersection_switchs != set():
                # verifica quais sections estão ligados a switch
                # comum as nós.
                switch = intersection_switchs.pop()
                sections_switchs = []
                # identificação dos sections requeridos
                for section in feeder.sections.values():
                    if section.n1.name == switch:
                        if section.n2.name == n1 or section.n2.name == n2:
                            sections_switchs.append(section)
                    elif section.n2.name == switch:
                        if section.n1.name == n1 or section.n1.name == n2:
                            sections_switchs.append(section)
                # caso o comprimento da lista seja dois, ou seja, há switch
                # entre dois ós de carga, a função retorna os sections.
                if len(sections_switchs) == 2:
                    return sections_switchs
            else:
                # se não existirem switchs comuns, verifica qual section
                # tem os nodes n1 e n2 como extremidade
                for section in feeder.sections.values():
                    if section.n1.name == n1:
                        if section.n2.name == n2:
                            return section
                    elif section.n1.name == n2:
                        if section.n2.name == n1:
                            return section


def _assign_substation_voltage(substation, voltage):
    """ Função que atribui tensão à subestação
     e a define para todos os nós de carga"""
    substation.voltage = voltage
    for feeder in substation.feeders.values():
        for node in feeder.load_nodes.values():
            node.voltage = R(voltage.r, voltage.i)
        for section in feeder.sections.values():
            section.flow = R(0.0, 0.0)


def _feeder_sweep(feeder):
    """ Função que varre os feeders pelo
    método varredura direta/inversa"""

    # guarda os nós de carga na variável feeder_nodes
    feeder_nodes = feeder.load_nodes.values()

    # guarda a rnp dos nós de carga na variável feder_rnp
    feder_rnp = feeder.load_nodes_tree.rnp

    # guarda a árvore de cada nós de carga
    load_nodes_tree = feeder.load_nodes_tree.tree

    # variáveis para o auxílio na determinação do nó mais profundo
    max_depth = 0

    # for percorre a rnp dos nós de carga tomando valores
    # em pares (profundidade, nó).
    for node_depth in feder_rnp.transpose():
        # pega os nomes dos nós de carga.
        feeder_nodes_names = [node.name for node in feeder_nodes]

        # verifica se a profundidade do nó é maior do que a
        # profundidade máxima e se ele está na lista de nós do feeder.
        if (int(node_depth[0]) > max_depth) \
           and (node_depth[1] in feeder_nodes_names):
            max_depth = int(node_depth[0])

    # depth recebe a profundidae máxima determinada
    depth = max_depth

    # seção do cálculo das potências partindo dos
    # nós com maiores profundidades até o nó raíz
    while depth >= 0:
        # guarda os nós com maiores profundidades.
        nodes = [feeder.load_nodes[node_depth[1]]
               for node_depth in feder_rnp.transpose() if
               int(node_depth[0]) == depth]

        # decrementodo da profundidade.
        depth -= 1

        # for que percorre os nós com a profundidade
        # armazenada na variável depth
        for node in nodes:
            # zera as potências para que na próxima
            # iteração não ocorra acúmulo.
            node.equivalent_power.r = 0.0
            node.equivalent_power.i = 0.0

            # armazena a árvore do nó de carga
            # armazenado na variável nó
            neighbors = load_nodes_tree[node.name]

            # guarda os pares (profundidade, nó)
            node_depth = [node_depth for node_depth in feder_rnp.transpose()
                       if node_depth[1] == node.name]
            downstream_neighbors = list()

            # for que percorre a árvore de cada nó de carga
            for neighbor in neighbors:
                # verifica quem é neighbor do nó desejado.
                depth_neighbor = [n_depth for n_depth in
                                feder_rnp.transpose()
                                if n_depth[1] == neighbor]

                # verifica se a profundidade do neighbor é maior
                if int(depth_neighbor[0][0]) > int(node_depth[0][0]):
                    # armazena os neighbors a jusante.
                    downstream_neighbors.append(
                        feeder.load_nodes[depth_neighbor[0][1]])

            # verifica se não há neighbor a jusante,
            # se não houverem o nó de carga analisado
            # é o último do ramo.
            if downstream_neighbors == []:
                node.equivalent_power.r += node.power.r / 3.0
                node.equivalent_power.i += node.power.i / 3.0
            else:
                # soma a power da carga associada ao nó atual
                node.equivalent_power.r += node.power.r / 3.0
                node.equivalent_power.i += node.power.i / 3.0

                # acrescenta à potência do nó atual
                # as potências dos nós a jusante
                for downstream_node in downstream_neighbors:
                    node.equivalent_power.r += downstream_node.equivalent_power.r
                    node.equivalent_power.i += downstream_node.equivalent_power.i

                    # chama a função busca_trecho para definir
                    # quais sections estão entre o nó atual e o nó a jusante
                    section = _search_section(feeder,
                                           node.name,
                                           downstream_node.name)
                    # se o section não for uma instancia da classe
                    # Section(quando há switch entre nós de cargas)
                    # a impedância é calculada
                    if not isinstance(section, Section):

                        r1, x1 = section[0].calc_impedance()
                        r2, x2 = section[1].calc_impedance()
                        r, x = r1 + r2, x1 + x2
                    # se o section atual for uma instancia da classe section
                    else:
                        r, x = section.calc_impedance()
                        # calculo das potências dos nós de carga a jusante.
                    node.equivalent_power.r += r * (downstream_node.equivalent_power.m ** 2) / \
                        downstream_node.voltage.m ** 2
                    node.equivalent_power.i += x * (downstream_node.equivalent_power.m ** 2) / \
                        downstream_node.voltage.m ** 2

    depth = 0
    # seção do cálculo de atualização das tensões
    while depth <= max_depth:
        # salva os nós de carga a montante
        nodes = [feeder.load_nodes[col_depth_node[1]]
               for col_depth_node in feder_rnp.transpose()
               if int(col_depth_node[0]) == depth + 1]
        # percorre os nós para guardar a árvore do nó requerido
        for node in nodes:
            neighbors = load_nodes_tree[node.name]
            # guarda os pares (profundidade,nó)
            node_depth = [col_depth_node
                       for col_depth_node in feder_rnp.transpose()
                       if col_depth_node[1] == node.name]
            upstream_neighbors = list()
            # verifica quem é neighbor do nó desejado.
            for neighbor in neighbors:
                depth_neighbor = [n_depth
                                for n_depth in feder_rnp.transpose()
                                if n_depth[1] == neighbor]
                if int(depth_neighbor[0][0]) < int(node_depth[0][0]):
                    # armazena os neighbors a montante.
                    upstream_neighbors.append(
                        feeder.load_nodes[depth_neighbor[0][1]])
            # armazena o primeiro neighbor a montante
            upstream_node = upstream_neighbors[0]
            section = _search_section(feeder, node.name, upstream_node.name)
            # se existir switch, soma a resistência dos dois sections
            if not isinstance(section, Section):

                r1, x1 = section[0].calc_impedance()
                r2, x2 = section[1].calc_impedance()
                r, x = r1 + r2, x1 + x2
            # caso não exista, a resistência é a do próprio section
            else:
                r, x = section.calc_impedance()

            v_mon = upstream_node.voltage.m

            p = node.equivalent_power.r
            q = node.equivalent_power.i

            # parcela de perdas
            p += r * (node.equivalent_power.m ** 2) / node.voltage.m ** 2
            q += x * (node.equivalent_power.m ** 2) / node.voltage.m ** 2

            v_jus = v_mon ** 2 - 2 * (r * p + x * q) + \
                (r ** 2 + x ** 2) * (p ** 2 + q ** 2) / v_mon ** 2
            v_jus = np.sqrt(v_jus)

            k1 = (p * x - q * r) / v_mon
            k2 = v_mon - (p * r - q * x) / v_mon

            ang = upstream_node.voltage.a * np.pi / 180.0 - np.arctan(k1 / k2)

            node.voltage.m = v_jus
            node.voltage.a = ang * 180.0 / np.pi

            print('Node Voltage {name}: {tens}'.format(
                name=node.name,
                tens=node.voltage.m * np.sqrt(3) / 1e3))

            # calcula o flow de current passante node section
            z = R(r, x)
            current = (node.voltage - upstream_node.voltage) / z
            # se houver switchs, ou seja, há dois sections a mesma current
            # é atribuida
            if not isinstance(section, Section):
                section[0].flow = current
                section[1].flow = current
            else:
                section.flow = current
        depth += 1
