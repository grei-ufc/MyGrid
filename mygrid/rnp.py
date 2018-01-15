# coding=utf-8
"""
node depth representation (RNP) module
"""

from collections import OrderedDict
from numpy import array, size, reshape, where, concatenate, mat, delete, ndarray, insert


class Node(object):
    """
    Node class
    ---------
        This class represents a node in the tree graph.

    Parameters
    ----------
        name : str node name
        neighbors : node neighbors
    """

    def __init__(self, name, neighbors=list()):
        assert isinstance(name, str)
        self.name = name
        assert isinstance(neighbors, list)
        self.neighbors = neighbors


class Edge(object):
    """
    Edge Class
    -------------
        This class represents a edge in the graph. 
        A edge links two nodes in a graph .

    Parameters
    ----------
        name : str edge name
    """

    n1 = None
    n2 = None

    def __init__(self, name):
        assert isinstance(name, str), 'O parametro name da classe Aresta deve ser do tipo string'
        self.name = name


class Tree(object):
    """
    Tree Class
    -------------
        A classe *Tree* representa um grafo do tipo tree. Uma tree é um grafo
        conexo e que não possui ciclos em sua estrutura.

        Oferece métodos para manipular, alterar e buscar informações dos ramos e nós
        da *Tree*.

    Parâmetros
    ----------
        tree : dict Dicionário que representa a árvore, onde as chaves são os nós
        e os valores são listas com os neighbors do nó que está como chave.
        dtype : tipo dos nós que podem ser strings ou inteiros
    """

    def __init__(self, tree, dtype=int):
        assert isinstance(tree, dict)

        self.dtype = dtype
        self.tree = tree
        self.root = None
        self._tree = None

    def order(self, root):
        """
        metodo ordena
        -------------
            Este método cria a representação no profundidade da tree

        Parâmetros
        ----------
            root : dtype Nó, presente na tree, que sera a root da representação
            nó profundidade

        """
        assert isinstance(root, self.dtype), 'Erro no tipo do parametro root!'

        if issubclass(self.dtype, int):
            self.rnp = array(mat('0; 0'), dtype=int)
        else:
            self.rnp = array(mat('0; 0'), dtype=str)

        self.root = root
        self.rnp[1][0] = root
        visited = []
        stack = []
        self._search(root, visited, stack)

    def _search(self, no, visited, stack):
        """
        método _search
        ------------
            Este método faz uma busca em profundidade na tree para que a
            representação no profundidade possa ser criada

        Parâmetros
        ----------
            no : dtype Nó a ser visitado
            visited : list Lista de nós já visited
            stack : list Lista para identificar em que nível do grafo a busca está
        """
        visited.append(no)
        stack.append(no)

        try:
            neighbors = self.tree[no]
        except KeyError:
            stack.pop()
            if stack:
                anter = stack.pop()
                return self._search(anter, visited, stack)
            else:
                return

        for i in neighbors:
            if i not in visited:
                next_ = i
                if issubclass(self.dtype, str):
                    self.rnp = concatenate((self.rnp, [[str(len(stack))], [i]]), axis=1)
                else:
                    self.rnp = concatenate((self.rnp, [[len(stack)], [i]]), axis=1)
                break
        else:
            stack.pop()
            if stack:
                anter = stack.pop()
                return self._search(anter, visited, stack)
            else:
                return
        return self._search(next_, visited, stack)

    def rnp_dic(self):
        """
        método rnp_dict
        ---------------
            Este método retorna a representação da tree rnp em forma de um
            dicionário ordenado
        """
        rnp = OrderedDict()
        for i in self.rnp.transpose():
            rnp[i[1]] = i[0]
        return rnp

    def prune(self, no, change_rnp=True):
        """
        método prune
        ------------
            Este método permite a realização da prune da tree definida pela classe *Tree*.
            Por meio dos parâmetro change_rnp é possivel realizar uma prune virtual ou uma
            prune real sobre a estrutura da tree.

        Parâmetros
        ----------
            no : dtype Indica o ponto onde a prune deve ser realizada.
            change_rnp : boolean Indica se a prune deve ser virtual ou real.
        """
        assert isinstance(no, self.dtype), 'O parâmetro nó deve ser do tipo dtype'
        rnp, indice = self._search_depth(no, return_array=True)

        depth = rnp[0, 0]
        prune_indices = list([indice])
        tree = dict()
        tree[rnp[1, 0]] = self.tree.pop(rnp[1, 0])

        for i in range(indice + 1, size(self.rnp, axis=1)):
            next_ = self.rnp[:, i]
            next_ = reshape(next_, (2, 1))
            if int(next_[0, 0]) > int(depth):
                rnp = concatenate((rnp, next_), axis=1)
                prune_indices.append(i)
                tree[next_[1, 0]] = self.tree.pop(next_[1, 0])
            else:
                break
        if change_rnp:
            self.rnp = delete(self.rnp, prune_indices, axis=1)

        # for exclui o vizinho do nó root da prune que remanesceu
        # na tree podada
        for i in tree[rnp[1, 0]]:
            if i not in tree.keys():
                tree[rnp[1, 0]].remove(i)
                self.tree[i].remove(rnp[1, 0])

        return rnp, tree

    def _insert_branch(self, no, prune):
        if issubclass(self.dtype, int):
            assert isinstance(no, int), 'O parâmetro no deve ser do tipo int'
        else:
            assert isinstance(no, str), 'O parâmetro no deve ser do tipo str'
        assert issubclass(type(prune), tuple), 'O parâmetro prune deve ser uma tupla'

        prune_rnp = prune[0]
        tree_prune = prune[1]

        # atualização da tree
        if no not in tree_prune[prune_rnp[1, 0]]:
            tree_prune[prune_rnp[1, 0]].append(no)
        if prune_rnp[1, 0] not in self.tree[no]:
            self.tree[no].append(prune_rnp[1, 0])
        self.tree.update(tree_prune)

        # atualização da rnp

        root_depth, indice = self._search_depth(no)
        root_depth_branch = prune_rnp[0, 0]

        for i in range(size(prune_rnp, axis=1)):
            node_depth = prune_rnp[0, i]
            new_depth = int(node_depth) - int(root_depth_branch) + int(root_depth) + 1

            if issubclass(self.dtype, str):
                prune_rnp[0][i] = str(new_depth)
            else:
                prune_rnp[0][i] = new_depth

        self.rnp = insert(self.rnp, [indice + 1], prune_rnp, axis=1)

    def insert_branch(self, no_de_inser, prune, root_node=None):
        if issubclass(self.dtype, int):
            assert isinstance(no_de_inser, int), 'O parâmetro no deve ser do tipo int'
        else:
            assert isinstance(no_de_inser, str), 'O parâmetro no deve ser do tipo str'

        assert issubclass(type(prune), tuple), 'O parâmetro prune deve ser uma tupla!'

        prune_rnp = prune[0]
        tree_prune = prune[1]

        # cria uma tree temporaria, ordena de acordo com o parametro de entrada
        # root_node e insere a arvore_temporaria na tree de destino por meio do
        # metodo de inserção 1
        temp_tree = Tree(tree=tree_prune, dtype=self.dtype)

        if root_node is not None:
            temp_tree.order(root_node)
        else:
            temp_tree.order(prune_rnp[1, 0])

        self._insert_branch(no_de_inser, (temp_tree.rnp, temp_tree.tree))


    def _search_depth(self, no, return_array=False):
        try:
            indice = where(self.rnp[1, :] == no)[0][0]
            depth = int(self.rnp[0][indice])
        except IndexError:
            raise IndexError('O nó especificado não existe na árvore!')

        if return_array:
            return array([[depth], [no]]), indice
        else:
            return depth, indice

    def path_node_to_root(self, no, direction=1):
        if issubclass(self.dtype, int):
            assert isinstance(no, int), 'O parâmetro no deve ser do tipo inteiro'
        else:
            assert isinstance(no, str), 'O parâmetro no deve ser do tipo string'

        assert direction == 1 or direction == 0, 'O parâmetro direction deve ser um inteiro de valor 1 ou 0'

        path, indice = self._search_depth(no, return_array=True)
        depth = int(path[0][0])
        for i in range(indice, -1, -1):
            next_ = self.rnp[:, i]
            next_ = reshape(next_, (2, 1))
            if int(next_[0, 0]) < depth:
                depth -= 1
                path = concatenate((path, next_), axis=1)
        if direction == 1:
            return path
        else:
            return path[:, range(size(path, axis=1) - 1, -1, -1)]

    def node_to_node_path(self, n1, n2, direction=1):

        if issubclass(self.dtype, int):
            assert isinstance(n1, int), 'O parâmetro n1 deve ser do tipo inteiro'
            assert isinstance(n2, int), 'O parâmetro n2 deve ser do tipo inteiro'
        else:
            assert isinstance(n1, str), 'O parâmetro n1 deve ser do tipo string'
            assert isinstance(n2, str), 'O parâmetro n2 deve ser do tipo string' \
                                        ''
        assert direction == 1 or direction == 0, 'O parâmetro direction deve ser um inteiro de valor 1 ou 0'

        path, indice = self._search_depth(n1, return_array=True)
        depth = int(path[0][0])

        for i in range(indice, -1, -1):
            next_ = self.rnp[:, i]
            next_ = reshape(next_, (2, 1))
            if int(next_[0, 0]) < depth:
                depth -= 1
                path = concatenate((path, next_), axis=1)
                if next_[1][0] == n2:
                    break
        else:
            n1, n2 = n2, n1

            path, indice = self._search_depth(n1, return_array=True)
            depth = int(path[0][0])

            for i in range(indice, -1, -1):
                next_ = self.rnp[:, i]
                next_ = reshape(next_, (2, 1))
                if int(next_[0, 0]) < depth:
                    depth -= 1
                    path = concatenate((path, next_), axis=1)
                    if next_[1][0] == n2:
                        break
            else:
                # raise AttributeError('Os nós n1 e n2
                # não pertencem ao mesmo ramo!')
                a1 = self.path_node_to_root(n2, direction=1)
                a2 = self.path_node_to_root(n1, direction=0)

                list_commom_nodes = [i for i in a2[1, :] if i in a1[1, :]]
                commom_node_depth = 0
                for no in a1.transpose():
                    if no[1] in list_commom_nodes:
                        if no[0] > commom_node_depth:
                            commom_node_depth = no[0]
                            no_comum = no[1]

                commom_node_indice = where(a1[1, :] == no_comum)[0][0]

                a1 = a1[:, :commom_node_indice + 1]

                commom_node_indice = where(a2[1, :] == no_comum)[0][0]
                a2 = a2[:, commom_node_indice + 1:]

                return concatenate((a1, a2), axis=1)

        if direction == 1:
            return path
        else:
            return path[:, range(size(path, axis=1) - 1, -1, -1)]



if __name__ == '__main__':
    # tree 1
    nodes1 = {3: [1],
            1: [3, 2, 7],
            7: [1, 8, 9, 4, 10],
            10: [7],
            4: [7, 5, 6],
            5: [4],
            6: [4],
            9: [7],
            8: [7],
            2: [1, 11, 12, 13],
            11: [2],
            12: [2, 13],
            13: [12]}

    # tree 2
    nodes2 = {14: [15],
            15: [14, 16, 19],
            16: [15, 17, 18],
            17: [16],
            18: [16],
            19: [15]}

    # definição da tree a1
    tree_1 = Tree(nodes1)

    # ordenação da tree a1
    tree_1.order(root=3)
    print('RNP representation of tree 1')
    print(tree_1.rnp)

    # definição da tree a2
    tree_2 = Tree(nodes2)

    # ordenação da tree a2
    tree_2.order(root=14)

    print('RNP representation of tree 2')
    print(tree_2.rnp)

    # operação de prune
    prune = tree_1.prune(7, change_rnp=True)
    print('Branch Prune in tree 1')
    print(prune)

    print('RNP representation of tree 1 after prune')
    print(tree_1.rnp)

    # print tree_1.path_node_to_root(no=12, direction=1)
    # print tree_1.node_to_node_path(n1=13, n2=2, direction=1)

    # operação de inserção
    tree_2.insert_branch(19, prune, 7)

    print('RNP representation of tree 1 after branch insertion of tree 1 prune')
    print(tree_2.rnp)