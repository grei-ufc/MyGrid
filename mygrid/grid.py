# -*- coding: utf-8 -*-

from terminaltables import AsciiTable
import numpy as np
from random import randint
from mygrid.rnp import Tree, Edge
from mygrid.util import Phasor, P, R, Base
from mygrid.util import p2r, r2p
import os
import pandas as pd
import math

np.seterr(divide = 'ignore')
np.seterr(invalid = 'ignore')

class GridElements(object):
    def __init__(self, name):
        self.load_nodes = dict()
        self.switchs = dict()
        self.sections = dict()

    def add_load_node(self, load_node):
        if isinstance(load_node, LoadNode):
            self.load_nodes[load_node.name] = load_node
        elif isinstance(load_node, list):
            for ln in load_node:
                self.load_nodes[ln.name] = ln

    def add_switch(self, switch):
        if isinstance(switch, Switch):
            self.switchs[switch.name] = switch
        elif isinstance(switch, list):
            for sw in switch:
                self.switchs[sw.name] = sw

    def add_section(self, section):
        if isinstance(section, Section):
            self.sections[section.name] = section
        elif isinstance(section, list):
            for sc in section:
                self.sections[sc.name] = sc

    def add_sector(self, sector):
        if isinstance(sector, Sector):
            self.sectors[sector.name] = sector
        elif isinstance(sector, list):
            for sc in sector:
                self.sectors[sc.name] = sc

    def add_grid_dist(self, grid_dist):
        if isinstance(grid_dist, DistGrid):
            self.grid_dist[grid_dist.name] = grid_dist
        elif isinstance(grid_dist, list):
            for gd in grid_dist:
                self.grid_dist[gd.name] = gd

    def create_grid(self):

        # ----------------------------------
        # determinacao de setores
        # ----------------------------------
        self.sectors = dict()
        visitados = list()
        i = 0
        for load_node in self.load_nodes.values():
            if load_node not in visitados:
                sector_load_nodes = list([load_node])
                neighbors = list()
                stack = list()
                visitados.append(load_node)
                stack.append(load_node)
                visitados, sector_load_nodes = self.search_sectors(load_node,
                                                                   self.load_nodes.values(),
                                                                   self.sections.values(),
                                                                   visitados,
                                                                   sector_load_nodes,
                                                                   stack)

                s = Sector(name='S' + str(i), load_nodes=sector_load_nodes)
                i += 1
                self.sectors[s.name] = s

        # ----------------------------------
        # determinacao dos vizinhos
        # dos nos de carga
        # ----------------------------------
        # for load_node in self.load_nodes.values():
        #     neighbors = list()
        for section in self.sections.values():
            section.n1.set_neighbors(section.n2)
            section.n2.set_neighbors(section.n1)

        # ----------------------------------
        # determinacao dos vizinhos
        # dos setores
        # ----------------------------------
        for sector in self.sectors.values():
            neighbors = list()
            for load_node in sector.load_nodes.values():
                for section in self.sections.values():
                    if section.n1 == load_node:
                        if section.switch is not None:
                            neighbors.append(section.n2.sector)
                    if section.n2 == load_node:
                        if section.switch is not None:
                            neighbors.append(section.n1.sector)
            sector.set_neighbors(neighbors)

        # ----------------------------------
        # determinacao dos setores
        # vizinhos das chaves
        # ----------------------------------
        for section in self.sections.values():
            if section.switch is not None:
                for sector in self.sectors.values():
                    if section.n1 in sector.load_nodes.values():
                        section.switch.set_sector(sector)
                    if section.n2 in sector.load_nodes.values():
                        section.switch.set_sector(sector)

        # ----------------------------------
        # busca dos setores de cada DistGrid
        # ----------------------------------
        visitados = list()
        dist_grid_sectors_list = list()
        for sector in self.sectors.values():
            if sector not in visitados:
                grid_dist_sectors = list([sector])
                neighbors = list()
                stack = list()
                visitados.append(sector)
                stack.append(sector)
                visitados, grid_dist_sectors = self.search_grid_dist_sectors(sector,
                                                                       self.sectors.values(),
                                                                       self.switchs.values(),
                                                                       visitados,
                                                                       grid_dist_sectors,
                                                                       stack)
                dist_grid_sectors_list.append(grid_dist_sectors)

        # ----------------------------------
        # busca das sections de cada alimentador
        # ----------------------------------
        visitados = list()
        dist_grid_sections_list = list()
        for load_node in self.load_nodes.values():
            if load_node not in visitados:
                grid_dist_sections = list()
                neighbors = list()
                stack = list()
                visitados.append(load_node)
                stack.append(load_node)
                visitados, grid_dist_sections = self.search_grid_dist_sections(load_node,
                                                                         self.load_nodes.values(),
                                                                         self.sections.values(),
                                                                         visitados,
                                                                         grid_dist_sections,
                                                                         stack)
                dist_grid_sections_list.append(grid_dist_sections)

        # ----------------------------------
        # busca dos nos raiz de cada alimentador
        # ----------------------------------
        root_sectors = list()
        for sector in self.sectors.values():
            for load_node in sector.load_nodes.values():
                if load_node.external_grid is not None:
                    root_sectors.append(sector)

        # ----------------------------------
        # instanciamento das DistGrids
        # ----------------------------------
        self.dist_grids = dict()
        i = 0
        aux = 0
        for root_sector in root_sectors:
            for dg_sectors in dist_grid_sectors_list:
                if root_sector in dg_sectors:
                    rs_load_node = list(root_sector.load_nodes.values())[0]
                    for section in self.sections.values():
                        if aux != i:
                            aux+=1
                            break
                        elif ((rs_load_node is section.n1) or (rs_load_node is section.n2)) and (section.switch.state is not 0):
                            for dg_sections in dist_grid_sections_list:
                                if section in dg_sections:
                                    dg = DistGrid(name='F' + str(i),
                                                  sectors=dg_sectors,
                                                  sections=dg_sections)
                                    i+=1
                                    dg.order(root=root_sector.name)
                                    dg.generate_load_nodes_tree()
                                    self.dist_grids[dg.name] = dg
                                    break

    def search_sectors(self, load_node, load_nodes, sections, visitados, sector_load_nodes, stack):
        for section in sections:
            if section.n1 == load_node:
                if section.switch == None and section.n2 not in visitados:
                    visitados.append(section.n2)
                    stack.append(section.n2)
                    sector_load_nodes.append(section.n2)
                    return self.search_sectors(section.n2, load_nodes, sections, visitados, sector_load_nodes, stack)
            if section.n2 == load_node:
                if section.switch == None and section.n1 not in visitados:
                    visitados.append(section.n1)
                    stack.append(section.n1)
                    sector_load_nodes.append(section.n1)
                    return self.search_sectors(section.n1, load_nodes, sections, visitados, sector_load_nodes, stack)
        else:
            stack.pop()
            if stack == []:
                return visitados, sector_load_nodes
            else:
                return self.search_sectors(stack[len(stack)-1], load_nodes, sections, visitados, sector_load_nodes, stack)


    def search_grid_dist_sectors(self, sector, sectors, switchs, visitados, grid_dist_sectors, stack):
        for switch in switchs:
            if switch.n1 == sector:
                if switch.state == 1 and switch.n2 not in visitados:
                    visitados.append(switch.n2)
                    stack.append(switch.n2)
                    grid_dist_sectors.append(switch.n2)
                    return self.search_grid_dist_sectors(switch.n2, sectors, switchs, visitados, grid_dist_sectors, stack)
            if switch.n2 == sector:
                if switch.state == 1 and switch.n1 not in visitados:
                    visitados.append(switch.n1)
                    stack.append(switch.n1)
                    grid_dist_sectors.append(switch.n1)
                    return self.search_grid_dist_sectors(switch.n1, sectors, switchs, visitados, grid_dist_sectors, stack)
        else:
            stack.pop()
            if stack == []:
                return visitados, grid_dist_sectors
            else:
                return self.search_grid_dist_sectors(stack[len(stack)-1], sectors, switchs, visitados, grid_dist_sectors, stack)

    def search_grid_dist_sections(self, load_node, load_nodes, sections, visitados, grid_dist_sections, stack):
        for section in sections:
            if section.n1 == load_node:
                if section.switch is not None:
                    if section.switch.state == 0:
                        grid_dist_sections.append(section)
                        continue
                if section.n2 not in visitados:
                    visitados.append(section.n2)
                    stack.append(section.n2)
                    grid_dist_sections.append(section)
                    return self.search_grid_dist_sections(section.n2, load_nodes, sections, visitados, grid_dist_sections, stack)
            if section.n2 == load_node:
                if section.switch is not None:
                    if section.switch.state == 0:
                        grid_dist_sections.append(section)
                        continue
                if section.n1 not in visitados:
                    visitados.append(section.n1)
                    stack.append(section.n1)
                    grid_dist_sectors.append(section)
                    return self.search_grid_dist_sections(section.n1, load_nodes, sections, visitados, grid_dist_sections, stack)
        else:
            stack.pop()
            if stack == []:
                return visitados, grid_dist_sections
            else:
                return self.search_grid_dist_sections(stack[len(stack)-1], load_nodes, sections, visitados, grid_dist_sections, stack)


    def nodes_table_voltage(self,type_volts="pu", Df= True):
        if type_volts=="pu":
            v="pu"
            va_name="Va (p.u)"
            vb_name="Vb (p.u)"
            vc_name="Vc (p.u)"

        elif type_volts=="module":
            v=1
            va_name="Va (V)"
            vb_name="Vb (V)"
            vc_name="Vc (V)"

        for i in self.dist_grids:
            load_nodes=self.dist_grids[i].load_nodes
            title="Grid_Name: "+ i
            node_data=[["node name",
                     va_name,
                     vb_name,
                     vc_name,
                     "Load_Pa (kVA)",
                     "Load_Pb (kVA)",
                     "Load_Pc (kVA)",
                     "DG_Pa (kW +KVar)",
                     "DG_Pb (kW +KVar)",
                     "DG_Pc (kW +KVar)"
                     ]]
            for name_node in load_nodes:

                node=self.load_nodes[name_node]
                pa=0.0+0.0j
                pb=0.0+0.0j
                pc=0.0+0.0j

                if node.generation is not None:
                    if type(node.generation) == type(list()):
                        for i in node.generation:
                            pa += i.Pa
                            pb += i.Pb
                            pc += i.Pc

                    else:

                        pa += node.generation.Pa
                        pb += node.generation.Pb
                        pc += node.generation.Pc


                node_data.append([node.name,\
                   str(np.round(np.abs(node.vpa)/(np.abs(node.voltage_nom)/np.sqrt(3) \
                    if v =="pu" else 1),4)) +\
                        "∠"+str(np.round(np.angle(node.vpa, deg=True),2))+"°",
                   str(np.round(np.abs(node.vpb)/(np.abs(node.voltage_nom)/np.sqrt(3) \
                    if v =="pu" else 1),4)) +\
                        "∠"+str(np.round(np.angle(node.vpb, deg=True),2))+"°",
                   str(np.round(np.abs(node.vpc)/(np.abs(node.voltage_nom)/np.sqrt(3) \
                    if v =="pu" else 1),4)) +\
                        "∠"+str(np.round(np.angle(node.vpc, deg=True),2))+"°",

                   str(round(np.abs(node.ppa)/1000,2))+u"∠"\
                   +str(round(np.angle(node.ppa, deg=True),2))+"°",
                   str(round(np.abs(node.ppb)/1000,2))+u"∠"\
                   +str(round(np.angle(node.ppb, deg=True),2))+"°",
                   str(round(np.abs(node.ppc)/1000,2))+u"∠"\
                   +str(round(np.angle(node.ppc, deg=True),2))+"°",

                   str(round(pa.real/1000,2)) + " + " + "j" + \
                   str(round(pa.imag/1000,2)),

                   str(round(pb.real/1000,2)) + " + " + "j" + \
                   str(round(pb.imag/1000,2)),

                   str(round(pc.real/1000,2)) + " + " + "j" + \
                   str(round(pc.imag/1000,2))])
            if Df:
                return pd.DataFrame(node_data)
            else:
                table=AsciiTable(node_data)
                table.title=title
                print(table.table)


class ExternalGrid(object):
    def __init__(self, name, vll, Z=None):
        self.vll = vll
        self.name=name

        if type(Z) == type(None):
            self.Z=np.zeros((3,3), dtype=complex)

        else:
            self.Z=Z


class Sector(Tree):

    def __init__(self, name, load_nodes, priority=0):
        assert isinstance(name, str), 'O parametro name da classe' \
                                      'Sector deve ser do tipo string'
        assert isinstance(load_nodes, list), 'O parametro load_nodes da classe' \
                                               'Sector deve ser do tipo list'
        assert (priority >= 0 and priority <= 10), 'O valo de priority'\
                                                       'deve estar entre 0-10'

        #assert isinstance(priority, int), 'O parâmetro Prioridade da classe' \
        #                                    'Sector deve ser do tipo int'
        self.name = name
        self.priority = priority

        self.load_nodes = dict()
        for node in load_nodes:
            node.sector = self
            self.load_nodes[node.name] = node

        self.link_node = None

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors
        self.associated_rnp = {i.name: None for i in self.neighbors}

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
                if k in self.load_nodes.values():
                    neighbors.append(k.name)
            tree_sector[i] = neighbors

        return tree_sector

    def calc_power(self):

        power = R(0.0, 0.0)
        for node in self.load_nodes.values():
            power = power + node.power

        return power

    def __repr__(self):
        return 'Sector: ' + self.name


class LoadNode(object):
    def __init__(self,
                 name,
                 power=None,
                 ppa=0.0+0.0j,
                 ppb=0.0+0.0j,
                 ppc=0.0+0.0j,
                 voltage=0.0+0.0j,
                 Vmin=0.98,
                 Vmax=1.05,
                 Vspecified=1.0,
                 DV_presc=0.002,
                 generation=None,
                 type_connection="wye",
                 shunt_capacitor=None,
                 external_grid=None,
                 zipmodel=[1.0, 0.0, 0.0]):
        assert isinstance(name, str), 'O parâmetro name da classe LoadNode' \
                                      ' deve ser do tipo string'

        self.name = name
        self.generation = generation
        self.type = "PQ"
        self.zipmodel = np.array(zipmodel)

        if type(self.generation) != type(None):

            if type(self.generation) == type(list()):
                for i in generation:
                    if i.type == "PV":
                        self.type = "PV"
                        break

            elif self.generation.type == "PV":
                self.type = "PV"


        self.type_connection=type_connection
        self.shunt_capacitor=shunt_capacitor
        self.neighbors=list()
        self.constant_currents_calc=False
        self.Vmin=Vmin
        self.Vmax=Vmax
        self.Vspecified=Vspecified
        self.DV_presc=DV_presc

        self.defective_phase=None

        self._vp = np.zeros((3, 1), dtype=complex)
        self._pp = np.zeros((3, 1), dtype=complex)
        self.i = np.zeros((3, 1), dtype=complex)
        self._ip = np.zeros((3, 1), dtype=complex)
        self.iin = np.zeros((3, 1), dtype=complex)
        self.ineu=self._ip.sum()
        self.D=np.array([[1,-1,0],[0,1,-1],[-1,0,1]])


        self.voltage=voltage
        self.voltage_nom=voltage
        self.ipq=np.zeros((3, 1), dtype=complex)
        self.iz=np.zeros((3, 1), dtype=complex)
        self.ii=np.zeros((3, 1), dtype=complex)
        self.Xf=np.zeros((7, 1), dtype=complex)

        if power is not None:
            self.config_load(power=power)
        else:
            self.config_load(ppa=ppa,ppb=ppb,ppc=ppc)

        self.config_voltage(voltage=self.voltage)

        if self.type_connection=="delta":
            self.vpm=self.vpl
            self.vp0l = self.vpl

        if self.type_connection=="wye":
            self.vpm=self.vp
            self.vp0 = self.vp

        self.z = np.divide(np.abs(self.vpm)**2, np.conjugate(self.pp))
        self.i_constant=np.abs(np.divide(self.pp, self.vpm))
        self._calc_currents()
        self.switchs = list()
        self.sector = None
        self.external_grid = external_grid



    def set_neighbors(self, neighbors):
        self.neighbors.append(neighbors)

    def set_ds_neighbors(self, ds):
        self.ds_neighbors=ds

    def set_us_neighbors(self, us):
        self.us_neighbors = us

    def set_section_ds(self, section_ds):
        self.section_ds=section_ds

    def section_us(self, section_us):
        set_self.section_us=section_us

    def config_load(self,
                    ppa=0.0+0.0j,
                    ppb=0.0+0.0j,
                    ppc=0.0+0.0j,
                    power=None):
        if power is not None:

            self.ppa = self.ppb = self.ppc = 1.0/3.0 * power

        else:
            self.ppa = ppa
            self.ppb = ppb
            self.ppc = ppc




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

        self.vpl=np.dot(self.D,self._vp)

    def _calc_currents(self):

        if self.type_connection=="delta":

            self.vpm=np.dot(self.D,self.vp)

        elif self.type_connection=="wye":
            self.vpm=self.vp



        if self.shunt_capacitor is not None:
            i_shunt_C=self.shunt_capacitor.calc_currents(self.vpa,self.vpb,self.vpc)
            i_shunt_C=np.where(np.isnan(i_shunt_C),np.zeros(np.shape(i_shunt_C), dtype=complex),i_shunt_C)

        else:
            i_shunt_C=0


        if type(self.generation) !=  type(None):

            if type(self.generation) == type(list()):
                i_gd=0+0j
                for i in self.generation:
                    if i.type_connection=="wye":
                        i_gd += np.conjugate(i.pp/self.vp)
                    elif i.type_connection=="delta":
                        i_g=np.conjugate(i.pp/self.vpl)
                        i_gd += np.dot(self.D.T,i_g)

            else:
                if self.generation.type_connection=="wye":
                    i_gd=np.conjugate(self.generation.pp/self.vp)
                elif self.generation.type_connection=="delta":
                    i_gd=np.conjugate(self.generation.pp/self.vpl)
                    i_gd=np.dot(self.D.T,i_gd)

        else:
            i_gd=0+0j

        if  self.zipmodel[0] !=0:

            self.ipq = np.multiply(self.zipmodel[0], np.conjugate(np.divide(self.pp, self.vpm)))
            self.ipq=np.where(np.isnan(self.ipq),np.zeros(np.shape(self.ipq), dtype=complex),self.ipq)

        if  self.zipmodel[1] !=0:

            self.iz = self.zipmodel[1] * np.divide(self.vpm, self.z)
            self.iz=np.where(np.isnan(self.iz),np.zeros(np.shape(self.iz), dtype=complex),self.iz)

        if  self.zipmodel[2] !=0:

            alpha=np.angle(self.vpm)-np.angle(self.pp)
            self.ii = self.zipmodel[2]*self.i_constant*(np.cos(alpha)+np.sin(alpha)*1j)
            self.ii=np.where(np.isnan(self.ii),np.zeros(np.shape(self.ii), dtype=complex),self.ii)




        self.i =  self.ipq  + self.iz + self.ii
        if self.type_connection=="delta":
            self.i=np.dot(self.D.T,self.i) + i_shunt_C+i_gd
        elif self.type_connection=="wye":
            self.i=self.i + i_shunt_C+i_gd


    @property
    def ip(self):
        return self._ip

    @ip.setter
    def ip(self, valor):
        self._ip = valor
        self._ip.shape = (3, 1)

    @property
    def vp(self):
        return self._vp

    @vp.setter
    def vp(self, valor):
        self._vp = valor
        self._vp.shape = (3, 1)

        self._vpa = valor[0,0]
        self._vpb = valor[1,0]
        self._vpc = valor[2,0]

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

    def __repr__(self):
        return 'Load Node: ' + self.name


class Generation(object):
    """ Modelo of PV or PQ generation.

    Parameters:
    ----------
    name : str
        generation name
    Pa : float
        complex power in phase a
    Pb : float
        complex power in phase b
    Pc : float
        complex power in phase c
    P : float
        three phase power
    Qmin : float
        minimum VAr
    Qmax : float
        maximum VAr
    Vmin : float
        minimum voltage in p.u
    Vmax : float
        maximum voltage in p.u
    Vspecified : float
        specified voltage in p.u
    DV_presc : float
        precision on p.u
    generation_type: str
        'PV' or 'PQ'
    type_connection : str
        'wye' or 'delta'
    """
    def __init__(self,name,Pa=0.0+0.0j,Pb=0.0+0.0j,Pc=0.0+0.0j,
                 P=None,Qmin=0.0+0.0j,Qmax=0.0+0.0j,
                 Vmin=0.95,Vmax=1.05,Vspecified=None,DV_presc=0.005,generation_type="PQ",
                 type_connection="wye",Z=None):


        self.type_connection=type_connection
        if type(Z) == type(None):
            self.Z=np.zeros((3,3), dtype=complex)

        else:
            self.Z=Z
        if generation_type=="PV":
            self.defective_phase=None
            self.name=name
            self.type="PV"
            self.limit_PV=False
            self.DV_presc=DV_presc

            if P is not None:
                self.P=-P
                self.Pa=self.Pb=self.Pc=1.0/3.0 *self.P
                self.phase_a_gd=True
                self.phase_b_gd=True
                self.phase_c_gd=True
                self.gd_type_phase="three"

            else:
                self.Pa=-Pa
                self.Pb=-Pb
                self.Pc=-Pc
                self.P=P


            self.Qmin=Qmin
            self.Qmax=Qmax
            self.Vmin=Vmin
            self.Vmax=Vmax

            if Vspecified is None:
                self.Vspecified=(Vmin+Vmax)/2

            else:
                self.Vspecified=Vspecified



        elif generation_type=="PQ":

            self.name=name
            self.type="PQ"

            if P is not None:
                self.P=-P
                self.Pa=self.Pb=self.Pc=-P/3

            else:

                self.Pa=-Pa
                self.Pb=-Pb
                self.Pc=-Pc
                self.P=P

        self.pp=np.array([[self.Pa],[self.Pb],[self.Pc]])

    def update_Q(self,Qa,Qb,Qc):

        self.Qa=Qa
        self.Qb=Qb
        self.Qc=Qc
        self.Pa= self.Qa+self.Pa
        self.Pb= self.Qb+self.Pb
        self.Pc= self.Qc+self.Pc
        self.P=  (self.Qa+self.Qb+self.Qc)+self.P



        self.pp=np.array([[self.Pa],[self.Pb],[self.Pc]])

        if np.imag(-self.P)>np.imag(self.Qmax):
            self.limit_PV=True


        elif np.imag(-self.P)<np.imag(self.Qmin):
            self.limit_PV=True


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
        for grid_dist in feeders:
            self.feeders[grid_dist.name] = grid_dist

        self.transformers = dict()
        for transformer in transformers:
            self.transformers[transformer.name] = transformer


class Section(Edge):
    def __init__(self,
                 name,
                 n1,
                 n2,
                 switch=None,
                 transformer=None,
                 conductor=None,
                 distributed_load=None,
                 line_model=None,
                 length=None):

        self.distributed_load = distributed_load
        assert isinstance(name, str), 'O parametro name da classe Section ' \
                                      'deve ser do tipo str'
        assert isinstance(n1, LoadNode), 'O parametro n1 da classe Section ' \
                                                                   'deve ser do tipo No de carga '
        assert isinstance(n2, LoadNode), 'O parâmetro n2 da classe Section ' \
                                                                   'deve ser do tipo No de carga '

        super(Section, self).__init__(name)
        self.n1 = n1
        self.n2 = n2
        self.switch = switch
        self.transformer = transformer

        if switch is not None:
            self.n1.switchs.append(self.switch)
            self.n2.switchs.append(self.switch)

        self.upstream_node = None
        self.downstream_node = None

        if transformer is not None:
            self._set_transformer_model()
            self.transformer_visited=False
            self.line_model = line_model
        else:
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

        self.A = np.linalg.inv(self.a)
        self.B = np.dot(self.A, self.b)

        for i in self.line_model.psorig.keys():
            if i not in self.line_model.phasing:
                self.A[self.line_model.psorig[i],self.line_model.psorig[i]] = 0.0

    def _set_transformer_model(self):
        self.a = self.transformer.a
        self.b = self.transformer.b
        self.c = self.transformer.c
        self.d = self.transformer.d
        self.A = self.transformer.A
        self.B = self.transformer.B

    # Em breve este metodo sera removido!!!!
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
                 loc=[],
                 neutral=False,
                 conductor=None,
                 neutral_conductor=None,
                 phasing=['a','b','c','n'],
                 Transpose=False,
                 units='Imperial'):


        self.transpose = Transpose
        self.conductor = conductor
        self.neutral_conductor = neutral_conductor
        self.loc = loc
        self.phasing = phasing
        self.psorig={'a':0,
                     'b':1,
                     'c':2}
        self.r_list=list()
        self.gmr_list = list()
        self.radius = list()
        self.aa = np.zeros

        for i in phasing:
            if i != 'n':
                self.r_list.append(self.conductor.r)
                self.gmr_list.append(self.conductor.gmr)
                self.radius.append(self.conductor.conductor_data['diameter']['value']*0.0833 / 2.0)

            else:
                self.r_list.append(self.neutral_conductor.r)
                self.gmr_list.append(self.neutral_conductor.gmr)
                self.radius.append(self.conductor.conductor_data['diameter']['value']*0.0833 / 2.0)







        # --------------------------------------
        # Series Impedance Z matrix calculation
        # --------------------------------------

        # primitive matriz calculation
        self.z = np.array(self._calc_primitive_z_matrix())
        # kron reduction, if there is neutral

        self.z = self._calc_phase_impedance_matrix(self.z)



        # calculation of sequence series impedance Z012 matrix
        self.Sequence()

        # --------------------------------------
        # Shunt Admittance Y matrix calculation
        # --------------------------------------

        # S distance matrix calculation
        self.p = np.array(self._calc_potencial_primitive_matrix())

        # kron reduction, if there is neutral
        self.p = self._calc_potential_coefficient_matrix(self.p)

        # shunt capacitance matrix calculation
        self.c = np.linalg.inv(self.p)

        # shunt admittance matrix calculation
        self.y = 1j * 2.0 * np.pi * 60.0 * self.c* 1e-6
        # convert the Z matrix units to ohms/kilometers if units in SI
        if units == 'SI':
            self.z = 1.0 / 1.60934 * self.z
            self.z = 1.0 / 1.60934 * self.y

        self.Parameters()
    def Parameters(self):
        # generalized line matrices calculation
        self.a = np.identity(3) + 0.5 * self.z * self.y
        self.b = self.z
        self.c = self.y  + 0.25 * self.y * self.z * self.y
        self.d = np.identity(3) + 0.5 * self.z * self.y

        ab = np.concatenate((self.a, self.b), axis=1)
        cd = np.concatenate((self.c, self.d), axis=1)
        self.abcd = np.concatenate((ab, cd), axis=0)

        self.A = np.linalg.inv(self.a)
        self.B = np.dot(self.A, self.b)
        for i in self.psorig.keys():
            if i not in self.phasing:
                self.A[self.psorig[i],self.psorig[i]] = 0.0



    def Sequence(self):
        A = np.array([[1.0, 1.0, 1.0],
                      [1.0, p2r(1.0, 240.0), p2r(1.0, 120.0)],
                      [1.0, p2r(1.0, 120.0), p2r(1.0, 240.0)]])
        if self.transpose:
            m_d = (self.z[0,0]+self.z[1,1]+self.z[2,2])/3
            m_f_d = (self.z[0,1]+self.z[0,2]+self.z[1,2])/3
            self.m = np.array([[m_d,m_f_d,m_f_d],[m_f_d,m_d,m_f_d],[m_f_d,m_f_d,m_d]])
            self.z=self.m
            self.z012 = np.dot(np.linalg.inv(A), np.dot(self.z, A))


        else:
            self.z012 = np.dot(np.linalg.inv(A), np.dot(self.z, A))

    def _calc_primitive_z_matrix(self):
        # carson equations reference:
        # William Kersting: Distribution System Modeling and Analysis
        # 1th edition, pag. 85
        Z = list()
        for i in range(len(self.loc)):
            z = list()
            for j in range(len(self.loc)):
                if i == j:
                    zij = self.r_list[i] + 0.09530 + 1j *  0.12134 * (np.log(1.0/self.gmr_list[i]) + 7.93402)
                else:
                    l = self.loc[i] - self.loc[j]
                    zij = 0.09530 + 1j * 0.12134 * (np.log(1.0/abs(l)) + 7.93402)
                z.append(zij)
            Z.append(z)

        return Z

    def _calc_potencial_primitive_matrix(self):
        P = list()

        # inch to feet conversion

        for i in range(len(self.loc)):
            p = list()
            for j in range(len(self.loc)):
                s = abs(self.loc[i] - self.loc[j].conjugate())
                d = abs(self.loc[i] - self.loc[j])
                if i == j:

                        pij = 11.17689 * np.log(s/self.radius[i])
                else:
                    pij = 11.17689 * np.log(s/d)
                p.append(pij)
            P.append(p)
        return P

    def _calc_phase_impedance_matrix(self, Z):
        # Kron Reduction
        size = len(self.phasing) if 'n' not in self.phasing else len(self.phasing)-1
        i, j = np.shape(Z)
        zij = Z[:size, :size]
        zij.shape = (size, size)
        zin = Z[:size, size:j]
        zin.shape = (size, j-size)
        znn = Z[size:, size:]
        znn.shape = (i-size, j-size)
        znj = Z[size:i, :size]
        znj.shape = (i-size, size)

        Z = zij - np.dot(np.dot(zin, np.linalg.inv(znn)), znj)
        zeq=np.zeros((3,3), dtype=complex)
        for i in self.psorig.keys():
            for j in self.psorig.keys():
                if i in self.phasing and j in self.phasing:
                    zeq[self.psorig[i],self.psorig[j]] = Z[self.phasing.index(i),self.phasing.index(j)]
                else:
                    if i==j:
                        zeq[self.psorig[i],self.psorig[j]] = 10e6
                    else:
                        zeq[self.psorig[i],self.psorig[j]] = 0

        return zeq

    def _calc_potential_coefficient_matrix(self, P):
        # Kron Reduction
        i, j = np.shape(P)
        size = len(self.phasing) if 'n' not in self.phasing else len(self.phasing)-1
        if self.__class__ == UnderGroundLine:
            if self.conductor.type == 'concentric':
                size = size/2

        pij = P[:size, :size]
        pij.shape = (size, size)
        pin = P[:size, size:j]
        pin.shape = (size, j-size)
        pnn = P[size:, size:]
        pnn.shape = (i-size, j-size)
        pnj = P[size:i, :size]
        pnj.shape = (i-size, size)
        P = pij - np.dot(np.dot(pin, np.linalg.inv(pnn)), pnj)

        yeq=np.zeros((3,3), dtype=complex)
        for i in self.psorig.keys():
            for j in self.psorig.keys():
                if i in self.phasing and j in self.phasing:
                    yeq[self.psorig[i],self.psorig[j]] = P[self.phasing.index(i),self.phasing.index(j)]
                else:
                    if i==j:
                        yeq[self.psorig[i],self.psorig[j]] = 10e9
                    else:
                        yeq[self.psorig[i],self.psorig[j]] = 0

        return yeq


class UnderGroundLine(LineModel):
    def __init__(self,
                 loc=[],
                 conductor=None,
                 phasing=['a','b','c'],
                 neutral_conductor=None,
                 Transpose=False,
                 type='concentric',
                 units='Imperial'):

        self.gmr_list=list()
        self.r_list=list()
        self.radius=list()
        self.conductor = conductor
        self.neutral_conductor =  neutral_conductor
        self.loc = list()
        self.type = type
        self.phasing = phasing
        self.psorig={'a':0,
                     'b':1,
                     'c':2}

        if self.conductor.type=='concentric':
            self.loc = loc
            self.loc.extend([x + self.conductor.R*1j  for x in loc])
            self.gmr_list.extend([conductor.gmr]*len(phasing))
            self.gmr_list.extend([conductor.GMRcn]*len(phasing))
            self.r_list.extend([conductor.r]*len(phasing))
            self.r_list.extend([conductor.rn]*len(phasing))


        elif self.conductor.type == "tapeshield":

            for i in phasing:
                if i == 'n':
                    self.loc.extend([x + self.conductor.R*1j  for x in self.loc])
                    self.r_list.extend([self.conductor.rn]*(len(phasing)-1))
                    self.gmr_list.extend([self.conductor.GMRcn]*(len(phasing)-1))

                    self.loc.append(loc[phasing.index(i)])
                    self.r_list.append(self.neutral_conductor.r)
                    self.gmr_list.append(self.neutral_conductor.gmr)
                    self.radius.append(self.neutral_conductor.conductor_data['diameter']['value']*0.0833 / 2.0)

                else:
                    self.loc.append(loc[phasing.index(i)])
                    self.r_list.append(self.conductor.r)
                    self.gmr_list.append(self.conductor.gmr)

        self._calc_potential_coefficient_matrix_()
        self.z = np.array(super()._calc_primitive_z_matrix())
        self.z = super()._calc_phase_impedance_matrix(self.z)



        # convert the Z matrix units to ohms/kilometers if units in SI
        if units == 'SI':
            self.z = 1.0 / 1.60934 * self.z
            self.z = 1.0 / 1.60934 * self.y
        super().Parameters()

    def _calc_potential_coefficient_matrix_(self):

        self.y=np.eye(3, dtype = complex)*0
        if self.conductor.type == 'concentric':
            self.p = (2*np.pi*self.conductor.e)/(np.log(24*self.conductor.R/self.conductor.dp) \
            - (1/self.conductor.k)*np.log(self.conductor.k*self.conductor.ds/(24*self.conductor.R)))
        elif self.conductor.type == 'tapeshield':
            self.p = 77.3619*10**-6 / np.log( ((self.conductor.ds - (self.conductor.T/2000)) / 2)\
            /(self.conductor.dp/2))

        for i in self.phasing:
            if i in self.psorig.keys():
                self.y[self.psorig[i],self.psorig[i]] = self.p*1j


class Shunt_Capacitor(object):
    """ Model of shunt capacitor

        Parameters
        ----------
        vll : float
            line voltage.
        Qa : float
            Var in phase a
        Qc : float
            Var in phase b
        Qb : float
            Var in phase c

        type_connection : str
            "wye" or "delta"

        """
    def __init__(self,vll, Qa,Qb,Qc,type_connection):
        self.vll=vll/1000
        self.Qa=Qa/1000
        self.Qb=Qb/1000
        self.Qc=Qc/1000
        self.type_connection=type_connection

    def calc_currents(self,va,vb,vc):
        """ Compute the injected current by shunt capacitor.

        Parameters
        ----------

        va : float
            voltage on phase a
        vb : float
            voltage on phase b
        vc : float
            voltage on phase c
        """

        if self.type_connection =="wye":
            self.ba=1j*self.Qa/(((self.vll/np.sqrt(3))**2)*1000)
            self.bb=1j*self.Qb/(((self.vll/np.sqrt(3))**2)*1000)
            self.bc=1j*self.Qc/(((self.vll/np.sqrt(3))**2)*1000)
            self.ia=self.ba*va
            self.ib=self.bb*vb
            self.ic=self.bc*vc
            self.ipc=np.array([[self.ia],[self.ib],[self.ic]])
            return self.ipc


        elif self.type_connection =="delta":
            self.ba=1j*self.Qa/(((self.vll/np.sqrt(3))**2)*1000)
            self.bb=1j*self.Qb/(((self.vll/np.sqrt(3))**2)*1000)
            self.bc=1j*self.Qc/(((self.vll/np.sqrt(3))**2)*1000)
            self.iab=self.ba*(va-vb)
            self.ibc=self.bb*(vb-vc)
            self.ica=self.bc*(vc-va)
            i_m=np.array([[self.iab],[self.ibc],[self.ica]])
            _m=np.array([[1,0,-1],[-1,1,0],[0,-1,1]])
            self.ipc=np.dot(_m,i_m)
            return self.ipc


class TransformerModel(object):
    def __init__(self,
                 name,
                 primary_voltage,
                 secondary_voltage,
                 power,
                 impedance=None,
                 R=5,
                 X=5,
                 connection='Dyn'):
        assert isinstance(name, str), 'O parâmetro name deve ser do tipo str'

        self.name = name
        self.connection = connection
        self.power = power
        if impedance is None:
            self.zbase = np.abs(secondary_voltage)**2 / np.abs(power)
            self.zt = self.zbase*(R +X*1j)/100
        else:
            self.zt = impedance
        self.z=np.identity((3), dtype=complex)*self.zt
        A = np.array([[1.0, 1.0, 1.0],
                      [1.0, p2r(1.0, 240.0), p2r(1.0, 120.0)],
                      [1.0, p2r(1.0, 120.0), p2r(1.0, 240.0)]])

        if self.connection == 'Dyn':
            self.VLL = primary_voltage
            self.Vll = secondary_voltage
            self.at = self.VLL / self.Vll
            self.nt = self.VLL / (self.Vll / np.sqrt(3.0))

            self.a = - self.nt / 3.0 * np.array([[0.0, 2.0, 1.0],
                                                 [1.0, 0.0, 2.0],
                                                 [2.0, 1.0, 0.0]])
            self.b = - self.nt / 3.0 * np.array([[0.0, 2.0 * self.zt, self.zt],
                                                 [self.zt, 0.0, 2.0 * self.zt],
                                                 [2.0 * self.zt, self.zt, 0.0]])
            self.c = np.zeros((3, 3))
            self.d = 1.0 / self.nt * np.array([[1.0, -1.0, 0.0],
                                               [0.0, 1.0, -1.0],
                                               [-1.0, 0.0, 1.0]])
            ab = np.concatenate((self.a, self.b), axis=1)
            cd = np.concatenate((self.c, self.d), axis=1)
            self.abcd = np.concatenate((ab, cd), axis=0)

            self.A = 1 / self.nt * np.array([[1.0, 0.0, -1.0],
                                             [-1.0, 1.0, 0.0],
                                             [0.0, -1.0, 1.0]])
            self.B = self.zt * np.identity(3)

            self.zt_012 = np.dot(np.linalg.inv(A), np.dot(self.B, A))


        elif self.connection == 'nyyn':

            self.VLL = primary_voltage
            self.Vll = secondary_voltage
            self.at = self.VLL / self.Vll
            self.nt = (self.VLL / self.Vll)

            self.a = -np.eye(3, dtype=complex)*self.nt
            self.b = -np.eye(3, dtype=complex)*self.zt*self.nt
            self.c = np.zeros((3, 3))
            self.d = np.eye(3, dtype=complex)/self.nt

            self.A = 1 / self.nt * np.array([[1.0, 0.0, 0.0],
                                             [0.0, 1.0, 0.0],
                                             [0.0, 0.0, 1.0]])

            self.B = self.zt * np.identity(3)


class Auto_TransformerModel(object):
    """ Model of Autotransformer

        Parameters:
        ----------
        name : str
            Autotransformer name
        step : float
            step of regulation
        tap_max : int
            limit of steps
        v_c : float
            Nominal voltage of regulator,
        v_c_min : float
            minimum threshold
        voltage : float
            regulation voltage
        connection : str
            only 'nYYn'
        tap_a : float
            fixed tap to phase 'a'
        tap_b float
            fixed tap to phase 'b'
        tap_c: float
            fixed tap to phase 'c'
        CTP : int
            Rated current on primary CT
        CTS : int
            Rated current on secondary CT
        R : float
            compensating voltage (real)
        X : float
            compensating voltage (image)
        r : float
            accumulated resistance
        x : float
            accumulated reactance

    """
    def __init__(self,
                 name,
                 step,
                 tap_max,
                 voltage,
                 vhold=122,
                 Npt = 20,
                 connection='nYYn',
                 tap_a=None,
                 tap_b=None,
                 tap_c=None,
                 CTP=None,
                 R=None,
                 X=None,
                 r=None,
                 x=None,
                 Z=0.0+0.0j,
                 step_pu=0.00625,
                 BD=2):

        self.step_pu=step_pu
        self.visited=False
        self.name = name
        self.step=step
        self.tap_max=tap_max
        self.voltage=voltage
        self.connection = connection
        self.tap_a=tap_a
        self.tap_b=tap_b
        self.tap_c=tap_c
        self.CTP=CTP
        self.CTS=5
        self.vn=self.voltage/np.sqrt(3)
        self.Npt=Npt
        self.v_c=vhold
        self.v_c_min=self.v_c-BD/2
        self.Z=Z
        self.BD=BD
        self.zz = np.eye(3)*self.Z


        if (R and X) != None:
            self.R=R
            self.X=X
            self.r=self.R/self.CTS
            self.x=self.X/self.CTS
            self.z=self.r + self.x*1j

            self.compesator_active=True
            self.CT=self.CTP/self.CTS


        elif (r and x) != None:
            self.r=r
            self.x=x
            self.R=self.r*self.CTP/self.Npt
            self.X=self.x*self.CTP/self.Npt
            self.z=self.r + self.x*1j

            self.compesator_active=True
            self.CT=self.CTP/self.CTS

        else:
            self.compesator_active=False



        if (self.tap_a and self.tap_b and self.tap_c) ==None:
            self.tap_manual=False
        else:
            self.tap_manual=True




        self.define_parameters(self.vn,self.vn,self.vn)

    def define_parameters(self,va,vb,vc):



        if not(self.tap_manual):
            self.aa=np.abs(self.v_c - abs(va))
            self.bb=np.abs(self.v_c - abs(vb))
            self.cc=np.abs(self.v_c - abs(vc))

            if self.v_c_min >abs(va):
                self.tap_a=self.aa/self.step
            else:
                self.tap_a=0
            if self.v_c_min >abs(vb):
                self.tap_b=self.bb/self.step
            else:
                self.tap_b=0

            if self.v_c_min >abs(vc):
                self.tap_c=self.cc/self.step
            else:
                self.tap_c=0


            self.define_tap()

        else:
            self.define_tap()

        self.a=np.array([[1/self.aR_a,0,0],
                         [0,1/self.aR_b,0],
                         [0,0,1/self.aR_c]])
        self.b=np.eye(3)*self.Z
        self.c=np.zeros((3,3))
        self.d=np.array([[self.aR_a,0,0],
                         [0,self.aR_b,0],
                         [0,0,self.aR_c]])

        self.ab = np.concatenate((self.a, self.b), axis=1)
        self.cd = np.concatenate((self.c, self.d), axis=1)
        self.abcd = np.concatenate((self.ab, self.cd), axis=0)

        self.A=self.d
        self.B=np.eye(3)*self.Z



    def define_tap(self):
        self.tap_a=np.round(self.tap_a)

        if self.tap_a < self.tap_max:
            self.aR_a=float(1+self.step_pu*self.tap_a)
        else:
            self.aR_a=float(1+self.step_pu*self.tap_max)

        self.tap_b=np.round(self.tap_b)

        if self.tap_b < self.tap_max:
            self.aR_b=float(1+self.step_pu*self.tap_b)
        else:
            self.aR_b=float(1+self.step_pu*self.tap_max)

        self.tap_c=np.round(self.tap_c)

        if self.tap_c < self.tap_max:
            self.aR_c=float(1+self.step_pu*self.tap_c)
        else:
            self.aR_c=float(1+self.step_pu*self.tap_max)




    def controler_voltage(self,ia,ib,ic,va,vb,vc):
        ia,ib,ic=ia/self.CT, ib/self.CT, ic/self.CT
        va,vb,vc=(va/self.Npt)-ia*self.z, (vb/self.Npt)-ib*self.z, (vc/self.Npt)-ic*self.z
        return va,vb,vc


class Switch(Edge):
    def __init__(self, name, state=1):
        assert state == 1 or state == 0, 'O parametro state deve ser um inteiro de valor 1 ou 0'
        super(Switch, self).__init__(name=name)
        self.state = state
        self.n1 = None
        self.n2 = None

    def set_sector(self, sector):
        if self.n1 is None:
            self.n1 = sector
        elif self.n2 is None:
            self.n2 = sector
        else:
            raise Exception('Switch sectors are defined!')

    def __repr__(self):
        if self.n1 is not None and self.n2 is not None:
            return 'Switch: %s - n1: %s, n2: %s' % (self.name, self.n1.name, self.n2.name)
        else:
            return 'Switch: %s' % self.name


class DistGrid(Tree):

    def __init__(self, name, sectors, sections):
        assert isinstance(name, str), 'O parametro name da classe DistGrid' \
                                      'deve ser do tipo string'
        assert isinstance(sectors, list), 'O parametro sectors da classe' \
                                          'DistGrid deve ser do tipo list'
        self.name = name

        self.sectors = dict()
        for sector in sectors:
            self.sectors[sector.name] = sector

        self.load_nodes = dict()
        for sector in sectors:
            for node in sector.load_nodes.values():
                self.load_nodes[node.name] = node

        self.sections = dict()
        self.sections_by_nodes = dict()
        for section in sections:
            self.sections[section.name] = section
            self.sections_by_nodes[(section.n1, section.n2)] = section



        self.switchs = dict()
        for section in sections:
            if section.switch is not None:
                self.switchs[section.switch.name] = section.switch

    def order(self, root):

        _grid_tree = self._generate_grid_tree()
        super(DistGrid, self).__init__(_grid_tree, str)

        super(DistGrid, self).order(root)

        self._associate_rnp()

        for sector in self.sectors.values():
            path = self.node_to_root_path(sector.name)
            if sector.name != root:
                downstream_sector = path[1, 1]
                sector.rnp = sector.associated_rnp[downstream_sector][1]

    def _associate_rnp(self):
        # RNP assotiated determination
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
                        if i in j.neighbors:
                            link_nodes.append((j, i))

                for node in link_nodes:
                    sector.order(node[1].name)
                    sector.associated_rnp[neighbor_sector.name] = (node[0],
                                                                sector.rnp)

    def _generate_grid_tree(self):
        """
        """
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
        visited.append(sector)
        stack.append(sector)

        # for percorre os sectors neighbors ao sector atual
        # que ainda não tenham sido visited
        neighbors = sector.neighbors
        for i in neighbors:

            # esta condição testa se existe uma ligação
            # entre os sectors de uma mesma subestação, mas
            # que possuem uma switch normalmente aberta entre eles.
            # caso isto seja constatado o laço for é interrompido.
            if i not in visited and i in self.sectors.values():
                for c in self.switchs.values():
                    if c.n1 == sector and c.n2 == i:
                        if c.state == 1:
                            break
                        else:
                            pass
                    elif c.n2 == sector and c.n1 == i:
                        if c.state == 1:
                            break
                        else:
                            pass
                else:
                    continue
                next_ = i
                neighbor_sector = self.sectors[i.name]
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
                return self._generate_load_nodes_tree(self.sectors[previous.name],
                                                       visited, stack)
            else:
                return
        return self._generate_load_nodes_tree(self.sectors[next_.name],
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
        prune = super(DistGrid, self).prune(node, change_rnp)
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

        # atualiza sectors do grid_dist
        self.sectors.update(sectors)

        # atualiza os nos de carga do grid_dist
        self.load_nodes.update(load_nodes)

        # atualiza as switchs do grid_dist
        self.switchs.update(switchs)

        # atualiza os sections do grid_dist
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
            super(DistGrid, self).insert_branch(node, (sectors_rnp, sectors_tree))
        else:
            super(DistGrid, self).insert_branch(node, (sectors_rnp, sectors_tree), root_node)

        # atualiza a tree de sectors do grid_dist
        self.update_grid_tree()

        # atualiza a tree de nos de carga do grid_dist
        self.generate_load_nodes_tree()


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
            self.r = self.conductor_data['resistence']['value']
            self.gmr = self.conductor_data['gmr']['value']


class Under_Ground_Conductor(object):
    def __init__(self,
                name = None,
                permittivity=867.079492,
                size = None,
                material = None,
                type="concentric",
                outsider_diameter = None,
                rp = None,
                GMRp = None,
                dp = None,
                k = None,
                rs = None,
                GMRs = None,
                ds = None,
                T=None,
                ampacity = None):
        self.type=type
        if type == "concentric":
            self.e=permittivity*0.01420*10**-6
            self.size = size
            self.material = material
            self.outsider_diameter = outsider_diameter
            self.r = rp
            self.gmr = GMRp
            self.dp = dp
            self.k = k
            self.rs = rs
            self.GMRs = GMRs
            self.ds = ds
            self.ampacity = ampacity

            self.R = (self.outsider_diameter - self.ds)/24
            self.rn =self.rs/self.k
            self.GMRcn=(self.GMRs*self.k*self.R**(self.k-1))**(1/self.k)

        elif type == "tapeshield":
            self.T = T
            self.ds = ds
            self.R=((ds/2)-(T/2000))/12
            self.r = rp
            self.gmr = GMRp
            self.GMRcn=self.R
            self.dp = dp
            self.rn=18.826/(ds*T)


class Distributed_Load(object):
    def __init__(self,
                 name = None,
                 ppa=0.0e3 + 0.0e3j,
                 ppb=0.0e3 + 0.0e3j,
                 ppc=0.0e3 + 0.0e3j,
                 type_connection="wye",
                 voltage=0.0 + 0.0j,
                 zipmodel=[1.0, 0.0, 0.0]):

        v = voltage / np.sqrt(3)
        self.type_connection = type_connection
        self.name = name
        self.zipmodel =  zipmodel
        self.pp = np.array([[ppa],[ppb],[ppc]], dtype=complex)
        self.vp = np.array([[p2r(v, 0.0)],[p2r(v, -120.0)],[p2r(v, 120.0)]], dtype = complex)
        self.D=np.array([[1,-1,0],[0,1,-1],[-1,0,1]])
        self.vpl = np.dot(self.D,self.vp)

        if self.type_connection=="delta":
            self.vpm=self.vpl

        if self.type_connection=="wye":
            self.vpm=self.vp

        self.z = np.divide(np.abs(self.vpm)**2, np.conjugate(self.pp))
        self.i_constant=np.abs(np.divide(self.pp, self.vpm))
        self.ipq = 0.0 +0.0j
        self.iz = 0.0 +0.0j
        self.ii = 0.0 +0.0j


    def calc_currents(self, vp):
        self.vp = vp
        self.vpl = np.dot(self.D,self.vp)

        if self.type_connection=="delta":
            self.vpm=self.vpl

        if self.type_connection=="wye":
            self.vpm=self.vp
        self.ipq = np.multiply(self.zipmodel[0], np.conjugate(np.divide(self.pp, self.vpm)))

        if  self.zipmodel[1] !=0:

            self.iz = self.zipmodel[1] * np.divide(self.vpm, self.z)
            self.iz=np.where(np.isnan(self.iz),np.zeros(np.shape(self.iz), dtype=complex),self.iz)

        if  self.zipmodel[2] !=0:

            alpha=np.angle(self.vpm)-np.angle(self.pp)
            self.ii = self.zipmodel[2]*self.i_constant*(np.cos(alpha)+np.sin(alpha)*1j)
            self.ii=np.where(np.isnan(self.ii),np.zeros(np.shape(self.ii), dtype=complex),self.ii)




        self.i =  self.ipq  + self.iz + self.ii
        if self.type_connection=="delta":
            self.i=np.dot(self.D.T,self.i)
        elif self.type_connection=="wye":
            self.i=self.i


if __name__ == '__main__':
    pass
