"""Funcao de hash do trabalho (dada pelo professor, slide 47)."""

import hashlib

PREFIXO = b"GBC083"


def meu_hash(s):
    """Recebe uma senha (str) e devolve o hash como string hexadecimal (64 chars)."""
    objeto_hash = hashlib.sha256()
    objeto_hash.update(PREFIXO)
    objeto_hash.update(s.encode("utf-8"))
    return objeto_hash.hexdigest()
