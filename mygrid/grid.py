from terminaltables import AsciiTable
import numpy as np
from random import randint
from mygrid.rnp import Tree, Edge
from mygrid.util import Phasor, P, R, Base
from mygrid.util import p2r, r2p
import os

class Sector(Tree):

    def __init__(self, name, neighbors, load_nodes, priority=0):
        assert isinstance(name, str), 'O parametro name da classe' \
                                      'Sector deve ser do tipo string'
        assert isinstance(neighbors, list), 'O parametro neighbors da classe' \
                                           ' Sector deve ser do tipo list'
        assert isinstance(load_nodes, list), 'O parametro load_nodes da classe' \
                                               'Sector deve ser do tipo list'
        assert (priority >= 0 and priority <= 10), 'O valo de priority'\
                                                       'deve estar entre 0-10'

        #assert isinstance(priority, int), 'O parâmetro Prioridade da classe' \
        #                                    'Sector deve ser do tipo int'
        self.name = name
        self.priority = priority
        self.neighbors = neighbors

        self.associated_rnp = {i: None for i in self.neighbors}

        self.load_nodes = dict()
        for node in load_nodes:
            node.sector = self.name
            self.load_nodes[node.name] = node

        self.link_node = None

        tree_sector = self._generates_tree_sector()
        super(Sector, self).__init__(tree_sector, str)

    def _generates_tree_sector(self):
        tree_sector = dict()
        # for percorre os nós de carga do sector
        for i, j in self.load_nodes.items():
            
            neighbors = list()
            # for percorre os neighbors do nó de carga
            for k in j.neighbors:
                # condição só considera vizinho o nó de carga que está
                # node mesmo sector que o nó de carga analisado
                if k in self.load_nodes.keys():
                    neighbors.append(k)
            tree_sector[i] = neighbors

        return tree_sector

    def calc_power(self):

        power = R(0.0, 0.0)
        for node in self.load_nodes.values():
            power = power + node.power

        return power

    def __str__(self):
        return 'Sector: ' + self.name


class LoadNode(object):
    def __init__(self,
                 name,
                 neighbors=None,
                 power=0.0+0.0j,
                 voltage=0.0+2j,
                 generation=None,
                 switchs=None):
        assert isinstance(name, str), 'O parâmetro name da classe LoadNode' \
                                      ' deve ser do tipo string'

        self.name = name
        self.neighbors = neighbors

        self._vp = np.zeros((3, 1), dtype=complex)
        self._pp = np.zeros((3, 1), dtype=complex)
        self.i = np.zeros((3, 1), dtype=complex)
        self._ip = np.zeros((3, 1), dtype=complex)

        self.config_load(power=power)
        self.config_voltage(voltage=voltage)

        if switchs is not None:
            assert isinstance(switchs, list), 'O parâmetro switchs da classe LoadNode' \
                                             ' deve ser do tipo list'
            self.switchs = switchs
        else:
            self.switchs = list()

        self.sector = None

    def config_load(self,
                    ppa=0.0+0.0j,
                    ppb=0.0+0.0j,
                    ppc=0.0+0.0j,
                    power=None,
                    zipmodel=[1.0, 0.0, 0.0]):
        if power is not None:
            self.ppa = self.ppb = self.ppc = 1.0/3.0 * power
        else:
            self.ppa = ppa
            self.ppb = ppb
            self.ppc = ppc

        self.zipmodel = np.array(zipmodel)

    def config_voltage(self,
                       vpa=0.0+0.0j,
                       vpb=0.0+0.0j,
                       vpc=0.0+0.0j,
                       voltage=None):
        if voltage is not None:
            v = abs(voltage) / np.sqrt(3)
            self.vpa = p2r(v, 0.0)
            self.vpb = p2r(v, -120.0)
            self.vpc = p2r(v, 120.0)
        else:
            self.vpa = vpa
            self.vpb = vpb
            self.vpc = vpc

        self._calc_currents()

    def _calc_currents(self):
        if self.pp.all() == 0.0+0.0j:
            self.i = np.zeros((3, 1), dtype=complex)
        else:
            self.ipq = self.zipmodel[0] * np.conjugate(self.pp / self.vp)
            self.z = np.abs(self.vp)**2 / np.conjugate(self.pp)
            self.iz = self.zipmodel[1] * (self.vp / self.z)
            self.ii = self.zipmodel[2] * self.vp / self.z
            self.i =  self.ipq + self.iz + self.ii
            self.i.shape = (3, 1)

    @property
    def VI(self):
        return self._VI

    @VI.setter
    def VI(self, valor):
        self._VI = valor
        self._vp = valor[:3, 0]
        self._vp.shape = (3, 1)
        aux = valor[3:, 0]
        aux.shape = (3, 1)
        self._ip += aux
        self._ip.shape = (3, 1)

    @property
    def ip(self):
        return self._ip
    
    @ip.setter
    def ip(self, valor):
        self._ip = valor
        self._ip.shape = (3, 1)
        self._VI = np.concatenate((self._vp, self._ip))

    @property
    def vp(self):
        return self._vp

    @vp.setter
    def vp(self, valor):
        self._vp = valor
        self._vp.shape = (3, 1)

        self._vpa = valor[0]
        self._vpb = valor[1]
        self._vpc = valor[2]

        self._VI = np.concatenate((self._vp, self._ip))

        self.config_voltage(vpa=self._vp[0, 0],
                            vpb=self._vp[1, 0],
                            vpc=self._vp[2, 0])

    @property
    def vpa(self):
        return self._vpa

    @vpa.setter
    def vpa(self, valor):
        self._vpa = valor
        self._vp[0] = valor

    @property
    def vpb(self):
        return self._vpb

    @vpb.setter
    def vpb(self, valor):
        self._vpb = valor
        self._vp[1] = valor

    @property
    def vpc(self):
        return self._vpc

    @vpc.setter
    def vpc(self, valor):
        self._vpc = valor
        self._vp[2] = valor

    @property
    def pp(self):
        return self._pp

    @pp.setter
    def pp(self, valor):
        self._pp = valor
        self._ppa = valor[0]
        self._ppb = valor[1]
        self._ppc = valor[2]

    @property
    def ppa(self):
        return self._ppa

    @ppa.setter
    def ppa(self, valor):
        self._ppa = valor
        self._pp[0] = valor

    @property
    def ppb(self):
        return self._ppb

    @ppb.setter
    def ppb(self, valor):
        self._ppb = valor
        self._pp[1] = valor

    @property
    def ppc(self):
        return self._ppc

    @ppc.setter
    def ppc(self, valor):
        self._ppc = valor
        self._pp[2] = valor

    def __str__(self):
        return 'Load Node: ' + self.name


class Substation(object):

    def __init__(self, name, feeders, transformers):
        assert isinstance(name, str), 'O parametro name da classe Substation ' \
                                      'deve ser do tipo str'
        assert isinstance(feeders, list), 'O parametro feeders da classe ' \
                                                'deve ser do tipo list'

        assert isinstance(transformers, list), 'O parametro feeders da classe ' \
                                               'deve ser do tipo list'
        self.name = name

        self.feeders = dict()
        for feeder in feeders:
            self.feeders[feeder.name] = feeder

        self.transformers = dict()
        for transformer in transformers:
            self.transformers[transformer.name] = transformer


class Section(Edge):
    def __init__(self,
                 name,
                 n1,
                 n2,
                 conductor=None,
                 line_model=None,
                 length=None):
        assert isinstance(name, str), 'O parametro name da classe Section ' \
                                      'deve ser do tipo str'
        assert isinstance(n1, LoadNode) or isinstance(n1, Switch), 'O parametro n1 da classe Section ' \
                                                                   'deve ser do tipo No de carga ' \
                                                                   'ou do tipo Switch'
        assert isinstance(n2, LoadNode) or isinstance(n2, Switch), 'O parâmetro n2 da classe Section ' \
                                                                   'deve ser do tipo No de carga ' \
                                                                   'ou do tipo Switch'

        super(Section, self).__init__(name)
        self.n1 = n1
        self.n2 = n2
        self.upstream_node = None
        self.downstream_node = None
        self.conductor = conductor
        self.length = length
        self.line_model = line_model
        self._set_line_model(line_model)

    def _set_line_model(self, line_model):
        self.Z = line_model.z * self.length
        self.Y = line_model.y * 1e-6 * self.length

        A = np.array([[1.0, 1.0, 1.0],
                      [1.0, p2r(1.0, 240.0), p2r(1.0, 120.0)],
                      [1.0, p2r(1.0, 120.0), p2r(1.0, 240.0)]])
        self.Z012 = np.dot(np.linalg.inv(A), np.dot(self.Z, A))

        self.a = np.identity(3) + 0.5 * self.Z * self.Y
        self.b = self.Z
        self.c = self.Y + 0.25 * self.Y * self.Z * self.Y
        self.d = np.identity(3) + 0.5 * self.Z * self.Y

        ab = np.concatenate((self.a, self.b), axis=1)
        cd = np.concatenate((self.c, self.d), axis=1)
        self.abcd = np.concatenate((ab, cd), axis=0)

    def calc_impedance(self):
        return (self.length * self.conductor.rp,
                self.length * self.conductor.xp)

    def __add__(self, other):
        if not isinstance(other, Section):
            raise TypeError('The object needs to be Secion to add!')
        else:
            s = Section(name=self.name + other.name,
                        n1=self.n1,
                        n2=self.n2,
                        line_model=self.line_model,
                        length=self.length + other.length)
            return s

    def __repr__(self):
        return 'Section: %s' % self.name

class LineModel(object):
    
    def __init__(self,
                 loc_a=0.0+0.0j,
                 loc_b=0.0+0.0j,
                 loc_c=0.0+0.0j,
                 loc_n=0.0+0.0j,
                 neutral=False,
                 conductor=None,
                 neutral_conductor=None,
                 units='Imperial'):
        
        self.loc_a = loc_a
        self.loc_b = loc_b
        self.loc_c = loc_c

        if neutral:
            self.loc = [loc_a, loc_b, loc_c, loc_n]
        else:
            self.loc = [loc_a, loc_b, loc_c]
        
        self.conductor = conductor
        self.neutral_conductor = neutral_conductor

        # --------------------------------------
        # Series Impedance Z matrix calculation
        # --------------------------------------

        # primitive matriz calculation
        self.z = np.array(self._calc_primitive_z_matrix(self.loc))

        # kron reduction, if there is neutral
        if np.shape(self.z) == (4, 4):
            self.z = self._calc_phase_impedance_matrix(self.z)

        # convert the Z matrix units to ohms/kilometers if units in SI
        if units == 'SI':
            self.z = 1.0 / 1.60934 * self.z

        # calculation of sequence series impedance Z012 matrix
        A = np.array([[1.0, 1.0, 1.0],
                      [1.0, p2r(1.0, 240.0), p2r(1.0, 120.0)],
                      [1.0, p2r(1.0, 120.0), p2r(1.0, 240.0)]])
        self.z012 = np.dot(np.linalg.inv(A), np.dot(self.z, A))

        # --------------------------------------
        # Shunt Admittance Y matrix calculation
        # --------------------------------------

        # S distance matrix calculation
        self.p = np.array(self._calc_potencial_primitive_matrix(self.loc))
        
        # kron reduction, if there is neutral
        if np.shape(self.p) == (4, 4):
            self.p = self._calc_potential_coefficient_matrix(self.p)

        # shunt capacitance matrix calculation
        self.c = np.linalg.inv(self.p)
        
        # shunt admittance matrix calculation
        self.y = 1j * 2.0 * np.pi * 60.0 * self.c

        # generalized line matrices calculation
        self.a = np.identity(3) + 0.5 * self.z * self.y * 1e-6
        self.b = self.z
        self.c = self.y * 1e-6 + 0.25 * self.y * self.z * self.y * 1e-12
        self.d = np.identity(3) + 0.5 * self.z * self.y * 1e-6

        ab = np.concatenate((self.a, self.b), axis=1)
        cd = np.concatenate((self.c, self.d), axis=1)
        self.abcd = np.concatenate((ab, cd), axis=0)

    def _calc_primitive_z_matrix(self, loc):
        # carson equations reference:
        # William Kersting: Distribution System Modeling and Analysis
        # 1th edition, pag. 85
        Z = list()
        r = self.conductor.conductor_data['resistence']['value']
        gmr = self.conductor.conductor_data['gmr']['value']
        rn = self.neutral_conductor.conductor_data['resistence']['value']
        gmrn = self.neutral_conductor.conductor_data['gmr']['value'] 
        for i in range(len(loc)):
            z = list()
            for j in range(len(loc)):
                if i == j:
                    if i == 3:
                        zij = rn + 0.09530  + 1j * 0.12134 * (np.log(1.0/gmrn) + 7.93402)
                    else:
                        zij = r + 0.09530 + 1j *  0.12134 * (np.log(1.0/gmr) + 7.93402)
                else:
                    l = loc[i] - loc[j]
                    zij = 0.09530 + 1j * 0.12134 * (np.log(1.0/abs(l)) + 7.93402)
                z.append(zij)
            Z.append(z)

        return Z

    def _calc_potencial_primitive_matrix(self, loc):
        P = list()
        r = self.conductor.conductor_data['diameter']['value'] / 2.0
        rn = self.neutral_conductor.conductor_data['diameter']['value'] / 2.0
        
        # inch to feet conversion
        r = r * 0.0833
        rn = rn * 0.0833
        for i in range(len(loc)):
            p = list()
            for j in range(len(loc)):
                s = abs(loc[i] - loc[j].conjugate())
                d = abs(loc[i] - loc[j])
                if i == j:
                    # conductor neutral case
                    if i == 3:
                        pij = 11.17689 * np.log(s/rn)
                    # no conductor neutral case
                    else:
                        pij = 11.17689 * np.log(s/r)
                else:
                    pij = 11.17689 * np.log(s/d)
                p.append(pij)
            P.append(p)
        return P

    def _calc_phase_impedance_matrix(self, Z):
        # Kron Reduction
        i, j = np.shape(Z)

        zij = Z[:3, :3]
        zij.shape = (3, 3)
        zin = Z[:i - 1, 3:j]
        zin.shape = (3, 1)
        znn = Z[3:, 3:]
        znn.shape = (1, 1)
        znj = Z[3:i, :j - 1]
        znj.shape = (1, 3)
        Z = zij - np.dot(np.dot(zin, np.linalg.inv(znn)), znj)
        return Z

    def _calc_potential_coefficient_matrix(self, P):
        # Kron Reduction
        i, j = np.shape(P)

        pij = P[:3, :3]
        pij.shape = (3, 3)
        pin = P[:i - 1, 3:j]
        pin.shape = (3, 1)
        pnn = P[3:, 3:]
        pnn.shape = (1, 1)
        pnj = P[3:i, :j - 1]
        pnj.shape = (1, 3)
        P = pij - np.dot(np.dot(pin, np.linalg.inv(pnn)), pnj)
        return P


class Feeder(Tree):
    def __init__(self, name, sectors, sections, switchs):
        assert isinstance(name, str), 'O parametro name da classe Feeder' \
                                      'deve ser do tipo string'
        assert isinstance(sectors, list), 'O parametro sectors da classe' \
                                          'Feeder deve ser do tipo list'
        assert isinstance(switchs, list), 'O parametro switchs da classe' \
                                         'Feeder deve ser do tipo list'
        self.name = name

        self.sectors = dict()
        for sector in sectors:
            self.sectors[sector.name] = sector

        self.switchs = dict()
        for switch in switchs:
            self.switchs[switch.name] = switch

        self.load_nodes = dict()
        for sector in sectors:
            for node in sector.load_nodes.values():
                self.load_nodes[node.name] = node

        self.sections = dict()
        for section in sections:
            self.sections[section.name] = section

        for sector in self.sectors.values():
            neighbors_sectors = list()
            for switch in self.switchs.values():
                if switch.n1 is sector:
                    neighbors_sectors.append(switch.n2)
                elif switch.n2 is sector:
                    neighbors_sectors.append(switch.n1)

            for neighbor_sector in neighbors_sectors:
                link_nodes = list()
                for i in sector.load_nodes.values():
                    for j in neighbor_sector.load_nodes.values():
                        if i.name in j.neighbors:
                            link_nodes.append((j, i))

                for node in link_nodes:
                    sector.order(node[1].name)
                    sector.associated_rnp[neighbor_sector.name] = (node[0],
                                                                sector.rnp)

        _grid_tree = self._generate_grid_tree()

        super(Feeder, self).__init__(_grid_tree, str)

    def order(self, root):
        super(Feeder, self).order(root)

        for sector in self.sectors.values():
            path = self.node_to_root_path(sector.name)
            if sector.name != root:
                downstream_sector = path[1, 1]
                sector.rnp = sector.associated_rnp[downstream_sector][1]

    def _generate_grid_tree(self):

        grid_tree = {i: list() for i in self.sectors.keys()}

        for switch in self.switchs.values():
            if switch.n1.name in self.sectors.keys() and switch.state == 1:
                grid_tree[switch.n1.name].append(switch.n2.name)
            if switch.n2.name in self.sectors.keys() and switch.state == 1:
                grid_tree[switch.n2.name].append(switch.n1.name)

        return grid_tree

    def generate_load_nodes_tree(self):

        # define os nós de carga do sector root da subestação como os primeiros
        # nós de carga a povoarem a tree nós de carga e a rnp nós de carga
        root_sector = self.sectors[self.rnp[1][0]]
        self.load_nodes_tree = Tree(tree=root_sector._generates_tree_sector(),
                                          dtype=str)
        self.load_nodes_tree.order(root=root_sector.rnp[1][0])

        # define as listas visited e stack, necessárias ao
        # processo recursivo de visita
        # dos sectors da subestação
        visited = []
        stack = []

        # inicia o processo iterativo de visita dos sectors
        # em busca de seus respectivos nós de carga
        self._generate_load_nodes_tree(root_sector, visited, stack)

    def _generate_load_nodes_tree(self, sector, visited, stack):

        # atualiza as listas de recursão
        visited.append(sector.name)
        stack.append(sector.name)

        # for percorre os sectors neighbors ao sector atual
        # que ainda não tenham sido visited
        neighbors = sector.neighbors
        for i in neighbors:

            # esta condição testa se existe uma ligação
            # entre os sectors de uma mesma subestação, mas
            # que possuem uma switch normalmente aberta entre eles.
            # caso isto seja constatado o laço for é interrompido.
            if i not in visited and i in self.sectors.keys():
                for c in self.switchs.values():
                    if c.n1.name == sector.name and c.n2.name == i:
                        if c.state == 1:
                            break
                        else:
                            pass
                    elif c.n2.name == sector.name and c.n1.name == i:
                        if c.state == 1:
                            break
                        else:
                            pass
                else:
                    continue
                next_ = i
                neighbor_sector = self.sectors[i]
                insertion_node, insertion_rnp = neighbor_sector.associated_rnp[sector.name]
                insertion_tree = neighbor_sector._generates_tree_sector()

                neighbor_sector.link_node = insertion_node

                neighbor_sector.rnp = insertion_rnp

                self.load_nodes_tree.insert_branch(insertion_node.name,
                                                      (insertion_rnp,
                                                       insertion_tree),
                                                      root_node=insertion_rnp[1, 0]
                                                      )
                break
            else:
                continue
        else:
            stack.pop()
            if stack:
                previous = stack.pop()
                return self._generate_load_nodes_tree(self.sectors[previous],
                                                       visited, stack)
            else:
                return
        return self._generate_load_nodes_tree(self.sectors[next_],
                                               visited,
                                               stack)

    def update_grid_tree(self):
        _grid_tree = self._generate_grid_tree()
        self.tree = _grid_tree

    def generate_grid_sections(self):

        self.sections = dict()

        j = 0
        for i in range(1, np.size(self.load_nodes_tree.rnp, axis=1)):
            depth_1 = int(self.load_nodes_tree.rnp[0, i])
            depth_2 = int(self.load_nodes_tree.rnp[0, j])

            while abs(depth_1 - depth_2) is not 1:
                if abs(depth_1 - depth_2) == 0:
                    j -= 1
                elif abs(depth_1 - depth_2) == 2:
                    j = i - 1
                depth_2 = int(self.load_nodes_tree.rnp[0, j])
            else:
                n_1 = str(self.load_nodes_tree.rnp[1, j])
                n_2 = str(self.load_nodes_tree.rnp[1, i])
                sector_1 = None
                sector_2 = None

                # verifica quais os nós de carga existentes nas extremidades do section
                # e se existe uma switch node section

                for sector in self.sectors.values():
                    if n_1 in sector.load_nodes.keys():
                        sector_1 = sector
                    if n_2 in sector.load_nodes.keys():
                        sector_2 = sector

                    if sector_1 is not None and sector_2 is not None:
                        break
                else:
                    if sector_1 is None:
                        n = n_1
                    else:
                        n = n_2
                    for sector in self.sectors.values():
                        if n in sector.load_nodes.keys() and np.size(sector.rnp, axis=1) == 1:
                            if sector_1 is None:
                                sector_1 = sector
                            else:
                                sector_2 = sector
                            break

                if sector_1 != sector_2:
                    for switch in self.switchs.values():
                        if switch.n1 in (sector_1, sector_2) and switch.n2 in (sector_1, sector_2):
                            self.sections[n_1 + n_2] = Section(name=n_1 + n_2,
                                                             n1=self.load_nodes[n_1],
                                                             n2=self.load_nodes[n_2],
                                                             switch=switch)
                else:
                    self.sections[n_1 + n_2] = Section(name=n_1 + n_2,
                                                     n1=self.load_nodes[n_1],
                                                     n2=self.load_nodes[n_2])

    def calc_power(self):
        power = R(0.0, 0.0)
        for node in self.load_nodes.values():
            power = power + node.power

        return power

    def prune(self, node, change_rnp=True):
        prune = super(Feeder, self).prune(node, change_rnp)
        sectors_rnp = prune[0]
        sectors_tree = prune[1]

        if change_rnp:
            # for povoa dicionario com sectors podados
            sectors = dict()
            for i in sectors_rnp[1, :]:
                sector = self.sectors.pop(i)
                sectors[sector.name] = sector

            # for povoa dicionario com nos de carga podados
            load_nodes = dict()
            for sector in sectors.values():
                for j in sector.load_nodes.values():
                    if j.name in self.load_nodes.keys():
                        load_node = self.load_nodes.pop(j.name)
                        load_nodes[load_node.name] = load_node

            # for atualiza a lista de nós de carga da subestação
            # excluindo os nós de carga podados
            for sector in self.sectors.values():
                for load_node in sector.load_nodes.values():
                    self.load_nodes[load_node.name] = load_node
                    if load_node.name in load_nodes.keys():
                        load_nodes.pop(load_node.name)

            # prune o ramo na tree da subetação
            prune = self.load_nodes_tree.prune(sectors[node].rnp[1, 0], change_rnp=change_rnp)
            load_nodes_rnp = prune[0]
            load_nodes_tree = prune[1]

            # for povoa dicionario de switchs que estao nos sections podados
            # e retira do dicionario de switchs da tree que esta sofrendo a prune
            # as switchs que não fazem fronteira com os sections remanescentes
            switchs = dict()
            for switch in self.switchs.values():
                if switch.n1.name in sectors.keys():
                    if not switch.n2.name in self.sectors.keys():
                        switchs[switch.name] = self.switchs.pop(switch.name)
                    else:
                        switch.state = 0
                        switchs[switch.name] = switch
                elif switch.n2.name in sectors.keys():
                    if not switch.n1.name in self.sectors.keys():
                        switchs[switch.name] = self.switchs.pop(switch.name)
                    else:
                        switch.state = 0
                        switchs[switch.name] = switch

            # for prune os sections dos sectors podados e povoa o dicionario sections
            # para que possa ser repassado juntamente com os outros dados da prune
            sections = dict()
            for node in load_nodes_rnp[1, :]:
                for section in self.sections.values():
                    if section.n1.name == node or section.n2.name == node:
                        sections[section.name] = self.sections.pop(section.name)

            return (sectors, sectors_tree, sectors_rnp,
                    load_nodes, load_nodes_tree, load_nodes_rnp,
                    switchs, sections)
        else:
            return sectors_rnp

    def insert_branch(self, node, prune, root_node=None):

        (sectors, sectors_tree, sectors_rnp,
         load_nodes, load_nodes_tree, load_nodes_rnp,
         switchs, sections) = prune

        # atualiza sectors do feeder
        self.sectors.update(sectors)

        # atualiza os nos de carga do feeder
        self.load_nodes.update(load_nodes)

        # atualiza as switchs do feeder
        self.switchs.update(switchs)

        # atualiza os sections do feeder
        self.sections.update(sections)

        if root_node is None:
            insert_to_sector = sectors[sectors_rnp[1, 0]]
        else:
            insert_to_sector = sectors[root_node]

        insert_in_sector = self.sectors[node]

        # for identifica se existe alguma switch que permita a inserção do ramo na tree
        # da subestação que ira receber a inserção.
        link_switchs = dict()
        # for percorre os nos de carga do sector de insersão
        for i in self.sectors[insert_in_sector.name].load_nodes.values():
            # for percorre as switchs associadas ao node de carga
            for j in i.switchs:
                # for percorre os nos de carga do sector root do ramo a ser inserido
                for w in sectors[insert_to_sector.name].load_nodes.values():
                    # se a switch pertence aos nos de carga i e w então é uma switch de ligação
                    if j in w.switchs:
                        link_switchs[j] = (i, w)

        if not link_switchs:
            print('A insersao não foi possível pois nenhuma switch de fronteira foi encontrada!')
            return

        i = randint(0, len(link_switchs) - 1)
        n1, n2 = link_switchs[link_switchs.keys()[i]]

        self.switchs[link_switchs.keys()[i]].state = 1

        if insert_to_sector.name == sectors[sectors_rnp[1, 0]].name:
            super(Feeder, self).insert_branch(node, (sectors_rnp, sectors_tree))
        else:
            super(Feeder, self).insert_branch(node, (sectors_rnp, sectors_tree), root_node)

        # atualiza a tree de sectors do feeder
        self.update_grid_tree()

        # atualiza a tree de nos de carga do feeder
        self.generate_load_nodes_tree()


class Switch(Edge):
    def __init__(self, name, state=1):
        assert state == 1 or state == 0, 'O parametro state deve ser um inteiro de valor 1 ou 0'
        super(Switch, self).__init__(name=name)
        self.state = state

    def __str__(self):
        if self.n1 is not None and self.n2 is not None:
            return 'Switch: %s - n1: %s, n2: %s' % (self.name, self.n1.name, self.n2.name)
        else:
            return 'Switch: %s' % self.name


class Transformer(object):
    def __init__(self, name, primary_voltage, secondary_voltage, power, impedance):
        assert isinstance(name, str), 'O parâmetro name deve ser do tipo str'
        assert isinstance(secondary_voltage, Phasor), 'O parâmetro secondary_voltage deve ser do tipo Fasor'
        assert isinstance(primary_voltage, Phasor), 'O parâmetro primary_voltage deve ser do tipo Fasor'
        assert isinstance(power, Phasor), 'O parâmetro power deve ser do tipo Fasor'
        assert isinstance(impedance, Phasor), 'O parâmetro impedance deve ser do tipo Fasor'

        self.name = name
        self.primary_voltage = primary_voltage
        self.secondary_voltage = secondary_voltage
        self.power = power
        self.impedance = impedance


class Conductor(object):
    def __init__(self,
                 name=None,
                 id=None,
                 rp=None,
                 xp=None,
                 rz=None,
                 xz=None,
                 ampacity=None):
        if name is not None: 
            self.name = name
            self.rp = float(rp)
            self.xp = float(xp)
            self.rz = float(rz)
            self.xz = float(xz)
            self.ampacity = float(ampacity)
        elif id is not None:
            import json
            basedir = os.path.abspath(os.path.dirname(__file__))
            fp = open(os.path.join(basedir, 'data/conductors.json'))
            conductors_data = json.load(fp)
            self.conductor_data = conductors_data[id]

if __name__ == '__main__':
    pass
