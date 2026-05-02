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