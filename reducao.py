"""Funcao de reducao R -- o "R" das cadeias da rainbow table."""

from lista_diceware import TAMANHO_ESPACO, indice_para_senha


def reduzir(h, coluna, palavras):
    """Reduz o hash hexadecimal h (str) a uma senha, usando a "cor" da coluna."""
    valor = int(h, 16)
    n = (valor + coluna) % TAMANHO_ESPACO    # dobra para dentro do espaco; +coluna = cor
    return indice_para_senha(n, palavras)
