"""Analise exploratoria das respostas sobre monitoria.

O CSV ja foi tratado manualmente antes desta etapa. Este script apenas faz a
leitura, padroniza campos, calcula os indicadores e gera os graficos.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

BASE = Path(__file__).parent
CSV = BASE / "Avaliação.csv"
OUT = BASE / "graficos"
OUT.mkdir(exist_ok=True)

ORDEM_FREQ = ["Não foi", "1", "2", "3", "4", "Mais de 4", "Só semana da prova"]
MAPA_GRUPO = {"Não participei de ambos": "Nenhum dos dois",
              "Somente participei das discussões com colegas": "Só colegas",
              "Somente tirei dúvidas com o monitor": "Só monitor", "Fiz ambos": "Ambos"}


def carregar_dados():
    df = pd.read_csv(CSV, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda c: c.str.strip() if pd.api.types.is_string_dtype(c) else c)
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    df.rename(columns={
        "Carimbo de data/hora": "data_hora",
        "Você participou das monitorias online/presencial?": "participou_monitoria",
        "Se participou, quantas vezes foi nas monitorias?": "freq_monitoria",
        "Estava presente no grupo do WhatsApp de introdução ao calculo, durante o período da matéria com contato direto com os monitores no grupo?": "no_grupo_whatsapp",
        "Ao estar presente nos grupos, você participou das discussões (compartilhamento de material e troca de informaçôes com colegas) no grupo ou conversou diretamente com o monitor?": "participacao_grupo",
        "Em geral, o quanto você considera importante a monitoria para seu aprendizado?": "importancia",
        "Caso você tenha participado de monitorias de Introdução ao Cálculo, quais foram os motivos para não gostar ou considerar que elas não foram úteis?": "motivos",
        "Por fim, qual foi sua nota final de introdução ao calculo? (Pós ou não PF)": "nota_final",
    }, inplace=True)
    df = df[["data_hora", "participou_monitoria", "freq_monitoria", "no_grupo_whatsapp",
             "participacao_grupo", "importancia", "motivos", "nota_final"]].copy()
    df["nota_final"] = pd.to_numeric(df["nota_final"], errors="coerce")
    df["nota_final"] = df["nota_final"].where(df["nota_final"].between(0, 10))
    df.loc[df["participou_monitoria"] == "Não", "freq_monitoria"] = "Não foi"
    df["freq_monitoria"] = df["freq_monitoria"].replace("Na semana das provas (2 ou 3)", "Só semana da prova")
    df["freq_num"] = df["freq_monitoria"].map({"Não foi": 0, "1": 1, "2": 2, "3": 3, "4": 4, "Mais de 4": 5})
    df["importancia_num"] = df["importancia"].map({"Não considero importante": 1, "Pouco importante": 2,
        "Relativamente importante": 3, "Muito importante": 4, "Extremamente importante": 5})
    df["participacao_grupo"] = df["participacao_grupo"].replace(MAPA_GRUPO)
    return df


def salvar(nome):
    plt.tight_layout()
    plt.savefig(OUT / nome, dpi=150, bbox_inches="tight")
    plt.close()


def grafico_frequencia(df):
    counts = df["freq_monitoria"].value_counts().reindex(ORDEM_FREQ).fillna(0)
    ax = counts.plot(kind="bar", color="#6baed6", figsize=(10, 6))
    ax.bar_label(ax.containers[0], fmt="%.0f")
    ax.set(title=f"Frequência de participação nas monitorias (n={len(df)})",
           xlabel="Número de vezes nas monitorias", ylabel="Quantidade de alunos")
    plt.xticks(rotation=0)
    salvar("1_frequencia_monitorias.png")


def grafico_proporcao(notas, coluna, ordem, titulo, xlabel, nome):
    categoria = notas[coluna].fillna("Sem resposta")
    tab = pd.crosstab(categoria, notas["nota_final"] >= 7, normalize="index") * 100
    tab = tab.reindex([x for x in ordem if x in tab.index])
    tab.columns = ["Nota < 7", "Nota >= 7"]
    n = categoria.value_counts()
    ax = tab.plot(kind="bar", stacked=True, color=["#fb6a6a", "#4daf4a"], figsize=(10, 6))
    for container in ax.containers:
        ax.bar_label(container, labels=[f"{v:.0f}%" if v >= 5 else "" for v in container.datavalues], label_type="center")
    ax.set_xticklabels([f"{i}\n(n={n[i]})" for i in tab.index], rotation=0)
    ax.set(title=titulo, xlabel=xlabel, ylabel="% dos alunos do grupo")
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    salvar(nome)


def grafico_importancia(df):
    ordem = ["Não considero importante", "Pouco importante", "Relativamente importante", "Muito importante", "Extremamente importante"]
    counts = df["importancia"].value_counts().reindex(ordem).fillna(0)
    ax = counts.plot(kind="bar", color="#9ecae1", figsize=(10, 6))
    ax.bar_label(ax.containers[0], fmt="%.0f")
    ax.set(title="Importância atribuída à monitoria (respostas válidas)", xlabel="Avaliação", ylabel="Quantidade de alunos")
    plt.xticks(rotation=20, ha="right")
    salvar("5_importancia_monitoria.png")


def grafico_motivos(df):
    base = df["motivos"].dropna().loc[lambda s: s.ne("")]
    motivos = base.str.split(";").explode().str.strip().value_counts().sort_values()
    ax = motivos.plot(kind="barh", color="#969696", figsize=(10, 6))
    ax.bar_label(ax.containers[0], fmt="%.0f", padding=3)
    ax.set(title="Motivos citados para não considerar a monitoria útil", xlabel="Número de menções", ylabel="Motivo")
    salvar("6_motivos_monitoria.png")


def imprimir_resultados(df):
    notas = df.dropna(subset=["nota_final"])
    print(f"Respostas: {len(df)} | com nota: {len(notas)} | sem nota: {len(df) - len(notas)}")
    print(f"Média: {notas.nota_final.mean():.2f} | mediana: {notas.nota_final.median():.2f} | desvio padrão: {notas.nota_final.std():.2f}")
    acima = (notas.nota_final >= 7).sum()
    print(f"Nota >= 7: {acima} ({acima / len(notas) * 100:.2f}%)")
    for coluna, titulo in [("participou_monitoria", "Nota por participação"), ("freq_monitoria", "Nota por frequência"), ("no_grupo_whatsapp", "Nota por presença no WhatsApp")]:
        print(f"\n{titulo}:")
        print(notas.groupby(coluna, dropna=False).nota_final.agg(["count", "mean", "median"]).round(2))
    print("\nNota por participação no grupo:")
    grupo = notas["participacao_grupo"].fillna("Sem resposta")
    print(notas.assign(participacao_grupo=grupo).groupby("participacao_grupo").nota_final.agg(["count", "mean", "median"]).round(2))
    print("\nImportância da monitoria (%):")
    print(df["importancia"].value_counts(normalize=True, dropna=True).mul(100).round(1))
    for coluna in ["freq_num", "importancia_num"]:
        d = df[[coluna, "nota_final"]].dropna()
        rho, p = stats.spearmanr(d[coluna], d.nota_final)
        print(f"Spearman {coluna}: rho={rho:.2f}, p={p:.3f}, n={len(d)}")
    foi = notas.loc[notas.participou_monitoria == "Sim", "nota_final"]
    nao_foi = notas.loc[notas.participou_monitoria == "Não", "nota_final"]
    _, p = stats.mannwhitneyu(foi, nao_foi, alternative="two-sided")
    print(f"Mann-Whitney: mediana Sim={foi.median():.2f}, Não={nao_foi.median():.2f}, diferença das médias={foi.mean() - nao_foi.mean():.2f}, p={p:.3f}")


def main():
    df = carregar_dados()
    notas = df.dropna(subset=["nota_final"])
    imprimir_resultados(df)
    grafico_frequencia(df)
    grafico_proporcao(notas, "participou_monitoria", ["Não", "Sim"], "Nota por participação nas monitorias", "Participou das monitorias?", "2_nota_x_participacao.png")
    grafico_proporcao(notas, "freq_monitoria", ORDEM_FREQ, "Nota por frequência nas monitorias", "Número de vezes nas monitorias", "3_nota_x_frequencia.png")
    grafico_proporcao(notas, "participacao_grupo", ["Nenhum dos dois", "Só colegas", "Só monitor", "Ambos", "Sem resposta"], "Nota por participação nos grupos de WhatsApp", "Como participou no grupo?", "4_nota_x_grupo_whatsapp.png")
    grafico_importancia(df)
    grafico_motivos(df)


if __name__ == "__main__":
    main()
