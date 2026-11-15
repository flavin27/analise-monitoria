import os
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

os.makedirs('graficos', exist_ok=True)

df = pd.read_csv("Avaliação.csv", skipinitialspace=True)
df.columns = df.columns.str.strip()

df = df.apply(lambda col: col.str.strip() if pd.api.types.is_string_dtype(col) else col)

df.rename(columns={
    'Carimbo de data/hora': 'data_hora',
    'Você participou das monitorias online/presencial?': 'participou_monitoria',
    'Se participou, quantas vezes foi nas monitorias?': 'freq_monitoria',
    'Estava presente no grupo do WhatsApp de introdução ao calculo, durante o período da matéria com contato direto com os monitores no grupo?': 'no_grupo_whatsapp',
    'Ao estar presente nos grupos, você participou das discussões (compartilhamento de material e troca de informaçôes com colegas) no grupo ou conversou diretamente com o monitor?': 'participacao_grupo',
    'Em geral, o quanto você considera importante a monitoria para seu aprendizado?': 'importancia',
    'Caso você tenha participado de monitorias de Introdução ao Cálculo, quais foram os motivos para não gostar ou considerar que elas não foram úteis?': 'motivos',
    'Por fim, qual foi sua nota final de introdução ao calculo? (Pós ou não PF)': 'nota_final',
}, inplace=True)

parametros = ['data_hora', 'participou_monitoria', 'freq_monitoria', 'no_grupo_whatsapp',
              'participacao_grupo', 'importancia', 'motivos', 'nota_final']
df = df[parametros].copy()

df['nota_final'] = pd.to_numeric(df['nota_final'], errors='coerce')
df['nota_final'] = df['nota_final'].where(df['nota_final'].between(0, 10))   # descarta valores fora de 0-10 (ex.: 51)

# Quem respondeu "Não" em participou entra como "Não foi" (3 respostas traziam número mesmo assim)
df.loc[df['participou_monitoria'] == 'Não', 'freq_monitoria'] = 'Não foi'
df['freq_monitoria'] = df['freq_monitoria'].replace('Na semana das provas (2 ou 3)', 'Só semana\nda prova')
ordem_freq = ['Não foi', '1', '2', '3', '4', 'Mais de 4', 'Só semana\nda prova']

# Comparações de nota usam só quem tem nota (sem isso, NaN cairia no grupo "< 7")
notas = df.dropna(subset=['nota_final']).copy()

media = notas['nota_final'].mean()
desvio_padrao = notas['nota_final'].std()

print(f"Respostas: {len(df)} | com nota: {len(notas)} | sem nota: {len(df) - len(notas)}")
print(f"Média da nota final: {media:.2f}")
print(f"Desvio padrão da nota final: {desvio_padrao:.2f}")

# Dividindo em grupos >=7 e <7
grupo_acima_igual_7 = notas[notas['nota_final'] >= 7]
grupo_abaixo_7 = notas[notas['nota_final'] < 7]

print(f"Alunos com nota >= 7: {len(grupo_acima_igual_7)} ({len(grupo_acima_igual_7) / len(notas) * 100:.2f}%)")
print(f"Alunos com nota < 7: {len(grupo_abaixo_7)} ({len(grupo_abaixo_7) / len(notas) * 100:.2f}%)")

grupo = notas['participacao_grupo'].replace({
    'Não participei de ambos': 'Nenhum dos dois',
    'Somente participei das discussões com colegas': 'Só colegas',
    'Somente tirei dúvidas com o monitor': 'Só monitor',
    'Fiz ambos': 'Ambos'})

# n, média e mediana da nota em cada caso
print("\nNota por participação nas monitorias:")
print(notas.groupby('participou_monitoria')['nota_final'].agg(['count', 'mean', 'median']).round(2))

print("\nNota por frequência nas monitorias:")
print(notas.groupby('freq_monitoria')['nota_final'].agg(['count', 'mean', 'median']).reindex(ordem_freq).dropna().astype({'count': int}).round(2)
      .rename(index=lambda x: x.replace('\n', ' ')))

print("\nNota por presença no grupo do WhatsApp:")
print(notas.groupby('no_grupo_whatsapp')['nota_final'].agg(['count', 'mean', 'median']).round(2))

print("\nNota por tipo de participação no grupo:")
print(notas.groupby(grupo)['nota_final'].agg(['count', 'mean', 'median']).round(2))


# Graficos

# Gráfico 1: frequência de participação nas monitorias (todos os respondentes)
freq_counts = df['freq_monitoria'].value_counts().reindex(ordem_freq).fillna(0)
plt.figure(figsize=(10, 6))
ax = freq_counts.plot(kind='bar', color='skyblue')
ax.bar_label(ax.containers[0])
plt.title('Frequência de Participação nas Monitorias')
plt.xlabel('Número de vezes nas monitorias')
plt.ylabel('Quantidade de alunos')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig('graficos/1_frequencia_monitorias.png')

# Gráfico 2: % de alunos com nota >= 7 (verde) e < 7 (vermelho) por participação nas monitorias
tab = pd.crosstab(notas['participou_monitoria'], notas['nota_final'] >= 7, normalize='index') * 100
tab.columns = ['Nota < 7', 'Nota >= 7']          # o crosstab ordena False, True
n = notas['participou_monitoria'].value_counts()
ax = tab.plot(kind='bar', stacked=True, color=['red', 'green'], alpha=0.7, figsize=(8, 6))
for c in ax.containers:
    ax.bar_label(c, labels=[f"{v:.0f}%" if v > 0 else "" for v in c.datavalues], label_type='center')
ax.set_xticklabels([f"{i}\n(n={n[i]})" for i in tab.index], rotation=0)
plt.title('Nota por Participação nas Monitorias')
plt.xlabel('Participou das monitorias?')
plt.ylabel('% dos alunos do grupo')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))   # legenda fora, para não cobrir as barras
plt.tight_layout()
plt.savefig('graficos/2_nota_x_participacao.png')

# Gráfico 3: o mesmo, por frequência nas monitorias
tab = pd.crosstab(notas['freq_monitoria'], notas['nota_final'] >= 7, normalize='index') * 100
tab = tab.reindex(ordem_freq).dropna()          # tira frequências sem nenhum aluno com nota
tab.columns = ['Nota < 7', 'Nota >= 7']
n = notas['freq_monitoria'].value_counts()
ax = tab.plot(kind='bar', stacked=True, color=['red', 'green'], alpha=0.7, figsize=(10, 6))
for c in ax.containers:
    ax.bar_label(c, labels=[f"{v:.0f}%" if v > 0 else "" for v in c.datavalues], label_type='center')
ax.set_xticklabels([f"{i}\n(n={n[i]})" for i in tab.index], rotation=0)
plt.title('Nota por Frequência nas Monitorias')
plt.xlabel('Número de vezes nas monitorias')
plt.ylabel('% dos alunos do grupo')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))   # legenda fora, para não cobrir as barras
plt.tight_layout()
plt.savefig('graficos/3_nota_x_frequencia.png')

# Gráfico 4: compartilhamento de material / troca com colegas e monitor
tab = pd.crosstab(grupo, notas['nota_final'] >= 7, normalize='index') * 100
tab = tab.reindex(['Nenhum dos dois', 'Só colegas', 'Só monitor', 'Ambos']).dropna()
tab.columns = ['Nota < 7', 'Nota >= 7']
n = grupo.value_counts()
ax = tab.plot(kind='bar', stacked=True, color=['red', 'green'], alpha=0.7, figsize=(9, 6))
for c in ax.containers:
    ax.bar_label(c, labels=[f"{v:.0f}%" if v > 0 else "" for v in c.datavalues], label_type='center')
ax.set_xticklabels([f"{i}\n(n={n[i]})" for i in tab.index], rotation=0)
plt.title('Nota por Participação nos Grupos de WhatsApp')
plt.xlabel('Como participou no grupo?')
plt.ylabel('% dos alunos do grupo')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))   # legenda fora, para não cobrir as barras
plt.tight_layout()
plt.savefig('graficos/4_nota_x_grupo_whatsapp.png')


#  CORRELAÇÕES E TESTES 
# Amostra pequena: os p-valores são só um indicativo

# Variáveis em número para o Spearman ("Só semana da prova" fica de fora por não ser uma contagem)
df['freq_num'] = df['freq_monitoria'].map({'Não foi': 0, '1': 1, '2': 2, '3': 3, '4': 4, 'Mais de 4': 5})
df['importancia_num'] = df['importancia'].map({
    'Não considero importante': 1, 'Pouco importante': 2, 'Relativamente importante': 3,
    'Muito importante': 4, 'Extremamente importante': 5})

print("\nCorrelação de Spearman com a nota:")
for coluna in ['freq_num', 'importancia_num']:
    d = df[[coluna, 'nota_final']].dropna()
    rho, p = stats.spearmanr(d[coluna], d['nota_final'])
    print(f"  {coluna}: rho={rho:.2f} p={p:.3f} n={len(d)}")

# Foi x não foi às monitorias (Mann-Whitney não assume nota "normal")
foi = notas.loc[notas['participou_monitoria'] == 'Sim', 'nota_final']
nao_foi = notas.loc[notas['participou_monitoria'] == 'Não', 'nota_final']
u, p = stats.mannwhitneyu(foi, nao_foi)
print(f"\nMediana foi: {foi.median():.2f} (n={len(foi)}) | não foi: {nao_foi.median():.2f} (n={len(nao_foi)}) | p={p:.3f}")