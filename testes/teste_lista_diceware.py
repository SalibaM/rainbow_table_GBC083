"""Testes do Passo 1: carregamento da lista Diceware e ponte indice<->senha."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from lista_diceware import (
    TAMANHO_ALFABETO,
    TAMANHO_ESPACO,
    carregar_palavras,
    indice_para_senha,
    senha_para_indice,
)

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")
PALAVRAS = carregar_palavras(CAMINHO_LISTA)


def test_contagem():
    # A lista tem que ter exatamente 7776 palavras
    assert len(PALAVRAS) == TAMANHO_ALFABETO == 7776


def test_indices_conhecidos():
    # Conferidos direto no arquivo .asc
    assert PALAVRAS[0] == "a"       # 11111
    assert PALAVRAS[1] == "a&p"     # 11112
    assert PALAVRAS[6] == "aaron"   # 11121
    assert PALAVRAS[-1] == "@"      # 66666


def test_formato_senha():
    assert indice_para_senha(6 * TAMANHO_ALFABETO + 6, PALAVRAS) == "aaron aaron"
    # Primeira e ultima senha do espaco
    assert indice_para_senha(0, PALAVRAS) == "a a"
    assert indice_para_senha(TAMANHO_ESPACO - 1, PALAVRAS) == "@ @"


def test_round_trip():
    for n in [0, 1, 7775, 7776, 123456, TAMANHO_ESPACO - 1]:
        senha = indice_para_senha(n, PALAVRAS)
        assert senha_para_indice(senha, PALAVRAS) == n


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
