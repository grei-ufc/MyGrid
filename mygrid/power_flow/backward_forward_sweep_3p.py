from mygrid.util import Phasor, R, P
from mygrid.util import r2p, p2r
from mygrid.grid import Section
import numpy as np


def calc_power_flow(dist_grid, Vnom):

    # -------------------------
    # variables declarations
    # -------------------------
    max_iterations = 100
    converg_crt = 0.001
    converg = 1e6
    iter = 0
    Vnom = Vnom / np.sqrt(3)

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
        _dist_grid_sweep(dist_grid, Vnom)

        # -------------------------
        # convergence verification
        # -------------------------
        for node in dist_grid.load_nodes.values():
            nodes_converg[node.name] = np.mean(abs(voltage_nodes[node.name] - node.vp))
        converg = max(nodes_converg.values())
        print('Max. diff between load nodes voltage values: {conv}'.format(conv=converg))

        # -------------------------
        # verificação de tensões 
        # das barras PV (se houverem).
        # -------------------------
        DG_unconv_ = _nodes_out_limit(dist_grid, Vnom)

        if DG_unconv_ != []:
            _define_power_insertion(DG_unconv_, dist_grid, Vnom)

            for node in dist_grid.load_nodes.values():
                node.config_voltage(voltage=node.voltage)
            
            calc_power_flow(dist_grid, Vnom * np.sqrt(3))


def _dist_grid_sweep(dist_grid, Vnom):
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
            node.vp = np.dot(section.A, upstream_node.vp) - \
                      np.dot(section.B, node.ip)
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


def _nodes_out_limit(dist_grid, Vnom):
    DG_unconv_ = list()
    for node in dist_grid.load_nodes.values():

        vaa = np.abs(node.vp[0]) / Vnom
        vbb = np.abs(node.vp[1]) / Vnom
        vcc = np.abs(node.vp[2]) / Vnom

        vphase_max = max([vaa,vbb,vcc])
        vphase_min = min([vaa,vbb,vcc])

        if (node.generation != None and node.generation.type == 'PV'):
            if (node.generation.no_limit_PV or (vphase_max) > node.generation.Vmax):
            
                node.generation.no_limit_PV = True
                
                if (vphase_min < node.generation.Vmin) and \
                    (vphase_max > node.generation.Vmax) or \
                    (node.generation.PV_Provides and node.generation.PV_Consumes):

                    if (vphase_min < node.generation.Vmin) and \
                        (vphase_max > node.generation.Vmax):

                        print("It is not possible to use a three-phase PV type generation" \
                                 +" to correct voltage levels by phase.")
                    else:
                        # node.generation.Pa-=node.generation.Qa
                        # node.generation.Pb-=node.generation.Qb
                        # node.generation.Pc-=node.generation.Qc
                        pass
                    
                elif ((vphase_min) < node.generation.Vmin or \
                    ((node.generation.Vspecified - (vphase_min)) \
                        > node.generation.DV_presc and\
                        (node.generation.PV_Provides))):

                    node.generation.PV_Provides = True
                    DG_unconv_.append(node)
                    

                elif ((vphase_max)>node.generation.Vmax or \
                    ((node.generation.Vspecified - (vphase_min)) \
                        < node.generation.DV_presc and\
                        (node.generation.PV_Consumes))):

                    node.generation.PV_Consumes = True
                    DG_unconv_.append(node)
            
    return DG_unconv_


def _define_power_insertion(DG_unconv_, dist_grid, Vnom):

    z_base = (Vnom)**2 / 100e6
    I_base = 100e6 / Vnom
    reactan_mat_ = np.ones((len(DG_unconv_), len(DG_unconv_))) * (0.0 + 1.0j)
    equal_section_ = {}

    for i in range(len(DG_unconv_)):

        section_list = list()
        reactan_mat_[i, i] = _sum_ind_react(dist_grid, DG_unconv_[i].name,section_list)
        equal_section_[i] = section_list

    for i in range(len(equal_section_)):
        for j in range(i+1,len(equal_section_)):
            reactan_mat_[i, j] = reactan_mat_[j, i] = _sum_com_react(i,j,equal_section_)
    
    
    inv_X = np.linalg.inv(reactan_mat_/z_base)
    delta_I = {}
    for j in range(3):
        delta_V = np.ones((len(DG_unconv_),1))
        for i in range(len(DG_unconv_)):
            if DG_unconv_[i].generation.PV_Provides:
                if  DG_unconv_[i].generation.gd_type_phase !=  "mono":
                    Vcurrent = np.min([np.abs(x) for x in DG_unconv_[i].vp])/Vnom
                else:
                    Vcurrent = (np.abs(x) for x in DG_unconv_[i].vp[j])/Vnom

            elif DG_unconv_[i].generation.PV_Consumes:
                if  DG_unconv_[i].generation.gd_type_phase !=  "mono":
                    Vcurrent = np.max([np.abs(x) for x in DG_unconv_[i].vp])/Vnom
                else:
                    Vcurrent = (np.abs(x) for x in DG_unconv_[i].vp[j])/Vnom

            delta_V[i,0] = DG_unconv_[i].generation.Vspecified - \
             (Vcurrent)
        delta_Q = inv_X.dot(delta_V) * 100e6
        delta_I[j] = inv_X.dot(delta_V) * I_base

    print(delta_I[0])
    print(delta_I[1])
    print(delta_I[2])
    
    for i in range(len(DG_unconv_)):
        vmin_dg = np.min([np.abs(x) for x in DG_unconv_[i].vp])
        DG_unconv_[i].generation.update_Q(delta_I[0][i][0] * vmin_dg,\
         delta_I[0][i][0] * vmin_dg, delta_I[0][i][0] * vmin_dg)


def _sum_com_react(i, j, equal_section_):
    reat_comm = 0
    for x in equal_section_[i]:
        if x  in equal_section_[j]:
            reat_comm +=  np.imag(x.line_model.z012[1,1])*x.length*1.0j

    # for x in equal_section_[j]:
    #     if x not in equal_section_[i]:
    #         reat_comm += np.imag(x.line_model.z012[1,1])*x.length*1.0j

    # for x in equal_section_[j]:
    #     if x in equal_section_[i]:
    #         reat_comm += np.imag(x.line_model.z012[1,1])*x.length*1.0j
    return reat_comm


def _sum_ind_react(dist_grid, n2, section_list):

    if dist_grid.root == n2:
        return 0

    for section in dist_grid.sections.values():

        if section.n1.name == n2:

            section_list.append(section)
            return _sum_ind_react(dist_grid,section.n2.name,section_list)+ \
            np.imag(section.line_model.z012[1,1])*section.length*1.0j

        elif section.n2.name == n2:

            section_list.append(section)
            return _sum_ind_react(dist_grid,section.n1.name,section_list)+ \
            np.imag(section.line_model.z012[1,1])*section.length*1.0j

