import streamlit as st
import time
import pandas as pd
from pipeline.orchestrator import rodar_auditoria

# Configuração da página corporativa
st.set_page_config(page_title="Zero Trust Audit Hub", page_icon="🛡️", layout="wide")

# Cabeçalho
st.markdown("<h1 style='text-align: center; color: #0D47A1;'>🛡️ Zero Trust Audit Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #555;'>Sistema Automatizado de Controles Internos e Segregação de Funções (SoD)</p>", unsafe_allow_html=True)
st.divider()

# Sidebar de Upload
st.sidebar.header("📁 Ingestão de Dados (Case 1)")
st.sidebar.markdown("Faça o upload dos arquivos para reperformar o controle.")
arquivo_desligados = st.sidebar.file_uploader("Base de Desligados (TXT)", type=['txt'])
arquivo_usuarios = st.sidebar.file_uploader("Acessos do Sistema (TXT)", type=['txt'])

# Motor de Execução
if arquivo_desligados and arquivo_usuarios:
    with st.spinner("Engrenagem de dados rodando as regras de Zero Trust..."):
        inicio = time.time()
        
        # Chama o nosso pipeline
        df_resultado = rodar_auditoria(arquivo_desligados, arquivo_usuarios)
        
        fim = time.time()
        tempo_execucao = fim - inicio

    st.success(f"✅ Auditoria de {len(df_resultado)} identidades concluída com sucesso em {tempo_execucao:.3f} segundos.")

    # Processamento de KPIs
    df_falhas = df_resultado[df_resultado['Classificação de Risco'] != '🟢 OK: Controle Efetivo']
    taxa_risco = (len(df_falhas) / len(df_resultado)) * 100 if len(df_resultado) > 0 else 0

    # Exibição dos KPIs (O que os gerentes amam ver)
    col1, col2, col3 = st.columns(3)
    col1.metric("Identidades Auditadas", len(df_resultado))
    col2.metric("Falhas de Controle Detectadas", len(df_falhas), delta_color="inverse")
    col3.metric("Taxa de Risco de Acessos", f"{taxa_risco:.1f}%")

    st.divider()

    # Tabela de Apontamentos (O Output da Auditoria)
    st.subheader("🚨 Matriz de Exceções (Apontamentos)")
    st.markdown("Abaixo estão os acessos indevidos encontrados que violam a política de desligamento.")
    
    colunas_exibicao = ['Matrícula', 'Nome', 'Cargo', 'Classificação de Risco', 'Data Desligamento', 'Data de Bloqueio', 'Data de Último Login', 'Status']
    st.dataframe(df_falhas[colunas_exibicao], use_container_width=True)

else:
    st.info("👈 Aguardando o upload dos arquivos 'Colaboradores_Desligados.txt' e 'Lista_deusuarios.txt' no menu lateral.")