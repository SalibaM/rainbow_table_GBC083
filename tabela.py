"""A rainbow table inteira -- varias cadeias (o Passo 6)."""

import csv
import random

from cadeia import construir_cadeia
from funcao_hash import meu_hash
from reducao import reduzir


def construir_tabela(altura, largura, palavras, semente=0, _hash=meu_hash, _reduzir=reduzir):
    """Constroi uma rainbow table com ~'altura' cadeias de largura 'largura'."""
    sorteador = random.Random(semente)     # gerador proprio, nao mexe no global
    tabela = {}
    for _ in range(altura):
        indice_inicio = sorteador.randrange(len(palavras) ** 2)   # inicio em [0, N)
        inicio, fim = construir_cadeia(indice_inicio, largura, palavras,
                                      _hash=_hash, _reduzir=_reduzir)
        tabela[fim] = inicio               # chave repetida (mescla) -> sobrescreve
    return tabela


def quebrar(h_alvo, tabela, largura, palavras, _hash=meu_hash, _reduzir=reduzir):
    """Tenta quebrar o hash h_alvo usando a tabela inteira."""
    for k in range(largura - 1, -1, -1):
        senha = _reduzir(h_alvo, k, palavras)          # seria P_{k+1}
        for coluna in range(k + 1, largura):
            senha = _reduzir(_hash(senha), coluna, palavras)
        candidato_fim = senha

        inicio = tabela.get(candidato_fim)
        if inicio is None:
            continue                                   # ninguem termina ai; proxima coluna

        candidata = inicio
        for coluna in range(k):
            candidata = _reduzir(_hash(candidata), coluna, palavras)

        if _hash(candidata) == h_alvo:
            return candidata

    return None                                        # nao foi coberta por esta tabela


CABECALHO = ["inicio", "fim"]


def salvar(tabela, caminho):
    """Grava a tabela em CSV (uma cadeia por linha: inicio, fim)."""
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(CABECALHO)
        for fim, inicio in tabela.items():
            escritor.writerow([inicio, fim])


def carregar(caminho):
    """Le o CSV gerado por salvar() e devolve o dict { fim: inicio }."""
    tabela = {}
    with open(caminho, "r", newline="", encoding="utf-8") as arquivo:
        leitor = csv.reader(arquivo)
        next(leitor, None)                 # pula o cabecalho
        for inicio, fim in leitor:
            tabela[fim] = inicio
    return tabela
