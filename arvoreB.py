# TRABALHO ÁRVORE-B
# ALUNO: JOSÉ HENRIQUE HERNANDES CARDOSO
# RA: 143470

from __future__ import annotations

# RENOMEAÇÃO DE TIPOS
Id = int
Offset = int
Rrn = int

# EXCEPTIONS PERSONALIZADAS
class ElementoRepetidoException(Exception):
    pass

# DECLARAÇÃO DE CLASSES
class Pagina:
    '''Uma página de uma árvore B de ordem n'''

    # ID é a chave da página
    chaves: list[dict[Id, Offset]]
    descendentes: list[Rrn]
    eh_raiz: bool

    def __init__(self):
        self.chaves = []
        self.descendentes = []
        self.eh_raiz = False

    def insere(self, id: Id, offset: Offset):
        '''
        Insere uma nova chave (id) com seu valor (offset) na página.

        :param id: Nova chave a ser inserida
        :param offset: Valor relacionado a chave

        :raises ElementoRepetidoException: Se fornecido id já estiver na página
        '''
        raise NotImplementedError
    
    def busca(self, id: Id) -> dict[Id, Offset] | None:
        '''
        Busca um elemento na página.

        :param id: Chave buscada
        :return: Dicionário {id: offset} do elemento ou None se não encontrar
        '''
        raise NotImplementedError