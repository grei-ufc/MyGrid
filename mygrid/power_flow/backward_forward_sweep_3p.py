from mygrid.util import Phasor, R, P
from mygrid.util import r2p, p2r
from mygrid.grid import Section
import numpy as np



def calc_power_flow(substation,Vnom):

        flag=0
        Vnom=Vnom/np.sqrt(3)
        # ---------------------------
        # loop in substation feeders
        # ---------------------------
        for feeder in substation.feeders.values():
            
            # -------------------------
            # variables declarations
            # -------------------------
            max_iterations = 50
            converg_crt = 0.001
            converg = 1e6
            iter = 0

            print('============================')
            print('Feeder {al} Sweep'.format(al=feeder.name))
            
            nodes_converg = dict()
            for node in feeder.load_nodes.values():
                nodes_converg[node.name] = 1e6

            # -------------------------------------
            # main loop for power flow calculation
            # -------------------------------------
            while iter <= max_iterations and converg > converg_crt:
                iter += 1
                print('<<<<-----------BFS------------>>>>')
                print('Iteration: {iter}'.format(iter=iter))

                voltage_nodes = dict()
                for node in feeder.load_nodes.values():
                    voltage_nodes[node.name] = node.vp

                # ----------------------------------
                # back-forward sweep implementation
                # ----------------------------------

                _feeder_sweep(feeder,Vnom)

                # -------------------------
                # convergence verification
                # -------------------------
                for node in feeder.load_nodes.values():
                    nodes_converg[node.name] = abs(np.mean(voltage_nodes[node.name]) -
                                                   np.mean(node.vp))

                converg = max(nodes_converg.values())
        
                print('Max. diff between load nodes voltage values: {conv}'.format(conv=converg))


        DG_unconv_=nodes_out_limit(substation,Vnom)

        if DG_unconv_ !=[]:
            define_power_insertion(DG_unconv_,feeder,Vnom)
            flag=1

        if flag != 0:
            substation.nodes_table_voltage()
            for feeder in substation.feeders.values():
                for node in feeder.load_nodes.values():
                    node.config_voltage(voltage=node.voltage)
            
            calc_power_flow(substation,Vnom*np.sqrt(3))
            return

        else:
            #substation.nodes_table_voltage()
            return








def _feeder_sweep(feeder,Vnom):
    
    """ Função que varre os feeders pelo
    método varredura direta/inversa"""

    feeder_rnp = feeder.load_nodes_tree.rnp
    load_nodes_tree = feeder.load_nodes_tree.tree

    # depth and max_depth recebem a profundidae maxima
    depth = max_depth = _get_feeder_max_depth(feeder)

    # ----------------------------------------------
    # Inicio da varredura inversa
    # ----------------------------------------------
    print('Backward Sweep phase <<<<----------')
    # seção do cálculo das potências partindo dos
    # nós com maiores profundidades até o nó raíz
    while depth >= 0:
        DG_unconv_=[]
        # guarda os nós com maiores profundidades.
        nodes = [feeder.load_nodes[node_depth[1]]
               for node_depth in feeder_rnp.transpose() if
               int(node_depth[0]) == depth]

        # decrementodo da profundidade.
        depth -= 1

        # for que percorre os nós com a profundidade
        # armazenada na variável depth
        for node in nodes:

            # zera as potências para que na próxima
            # iteração do fluxo de carga não ocorra acúmulo.
            node.ip = np.zeros((3, 1), dtype=complex)

            downstream_neighbors = _get_downstream_neighbors_nodes(node, feeder)

            # verifica se não há neighbor a jusante,
            # se não houverem o nó de carga analisado
            # é o último do ramo.
            if downstream_neighbors == []:
                node.ip = node.i
            else:
                # soma a power da carga associada ao nó atual
                node.ip = node.i
                # acrescenta à potência do nó atual
                # as potências dos nós a jusante
                for downstream_node in downstream_neighbors:
                    # chama a função busca_trecho para definir
                    # quais sections estão entre o nó atual e o nó a jusante
                    section = _search_section(feeder,
                                              node.name,
                                              downstream_node.name)
                    # se o section não for uma instancia da classe
                    # Section(quando há switch entre nós de cargas)
                    # a impedância é calculada
                    if not isinstance(section, Section):
                        section = section[0] + section[1]
                    # se o section atual for uma instancia da classe section
                    else:
                        pass

                    VI = np.dot(section.abcd,
                                downstream_node.VI)
                    aux = VI[3:, 0]
                    aux.shape = (3, 1)
                    node.ip += aux
                    downstream_node.iin=aux
                    print(node.name,np.abs(downstream_node.VI),np.abs(VI))
                    print(node.name + '<<<---' + downstream_node.name)

            
    print('Forward Sweep phase ---------->>>>')

    depth = 0
    # seção do cálculo de atualização das tensões
    while depth <= max_depth:
        # salva os nós de carga a montante
        nodes = [feeder.load_nodes[col_depth_node[1]]
                 for col_depth_node in feeder_rnp.transpose()
                 if int(col_depth_node[0]) == depth + 1]

        # percorre os nós para guardar a árvore do nó requerido
        for node in nodes:

            upstream_node = _get_upstream_neighbor_node(feeder, node)
            
            section = _search_section(feeder, node.name, upstream_node.name)

            # se existir switch, soma a resistência dos dois sections
            if not isinstance(section, Section):
                section = section[0] + section[1]
            # caso não exista, a resistência é a do próprio section
            else:
                pass

            V_2=upstream_node.VI[:3,0]
            V_2.shape = (3, 1)
            I_2=node.iin
            I_2.shape = (3, 1)
            VI_2=np.concatenate((V_2, I_2))
           
            print(np.abs(VI_2)) 
            VI = np.dot(np.linalg.inv(section.abcd),
                        VI_2)
            

            node.vp = VI[:3, 0]


            if depth == 0:
                upstream_node.vp = upstream_node.vp

            print(upstream_node.name + '--->>>' + node.name)
        depth += 1
    




def nodes_out_limit(substation,Vnom):
    DG_unconv_=[]
    for feeder in substation.feeders.values():
        for node in feeder.load_nodes.values():

            vaa=np.abs(node.vp[0])/Vnom
            vbb=np.abs(node.vp[1])/Vnom
            vcc=np.abs(node.vp[2])/Vnom

            vphase_max=max([vaa,vbb,vcc])
            vphase_min=min([vaa,vbb,vcc])

            if (node.generation!=None and node.generation.type=="PV")\
             and (node.generation.no_limit_PV \
                or (vphase_max)>node.generation.Vmax):
                
                node.generation.no_limit_PV=True
                
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
                    
                elif ((vphase_min)<node.generation.Vmin or \
                    ((node.generation.Vspecified - (vphase_min)) \
                        > node.generation.DV_presc and\
                        (node.generation.PV_Provides))):

                    node.generation.PV_Provides=True
                    DG_unconv_.append(node)
                    

                elif ((vphase_max)>node.generation.Vmax or \
                    ((node.generation.Vspecified - (vphase_min)) \
                        < node.generation.DV_presc and\
                        (node.generation.PV_Consumes))):

                    node.generation.PV_Consumes=True
                    DG_unconv_.append(node)
            
    return DG_unconv_

    


def _get_feeder_max_depth(feeder):
    
    feeder_nodes = feeder.load_nodes.values()
    feeder_rnp = feeder.load_nodes_tree.rnp
    
    max_depth = 0

    # for percorre a rnp dos nós de carga tomando valores
    # em pares (profundidade, nó).
    for node_depth in feeder_rnp.transpose():
        # obtem os nomes dos nos de carga.
        feeder_nodes_names = [node.name for node in feeder_nodes]

        # verifica se a profundidade do nó é maior do que a
        # profundidade máxima e se ele está na lista de nós do feeder.
        if (int(node_depth[0]) > max_depth) \
           and (node_depth[1] in feeder_nodes_names):
            max_depth = int(node_depth[0])

    return max_depth


def _get_downstream_neighbors_nodes(node, feeder):

    feeder_rnp = feeder.load_nodes_tree.rnp
    load_nodes_tree = feeder.load_nodes_tree.tree

    # guarda os pares (profundidade, nó)
    node_depth = [node_depth for node_depth in feeder_rnp.transpose()
                  if node_depth[1] == node.name]

    neighbors = load_nodes_tree[node.name]
    downstream_neighbors = list()

    # for que percorre a árvore de cada nó de carga vizinho
    for neighbor in neighbors:
        
        # Tem como melhorar

        # verifica quem é neighbor do nó desejado.
        depth_neighbor = [n_depth for n_depth in
                          feeder_rnp.transpose()
                          if n_depth[1] == neighbor]

        # verifica se a profundidade do neighbor é maior
        if int(depth_neighbor[0][0]) > int(node_depth[0][0]):
            # armazena os neighbors a jusante.
            downstream_neighbors.append(
                feeder.load_nodes[depth_neighbor[0][1]])

    return downstream_neighbors


def _get_upstream_neighbor_node(feeder, node):
    
    feeder_rnp = feeder.load_nodes_tree.rnp
    load_nodes_tree = feeder.load_nodes_tree.tree

    neighbors = load_nodes_tree[node.name]
    # guarda os pares (profundidade,nó)
    node_depth = [col_depth_node
               for col_depth_node in feeder_rnp.transpose()
               if col_depth_node[1] == node.name]
    upstream_neighbors = list()
    # verifica quem é neighbor do nó desejado.
    for neighbor in neighbors:
        depth_neighbor = [n_depth
                        for n_depth in feeder_rnp.transpose()
                        if n_depth[1] == neighbor]
        if int(depth_neighbor[0][0]) < int(node_depth[0][0]):
            # armazena os neighbors a montante.
            upstream_neighbors.append(
                feeder.load_nodes[depth_neighbor[0][1]])

    # retorna o primeiro neighbor a montante
    return upstream_neighbors[0]


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

def define_power_insertion(DG_unconv_,feeder,Vnom):

    z_base=(Vnom)**2/100e6
    I_base=100e6/Vnom
    reactan_mat_=np.ones((len(DG_unconv_),len(DG_unconv_)))*(0.0+1.0j)
    equal_section_={}

    for i in range(len(DG_unconv_)):

        section_list=list()
        reactan_mat_[i,i]=sum_ind_react(feeder, DG_unconv_[i].name,section_list)
        equal_section_[i]=section_list

    for i in range(len(equal_section_)):
        for j in range(i+1,len(equal_section_)):
            reactan_mat_[i,j]=reactan_mat_[j,i]=sum_com_react(i,j,equal_section_)
    
    
    inv_X=np.linalg.inv(reactan_mat_/z_base)
    delta_I={}
    for j in range(3):
        delta_V=np.ones((len(DG_unconv_),1))
        for i in range(len(DG_unconv_)):
            if DG_unconv_[i].generation.PV_Provides:
                if  DG_unconv_[i].generation.gd_type_phase != "mono":
                    Vcurrent=np.min([np.abs(x) for x in DG_unconv_[i].vp])/Vnom
                else:
                    Vcurrent=(np.abs(x) for x in DG_unconv_[i].vp[j])/Vnom

            elif DG_unconv_[i].generation.PV_Consumes:
                if  DG_unconv_[i].generation.gd_type_phase != "mono":
                    Vcurrent=np.max([np.abs(x) for x in DG_unconv_[i].vp])/Vnom
                else:
                    Vcurrent=(np.abs(x) for x in DG_unconv_[i].vp[j])/Vnom

            delta_V[i,0]=DG_unconv_[i].generation.Vspecified - \
             (Vcurrent)
        delta_Q=inv_X.dot(delta_V)*100e6
        delta_I[j]=inv_X.dot(delta_V)*I_base

    
    

    # print(delta_V)
    # print(inv_X)
    # print(delta_Q)
    print(delta_I[0])
    print(delta_I[1])
    print(delta_I[2])
    
    for i in range(len(DG_unconv_)):
        vmin_dg=np.min([np.abs(x) for x in DG_unconv_[i].vp])
        DG_unconv_[i].generation.update_Q(delta_I[0][i][0]*vmin_dg,\
         delta_I[0][i][0]*vmin_dg, delta_I[0][i][0]*vmin_dg)



 
def sum_com_react(i,j,equal_section_):
    reat_comm=0
    for x in equal_section_[i]:
        if x  in equal_section_[j]:
            reat_comm += np.imag(x.line_model.z012[1,1])*x.length*1.0j

    # for x in equal_section_[j]:
    #     if x not in equal_section_[i]:
    #         reat_comm += np.imag(x.line_model.z012[1,1])*x.length*1.0j

    # for x in equal_section_[j]:
    #     if x in equal_section_[i]:
    #         reat_comm += np.imag(x.line_model.z012[1,1])*x.length*1.0j
    return reat_comm

def sum_ind_react(feeder, n2,section_list):

    if feeder.root==n2:
        return 0

    for section in feeder.sections.values():

        if section.n1.name == n2:

            section_list.append(section)
            return sum_ind_react(feeder,section.n2.name,section_list)+ \
            np.imag(section.line_model.z012[1,1])*section.length*1.0j

        elif section.n2.name == n2:

            section_list.append(section)
            return sum_ind_react(feeder,section.n1.name,section_list)+ \
            np.imag(section.line_model.z012[1,1])*section.length*1.0j

def define_power_phase(a,b,c):
    power_phases=[]

    return power_phases