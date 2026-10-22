"""Uma CADEIA da rainbow table -- uma "linha" da tabela."""

from lista_diceware import indice_para_senha
from funcao_hash import meu_hash
from reducao import reduzir


def construir_cadeia(indice_inicio, largura, palavras, _hash=meu_hash, _reduzir=reduzir):
    """Constroi a cadeia que comeca no indice 'indice_inicio' e aplica 'largura' reducoes."""
    inicio = indice_para_senha(indice_inicio, palavras)
    senha = inicio
    for coluna in range(largura):          # coluna 0, 1, ..., largura-1
        h = _hash(senha)                   # H: senha -> hash
        senha = _reduzir(h, coluna, palavras)  # R com a cor da coluna: hash -> proxima senha
    return inicio, senha                   # (inicio=P0, fim=PW)


def buscar_na_cadeia(h_alvo, indice_inicio, largura, palavras):
    """Procura, DENTRO desta unica cadeia, a senha cujo hash e h_alvo."""
    inicio, fim = construir_cadeia(indice_inicio, largura, palavras)

    for k in range(largura - 1, -1, -1):
        senha = reduzir(h_alvo, k, palavras)        # seria P_{k+1}
        for coluna in range(k + 1, largura):
            h = meu_hash(senha)
            senha = reduzir(h, coluna, palavras)
        if senha != fim:
            continue                                # hipotese falhou; proxima coluna

        candidata = inicio
        for coluna in range(k):                     # aplica as colunas 0..k-1
            h = meu_hash(candidata)
            candidata = reduzir(h, coluna, palavras)

        if meu_hash(candidata) == h_alvo:
            return candidata

    return None                                     # nao esta nesta cadeia
