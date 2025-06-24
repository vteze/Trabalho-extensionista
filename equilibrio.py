import pandas as pd

# Carregamento dos dados
enade_arq1 = pd.read_csv("microdados2021_arq1.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq3 = pd.read_csv("microdados2021_arq3.txt", sep=';', encoding='latin1', low_memory=False)

# Combinação direta por índice
enade_completo = pd.concat([
    enade_arq1[['CO_CURSO', 'CO_MODALIDADE', 'CO_GRUPO']].reset_index(drop=True),
    enade_arq3[['NT_GER']].reset_index(drop=True)
], axis=1)

# Filtrar apenas registros com nota presente
enade_com_nota = enade_completo[enade_completo["NT_GER"].notnull()]

# Agrupar por CO_GRUPO e CO_MODALIDADE, contando as notas
contagem = enade_com_nota.groupby(["CO_GRUPO", "CO_MODALIDADE"]).size().unstack(fill_value=0)

# Renomear as colunas para facilitar
contagem.columns = ["Presencial", "EAD"]

# Calcular a diferença absoluta entre Presencial e EAD
contagem["Diferenca_Absoluta"] = abs(contagem["Presencial"] - contagem["EAD"])

# Ordenar pelos grupos mais equilibrados (menor diferença)
contagem_ordenada = contagem.sort_values(by="Diferenca_Absoluta", ascending=True)

print(contagem_ordenada.head(10))  # Mostrar os 10 grupos mais equilibrados
