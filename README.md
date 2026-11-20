# Análise de dados relacionados à monitoria de Introdução ao Cálculo

## Tratamento dos dados

As respostas do formulário foram tratadas manualmente antes da execução deste
projeto, pois a base é pequena. O `main.py` não altera o arquivo original: ele
apenas lê o CSV, padroniza nomes e respostas e cria variáveis auxiliares para a
análise. As decisões manuais foram:

* notas zero foram mantidas como 0;
* notas de P1 e P2 foram substituídas pela média;
* respostas com somente P1 foram mantidas conforme o tratamento realizado;
* quando havia mais de uma opção de nota, foi mantida a menor.

O script também transforma respostas "Não" em `Não foi` na frequência,
converte a escala de importância para números de 1 a 5 e separa múltiplos
motivos por ponto e vírgula apenas para contar menções. O dataset não é salvo
nem sobrescrito pelo programa.

## O que é gerado

Além dos quatro gráficos originais, são gerados:

* `5_importancia_monitoria.png`: distribuição da importância atribuída à monitoria;
* `6_motivos_monitoria.png`: frequência dos motivos citados pelos alunos.

Os gráficos de nota usam somente as respostas com nota válida. Respostas sem
resposta nas variáveis categóricas aparecem como `Sem resposta` quando a
comparação as inclui. Grupos muito pequenos devem ser interpretados com
cautela.

## Limitações

Esta é uma análise observacional de uma amostra pequena. Diferenças entre
participantes e não participantes não demonstram causalidade: alunos com mais
dificuldade podem ter procurado a monitoria com maior frequência. Os testes
estatísticos são exploratórios e devem ser acompanhados pelos tamanhos dos
grupos, médias, medianas e contexto das respostas.

## Como rodar
Necessário ter Python instalado, o dataset `Avaliação.csv` e as bibliotecas
`pandas`, `scipy` e `matplotlib`.

```bash
python main.py
```
