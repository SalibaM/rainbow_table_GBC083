"""Experimentos da rainbow table (Passo 8) -- PRIMEIRA PECA."""

import csv
import os
import platform
import random
import tempfile
import time

from lista_diceware import TAMANHO_ESPACO, carregar_palavras, indice_para_senha
from funcao_hash import meu_hash
from reducao import reduzir
from tabela import construir_tabela, quebrar, salvar


# Hardware

def _ram_total_gb():
    """RAM fisica total em GB (melhor esforco; None se nao der para descobrir)."""
    try:
        if os.name == "nt":                       # Windows: GlobalMemoryStatusEx
            import ctypes

            class _MEM(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            estado = _MEM()
            estado.dwLength = ctypes.sizeof(_MEM)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(estado))
            return round(estado.ullTotalPhys / (1024 ** 3), 1)
        # Unix/Mac: paginas * tamanho da pagina
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024 ** 3), 1)
    except Exception:
        return None


def descrever_hardware():
    """Devolve um dict com as caracteristicas da maquina e do interpretador."""
    return {
        "sistema": f"{platform.system()} {platform.release()}",
        "versao_so": platform.version(),
        "processador": platform.processor() or platform.machine(),
        "nucleos_logicos": os.cpu_count(),
        "ram_gb": _ram_total_gb(),
        "python": platform.python_version(),
    }


def reduzir_uma_cor(h, coluna, palavras):
    """Reducao de COR UNICA: ignora a coluna -> todas as colunas usam a MESMA"""
    return reduzir(h, 0, palavras)


class Perfil:
    """Conta quantos hashes e reducoes uma quebra consome."""

    def __init__(self, reduzir_base=reduzir):
        self.hashes = 0
        self.reducoes = 0
        self._reduzir_base = reduzir_base

    def hash(self, s):
        self.hashes += 1
        return meu_hash(s)

    def reduzir(self, h, coluna, palavras):
        self.reducoes += 1
        return self._reduzir_base(h, coluna, palavras)


def contar_operacoes_quebra(h_alvo, tabela, largura, palavras, _reduzir=reduzir):
    """Quebra contando operacoes. Devolve (resultado, n_hashes, n_reducoes)."""
    perfil = Perfil(reduzir_base=_reduzir)
    resultado = quebrar(h_alvo, tabela, largura, palavras,
                        _hash=perfil.hash, _reduzir=perfil.reduzir)
    return resultado, perfil.hashes, perfil.reducoes


def cronometrar_quebra(h_alvo, tabela, largura, palavras):
    """Quebra medindo o tempo (perf_counter), com as funcoes padrao (sem"""
    inicio = time.perf_counter()
    resultado = quebrar(h_alvo, tabela, largura, palavras)
    return resultado, time.perf_counter() - inicio


# Uma configuracao: constroi a tabela e mede tudo

def medir_configuracao(altura, largura, palavras, semente=0,
                       n_amostra=200, semente_amostra=12345,
                       _reduzir=reduzir, rotulo="rainbow"):
    """Constroi UMA tabela (altura x largura) e devolve um dict com as metricas"""
    N = len(palavras) ** 2

    # --- construcao (cronometrada) ---
    inicio_constr = time.perf_counter()
    tabela = construir_tabela(altura, largura, palavras, semente=semente, _reduzir=_reduzir)
    tempo_construcao = time.perf_counter() - inicio_constr
    pares = len(tabela)

    descritor, caminho = tempfile.mkstemp(suffix=".csv")
    os.close(descritor)
    try:
        salvar(tabela, caminho)
        disco_bytes = os.path.getsize(caminho)
    finally:
        os.remove(caminho)

    sorteador = random.Random(semente_amostra)
    alvos = [meu_hash(indice_para_senha(sorteador.randrange(N), palavras))
             for _ in range(n_amostra)]

    acertos = 0
    ops_hit = n_hit = 0
    ops_miss = n_miss = 0
    for h in alvos:
        resultado, n_hashes, n_reducoes = contar_operacoes_quebra(
            h, tabela, largura, palavras, _reduzir=_reduzir)
        if resultado is not None:
            acertos += 1
            n_hit += 1
            ops_hit += n_hashes + n_reducoes
        else:
            n_miss += 1
            ops_miss += n_hashes + n_reducoes

    inicio_tempo = time.perf_counter()
    for h in alvos:
        quebrar(h, tabela, largura, palavras, _reduzir=_reduzir)
    tempo_medio_us = (time.perf_counter() - inicio_tempo) / n_amostra * 1e6

    return {
        "rotulo": rotulo,
        "altura": altura,
        "largura": largura,
        "produto": altura * largura,
        "pares_guardados": pares,
        "taxa_sobrevivencia": round(pares / altura, 4),
        "cota_teorica": round(altura * largura / N, 4),
        "tempo_construcao_s": round(tempo_construcao, 3),
        "disco_bytes": disco_bytes,
        "n_amostra": n_amostra,
        "acertos": acertos,
        "taxa_acerto": round(acertos / n_amostra, 4),
        "tempo_medio_quebra_us": round(tempo_medio_us, 1),
        "ops_media_hit": round(ops_hit / n_hit, 1) if n_hit else None,
        "ops_media_miss": round(ops_miss / n_miss, 1) if n_miss else None,
    }


def varrer(palavras, produto, larguras, semente=0, n_amostra=200):
    """Para cada largura em 'larguras', usa altura = produto // largura (mantendo"""
    linhas = []
    for largura in larguras:
        altura = produto // largura
        print(f"  medindo altura={altura:>7} x largura={largura:>5} ...", end="", flush=True)
        linha = medir_configuracao(altura, largura, palavras,
                                   semente=semente, n_amostra=n_amostra)
        linhas.append(linha)
        print(f" acerto={linha['taxa_acerto']:.3f}  "
              f"constr={linha['tempo_construcao_s']}s  "
              f"sobreviv={linha['taxa_sobrevivencia']:.3f}")
    return linhas


def cobertura_distinta(altura, largura, palavras, semente=0, _reduzir=reduzir):
    """Constroi as cadeias (mesma semente) e conta quantas senhas DISTINTAS"""
    sorteador = random.Random(semente)
    N = len(palavras) ** 2
    cobertos = set()
    for _ in range(altura):
        senha = indice_para_senha(sorteador.randrange(N), palavras)
        cobertos.add(senha)
        for coluna in range(largura):
            senha = _reduzir(meu_hash(senha), coluna, palavras)
            cobertos.add(senha)
    return len(cobertos), altura * (largura + 1)


def comparar_cores(altura, largura, palavras, semente=0):
    """Compara rainbow vs 1 cor pela COBERTURA DISTINTA (so construcao, sem"""
    linhas = []
    for rotulo, reducao in (("rainbow", reduzir), ("1cor", reduzir_uma_cor)):
        distintas, total = cobertura_distinta(altura, largura, palavras,
                                              semente=semente, _reduzir=reducao)
        linhas.append({
            "rotulo": rotulo,
            "altura": altura,
            "largura": largura,
            "pontos_totais": total,              # altura * (largura + 1)
            "senhas_distintas": distintas,       # cobertura real (set)
            "aproveitamento": round(distintas / total, 4),   # distintas / total
            "cobertura_do_espaco": round(distintas / (len(palavras) ** 2), 4),
        })
    return linhas


def curva_eficacia(palavras, alturas, largura=100, semente=0, n_amostra=500):
    """Constroi tabelas de cobertura CRESCENTE (largura fixa, altura aumentando)"""
    linhas = []
    for altura in alturas:
        produto = altura * largura
        print(f"  altura={altura:>7} x largura={largura} (produto={produto:,}) ...",
              end="", flush=True)
        linha = medir_configuracao(altura, largura, palavras,
                                   semente=semente, n_amostra=n_amostra)
        linhas.append(linha)
        print(f" acerto={linha['taxa_acerto']:.3f}  "
              f"constr={linha['tempo_construcao_s']}s  "
              f"sobreviv={linha['taxa_sobrevivencia']:.3f}")
    return linhas


def escrever_csv(linhas, caminho):
    """Grava a lista de dicts como CSV (uma linha por configuracao)."""
    campos = list(linhas[0].keys())
    with open(caminho, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)


def salvar_hardware(caminho):
    """Grava as specs da maquina num arquivo texto (contexto dos tempos)."""
    with open(caminho, "w", encoding="utf-8") as arquivo:
        for chave, valor in descrever_hardware().items():
            arquivo.write(f"{chave}={valor}\n")


def _executar_grande(palavras, resultados_dir):
    """Run GRANDE: curva eficacia x cobertura (largura fixa, altura crescente)."""
    LARGURA = 100
    ALTURAS = [60_000, 150_000, 300_000, 450_000, 600_000]
    print(f"\nCurva de eficacia (largura fixa = {LARGURA}, cobertura crescente):")
    linhas = curva_eficacia(palavras, ALTURAS, largura=LARGURA, semente=0, n_amostra=500)
    caminho = os.path.join(resultados_dir, "curva_eficacia_grande.csv")
    escrever_csv(linhas, caminho)
    print(f"\nCSV salvo em: {caminho}")


def _executar_medio(palavras, resultados_dir):
    """Run MEDIO (padrao): varredura do trade-off + comparacao rainbow vs 1 cor."""
    PRODUTO = 1_000_000
    LARGURAS = [25, 50, 100, 200]
    print(f"\nVarredura (produto altura x largura = {PRODUTO:,}, cota ~ {PRODUTO/TAMANHO_ESPACO:.3%}):")
    linhas = varrer(palavras, PRODUTO, LARGURAS, semente=0, n_amostra=200)

    caminho_csv = os.path.join(resultados_dir, "varredura_media.csv")
    escrever_csv(linhas, caminho_csv)
    print(f"\nCSV salvo em: {caminho_csv}")

    print("\nCobertura distinta: rainbow vs 1 cor (produto fixo = 500.000):")
    comparacao = []
    for largura in (50, 200, 500):
        altura = 500_000 // largura
        comparacao.extend(comparar_cores(altura, largura, palavras, semente=0))
    for linha in comparacao:
        print(f"  {linha['rotulo']:8} largura={linha['largura']:>4}  "
              f"distintas={linha['senhas_distintas']:>7}  "
              f"aproveit={linha['aproveitamento']:.3f}")
    caminho_cmp = os.path.join(resultados_dir, "rainbow_vs_1cor.csv")
    escrever_csv(comparacao, caminho_cmp)
    print(f"CSV salvo em: {caminho_cmp}")


if __name__ == "__main__":
    import sys

    RAIZ = os.path.dirname(os.path.abspath(__file__))
    palavras = carregar_palavras(os.path.join(RAIZ, "dados", "lista_diceware.asc"))
    resultados_dir = os.path.join(RAIZ, "resultados")
    os.makedirs(resultados_dir, exist_ok=True)

    print("Hardware desta maquina:")
    for chave, valor in descrever_hardware().items():
        print(f"  {chave:16} = {valor}")
    salvar_hardware(os.path.join(resultados_dir, "hardware.txt"))

    if len(sys.argv) > 1 and sys.argv[1] == "grande":
        _executar_grande(palavras, resultados_dir)
    else:
        _executar_medio(palavras, resultados_dir)
