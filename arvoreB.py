# TRABALHO ÁRVORE-B
# ALUNO: JOSÉ HENRIQUE HERNANDES CARDOSO
# RA: 143470

from __future__ import annotations
from dataclasses import dataclass
from io import BufferedReader, BufferedWriter, BufferedRandom
from struct import pack, unpack, calcsize
from math import ceil as arredonda_cima, floor as arredonda_baixo

# CONSTANTES
NOME_ARQ_ARVORE = 'btree.dat'
NOME_ARQ_DADOS = 'games.dat'

ORDEM_ARVORE = 6
RRN_INVALIDO = -1

# formato das páginas: pares ID-Offset | RRNs descendentes
ID_FORMAT = 'i'
OFFSET_FORMAT = 'l'
RRN_FORMAT = 'i'

# DEFINIÇÃO DE TIPOS
Id = int
Offset = int
Rrn = int

@dataclass
class ParIdOffset:
    '''Relaciona um ID a um offset de um arquivo'''
    id: Id
    offset: Offset

CHAVE_INVALIDA = ParIdOffset(-1 , -1)

@dataclass
class RetornoBuscaPag:
    '''Dados de retorno após uma busca em uma página'''
    achou: bool
    pos: int

@dataclass
class RetornoInsercao:
    '''Dados de retorno após uma inserção na árvore-B'''
    chave_promo: ParIdOffset
    filho_dir_promo: Rrn

@dataclass
class RetornoDivisao:
    '''Dados de retorno após uma divisão de uma página na árvore-B'''
    chave_promo: ParIdOffset
    filho_dir_promo: Rrn
    nova_pag: Pagina

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
    chaves: list[ParIdOffset]
    descendentes: list[Rrn]

    num_chaves: int
    max_descendentes: int
    max_chaves: int

    def __init__(self, ordem: int):
        '''
        Inicia uma nova página vazia.

        :param ordem: ordem da página
        '''
        self.max_descendentes = ordem
        self.max_chaves = ordem - 1
        self.num_chaves = 0

        self.chaves = [CHAVE_INVALIDA] * self.max_chaves
        self.descendentes = [RRN_INVALIDO] * self.max_descendentes


    def carrega_dados(self, format: str, dados_binario: bytes):
        '''
        Extrai os dados de uma página de uma cadeia binária para a página.

        :param format: Formato da decodificação seguindo o padrão da biblioteca struct.
        :param dados_binario: Cadeia binária com as informações da página.
        '''
        dados = unpack(format, dados_binario)
        
        i_dados = 0
        # Carrega IDs e offsets
        i_chaves = 0
        while i_chaves < self.max_chaves:
            self.chaves[i_chaves] = ParIdOffset(dados[i_dados], dados[i_dados + 1])
            if dados[i_dados] != -1:
                self.num_chaves += 1

            i_chaves += 1
            i_dados += 2
        
        # Carrega RRNs dos descendentes
        i_desc = 0
        while i_desc < self.max_descendentes:
            self.descendentes[i_desc] = dados[i_dados]
            i_desc += 1
            i_dados += 1

    def codifica_dados(self, format: str) -> bytes:
        '''
        Codifica os dados da página em bytes de acordo com o formato especificado.

        :param format: Formato da codificação seguindo o padrão da biblioteca struct.
                       Requer que ele seja suficiente para codificar todos os dados.
        '''
        dados = []
        # Separa IDs dos offsets
        for chave in self.chaves:
            dados.append(chave.id)
            dados.append(chave.offset)
        
        dados += self.descendentes
        return pack(format, *dados)
    
    def busca(self, id: Id) -> RetornoBuscaPag:
        '''
        Busca uma chave na página.

        :param id: ID da chave buscada.
        :return: Inidica se encontrou o elemento e a posição do elemento. Se não
                 encontrou, a posição aponta para o descendente onde o elemento
                 pode estar.
        '''
        i = 0
        while i < self.num_chaves and id > self.chaves[i].id:
            i += 1

        if i < self.num_chaves and id == self.chaves[i].id:
            return RetornoBuscaPag(True, i) 
        else:
            return RetornoBuscaPag(False, i)
            

    def insere(self, chave: ParIdOffset, descendente: Rrn):
        '''
        Insere uma nova chave na página

        :param chave: Nova chave a ser inserida.
        :param descendente: Descendente a direita da chave
        '''
        if self.cheia():
            self.chaves.append(CHAVE_INVALIDA)
            self.descendentes.append(RRN_INVALIDO)
        
        i = self.num_chaves
        while i > 0 and chave.id < self.chaves[i-1].id:
            self.chaves[i] = self.chaves[i-1]
            self.descendentes[i+1] = self.descendentes[i]
            i -= 1
        
        self.chaves[i] = chave
        self.descendentes[i+1] = descendente
        self.num_chaves += 1
    
    def eh_folha(self) -> bool:
        '''
        Retorna True se a página é folha. False, caso contrário.
        '''
        for desc in self.descendentes:
            if desc != RRN_INVALIDO:
                return False
        return True

    def cheia(self) -> bool:
        '''
        Retorna True se a página está cheia. False caso contrário.
        '''
        return self.num_chaves >= self.max_chaves

class ArvoreB:
    '''
    Uma árvore-B de ordem n.

    As chaves da árvore são IDs que se relacionam
    a offsets de um arquivo de registros.
    '''

    arquivo: BufferedRandom
    cabecalho_fmt: str # Ordem, num páginas, RRN da raiz
    tam_cabecalho_fmt: int

    pagina_fmt: str
    tam_pagina_fmt: int

    ordem: int
    num_paginas: int
    rrn_raiz: Rrn

    def __init__(self, arquivo: BufferedRandom, ordem: int, carrega_dados: bool):
        '''
        Inicia uma árvore-B vazia relacionada a um arquivo.

        :param ordem: Ordem da árvore-B.
        :param arquivo: Arquivo relacionado a árvore-B.
        :param carrega_dados: Se True, carrega os dados do arquivo (considera a ordem no arquivo).
                              Se False, apaga os dados do arquivo e inicia uma nova árvore vazia.
        '''
        self.arquivo = arquivo
        self.cabecalho_fmt = 'ii' + RRN_FORMAT
        self.tam_cabecalho_fmt = calcsize(self.cabecalho_fmt)

        self.ordem = ordem
        self.pagina_fmt = (ID_FORMAT + OFFSET_FORMAT)*(self.ordem-1) + RRN_FORMAT*self.ordem
        self.tam_pagina_fmt = calcsize(self.pagina_fmt)

        if carrega_dados:
            self.carrega_dados()
            # Atualiza o format para a nova ordem lida do arquivo
            self.pagina_fmt = (ID_FORMAT + OFFSET_FORMAT)*(self.ordem-1) + RRN_FORMAT*self.ordem
            self.tam_pagina_fmt = calcsize(self.pagina_fmt)
        else:
            self.arquivo.truncate(0) # apaga dados do arquivo
            # Cria página inicial vazia
            raiz = Pagina(ordem)
            self.escreve_pagina(raiz, 0)
            self.rrn_raiz = 0
            self.num_paginas = 1

        

    def carrega_dados(self):
        '''
        Carrega as informações do arquivo para a árvore-B.
        '''
        # carrega a ordem, num_paginas e rrn_raiz do cabeçalho
        tam_format = calcsize(self.cabecalho_fmt)
        dados_binario = self.arquivo.read(tam_format)
        dados = unpack(self.cabecalho_fmt, dados_binario)

        self.ordem = dados[0]
        self.num_paginas = dados[1]
        self.rrn_raiz = dados[2]
    
    def escreve_arvore(self):
        '''
        Salva os dados da árvore no cabeçalho do arquivo.
        '''
        cabecalho = (self.ordem, self.num_paginas, self.rrn_raiz)
        cabecalho_bytes = pack(self.cabecalho_fmt, *cabecalho)
        self.arquivo.seek(0)
        self.arquivo.write(cabecalho_bytes)

    def carrega_pag(self, rrn: Rrn) -> Pagina:
        '''
        Carrega uma página pra memória.

        :param rrn: RRN da página a ser carregada.
        :return: Pagina com os dados carregados.
        '''
        self.arquivo.seek(self.tam_cabecalho_fmt + self.tam_pagina_fmt*rrn)
        dados_binario = self.arquivo.read(self.tam_pagina_fmt)

        pagina = Pagina(self.ordem)
        pagina.carrega_dados(self.pagina_fmt, dados_binario)
        return pagina
    
    def escreve_pagina(self, pagina: Pagina, rrn: Rrn):
        '''
        Escreve uma página no arquivo da árvore-B.

        :param pagina: Página a ser escrita.
        :param rrn: RRN onde a página será escrita.
        '''
        codificado = pagina.codifica_dados(self.pagina_fmt)

        self.arquivo.seek(self.tam_cabecalho_fmt + self.tam_pagina_fmt*rrn)
        self.arquivo.write(codificado)

    def divide_pagina(self, pagina: Pagina, chave: ParIdOffset, desc_dir: Rrn) -> RetornoDivisao:
        '''
        Realiza o processo de divisão de uma página.
        A página é atualizada com os novos dados ao final do processo.

        :param pagina: Página que será dividia.
        :param chave: Chave que será inserida no processo da divisão.
        :param filho_dir: Filho a direita da chave que será inserida.
        '''
        # Como página deve estar cheia, insere cria um campo de
        # chave a mais que deve ser removido ao final.
        pagina.insere(chave, desc_dir)
        meio = self.ordem // 2
        chave_promo = pagina.chaves[meio]
        filho_dir_promo = self.num_paginas

        nova_pag = Pagina(self.ordem)
        # Remove elemento do meio e move descentente a esquerda para nova pagina
        pagina.chaves[meio] = CHAVE_INVALIDA
        nova_pag.descendentes[0] = pagina.descendentes[meio+1]
        pagina.descendentes[meio+1] = RRN_INVALIDO
        # Move elementos pra frente do meio para a nova pagina
        i_pag = meio + 1
        while i_pag < pagina.num_chaves:
            nova_pag.insere(pagina.chaves[i_pag], pagina.descendentes[i_pag+1])
            pagina.chaves[i_pag] = CHAVE_INVALIDA
            pagina.descendentes[i_pag+1] = RRN_INVALIDO

            i_pag += 1
        
        # Corrige num_chaves das páginas
        pagina.num_chaves = arredonda_cima((self.ordem - 1)/2)
        nova_pag.num_chaves = arredonda_baixo((self.ordem - 1)/2)
        # Remove elemento extra da inserção
        pagina.chaves.pop()
        pagina.descendentes.pop()

        self.num_paginas += 1
        return RetornoDivisao(chave_promo, filho_dir_promo, nova_pag)

    def insere_na_arvore(self, chave: ParIdOffset, rrn: Rrn) -> RetornoInsercao:
        '''
        Insere uma chave em uma página da árvore.

        :param chave: Chave a ser inserida.
        :param rrn: RRN da página.
        :returns: Dados da promoção (se a chave for inválida, não houve).

        :raises ElementoRepetidoException: Se o id fornecido já estiver na página.
        '''
        if rrn == RRN_INVALIDO:
            return RetornoInsercao(chave, RRN_INVALIDO)
        
        pagina = self.carrega_pag(rrn)
        res_busca = pagina.busca(chave.id)

        if res_busca.achou:
            raise ElementoRepetidoException
        
        res_insercao = self.insere_na_arvore(chave, pagina.descendentes[res_busca.pos])
        if res_insercao.chave_promo == CHAVE_INVALIDA:
            return RetornoInsercao(CHAVE_INVALIDA, RRN_INVALIDO)
        
        elif not pagina.cheia():
            pagina.insere(res_insercao.chave_promo, res_insercao.filho_dir_promo)
            self.escreve_pagina(pagina, rrn)
            return RetornoInsercao(CHAVE_INVALIDA, RRN_INVALIDO)
        else:
            res_divisao = self.divide_pagina(pagina, res_insercao.chave_promo,
                                          res_insercao.filho_dir_promo)
            self.escreve_pagina(pagina, rrn)
            self.escreve_pagina(res_divisao.nova_pag, res_divisao.filho_dir_promo)
            return RetornoInsercao(res_divisao.chave_promo, res_divisao.filho_dir_promo)

    def insere(self, id: Id, offset: Offset):
        '''
        Insere uma nova chave (id) com seu valor (offset) na árvore.

        :param id: Nova chave a ser inserida.
        :param offset: Valor relacionado a chave.

        :raises ElementoRepetidoException: Se o id fornecido já estiver na árvore.
        '''
        res_insere = self.insere_na_arvore(ParIdOffset(id, offset), self.rrn_raiz)

        if res_insere.chave_promo != CHAVE_INVALIDA:
            nova_raiz = Pagina(self.ordem)
            nova_raiz.descendentes[0] = self.rrn_raiz
            nova_raiz.insere(res_insere.chave_promo, res_insere.filho_dir_promo)

            rrn_nova_raiz = self.num_paginas
            self.escreve_pagina(nova_raiz, rrn_nova_raiz)
            self.rrn_raiz = rrn_nova_raiz
            self.num_paginas += 1
        
    def exibe_arvore(self):
        '''
        Exibe a árvore na tela.
        '''
        for i in range(self.num_paginas):
            pagina = self.carrega_pag(i)
            ids = []
            offsets = []
            for chave in pagina.chaves:
                ids.append(chave.id)
                offsets.append(chave.offset)
            if i == self.rrn_raiz: print('-='*14 + " RAIZ " + "-="*14)
            print(f"PAGINA {i}:")
            print("      CHAVES = " + " | ".join(f"{c:>5}" for c in ids)) 
            print("     OFFSETS = " + " | ".join(f"{o:>5}" for o in offsets))
            print("DESCENDENTES = " + " | ".join(f"{d:>5}" for d in pagina.descendentes))
            if i == self.rrn_raiz: print('-='*31)
            print("\n")


# CARREGA INDICES PARA A ÁRVORE-B
def carrega_indice(arvore_b: ArvoreB, nome_arq_dados: str):
    '''
    Carrega os indices de um arquivo de registros para uma árvore-B.

    :param arvore_b: Arvore que receberá o indice.
    :param nome_arq_dados: Nome do arquivo de dados com os registros.
    '''
    with open(nome_arq_dados, 'br') as dados:
        offset: Offset = 0
        tam_registro_bytes = dados.read(2)

        while tam_registro_bytes:
            tam_registro = int.from_bytes(tam_registro_bytes, 'little')

            registro_string = dados.read(tam_registro).decode()
            id_registro = int(registro_string.split('|')[0])

            arvore_b.insere(id_registro, offset)

            offset += 2 + tam_registro
            tam_registro_bytes = dados.read(2)
        

def main():
    with open(NOME_ARQ_ARVORE, 'r+b') as arq_arvore:
        arvore_b = ArvoreB(arq_arvore, ORDEM_ARVORE, carrega_dados=False)

        carrega_indice(arvore_b, NOME_ARQ_DADOS)
        arvore_b.exibe_arvore()

    

if __name__ == "__main__":
    main()