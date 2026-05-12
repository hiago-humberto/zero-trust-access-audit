from pipeline.ingestion import carregar_dados, ler_arquivo_seguro
from pipeline.transformation import aplicar_regras_zero_trust, aplicar_regras_transferencias, aplicar_regras_fantasmas
import pandas as pd

def rodar_auditoria(arquivo_desligados, arquivo_usuarios):
    df_desligados, df_usuarios = carregar_dados(arquivo_desligados, arquivo_usuarios)
    return aplicar_regras_zero_trust(df_desligados, df_usuarios)

def rodar_auditoria_transferencias(arquivo_transferidos, arquivo_usuarios):
    df_transferidos, df_usuarios = carregar_dados(arquivo_transferidos, arquivo_usuarios)
    return aplicar_regras_transferencias(df_transferidos, df_usuarios)

def rodar_auditoria_fantasmas(arquivo_ativos, arquivo_desligados, arquivo_usuarios):
    # Usando a nossa nova leitura blindada para os fantasmas
    df_ativos = ler_arquivo_seguro(arquivo_ativos)
    df_desligados = ler_arquivo_seguro(arquivo_desligados)
    df_usuarios = ler_arquivo_seguro(arquivo_usuarios)
    
    return aplicar_regras_fantasmas(df_ativos, df_desligados, df_usuarios)