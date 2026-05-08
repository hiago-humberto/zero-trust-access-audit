import pandas as pd
import numpy as np

def aplicar_regras_zero_trust(df_desligados, df_acessos):
    # 1. Tratamento e Validação de Schema
    df_desligados['Data Desligamento'] = pd.to_datetime(df_desligados['Data Desligamento'], format='%d/%m/%Y', errors='coerce')
    df_acessos['Data de Bloqueio'] = pd.to_datetime(df_acessos['Data de Bloqueio'], format='%d/%m/%Y', errors='coerce')
    df_acessos['Data de Último Login'] = pd.to_datetime(df_acessos['Data de Último Login'], format='%d/%m/%Y', errors='coerce')
    
    # Limpeza do ID e Matrícula
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    df_desligados['Matrícula'] = df_desligados['Matrícula'].astype(float)

    # 2. Cruzamento Vetorizado com sufixos para evitar duplicidade ambígua
    df_cruzamento = pd.merge(
        df_desligados, 
        df_acessos, 
        left_on='Matrícula', 
        right_on='Matricula_Clean', 
        how='inner',
        suffixes=('', '_TI') # Mantém o nome original no RH e adiciona _TI no que for repetido do sistema
    )

    # 3. Regras de ITGC
    condicoes_risco = [
        (df_cruzamento['Data de Último Login'] > df_cruzamento['Data Desligamento']),
        (df_cruzamento['Status'] == 'Ativo'),
        (df_cruzamento['Data de Bloqueio'] > df_cruzamento['Data Desligamento'] + pd.Timedelta(days=7))
    ]

    classificacoes = [
        '🔴 CRÍTICO: Acesso após Desligamento',
        '🔴 CRÍTICO: Usuário ainda Ativo',
        '🟠 MÉDIO: Bloqueio fora da SLA (> 7 dias)'
    ]

    df_cruzamento['Classificação de Risco'] = np.select(condicoes_risco, classificacoes, default='🟢 OK')
    
    # Seleção segura da área para o gráfico (usa a coluna original do RH)
    df_cruzamento['Area_Risco'] = df_cruzamento['Área']
    
    return df_cruzamento

def aplicar_regras_transferencias(df_transferidos, df_acessos):
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    df_transferidos['Matrícula'] = df_transferidos['Matrícula'].astype(float)

    # Merge com sufixos também nas transferências
    df_cruzamento = pd.merge(
        df_transferidos, 
        df_acessos, 
        left_on='Matrícula', 
        right_on='Matricula_Clean', 
        how='inner',
        suffixes=('', '_TI')
    )

    def checar_risco_sod(row):
        area_origem = str(row['Área Origem']).strip().upper()
        modulos_acesso = str(row['Módulo']).upper()
        if str(row['Status']).upper() == 'ATIVO' and area_origem in modulos_acesso:
            return '🟠 MÉDIO: Acesso mantido na Área de Origem (SoD)'
        return '🟢 OK'

    df_cruzamento['Classificação de Risco'] = df_cruzamento.apply(checar_risco_sod, axis=1)
    df_cruzamento['Area_Risco'] = df_cruzamento['Área Destino']
    return df_cruzamento

def aplicar_regras_fantasmas(df_ativos, df_desligados, df_acessos):
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    # Garante a união de todos os IDs conhecidos pelo RH
    ids_rh = set(df_ativos['Matrícula'].dropna()).union(set(df_desligados['Matrícula'].dropna()))
    
    # Identifica quem está ativo no sistema mas não existe no RH
    fantasmas = df_acessos[(df_acessos['Status'].str.upper() == 'ATIVO') & (~df_acessos['Matricula_Clean'].isin(ids_rh))].copy()
    
    fantasmas['Classificação de Risco'] = '🔴 CRÍTICO: Conta Fantasma'
    fantasmas['Area_Risco'] = 'TI / Shadow IT'
    return fantasmas