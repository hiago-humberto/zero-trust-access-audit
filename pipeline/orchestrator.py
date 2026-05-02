from pipeline.ingestion import carregar_dados
from pipeline.transformation import aplicar_regras_zero_trust
from pipeline.transformation import aplicar_regras_zero_trust, aplicar_regras_transferencias # Adicionei o import aqui

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