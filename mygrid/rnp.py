"""
módulo de representação nó profundidade
"""

from collections import OrderedDict
from numpy import array, size, reshape, where, concatenate, mat, delete, ndarray, insert


class No(object):
    """
    Classe No
    ---------
        Classe que representa qualquer instancia que represente um nó em um
        grafo

    Parâmetros
    ----------
        nome : str identifica o nó
        vizinhos : list identifica os nós que estão na vizinhança
    """

    def __init__(self, nome, vizinhos=list()):
        assert isinstance(nome, str)
        self.nome = nome
        assert isinstance(vizinhos, list)
        self.vizinhos = vizinhos


class Aresta(object):
    """
    Classe Aresta
    -------------
        Classe que representa qualquer instancia que represente uma aresta em um grafo,
        uma aresta liga dois nós vizinhos e pode ser ou não direcionada.

    Parâmetros
    ----------
        nome : str identifica a aresta
    """

    n1 = None
    n2 = None

    def __init__(self, nome):
        assert isinstance(nome, str), 'O parâmetro nome da classe Aresta deve ser do tipo string'
        self.nome = nome


class Arvore(object):
    """
    Classe Arvore
    -------------
        A classe *Arvore* representa um grafo do tipo arvore. Uma arvore é um grafo
        conexo e que não possui ciclos em sua estrutura.

        Oferece métodos para manipular, alterar e buscar informações dos ramos e nós
        da *Arvore*.

    Parâmetros
    ----------
        arvore : dict Dicionário que representa a árvore, onde as chaves são os nós
        e os valores são listas com os vizinhos do nó que está como chave.
        dtype : tipo dos nós que podem ser strings ou inteiros
    """

    def __init__(self, arvore, dtype=int):
        assert isinstance(arvore, dict)

        self.dtype = dtype
        self.arvore = arvore
        self.raiz = None
        self._arvore = None

    def ordenar(self, raiz):
        """
        metodo ordena
        -------------
            Este método cria a representação no profundidade da arvore

        Parâmetros
        ----------
            raiz : dtype Nó, presente na arvore, que sera a raiz da representação
            nó profundidade

        """
        assert isinstance(raiz, self.dtype), 'Erro no tipo do parâmetro raiz!'

        if issubclass(self.dtype, int):
            self.rnp = array(mat('0; 0'), dtype=int)
        else:
            self.rnp = array(mat('0; 0'), dtype=str)

        self.raiz = raiz
        self.rnp[1][0] = raiz
        visitados = []
        pilha = []
        self._proc(raiz, visitados, pilha)

    def _proc(self, no, visitados, pilha):
        """
        método _proc
        ------------
            Este método faz uma busca em profundidade na arvore para que a
            representação nó profundidade possa ser criada

        Parâmetros
        ----------
            no : dtype Nó a ser visitado
            visitados : list Lista de nós já visitados
            pilha : list Lista para identificar em que nível do grafo a busca está
        """
        visitados.append(no)
        pilha.append(no)

        try:
            visinhos = self.arvore[no]
        except KeyError:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._proc(anter, visitados, pilha)
            else:
                return

        for i in visinhos:
            if i not in visitados:
                prox = i
                if issubclass(self.dtype, str):
                    self.rnp = concatenate((self.rnp, [[str(len(pilha))], [i]]), axis=1)
                else:
                    self.rnp = concatenate((self.rnp, [[len(pilha)], [i]]), axis=1)
                break
        else:
            pilha.pop()
            if pilha:
                anter = pilha.pop()
                return self._proc(anter, visitados, pilha)
            else:
                return
        return self._proc(prox, visitados, pilha)

    def rnp_dic(self):
        """
        método rnp_dict
        ---------------
            Este método retorna a representação da arvore rnp em forma de um
            dicionário ordenado
        """
        rnp = OrderedDict()
        for i in self.rnp.transpose():
            rnp[i[1]] = i[0]
        return rnp

    def podar(self, no, alterar_rnp=False):
        """
        método podar
        ------------
            Este método permite a realização da poda da arvore definida pela classe *Arvore*.
            Por meio dos parâmetro alterar_rnp é possivel realizar uma poda virtual ou uma
            poda real sobre a estrutura da arvore.

        Parâmetros
        ----------
            no : dtype Indica o ponto onde a poda deve ser realizada.
            alterar_rnp : boolean Indica se a poda deve ser virtual ou real.
        """
        assert isinstance(no, self.dtype), 'O parâmetro nó deve ser do tipo dtype'
        rnp, indice = self._busca_prof(no, retorna_array=True)

        prof = rnp[0, 0]
        indices_poda = list([indice])
        arvore = dict()
        arvore[rnp[1, 0]] = self.arvore.pop(rnp[1, 0])

        for i in range(indice + 1, size(self.rnp, axis=1)):
            prox = self.rnp[:, i]
            prox = reshape(prox, (2, 1))
            if int(prox[0, 0]) > int(prof):
                rnp = concatenate((rnp, prox), axis=1)
                indices_poda.append(i)
                arvore[prox[1, 0]] = self.arvore.pop(prox[1, 0])
            else:
                break
        if alterar_rnp:
            self.rnp = delete(self.rnp, indices_poda, axis=1)

        # for exclui o vizinho do nó raiz da poda que remanesceu
        # na arvore podada
        for i in arvore[rnp[1, 0]]:
            if i not in arvore.keys():
                arvore[rnp[1, 0]].remove(i)
                self.arvore[i].remove(rnp[1, 0])

        return rnp, arvore

    def _inserir_ramo(self, no, poda):
        if issubclass(self.dtype, int):
            assert isinstance(no, int), 'O parâmetro no deve ser do tipo int'
        else:
            assert isinstance(no, str), 'O parâmetro no deve ser do tipo str'
        assert issubclass(type(poda), tuple), 'O parâmetro poda deve ser uma tupla'

        poda_rnp = poda[0]
        poda_arvore = poda[1]

        # atualização da arvore
        if no not in poda_arvore[poda_rnp[1, 0]]:
            poda_arvore[poda_rnp[1, 0]].append(no)
        if poda_rnp[1, 0] not in self.arvore[no]:
            self.arvore[no].append(poda_rnp[1, 0])
        self.arvore.update(poda_arvore)

        # atualização da rnp

        prof_raiz, indice = self._busca_prof(no)
        prof_raiz_ramo = poda_rnp[0, 0]

        for i in range(size(poda_rnp, axis=1)):
            prof_no = poda_rnp[0, i]
            nova_prof = int(prof_no) - int(prof_raiz_ramo) + int(prof_raiz) + 1

            if issubclass(self.dtype, str):
                poda_rnp[0][i] = str(nova_prof)
            else:
                poda_rnp[0][i] = nova_prof

        self.rnp = insert(self.rnp, [indice + 1], poda_rnp, axis=1)

    def inserir_ramo(self, no_de_inser, poda, no_raiz=None):
        if issubclass(self.dtype, int):
            assert isinstance(no_de_inser, int), 'O parâmetro no deve ser do tipo int'
        else:
            assert isinstance(no_de_inser, str), 'O parâmetro no deve ser do tipo str'

        assert issubclass(type(poda), tuple), 'O parâmetro poda deve ser uma tupla!'

        poda_rnp = poda[0]
        poda_arvore = poda[1]

        # cria uma arvore temporaria, ordena de acordo com o parametro de entrada
        # no_raiz e insere a arvore_temporaria na arvore de destino por meio do
        # metodo de inserção 1
        arvore_temp = Arvore(arvore=poda_arvore, dtype=self.dtype)

        if no_raiz is not None:
            arvore_temp.ordenar(no_raiz)
        else:
            arvore_temp.ordenar(poda_rnp[1, 0])

        self._inserir_ramo(no_de_inser, (arvore_temp.rnp, arvore_temp.arvore))


    def _busca_prof(self, no, retorna_array=False):
        try:
            indice = where(self.rnp[1, :] == no)[0][0]
            prof = int(self.rnp[0][indice])
        except IndexError:
            raise IndexError('O nó especificado não existe na árvore!')

        if retorna_array:
            return array([[prof], [no]]), indice
        else:
            return prof, indice

    def caminho_no_para_raiz(self, no, sentido=1):
        if issubclass(self.dtype, int):
            assert isinstance(no, int), 'O parâmetro no deve ser do tipo inteiro'
        else:
            assert isinstance(no, str), 'O parâmetro no deve ser do tipo string'

        assert sentido == 1 or sentido == 0, 'O parâmetro sentido deve ser um inteiro de valor 1 ou 0'

        caminho, indice = self._busca_prof(no, retorna_array=True)
        prof = int(caminho[0][0])
        for i in range(indice, -1, -1):
            prox = self.rnp[:, i]
            prox = reshape(prox, (2, 1))
            if int(prox[0, 0]) < prof:
                prof -= 1
                caminho = concatenate((caminho, prox), axis=1)
        if sentido == 1:
            return caminho
        else:
            return caminho[:, range(size(caminho, axis=1) - 1, -1, -1)]

    def caminho_no_para_no(self, n1, n2, sentido=1):

        if issubclass(self.dtype, int):
            assert isinstance(n1, int), 'O parâmetro n1 deve ser do tipo inteiro'
            assert isinstance(n2, int), 'O parâmetro n2 deve ser do tipo inteiro'
        else:
            assert isinstance(n1, str), 'O parâmetro n1 deve ser do tipo string'
            assert isinstance(n2, str), 'O parâmetro n2 deve ser do tipo string' \
                                        ''
        assert sentido == 1 or sentido == 0, 'O parâmetro sentido deve ser um inteiro de valor 1 ou 0'

        caminho, indice = self._busca_prof(n1, retorna_array=True)
        prof = int(caminho[0][0])

        for i in range(indice, -1, -1):
            prox = self.rnp[:, i]
            prox = reshape(prox, (2, 1))
            if int(prox[0, 0]) < prof:
                prof -= 1
                caminho = concatenate((caminho, prox), axis=1)
                if prox[1][0] == n2:
                    break
        else:
            n1, n2 = n2, n1

            caminho, indice = self._busca_prof(n1, retorna_array=True)
            prof = int(caminho[0][0])

            for i in range(indice, -1, -1):
                prox = self.rnp[:, i]
                prox = reshape(prox, (2, 1))
                if int(prox[0, 0]) < prof:
                    prof -= 1
                    caminho = concatenate((caminho, prox), axis=1)
                    if prox[1][0] == n2:
                        break
            else:
                # raise AttributeError('Os nós n1 e n2
                # não pertencem ao mesmo ramo!')
                a1 = self.caminho_no_para_raiz(n2, sentido=1)
                a2 = self.caminho_no_para_raiz(n1, sentido=0)

                list_nos_comuns = [i for i in a2[1, :] if i in a1[1, :]]
                prof_no_comum = 0
                for no in a1.transpose():
                    if no[1] in list_nos_comuns:
                        if no[0] > prof_no_comum:
                            prof_no_comum = no[0]
                            no_comum = no[1]

                indice_no_comum = where(a1[1, :] == no_comum)[0][0]

                a1 = a1[:, :indice_no_comum + 1]

                indice_no_comum = where(a2[1, :] == no_comum)[0][0]
                a2 = a2[:, indice_no_comum + 1:]

                return concatenate((a1, a2), axis=1)

        if sentido == 1:
            return caminho
        else:
            return caminho[:, range(size(caminho, axis=1) - 1, -1, -1)]


class Floresta(object):
    """
    Classe Floresta
    ---------------
    documentacao classe Floresta
    """

    def __init__(self, floresta):
        assert isinstance(floresta, list)
        pass


if __name__ == '__main__':
    # arvore 1
    nos1 = {3: [1],
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

    # arvore 2
    nos2 = {14: [15],
            15: [14, 16, 19],
            16: [15, 17, 18],
            17: [16],
            18: [16],
            19: [15]}

    # definição da arvore a1
    arv_1 = Arvore(nos1)

    # ordenação da arvore a1
    arv_1.ordenar(raiz=3)
    print('Representação RNP da arvore 1')
    print(arv_1.rnp)

    # definição da arvore a2
    arv_2 = Arvore(nos2)

    # ordenação da arvore a2
    arv_2.ordenar(raiz=14)

    print('Representação RNP da arvore 2')
    print(arv_2.rnp)

    # operação de poda
    poda = arv_1.podar(7, alterar_rnp=True)
    print('Ramo Podado da arvore 1')
    print(poda)

    print('Representação RNP da arvore 1 depois da poda')
    print(arv_1.rnp)

    # operação de inserção
    arv_2.inserir_ramo(19, poda, 7)

    print('Representação RNP da arvore 2 depois da inserção do ramo podado da arvore 1')
    print(arv_2.rnp)