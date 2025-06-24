import pandas as pd

data_dir = "C:/Users/PICHAU/Desktop/coleta de dados/trabalho final/TDE_pt2/TDE_pt2/"


# -------------------------------
# 1. Carregamento dos dados
# -------------------------------
enade_arq1 = pd.read_csv(f"{data_dir}microdados2021_arq1.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq3 = pd.read_csv(f"{data_dir}microdados2021_arq3.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq14 = pd.read_csv(f"{data_dir}microdados2021_arq14.txt", sep=';', encoding='latin1', low_memory=False)
censo_cursos = pd.read_csv(f"{data_dir}MICRODADOS_CADASTRO_CURSOS_2021.CSV", sep=';', encoding='latin1', low_memory=False)
censo_ies = pd.read_csv(f"{data_dir}MICRODADOS_CADASTRO_IES_2021.CSV", sep=';', encoding='latin1', low_memory=False)
# -------------------------------
# 2. Combinação direta por índice (concatenação)
# -------------------------------

# Inclui todas as colunas relevantes do arq1, e acrescenta NT_GER e QE_I08 na mesma ordem
enade_completo = pd.concat([
    enade_arq1[["CO_CURSO", "CO_MODALIDADE", "CO_GRUPO"]],
    enade_arq3[["NT_GER"]],
    enade_arq14[["QE_I08"]]
], axis=1)

# -------------------------------
# 3. Filtro: apenas Ciência da Computação (grupo 4004)
# -------------------------------

enade_completo = enade_completo[enade_completo["CO_GRUPO"] == 906]

# -------------------------------
# 4. Funções de análise exploratória
# -------------------------------

def totalRegistros():
    print("Total de registros da base filtrada (Licenciaturam em Letras-Português e Espanhol):", len(enade_completo))

def distribuicaoModalidades():
    print("\nFrequência por modalidade:")
    modalidade_mapeada = enade_completo["CO_MODALIDADE"].map({1: "Presencial", 0: "EAD"})
    print(modalidade_mapeada.value_counts().reindex(["Presencial", "EAD"], fill_value=0))

def proporcaoAusentes():
    print("\nProporção de valores ausentes nas variáveis principais:")
    print(enade_completo[["NT_GER", "QE_I08"]].isnull().mean() * 100)

def frequenciaRenda():
    print("\nFrequência das faixas de renda (QE_I08):")
    mapa_renda = {
        'A': 'Até 1,5 salário mínimo (até R$ 1.650,00)',
        'B': 'De 1,5 a 3 salários mínimos (R$ 1.650,01 a R$ 3.300,00)',
        'C': 'De 3 a 4,5 salários mínimos (R$ 3.300,01 a R$ 4.950,00)',
        'D': 'De 4,5 a 6 salários mínimos (R$ 4.950,01 a R$ 6.600,00)',
        'E': 'De 6 a 10 salários mínimos (R$ 6.600,01 a R$ 11.000,00)',
        'F': 'De 10 a 30 salários mínimos (R$ 11.000,01 a R$ 33.000,00)',
        'G': 'Acima de 30 salários mínimos (mais de R$ 33.000,00)'
    }
    renda_traduzida = enade_completo["QE_I08"].map(mapa_renda)
    print(renda_traduzida.value_counts())

def mediaModalidade():
    print("\nMédia geral da nota por modalidade:")
    enade_completo["MODALIDADE"] = enade_completo["CO_MODALIDADE"].map({1: "Presencial", 0: "EAD"})
    medias = enade_completo.groupby("MODALIDADE")["NT_GER"].mean().reindex(["Presencial", "EAD"])
    print(medias.fillna(0))

def print15enadeC():
    print("\nPrimeiras 15 linhas do dataframe enade_completo:")
    print(enade_completo.head(15))

def notaPresencialAusentesPresentes():
    """
    Mostra a quantidade de valores presentes e ausentes na variável NT_GER,
    filtrando apenas alunos da modalidade presencial.
    """
    # Filtrar apenas modalidade presencial
    presencial = enade_completo[enade_completo["CO_MODALIDADE"] == 1]
    
    # Contagem de ausentes e presentes
    ausentes = presencial["NT_GER"].isnull().sum()
    presentes = presencial["NT_GER"].notnull().sum()
    
    print(f"Valores presentes em NT_GER (Presencial): {presentes}")
    print(f"Valores ausentes em NT_GER (Presencial): {ausentes}")

def notaEADAusentesPresentes():
    """
    Mostra a quantidade de valores presentes e ausentes na variável NT_GER,
    filtrando apenas alunos da modalidade EAD.
    """
    # Filtrar apenas modalidade EADS
    ead = enade_completo[enade_completo["CO_MODALIDADE"] == 0]
    
    # Contagem de ausentes e presentes
    ausentes = ead["NT_GER"].isnull().sum()
    presentes = ead["NT_GER"].notnull().sum()
    
    print(f"Valores presentes em NT_GER (EAD): {presentes}")
    print(f"Valores ausentes em NT_GER (EAD): {ausentes}")



# -------------------------------
# Execução das funções
# -------------------------------

if __name__ == "__main__":
    totalRegistros()
    distribuicaoModalidades()
    proporcaoAusentes()
    frequenciaRenda()
    mediaModalidade()
    print15enadeC()
    notaPresencialAusentesPresentes()
    notaEADAusentesPresentes()
