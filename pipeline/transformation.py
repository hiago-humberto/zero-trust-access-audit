import pandas as pd
import numpy as np

def aplicar_regras_zero_trust(df_desligados, df_acessos):
    # 1. Tratamento e Validação de Schema
    df_desligados['Data Desligamento'] = pd.to_datetime(df_desligados['Data Desligamento'], format='%d/%m/%Y', errors='coerce')
    df_acessos['Data de Bloqueio'] = pd.to_datetime(df_acessos['Data de Bloqueio'], format='%d/%m/%Y', errors='coerce')
    df_acessos['Data de Último Login'] = pd.to_datetime(df_acessos['Data de Último Login'], format='%d/%m/%Y', errors='coerce')
    
    # Limpeza do ID (Tira as letras, ex: AC1212 vira 1212)
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    df_desligados['Matrícula'] = df_desligados['Matrícula'].astype(float)

    # 2. Cruzamento Vetorizado
    df_cruzamento = pd.merge(
        df_desligados, 
        df_acessos, 
        left_on='Matrícula', 
        right_on='Matricula_Clean', 
        how='inner'
    )

    # 3. Regras de ITGC (Information Technology General Controls)
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

    # Aplica as tags de risco
    df_cruzamento['Classificação de Risco'] = np.select(condicoes_risco, classificacoes, default='🟢 OK: Controle Efetivo')

    # Retorna o DataFrame completo (os OKs e as Falhas) para o dashboard calcular os KPIs
    return df_cruzamento

def aplicar_regras_transferencias(df_transferidos, df_acessos):
    # 1. Tratamento e Validação de Schema
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    df_transferidos['Matrícula'] = df_transferidos['Matrícula'].astype(float)

    # 2. Cruzamento Vetorizado
    df_cruzamento = pd.merge(
        df_transferidos, 
        df_acessos, 
        left_on='Matrícula', 
        right_on='Matricula_Clean', 
        how='inner'
    )

    # 3. Regra de ITGC: O colaborador transferido ainda tem acesso à área antiga?
    def checar_risco_sod(row):
        area_origem = str(row['Área Origem']).strip().upper()
        modulos_acesso = str(row['Módulo']).upper()
        status_acesso = str(row['Status']).upper()
        
        # Se ele for ativo e a área antiga ainda estiver na string do módulo
        if status_acesso == 'ATIVO' and area_origem in modulos_acesso:
            return '🟠 MÉDIO: Acesso mantido na Área de Origem (Falha SoD)'
        return '🟢 OK: Controle Efetivo'

    df_cruzamento['Classificação de Risco'] = df_cruzamento.apply(checar_risco_sod, axis=1)
    return df_cruzamento

def aplicar_regras_fantasmas(df_ativos, df_desligados, df_acessos):
    # Tratamento de Schema
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    df_ativos['Matrícula'] = df_ativos['Matrícula'].astype(float)
    df_desligados['Matrícula'] = df_desligados['Matrícula'].astype(float)

    # Filtra apenas quem tem acesso ativo no sistema hoje
    acessos_ativos = df_acessos[df_acessos['Status'].str.upper() == 'ATIVO'].copy()

    # Cria um conjunto (Set) com TODOS os IDs válidos do RH
    ids_rh = set(df_ativos['Matrícula'].dropna()).union(set(df_desligados['Matrícula'].dropna()))

    # O Pulo do Gato: Pega quem está ativo no sistema, MAS não está no conjunto do RH
    fantasmas = acessos_ativos[~acessos_ativos['Matricula_Clean'].isin(ids_rh)].copy()
    
    fantasmas['Classificação de Risco'] = '🔴 CRÍTICO: Conta Fantasma (Sem Vínculo RH)'

    return fantasmas