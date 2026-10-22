"""Testes do Passo 5: buscar_na_cadeia -- procurar um hash dentro de UMA cadeia."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from lista_diceware import (
    TAMANHO_ESPACO,
    carregar_palavras,
    indice_para_senha,
    senha_para_indice,
)
from funcao_hash import meu_hash
from reducao import reduzir
from cadeia import construir_cadeia, buscar_na_cadeia

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")
PALAVRAS = carregar_palavras(CAMINHO_LISTA)

INICIO_IDX = 0      # senha inicial "a a"
LARGURA = 6


def _senhas_da_cadeia(indice_inicio, largura):
    """Refaz a cadeia e devolve [P0, P1, ..., P_W]."""
    senha = indice_para_senha(indice_inicio, PALAVRAS)
    senhas = [senha]
    for coluna in range(largura):
        senha = reduzir(meu_hash(senha), coluna, PALAVRAS)
        senhas.append(senha)
    return senhas


SENHAS = _senhas_da_cadeia(INICIO_IDX, LARGURA)


def test_encontra_no_inicio():
    h = meu_hash(SENHAS[0])
    achada = buscar_na_cadeia(h, INICIO_IDX, LARGURA, PALAVRAS)
    assert achada is not None
    assert meu_hash(achada) == h


def test_encontra_no_meio():
    # Hash de uma senha do meio (coluna 3).
    h = meu_hash(SENHAS[3])
    achada = buscar_na_cadeia(h, INICIO_IDX, LARGURA, PALAVRAS)
    assert achada is not None
    assert meu_hash(achada) == h


def test_encontra_na_ultima_coluna():
    h = meu_hash(SENHAS[LARGURA - 1])
    achada = buscar_na_cadeia(h, INICIO_IDX, LARGURA, PALAVRAS)
    assert achada is not None
    assert meu_hash(achada) == h


def test_senha_fora_da_cadeia_retorna_none():
    indices_na_cadeia = {senha_para_indice(s, PALAVRAS) for s in SENHAS}
    idx_fora = next(i for i in range(10_000) if i not in indices_na_cadeia)
    h = meu_hash(indice_para_senha(idx_fora, PALAVRAS))
    assert buscar_na_cadeia(h, INICIO_IDX, LARGURA, PALAVRAS) is None


def test_falso_alarme_e_rejeitado():
    _, fim = construir_cadeia(INICIO_IDX, LARGURA, PALAVRAS)
    idx_fim = senha_para_indice(fim, PALAVRAS)
    valor = (idx_fim - (LARGURA - 1)) % TAMANHO_ESPACO
    h_falso = f"{valor:064x}"                 # hash sintetico de 64 digitos hex

    assert reduzir(h_falso, LARGURA - 1, PALAVRAS) == fim
    assert buscar_na_cadeia(h_falso, INICIO_IDX, LARGURA, PALAVRAS) is None


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
