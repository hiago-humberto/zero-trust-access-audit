from pipeline.ingestion import carregar_dados
from pipeline.transformation import aplicar_regras_zero_trust
from pipeline.transformation import aplicar_regras_zero_trust, aplicar_regras_transferencias, aplicar_regras_fantasmas # Adicionei o import aqui
import pandas as pd

def rodar_auditoria(arquivo_desligados, arquivo_usuarios):
    # 1. Extrai
    df_desligados, df_usuarios = carregar_dados(arquivo_desligados, arquivo_usuarios)
    
    # 2. Transforma e Audita
    df_auditado = aplicar_regras_zero_trust(df_desligados, df_usuarios)
    
    return df_auditado

#  Orquestrador do Case 2
def rodar_auditoria_transferencias(arquivo_transferidos, arquivo_usuarios):
    df_transferidos, df_usuarios = carregar_dados(arquivo_transferidos, arquivo_usuarios)
    return aplicar_regras_transferencias(df_transferidos, df_usuarios)

# NOVO: Orquestrador de Contas Fantasmas
def rodar_auditoria_fantasmas(arquivo_ativos, arquivo_desligados, arquivo_usuarios):
    # Lendo direto aqui para simplificar a ingestão tripla
    df_ativos = pd.read_csv(arquivo_ativos, sep='\t', encoding='latin-1')
    df_desligados = pd.read_csv(arquivo_desligados, sep='\t', encoding='latin-1')
    df_usuarios = pd.read_csv(arquivo_usuarios, sep='\t', encoding='latin-1')
    
    return aplicar_regras_fantasmas(df_ativos, df_desligados, df_usuarios)