import pandas as pd

#Carregar os datasets
enade_arq1 = pd.read_csv("microdados2021_arq1.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq3 = pd.read_csv("microdados2021_arq3.txt", sep=';', encoding='latin1', low_memory=False)
enade_arq14 = pd.read_csv("microdados2021_arq14.txt", sep=';', encoding='latin1', low_memory=False)
censo_cursos = pd.read_csv("MICRODADOS_CADASTRO_CURSOS_2021.CSV", sep=';', encoding='latin1', low_memory=False)
cadastro_ies = pd.read_csv("MICRODADOS_CADASTRO_IES_2021.CSV", sep=';', encoding='latin1', low_memory=False)

#Construir o dataframe ENADE completo (com as variáveis que vamos usar)
enade_completo = pd.concat([
    enade_arq1[["CO_CURSO", "CO_MODALIDADE", "CO_IES", "CO_GRUPO"]],
    enade_arq3[["NT_GER"]],
    enade_arq14[["QE_I08"]]
], axis=1)

#Filtrar só o curso Letras - Português e Espanhol (CO_GRUPO == 906)
enade_completo = enade_completo[enade_completo["CO_GRUPO"] == 906]

#Remover alunos que não têm nota do ENADE (NT_GER nulo)
enade_completo = enade_completo.dropna(subset=["NT_GER"])

#Preparar CENSO
censo_cursos_reduzido = censo_cursos[[
    "CO_CURSO", 
    "CO_IES", 
    "TP_MODALIDADE_ENSINO"
]]

#Fazer o merge (LEFT JOIN), usando CO_CURSO + CO_IES + modalidade
enade_censo_merged = pd.merge(
    enade_completo,
    censo_cursos_reduzido,
    how="left",
    left_on=["CO_CURSO", "CO_IES", "CO_MODALIDADE"],
    right_on=["CO_CURSO", "CO_IES", "TP_MODALIDADE_ENSINO"]
)

#Trazer NO_REGIAO_IES a partir do cadastro IES
cadastro_ies_reduzido = cadastro_ies[["CO_IES", "NO_REGIAO_IES"]]

enade_censo_regiao = pd.merge(
    enade_censo_merged,
    cadastro_ies_reduzido,
    how="left",
    on="CO_IES"
)

#Relatórios
total_alunos = len(enade_censo_regiao)

#Contagem de Presencial e EAD
modalidade_mapeada = enade_censo_regiao["CO_MODALIDADE"].map({1: "Presencial", 0: "EAD"})
contagem_modalidades = modalidade_mapeada.value_counts()

print("\n[INFO] --- RELATÓRIO FINAL ---")
print(f"[INFO] Total de alunos no ENADE (curso 906, com nota): {total_alunos}")
print(f"[INFO] Total de alunos PRESENCIAL: {contagem_modalidades.get('Presencial', 0)}")
print(f"[INFO] Total de alunos EAD: {contagem_modalidades.get('EAD', 0)}")
print("[INFO] ------------------------\n")

#Selecionar apenas as colunas finais para o Power BI (SEM TP_CATEGORIA_ADMINISTRATIVA)
enade_final = enade_censo_regiao[[
    "CO_MODALIDADE", 
    "NT_GER", 
    "QE_I08", 
    "NO_REGIAO_IES"
]]

#Salvar o CSV final
enade_final.to_csv("censo_enade_letras2021.csv", index=False, encoding='utf-8-sig')

print("[INFO] CSV 'censo_enade_letras2021.csv' gerado com sucesso!\n")