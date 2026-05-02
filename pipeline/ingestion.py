import pandas as pd
import streamlit as st

@st.cache_data # Faz cache na memória para a tela não recarregar do zero toda hora
def carregar_dados(arquivo_desligados, arquivo_usuarios):
    # O Streamlit entrega o upload como um arquivo, o Pandas lê direto!
    df_desligados = pd.read_csv(arquivo_desligados, sep='\t', encoding='latin-1')
    df_usuarios = pd.read_csv(arquivo_usuarios, sep='\t', encoding='latin-1')
    
    return df_desligados, df_usuarios