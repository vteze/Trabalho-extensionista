import pandas as pd
import os

# --- Configuração do diretório de dados ---
data_dir = "C:/Users/PICHAU/Desktop/coleta de dados/trabalho final/TDE_pt2/TDE_pt2/"


# -------------------------------
# 1. Carregamento dos dados
# -------------------------------
enade_arq1 = pd.read_csv(f"{data_dir}microdados2021_arq1.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq3 = pd.read_csv(f"{data_dir}microdados2021_arq3.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq14 = pd.read_csv(f"{data_dir}microdados2021_arq14.txt", sep=';', encoding='latin1', low_memory=False)
censo_cursos = pd.read_csv(f"{data_dir}MICRODADOS_CADASTRO_CURSOS_2021.CSV", sep=';', encoding='latin1', low_memory=False)
censo_ies = pd.read_csv(f"{data_dir}MICRODADOS_CADASTRO_IES_2021.CSV", sep=';', encoding='latin1', low_memory=False)

# ----------------------------------------------------
# 2. Padronização de nomes das colunas
# ----------------------------------------------------
enade_arq1 = enade_arq1.rename(columns={"NU_ANO": "NU_ANO_ENADE"})
enade_arq3 = enade_arq3.rename(columns={"NU_ANO": "NU_ANO_ENADE"})
enade_arq14 = enade_arq14.rename(columns={"NU_ANO": "NU_ANO_ENADE"})

censo_cursos = censo_cursos.rename(columns={
    "NO_REGIAO": "NO_REGIAO_CURSO",
    "CO_REGIAO": "CO_REGIAO_CURSO",
    "NO_UF": "NO_UF_CURSO",
    "SG_UF": "SG_UF_CURSO",
    "CO_UF": "CO_UF_CURSO",
    "NO_MUNICIPIO": "NO_MUNICIPIO_CURSO",
    "CO_MUNICIPIO": "CO_MUNICIPIO_CURSO",
    "TP_ORGANIZACAO_ACADEMICA": "TP_ORGANIZACAO_ACADEMICA_CURSO",
    "TP_CATEGORIA_ADMINISTRATIVA": "TP_CATEGORIA_ADMINISTRATIVA_CURSO"
})

censo_ies = censo_ies.rename(columns={
    "NO_UF_IES": "UF_IES",
    "TP_ORGANIZACAO_ACADEMICA": "TP_ORGANIZACAO_ACADEMICA_IES",
    "TP_CATEGORIA_ADMINISTRATIVA": "TP_CATEGORIA_ADMINISTRATIVA_IES" # Mantido o rename
})

# ----------------------------------------------------------------------
# 3. Filtrar ENADE para CO_GRUPO = 906 (Letras)
# ----------------------------------------------------------------------
enade_arq1 = enade_arq1[enade_arq1["CO_GRUPO"] == 906].copy()

# ----------------------------------------------------------------------
# 4. Unir dados complementares do ENADE (NT_GER e QE_I08)
# ----------------------------------------------------------------------
enade_completo = pd.merge(
    enade_arq1,
    enade_arq3[["NU_ANO_ENADE", "CO_CURSO", "NT_GER"]],
    on=["NU_ANO_ENADE", "CO_CURSO"],
    how="left"
)
enade_completo = pd.merge(
    enade_completo,
    enade_arq14[["NU_ANO_ENADE", "CO_CURSO", "QE_I08"]],
    on=["NU_ANO_ENADE", "CO_CURSO"],
    how="left"
)

# ----------------------------------------------------------------------
# 5. Mesclar com dados do Censo de Cursos e tratar CO_IES duplicado
# ----------------------------------------------------------------------
# Verificar se 'CO_CURSO' existe na base de cursos e em enade_completo
if "CO_CURSO" not in censo_cursos.columns or "CO_CURSO" not in enade_completo.columns:
    raise ValueError("Coluna CO_CURSO não encontrada em censo_cursos ou enade_completo.")

# Merge com dados de cursos para obter CO_IES (e outras colunas)
# Especificamos suffixes para lidar com CO_IES_x (do ENADE) e CO_IES_y (do Censo Cursos)
cursos_ies_info = censo_cursos[["CO_CURSO", "CO_IES"]].drop_duplicates()
enade_completo = pd.merge(
    enade_completo,
    cursos_ies_info,
    on="CO_CURSO",
    how="left",
    suffixes=('_enade', '_censo_curso') # Usando sufixos mais descritivos
)

# TRATAMENTO DO CO_IES DUPLICADO:
# Se 'CO_IES_enade' existe, ele é o CO_IES original do ENADE.
# Renomeamos para 'CO_IES' e removemos a versão do censo.
if 'CO_IES_enade' in enade_completo.columns:
    enade_completo = enade_completo.rename(columns={'CO_IES_enade': 'CO_IES'})
    # Remove a coluna CO_IES_censo_curso se ela foi criada
    if 'CO_IES_censo_curso' in enade_completo.columns:
        enade_completo = enade_completo.drop(columns=['CO_IES_censo_curso'])
# Se 'CO_IES_enade' não existe, mas 'CO_IES' existe (sem sufixo), mantemos como está.
# Caso contrário, algo deu errado e CO_IES não está presente.
elif 'CO_IES' not in enade_completo.columns:
    raise ValueError("Falha crítica: A coluna CO_IES não está presente no dataframe enade_completo após a mesclagem inicial.")


# ----------------------------------------------------------------------
# 6. Mesclar com dados do Censo de IES (pelo CO_IES)
# ----------------------------------------------------------------------
enade_completo = pd.merge(
    enade_completo,
    censo_ies[["CO_IES", "NO_IES", "UF_IES", "TP_ORGANIZACAO_ACADEMICA_IES", "TP_CATEGORIA_ADMINISTRATIVA_IES"]], # Incluído TP_CATEGORIA_ADMINISTRATIVA_IES
    on="CO_IES",
    how="left"
)

# ----------------------------------------------------------------------
# 7. Remover colunas duplicadas por nome (caso algum merge tenha causado isso)
# ----------------------------------------------------------------------

enade_completo = enade_completo.loc[:, ~enade_completo.columns.duplicated()].copy()


# ----------------------------------------------------------------------
# 8. Limpeza e Transformação Final dos Dados
# ----------------------------------------------------------------------

enade_completo = enade_completo.dropna(subset=["NT_GER", "QE_I08"]).copy()
enade_completo = enade_completo[~((enade_completo["CO_MODALIDADE"] == 0) & (enade_completo["NT_GER"] == 0.0))].copy()
enade_completo = enade_completo[enade_completo["NT_GER"] != 0.0].copy()

# 7.1 Mapear CO_MODALIDADE para texto legível
enade_completo["MODALIDADE"] = enade_completo["CO_MODALIDADE"].map({
    0: "EAD",
    1: "Presencial"
})

# 7.2 Mapear QE_I08 (faixa de renda) para descrição
mapa_renda = {
    'A': 'Até 1,5 salário mínimo (até R$ 1.650,00)',
    'B': 'De 1,5 a 3 salários mínimos (R$ 1.650,01 a R$ 3.300,00)',
    'C': 'De 3 a 4,5 salários mínimos (R$ 3.300,01 a R$ 4.950,00)',
    'D': 'De 4,5 a 6 salários mínimos (R$ 4.950,01 a R$ 6.600,00)',
    'E': 'De 6 a 10 salários mínimos (R$ 6.600,01 a R$ 11.000,00)',
    'F': 'De 10 a 30 salários mínimos (R$ 11.000,01 a R$ 33.000,00)',
    'G': 'Acima de 30 salários mínimos (mais de R$ 33.000,00)'
}
enade_completo["FAIXA_RENDA"] = enade_completo["QE_I08"].map(mapa_renda)


# ----------------------------------------------------------------------
# 9. Exibir resultados básicos e salvar
# ----------------------------------------------------------------------
print("\n--- Processamento Concluído ---")
print("Colunas do dataframe final:", list(enade_completo.columns))
print("Total de registros:", len(enade_completo))
print("\nAmostra dos dados:")
print(enade_completo.head())

enade_completo.to_csv("enade_integrado_cc_906.csv", sep=';', index=False, encoding='latin1')
print("\nDataFrame integrado salvo como 'enade_integrado_cc_906.csv'")