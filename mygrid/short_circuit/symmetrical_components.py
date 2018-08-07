# -*- coding: utf-8 -*-
from mygrid.util import P, R, Base
from mygrid.grid import Switch

def config_objects(substation,
                   positive_eq_impedance=0.0,
                   zero_eq_impedance=0.0):
    """conifg_objects: configura os objetos da substecao para calculo 
    de sc-circuito."""
    substation.positive_impedance = positive_eq_impedance
    substation.zero_impedance = zero_eq_impedance
    substation.positive_equivalent_impedance = positive_eq_impedance
    substation.zero_equivalent_impedance = zero_eq_impedance

    for transformer in substation.transformers.values():
        substation.sub_base = Base(transformer.secondary_voltage.m,
                                   transformer.power.m)
        break

    for feeder in substation.feeders.values():
        for section in feeder.sections.values():
            section.positive_impedance = (section.conductor.rp + section.conductor.xp * 1j) * section.length
            section.zero_impedance = (section.conductor.rz + section.conductor.xz * 1j) * section.length

            section.contact_resistence = 100.0

            section.base = substation.sub_base

            section.positive_equivalent_impedance = section.positive_impedance / section.base.impedance
            section.zero_equivalent_impedance = section.zero_impedance / section.base.impedance

            section.flow = R(r=0.0, i=0.0)

    calc_equivalent_impedance(substation)


def calc_short_circuit(substation, sc_type):

    if sc_type == 'three-phase':
        three_phase_sc = [['Section 3l', 'SS pu', 'SS A']]
        for current_feeder, r in substation.feeders.items():
            for section in substation.feeders[current_feeder].sections.values():
                sc = _calc_three_phase_sc(section)
                three_phase_sc.append([section.name,
                                        str(sc.pu),
                                        str(sc.m)])

        return three_phase_sc

    elif sc_type == 'line-to-ground':
        line_to_ground_sc = [['Section l2g', 'SS pu', 'SS A']]
        for current_feeder, r in substation.feeders.items():
            for section in substation.feeders[current_feeder].sections.values():
                sc = _calc_line_to_groud_sc(section)
                line_to_ground_sc.append([section.name,
                                         str(sc.pu),
                                         str(sc.m)])

        return line_to_ground_sc

    elif sc_type == 'line-to-line':
        line_to_line_sc = [['Section l2l', 'SS pu', 'SS A']]
        for current_feeder, r in substation.feeders.items():
            for section in substation.feeders[current_feeder].sections.values():
                sc = calc_line_to_line_sc(section)
                line_to_line_sc.append([section.name,
                                       str(sc.pu),
                                       str(sc.m)])

        return line_to_line_sc

    elif sc_type == 'line-to-ground-min':
        line_to_ground_min_sc = [['Section l2g min', 'SS pu', 'SS A']]
        for current_feeder, r in substation.feeders.items():
            for section in substation.feeders[current_feeder].sections.values():
                sc = _calc_line_to_ground_min_sc(section)
                line_to_ground_min_sc.append([section.name,
                                                str(sc.pu),
                                                str(sc.m)])

        return line_to_ground_min_sc


def calc_equivalent_impedance(substation):

    visited_sections = []  # guarda os sections em que já foram calculados a impedância equivalente

    for current_feeder, r in substation.feeders.items():  # procura o nó inicial(root) do feeder
        for i in substation.feeders[current_feeder].sections.values():
            for j in substation.feeders[current_feeder].sectors[r.load_nodes_tree.root].load_nodes.keys():
                next_node = substation.feeders[current_feeder].sectors[r.load_nodes_tree.root].load_nodes[j]  # nó a partir do qual será procurado sections conectados a ele
                current_section = substation  # último section que foi calculado a impedância equivalente
                break
            break
        break

    _calc_equivalent_impedance(substation, current_section, next_node, current_feeder, visited_sections)


def _calc_equivalent_impedance(substation, previous_section, current_node, current_feeder, visited_sections):
    for i in substation.feeders[current_feeder].sections.values():
        if i not in visited_sections and (i.n1 or i.n2) == current_node:  # procura sections conectados ao current_node (next_node da execução anterior)
            if type(current_node) == Switch:  # verifica se a ligação é feita por meio de chave, verificando-se o state da chave
                if current_node.state == 0:
                    continue
                else:
                    pass
            else:
                pass

            # calcula impedância equivalente do section
            i.positive_equivalent_impedance = i.positive_equivalent_impedance + previous_section.positive_equivalent_impedance
            i.zero_equivalent_impedance = i.zero_equivalent_impedance + previous_section.zero_equivalent_impedance
            visited_sections.append(i)
            current_section = i

            # procura o pro_no para calcular as proximas impedancias equivalentes
            if current_node == i.n1:
                next_node = i.n2
            else:
                next_node = i.n1

            _calc_equivalent_impedance(substation, current_section, next_node, current_feeder, visited_sections)
        else:
            pass
    return


def _calc_impedance(section):
    return (section.length * section.conductor.rp,
            section.length * section.conductor.xp)


def _calc_line_to_groud_sc(section):
    sc1 = (3.0) * section.base.current / (2 * section.positive_equivalent_impedance + section.zero_equivalent_impedance)
    sc_current = R(sc1.real, sc1.imag)
    sc_current.base = section.base.current
    return sc_current


def calc_line_to_line_sc(section):
    sc2 = (3 ** 0.5) * section.base.current / (2 * section.positive_equivalent_impedance)
    sc_current = R(sc2.real, sc2.imag)
    sc_current.base = section.base.current
    return sc_current


def _calc_three_phase_sc(section):
    sc3 = 1.0 * section.base.current / (section.positive_equivalent_impedance)
    sc_current = R(sc3.real, sc3.imag)
    sc_current.base = section.base.current
    return sc_current


def _calc_line_to_ground_min_sc(section):
    sc1m = 3.0 * section.base.current / (2 * section.positive_equivalent_impedance + section.zero_equivalent_impedance+3*section.contact_resistence/section.base.impedance)
    sc_current = R(sc1m.real, sc1m.imag)
    sc_current.base = section.base.current
    return sc_current
