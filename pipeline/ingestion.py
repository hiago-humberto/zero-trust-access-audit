import pandas as pd
import streamlit as st

def ler_arquivo_seguro(arquivo):
    try:
        # Tenta ler com UTF-8 (padrão do nosso gerador Python)
        df = pd.read_csv(arquivo, sep='\t', encoding='utf-8')
    except Exception:
        # Se der erro, rebobina a fita e tenta Latin-1 (padrão de empresa de exemplo)
        arquivo.seek(0)
        df = pd.read_csv(arquivo, sep='\t', encoding='latin-1')
    
    # Limpeza ninja: tira espaços invisíveis perdidos nos cabeçalhos
    df.columns = df.columns.str.strip()
    return df

def carregar_dados(arquivo_desligados, arquivo_usuarios):
    df_desligados = ler_arquivo_seguro(arquivo_desligados)
    df_usuarios = ler_arquivo_seguro(arquivo_usuarios)
    return df_desligados, df_usuarios