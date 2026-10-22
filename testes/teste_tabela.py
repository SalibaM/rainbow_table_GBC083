"""Testes do Passo 6: construir_tabela + quebrar (a tabela inteira)."""

import os
import random
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from lista_diceware import carregar_palavras
from funcao_hash import meu_hash
from reducao import reduzir
from tabela import construir_tabela, quebrar

CAMINHO_LISTA = os.path.join(RAIZ, "dados", "lista_diceware.asc")
PALAVRAS = carregar_palavras(CAMINHO_LISTA)


def _refaz_cadeia(inicio, largura):
    """Reconstroi [P0, P1, ..., P_W] a partir da senha de inicio."""
    senha = inicio
    senhas = [senha]
    for coluna in range(largura):
        senha = reduzir(meu_hash(senha), coluna, PALAVRAS)
        senhas.append(senha)
    return senhas


def test_determinismo_semente():
    a = construir_tabela(100, 20, PALAVRAS, semente=7)
    b = construir_tabela(100, 20, PALAVRAS, semente=7)
    assert a == b
    c = construir_tabela(100, 20, PALAVRAS, semente=8)
    assert a != c


def test_dedup_nunca_passa_da_altura():
    # fica menor (os fins repetidos colapsam).
    altura = 200
    tabela = construir_tabela(altura, 30, PALAVRAS, semente=3)
    assert len(tabela) <= altura


def test_quebra_senha_coberta():
    largura = 30
    tabela = construir_tabela(100, largura, PALAVRAS, semente=1)
    fim, inicio = next(iter(tabela.items()))
    senhas = _refaz_cadeia(inicio, largura)
    assert senhas[largura] == fim           # a reconstrucao bate com o fim guardado
    alvo = senhas[largura // 2]             # uma senha do meio
    h = meu_hash(alvo)
    achada = quebrar(h, tabela, largura, PALAVRAS)
    assert achada is not None
    assert meu_hash(achada) == h


def test_taxa_de_acerto_em_senhas_cobertas():
    largura = 40
    tabela = construir_tabela(300, largura, PALAVRAS, semente=5)
    rng = random.Random(123)
    amostra = rng.sample(list(tabela.items()), min(40, len(tabela)))
    acertos = 0
    for fim, inicio in amostra:
        senhas = _refaz_cadeia(inicio, largura)
        k = rng.randrange(largura)          # coluna com hash (0..largura-1)
        h = meu_hash(senhas[k])
        achada = quebrar(h, tabela, largura, PALAVRAS)
        if achada is not None:
            assert meu_hash(achada) == h    # jamais uma senha errada
            acertos += 1
    taxa = acertos / len(amostra)
    assert taxa == 1.0                      # senhas cobertas pela cadeia-sobrevivente


def test_sem_falso_positivo_em_senhas_aleatorias():
    largura = 30
    tabela = construir_tabela(100, largura, PALAVRAS, semente=2)
    rng = random.Random(999)
    N = len(PALAVRAS) ** 2
    for _ in range(50):
        from lista_diceware import indice_para_senha
        senha = indice_para_senha(rng.randrange(N), PALAVRAS)
        h = meu_hash(senha)
        achada = quebrar(h, tabela, largura, PALAVRAS)
        assert achada is None or meu_hash(achada) == h


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
