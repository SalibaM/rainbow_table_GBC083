# Rainbow Table — GBC083

Implementação de uma *rainbow table* em Python para quebrar senhas pequenas
baseadas no Diceware (duas palavras da lista do Reinhold). A função de redução
usa uma cor por coluna, para reduzir a repetição entre as cadeias. Trabalho da
disciplina de Segurança da Informação (GBC083), Professor Ivan Sendin.

## Como funciona, em uma linha

Cada cadeia alterna hash (SHA-256 com o prefixo `GBC083`) e redução, e a tabela
guarda apenas o começo e o fim de cada cadeia. Na busca, refazemos o caminho da
última coluna para a primeira até bater com um fim guardado, e confirmamos a
senha pelo hash.

## Estrutura

```
lista_diceware.py   carrega a lista e converte número <-> senha
funcao_hash.py      meu_hash (SHA-256 + prefixo GBC083)
reducao.py          a redução com as cores
cadeia.py           monta uma cadeia e procura dentro dela
tabela.py           monta a tabela, quebra e salva/carrega em disco
experimentos.py     medições (trade-off, eficácia, rainbow vs cor única)
graficos.py         gera os gráficos a partir dos CSVs
demo_uma_linha.py   imprime uma cadeia passo a passo
testes/             testes automáticos, um arquivo por módulo
dados/              lista Diceware (entrada)
```

## Como rodar

```bash
# testes
python -m pytest testes
# ou, sem pytest, rodando um arquivo direto:
python testes/teste_tabela.py

# demonstração de uma cadeia
python demo_uma_linha.py

# experimentos (gera os CSVs em resultados/)
python experimentos.py          # varredura média + rainbow vs cor única
python experimentos.py grande   # curva de eficácia (demora mais)

# gráficos (lê os CSVs e salva os PNGs em resultados/)
python graficos.py
```

Precisa de Python 3 e, só para os gráficos, de `matplotlib`.
