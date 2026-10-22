"""Demonstracao didatica: constroi UMA cadeia e imprime cada passo (senha -> hash -> senha -> hash -> ...), para ver a mecanica funcionando."""

import os
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, RAIZ)

from lista_diceware import carregar_palavras, indice_para_senha
from funcao_hash import meu_hash
from reducao import reduzir
from cadeia import construir_cadeia

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")


def hash_curto(h):
    """Encurta o hash so para a impressao ficar legivel (nao muda a conta)."""
    return h[:12] + "..." + h[-6:]


def main():
    palavras = carregar_palavras(CAMINHO_LISTA)

    indice_inicio = 0      # senha inicial "a a"
    largura = 6            # 6 reducoes -> cadeia curtinha, facil de acompanhar

    inicio = indice_para_senha(indice_inicio, palavras)
    print(f"Cadeia a partir do indice {indice_inicio}  (inicio = {inicio!r}), largura = {largura}")
    print("-" * 70)

    senha = inicio
    for coluna in range(largura):
        h = meu_hash(senha)                     # H: senha -> hash
        prox = reduzir(h, coluna, palavras)     # R com a cor da coluna
        print(f"coluna {coluna}:  {senha!r:>18}  --H-->  {hash_curto(h)}  --R{coluna}-->  {prox!r}")
        senha = prox

    print("-" * 70)
    print(f"fim da cadeia = {senha!r}")

    _, fim_funcao = construir_cadeia(indice_inicio, largura, palavras)
    print(f"construir_cadeia devolveu: inicio={inicio!r}, fim={fim_funcao!r}")
    assert senha == fim_funcao, "divergencia entre o demo e construir_cadeia!"
    print("OK: o demo e construir_cadeia concordam.")


if __name__ == "__main__":
    main()
