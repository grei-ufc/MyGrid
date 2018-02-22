from mygrid.util import Phasor, R, P
from mygrid.util import r2p, p2r
from mygrid.grid import Section
import numpy as np


def calc_power_flow(dist_grid):

    # -------------------------
    # variables declarations
    # -------------------------
    max_iterations = 100
    converg_crt = 0.001
    converg = 1e6
    iter = 0

    print('============================')
    print('Distribution Grid {dg} Sweep'.format(dg=dist_grid.name))
    
    nodes_converg = dict()
    for node in dist_grid.load_nodes.values():
        nodes_converg[node.name] = 1e6

    # -------------------------------------
    # main loop for power flow calculation
    # -------------------------------------
    while iter <= max_iterations and converg > converg_crt:
        iter += 1
        print('<<<<-----------BFS------------>>>>')
        print('Iteration: {iter}'.format(iter=iter))

        voltage_nodes = dict()
        for node in dist_grid.load_nodes.values():
            voltage_nodes[node.name] = node.vp

        # ----------------------------------
        # back-forward sweep implementation
        # ----------------------------------
        _dist_grid_sweep(dist_grid)

        # -------------------------
        # convergence verification
        # -------------------------
        for node in dist_grid.load_nodes.values():
            nodes_converg[node.name] = np.mean(abs(voltage_nodes[node.name] - node.vp))
        converg = max(nodes_converg.values())
        print('Max. diff between load nodes voltage values: {conv}'.format(conv=converg))


def _dist_grid_sweep(dist_grid):
    """ Função que varre a dist_grid pelo
    método varredura direta/inversa"""

    dist_grid_rnp = dist_grid.load_nodes_tree.rnp
    load_nodes_tree = dist_grid.load_nodes_tree.tree

    # depth and max_depth recebem a profundidae maxima
    depth = max_depth = _get_dist_grid_max_depth(dist_grid)

    # ----------------------------------------------
    # Inicio da varredura inversa
    # ----------------------------------------------
    print('Backward Sweep phase <<<<----------')
    # seção do cálculo das potências partindo dos
    # nós com maiores profundidades até o nó raíz
    while depth >= 0:
        # guarda os nós com maiores profundidades.
        nodes = [dist_grid.load_nodes[node_depth[1]]
               for node_depth in dist_grid_rnp.transpose() if
               int(node_depth[0]) == depth]

        # decrementodo da profundidade.
        depth -= 1

        # for que percorre os nós com a profundidade
        # armazenada na variável depth
        for node in nodes:

            # atualiza o valor de corrente passante com o valor
            # da corente da carga para que na prox. iteração 
            # do fluxo de carga não ocorra acúmulo.
            node.ip = node.i

            downstream_neighbors = _get_downstream_neighbors_nodes(node, dist_grid)

            # verifica se não há neighbor a jusante,
            # se não houverem o nó de carga analisado
            # é o último do ramo.
            if downstream_neighbors == []:
                continue
            else:
                # precorre os nos a jusante do no atual
                # para calculo de fluxos passantes
                for downstream_node in downstream_neighbors:
                    # chama a função busca_trecho para definir
                    # quais sections estão entre o nó atual e o nó a jusante
                    section = _search_section(dist_grid,
                                              node,
                                              downstream_node)
                    
                    # ------------------------------------
                    # Equacionamento: Calculo de corretes
                    # ------------------------------------
                    node.ip += np.dot(section.c, downstream_node.vp) + \
                               np.dot(section.d, downstream_node.ip)

                    # -------------------------------------

                    print(node.name + '<<<---' + downstream_node.name)

    print('Forward Sweep phase ---------->>>>')

    depth = 1
    # seção do cálculo de atualização das tensões
    while depth <= max_depth:
        # salva os nós de carga a montante
        nodes = [dist_grid.load_nodes[col_depth_node[1]]
                 for col_depth_node in dist_grid_rnp.transpose()
                 if int(col_depth_node[0]) == depth]

        # percorre os nós para guardar a árvore do nó requerido
        for node in nodes:

            upstream_node = _get_upstream_neighbor_node(dist_grid, node)
            section = _search_section(dist_grid, node, upstream_node)

            # ------------------------------------
            # Equacionamento: Calculo de tensoes
            # ------------------------------------
            node.vp = np.dot(section.A, upstream_node.vp) - np.dot(section.B, node.ip)
            # ------------------------------------
            print(upstream_node.name + '--->>>' + node.name)
        depth += 1


def _get_dist_grid_max_depth(dist_grid):
    
    dist_grid_nodes = dist_grid.load_nodes.values()
    dist_grid_rnp = dist_grid.load_nodes_tree.rnp
    
    max_depth = 0

    # for percorre a rnp dos nós de carga tomando valores
    # em pares (profundidade, nó).
    for node_depth in dist_grid_rnp.transpose():
        # obtem os nomes dos nos de carga.
        dist_grid_nodes_names = [node.name for node in dist_grid_nodes]

        # verifica se a profundidade do nó é maior do que a
        # profundidade máxima e se ele está na lista de nós do dist_grid.
        if (int(node_depth[0]) > max_depth) \
           and (node_depth[1] in dist_grid_nodes_names):
            max_depth = int(node_depth[0])

    return max_depth


def _get_downstream_neighbors_nodes(node, dist_grid):

    dist_grid_rnp = dist_grid.load_nodes_tree.rnp
    load_nodes_tree = dist_grid.load_nodes_tree.tree

    # guarda os pares (profundidade, nó)
    node_depth = [node_depth for node_depth in dist_grid_rnp.transpose()
                  if node_depth[1] == node.name]

    neighbors = load_nodes_tree[node.name]
    downstream_neighbors = list()

    # for que percorre a árvore de cada nó de carga vizinho
    for neighbor in neighbors:
        
        # Tem como melhorar

        # verifica quem é neighbor do nó desejado.
        depth_neighbor = [n_depth for n_depth in
                          dist_grid_rnp.transpose()
                          if n_depth[1] == neighbor]

        # verifica se a profundidade do neighbor é maior
        if int(depth_neighbor[0][0]) > int(node_depth[0][0]):
            # armazena os neighbors a jusante.
            downstream_neighbors.append(
                dist_grid.load_nodes[depth_neighbor[0][1]])

    return downstream_neighbors


def _get_upstream_neighbor_node(dist_grid, node):
    
    dist_grid_rnp = dist_grid.load_nodes_tree.rnp
    load_nodes_tree = dist_grid.load_nodes_tree.tree

    neighbors = load_nodes_tree[node.name]
    # guarda os pares (profundidade,nó)
    node_depth = [col_depth_node
               for col_depth_node in dist_grid_rnp.transpose()
               if col_depth_node[1] == node.name]
    upstream_neighbors = list()
    # verifica quem é neighbor do nó desejado.
    for neighbor in neighbors:
        depth_neighbor = [n_depth
                        for n_depth in dist_grid_rnp.transpose()
                        if n_depth[1] == neighbor]
        if int(depth_neighbor[0][0]) < int(node_depth[0][0]):
            # armazena os neighbors a montante.
            upstream_neighbors.append(
                dist_grid.load_nodes[depth_neighbor[0][1]])

    # retorna o primeiro neighbor a montante
    return upstream_neighbors[0]


def _search_section(dist_grid, n1, n2):
    """Função que busca sections em um alimendador entre os nos
      n1 e n2"""

    for section in dist_grid.sections.values():
        nodes = list([section.n1, section.n2])
        if (n1 in nodes) and (n2 in nodes):
            return section
