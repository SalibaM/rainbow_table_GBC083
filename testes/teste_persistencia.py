"""Testes do Passo 7: salvar/carregar a tabela (round-trip em disco)."""

import os
import random
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from lista_diceware import carregar_palavras
from funcao_hash import meu_hash
from reducao import reduzir
from tabela import construir_tabela, quebrar, salvar, carregar

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")
PALAVRAS = carregar_palavras(CAMINHO_LISTA)


def _arquivo_temp():
    descritor, caminho = tempfile.mkstemp(suffix=".csv")
    os.close(descritor)
    return caminho


def test_round_trip_identico():
    tabela = construir_tabela(150, 25, PALAVRAS, semente=4)
    caminho = _arquivo_temp()
    try:
        salvar(tabela, caminho)
        recarregada = carregar(caminho)
        assert recarregada == tabela
    finally:
        os.remove(caminho)


def test_quebra_igual_antes_e_depois():
    largura = 30
    tabela = construir_tabela(100, largura, PALAVRAS, semente=6)
    fim, inicio = next(iter(tabela.items()))
    senha = inicio
    for coluna in range(largura // 2):
        senha = reduzir(meu_hash(senha), coluna, PALAVRAS)
    h = meu_hash(senha)
    antes = quebrar(h, tabela, largura, PALAVRAS)

    caminho = _arquivo_temp()
    try:
        salvar(tabela, caminho)
        recarregada = carregar(caminho)
    finally:
        os.remove(caminho)
    depois = quebrar(h, recarregada, largura, PALAVRAS)

    assert antes is not None
    assert antes == depois


def test_arquivo_tem_cabecalho_e_linhas():
    tabela = construir_tabela(20, 10, PALAVRAS, semente=0)
    caminho = _arquivo_temp()
    try:
        salvar(tabela, caminho)
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [linha.rstrip("\n") for linha in f]
    finally:
        os.remove(caminho)
    assert linhas[0] == "inicio,fim"
    assert len(linhas) == len(tabela) + 1      # +1 do cabecalho


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
