import pandas as pd
import numpy as np

def processar_auditoria_desligados(df_desligados, df_acessos):
    """
    Motor de Auditoria Zero Trust: Cruza dados de RH e TI aplicando regras de ITGC.
    """
    
    # 1. Tratamento de Schema e Normalização (Sem quebrar o código)
    df_desligados['Data Desligamento'] = pd.to_datetime(df_desligados['Data Desligamento'], format='%d/%m/%Y', errors='coerce')
    df_acessos['Data de Bloqueio'] = pd.to_datetime(df_acessos['Data de Bloqueio'], format='%d/%m/%Y', errors='coerce')
    df_acessos['Data de Último Login'] = pd.to_datetime(df_acessos['Data de Último Login'], format='%d/%m/%Y', errors='coerce')
    
    # Extrair ID limpo da base de acessos (pois estava misturado com letras, ex: AC1212)
    # Pega apenas os números do ID do sistema para cruzar com a matrícula
    df_acessos['Matricula_Clean'] = df_acessos['ID'].str.extract('(\d+)').astype(float)
    df_desligados['Matrícula'] = df_desligados['Matrícula'].astype(float)

    # 2. O Cruzamento (Merge Vetorizado - Adeus iterrows!)
    df_cruzamento = pd.merge(
        df_desligados, 
        df_acessos, 
        left_on='Matrícula', 
        right_on='Matricula_Clean', 
        how='inner'
    )

    # 3. O Cérebro do Auditor: Aplicando as regras de negócio reais
    condicoes_risco = [
        # RISCO ALTO: Logou no sistema APÓS ser demitido
        (df_cruzamento['Data de Último Login'] > df_cruzamento['Data Desligamento']),
        
        # RISCO ALTO: Continua com status Ativo mesmo estando na lista de demitidos
        (df_cruzamento['Status'] == 'Ativo'),
        
        # RISCO MÉDIO (Falha de Controle): Bloqueio demorou mais que os 7 dias de contingência
        (df_cruzamento['Data de Bloqueio'] > df_cruzamento['Data Desligamento'] + pd.Timedelta(days=7))
    ]

    classificacoes = [
        '🔴 CRÍTICO: Acesso após Desligamento',
        '🔴 CRÍTICO: Usuário ainda Ativo',
        '🟠 MÉDIO: Bloqueio fora da SLA (> 7 dias)'
    ]

    # Aplica as regras: se não cair em nenhuma, o status é OK
    df_cruzamento['Classificação de Risco'] = np.select(condicoes_risco, classificacoes, default='🟢 OK: Controle Efetivo')

    # Filtra apenas as falhas (exclui os OKs) para o relatório final
    df_falhas = df_cruzamento[df_cruzamento['Classificação de Risco'] != '🟢 OK: Controle Efetivo']
    
    # Seleciona as colunas para o output de negócio
    colunas_finais = [
        'Matrícula', 'Nome', 'Cargo', 'Classificação de Risco', 
        'Data Desligamento', 'Data de Bloqueio', 'Data de Último Login', 'Status'
    ]
    
    return df_falhas[colunas_finais]

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