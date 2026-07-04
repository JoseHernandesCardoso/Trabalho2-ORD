# TRABALHO ÁRVORE-B
# ALUNO: JOSÉ HENRIQUE HERNANDES CARDOSO
# RA: 143470

from __future__ import annotations
from math import ceil as arredonda_cima, floor as arredonda_baixo


# DEFINIÇÃO DE TIPOS
Id = int
Offset = int
Rrn = int


# EXCEPTIONS PERSONALIZADAS
class ElementoRepetidoException(Exception):
    pass


# DECLARAÇÃO DE CLASSES
class Pagina:
    '''
    Uma página de uma árvore-B de ordem n.

    As chaves da página são IDs que se relacionam
    a offsets de um arquivo de registros.
    '''

    # ID é a chave da página
    chaves: list[dict[Id, Offset]]
    descendentes: list[Rrn]
    ordem: int

    min_descendentes: int
    max_descendentes: int
    min_chaves: int
    max_chaves: int

    eh_raiz: bool

    def __init__(self, ordem: int):
        self.chaves = []
        self.descendentes = []

        self.ordem = ordem
        self.min_descendentes = arredonda_cima(ordem / 2)
        self.max_descendentes = ordem
        self.min_chaves = arredonda_cima(ordem / 2) - 1
        self.max_chaves = ordem - 1

        self.eh_raiz = False

    def insere(self, id: Id, offset: Offset) -> bool:
        '''
        Insere uma nova chave (id) com seu valor (offset) na página.

        :param id: Nova chave a ser inserida.
        :param offset: Valor relacionado a chave.
        :return: True se conseguiu inserir com sucesso, False se der overflow. 

        :raises ElementoRepetidoException: Se o id fornecido já estiver na página.
        '''
        raise NotImplementedError
    
    def busca(self, id: Id) -> Offset | None:
        '''
        Busca um elemento na página.

        :param id: Chave buscada.
        :return: offset do elemento buscado ou None se não encontrar.
        '''
        raise NotImplementedError


class ArvoreB:
    '''
    Uma árvore-B de ordem n.

    As chaves da árvore são IDs que se relacionam
    a offsets de um arquivo de registros.
    '''

    raiz: Pagina
    ordem: int

    def __init__(self, ordem: int):
        self.raiz = Pagina(ordem)
        self.raiz.eh_raiz = True

    def insere(self, id: Id, offset: Offset):
        '''
        Insere uma nova chave (id) com seu valor (offset) na árvore.

        :param id: Nova chave a ser inserida.
        :param offset: Valor relacionado a chave.

        :raises ElementoRepetidoException: Se o id fornecido já estiver na árvore.
        '''
        raise NotImplementedError
    
    def busca(self, id: Id) -> dict[Id, Offset]:
        '''
        Busca um elemento na árvore.

        :param id: Chave buscada.
        :return: offset do elemento buscado ou None se não encontrar.
        '''
        raise NotImplementedError