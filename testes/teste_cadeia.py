"""Testes do Passo 4: construir_cadeia -- uma linha da rainbow table."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from lista_diceware import carregar_palavras, indice_para_senha
from funcao_hash import meu_hash
from reducao import reduzir
from cadeia import construir_cadeia

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")
PALAVRAS = carregar_palavras(CAMINHO_LISTA)


def test_inicio_e_a_senha_do_indice():
    inicio, _ = construir_cadeia(0, 6, PALAVRAS)
    assert inicio == indice_para_senha(0, PALAVRAS)   # indice 0 -> "a a"


def test_largura_zero_nao_reduz():
    inicio, fim = construir_cadeia(123, 0, PALAVRAS)
    assert inicio == fim == indice_para_senha(123, PALAVRAS)


def test_determinismo():
    assert construir_cadeia(5000, 10, PALAVRAS) == construir_cadeia(5000, 10, PALAVRAS)


def test_bate_com_reconstrucao_manual():
    indice_inicio, largura = 777, 8
    senha = indice_para_senha(indice_inicio, PALAVRAS)
    for coluna in range(largura):
        h = meu_hash(senha)
        senha = reduzir(h, coluna, PALAVRAS)
    _, fim = construir_cadeia(indice_inicio, largura, PALAVRAS)
    assert senha == fim


def test_largura_muda_o_fim():
    _, fim5 = construir_cadeia(42, 5, PALAVRAS)
    _, fim6 = construir_cadeia(42, 6, PALAVRAS)
    assert fim5 != fim6


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
