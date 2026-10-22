"""Carrega a lista Diceware (Reinhold) e faz a ponte entre:"""

import re


TAMANHO_ALFABETO = 7776            # numero de palavras na lista Diceware
PALAVRAS_POR_SENHA = 2             # senhas "pequenas": 2 palavras
TAMANHO_ESPACO = TAMANHO_ALFABETO ** PALAVRAS_POR_SENHA   # 60.466.176
SEPARADOR = " "                    # como as palavras sao juntadas numa senha

_LINHA_PALAVRA = re.compile(r"^\d{5}\s+(\S+)\s*$")


def carregar_palavras(caminho):
    """Le o arquivo .asc do Diceware e devolve a lista das 7776 palavras, na ordem do arquivo (indice 11111 -> posicao 0, ..."""
    palavras = []
    with open(caminho, encoding="utf-8") as arquivo:
        for linha in arquivo:
            casamento = _LINHA_PALAVRA.match(linha)
            if casamento:
                palavras.append(casamento.group(1))

    if len(palavras) != TAMANHO_ALFABETO:   # se nao carregou 7776 palavras, deu errado
        raise ValueError(
            f"Esperava {TAMANHO_ALFABETO} palavras, li {len(palavras)}."
        )
    if len(set(palavras)) != TAMANHO_ALFABETO:   # se tiver alguma repetida, tambem esta errado
        raise ValueError("A lista tem palavras repetidas.")

    return palavras


def indice_para_senha(n, palavras):
    """Converte um indice n (0 <= n < TAMANHO_ESPACO) na senha correspondente."""
    if not (0 <= n < TAMANHO_ESPACO):
        raise ValueError(f"indice fora do espaco: {n}")
    i, j = divmod(n, TAMANHO_ALFABETO)
    return palavras[i] + SEPARADOR + palavras[j]


def senha_para_indice(senha, palavras):
    """Operacao inversa de indice_para_senha: dada a senha "p1 p2", devolve o indice numerico n daquele par dentro do espaco de 60.466.176 senhas."""
    partes = senha.split(SEPARADOR)
    if len(partes) != PALAVRAS_POR_SENHA:
        raise ValueError(f"senha nao tem {PALAVRAS_POR_SENHA} palavras: {senha!r}")
    p1, p2 = partes
    i = palavras.index(p1)   # ValueError se a palavra nao existir na lista
    j = palavras.index(p2)
    return i * TAMANHO_ALFABETO + j
