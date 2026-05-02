from pipeline.ingestion import carregar_dados
from pipeline.transformation import aplicar_regras_zero_trust

def rodar_auditoria(arquivo_desligados, arquivo_usuarios):
    # 1. Extrai
    df_desligados, df_usuarios = carregar_dados(arquivo_desligados, arquivo_usuarios)
    
    # 2. Transforma e Audita
    df_auditado = aplicar_regras_zero_trust(df_desligados, df_usuarios)
    
    return df_auditado