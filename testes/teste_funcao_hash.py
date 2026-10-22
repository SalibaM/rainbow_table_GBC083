"""Testes do Passo 2: funcao de hash meu_hash (SHA-256 + prefixo GBC083)."""

import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

from funcao_hash import meu_hash


def test_vetor_do_slide():
    # Slide 47: echo -n GBC0831234 | sha256sum
    esperado = "5042f15f93d4f75df9cdff09d062d607eaa0140a930b9023c43ca7cc58609b8f"
    assert meu_hash("1234") == esperado


def test_formato_hexdigest():
    h = meu_hash("qualquer coisa")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)


def test_determinismo():
    assert meu_hash("cleft cam") == meu_hash("cleft cam")


def test_sensibilidade():
    assert meu_hash("1234") != meu_hash("1235")
    import hashlib
    sha_puro = hashlib.sha256(b"1234").hexdigest()
    assert meu_hash("1234") != sha_puro


if __name__ == "__main__":
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_"):
            funcao()
            print(f"OK  {nome}")
    print("Todos os testes passaram.")
