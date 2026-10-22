"""Testes do Passo 3: funcao de reducao reduzir(h, coluna) e as cores."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from lista_diceware import TAMANHO_ALFABETO, carregar_palavras, senha_para_indice
from funcao_hash import meu_hash
from reducao import reduzir

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")
PALAVRAS = carregar_palavras(CAMINHO_LISTA)


def test_saida_e_senha_valida():
    for entrada in ["1234", "cleft cam", "abc", "senha teste", "xyz"]:
        h = meu_hash(entrada)
        senha = reduzir(h, 0, PALAVRAS)
        assert len(senha.split(" ")) == 2
        idx = senha_para_indice(senha, PALAVRAS)  # so nao explode se for valida
        assert 0 <= idx < TAMANHO_ALFABETO ** 2


def test_cores_diferentes_dao_senhas_diferentes():
    h = meu_hash("1234")
    senhas = {reduzir(h, coluna, PALAVRAS) for coluna in range(50)}
    assert len(senhas) == 50   # as 50 cores deram 50 senhas distintas


def test_determinismo():
    h = meu_hash("mustang")
    assert reduzir(h, 7, PALAVRAS) == reduzir(h, 7, PALAVRAS)


def test_relacao_com_a_formula():
    from lista_diceware import TAMANHO_ESPACO, indice_para_senha
    h = meu_hash("abc")
    coluna = 3
    n_esperado = (int(h, 16) + coluna) % TAMANHO_ESPACO
    assert reduzir(h, coluna, PALAVRAS) == indice_para_senha(n_esperado, PALAVRAS)


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
