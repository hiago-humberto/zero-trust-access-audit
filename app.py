import streamlit as st
import time
import pandas as pd
import io
from pipeline.orchestrator import rodar_auditoria, rodar_auditoria_transferencias

st.set_page_config(page_title="Zero Trust Audit Hub", page_icon="🛡️", layout="wide")

st.markdown("<h1 style='text-align: center; color: #0D47A1;'>🛡️ Zero Trust Audit Hub</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2em; color: #555;'>Sistema Automatizado de Controles Internos e Segregação de Funções (SoD)</p>", unsafe_allow_html=True)
st.divider()

# O SEGREDO DO DESIGN: Menu de Navegação Lateral
modo_auditoria = st.sidebar.radio(
    "📌 Selecione a Política de Auditoria:",
    ("1. Revogação de Acessos (Desligados)", "2. Revisão de Acessos (Transferidos)", "3. Auditoria Completa (Consolidada)")
)

st.sidebar.divider()
st.sidebar.header("📁 Ingestão de Dados")

# Renderização Condicional da Tela
if modo_auditoria == "1. Revogação de Acessos (Desligados)":
    st.subheader("Auditoria de Desligamentos (Offboarding)")
    arquivo_base = st.sidebar.file_uploader("Base de Desligados (TXT)", type=['txt'])
    arquivo_usuarios = st.sidebar.file_uploader("Acessos do Sistema (TXT)", type=['txt'])

    if arquivo_base and arquivo_usuarios:
        with st.spinner("Analisando logs de bloqueio e acessos póstumos..."):
            inicio = time.time()
            df_resultado = rodar_auditoria(arquivo_base, arquivo_usuarios)
            tempo_execucao = time.time() - inicio

        st.success(f"✅ Auditoria concluída em {tempo_execucao:.3f} segundos.")
        df_falhas = df_resultado[df_resultado['Classificação de Risco'] != '🟢 OK: Controle Efetivo']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Identidades Auditadas", len(df_resultado))
        col2.metric("Falhas Detectadas", len(df_falhas), delta_color="inverse")
        col3.metric("Taxa de Risco", f"{(len(df_falhas) / len(df_resultado)) * 100:.1f}%" if len(df_resultado) > 0 else "0%")

        st.dataframe(df_falhas[['Matrícula', 'Nome', 'Cargo', 'Classificação de Risco', 'Data Desligamento', 'Data de Bloqueio', 'Data de Último Login']], use_container_width=True)

elif modo_auditoria == "2. Revisão de Acessos (Transferidos)":
    st.subheader("Auditoria de Transferências (Segregação de Funções)")
    arquivo_base = st.sidebar.file_uploader("Base de Transferidos (TXT)", type=['txt'])
    arquivo_usuarios = st.sidebar.file_uploader("Acessos do Sistema (TXT)", type=['txt'])

    if arquivo_base and arquivo_usuarios:
        with st.spinner("Analisando matriz de perfis e conflitos de módulo..."):
            inicio = time.time()
            df_resultado = rodar_auditoria_transferencias(arquivo_base, arquivo_usuarios)
            tempo_execucao = time.time() - inicio

        st.success(f"✅ Auditoria concluída em {tempo_execucao:.3f} segundos.")
        df_falhas = df_resultado[df_resultado['Classificação de Risco'] != '🟢 OK: Controle Efetivo']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Colaboradores Transferidos", len(df_resultado))
        col2.metric("Conflitos SoD Detectados", len(df_falhas), delta_color="inverse")
        col3.metric("Taxa de Risco", f"{(len(df_falhas) / len(df_resultado)) * 100:.1f}%" if len(df_resultado) > 0 else "0%")

        st.dataframe(df_falhas[['Matrícula', 'Nome', 'Cargo Destino', 'Área Origem', 'Área Destino', 'Módulo', 'Classificação de Risco']], use_container_width=True)

elif modo_auditoria == "3. Auditoria Completa (Consolidada)":
    st.subheader("Auditoria Master (ITGC Completo)")
    st.markdown("Faça o upload de todas as bases para gerar o parecer consolidado.")
    
    arquivo_desligados = st.sidebar.file_uploader("Base de Desligados (TXT)", type=['txt'])
    arquivo_transferidos = st.sidebar.file_uploader("Base de Transferidos (TXT)", type=['txt'])
    arquivo_usuarios = st.sidebar.file_uploader("Acessos do Sistema (TXT)", type=['txt'])

    if arquivo_desligados and arquivo_transferidos and arquivo_usuarios:
        with st.spinner("Processando Motor Zero Trust para todas as identidades..."):
            inicio = time.time()
            
            # Roda as duas auditorias simultaneamente
            df_resultado_desligados = rodar_auditoria(arquivo_desligados, arquivo_usuarios)
            df_resultado_transferidos = rodar_auditoria_transferencias(arquivo_transferidos, arquivo_usuarios)
            
            # Filtra apenas as falhas
            df_falhas_desl = df_resultado_desligados[df_resultado_desligados['Classificação de Risco'] != '🟢 OK: Controle Efetivo']
            df_falhas_transf = df_resultado_transferidos[df_resultado_transferidos['Classificação de Risco'] != '🟢 OK: Controle Efetivo']
            
            tempo_execucao = time.time() - inicio

        st.success(f"✅ Auditoria Master concluída em {tempo_execucao:.3f} segundos.")
        
        # Resumo Executivo
        col1, col2 = st.columns(2)
        col1.metric("🚨 Falhas em Desligamentos", len(df_falhas_desl))
        col2.metric("🚨 Conflitos de Transferência (SoD)", len(df_falhas_transf))
        
        st.divider()
        
        # GERADOR DO EXCEL MULTI-ABAS
        st.subheader("📥 Exportar Parecer de Auditoria")
        st.markdown("Baixe o relatório consolidado em Excel contendo as abas detalhadas de cada risco.")
        
        # Cria o arquivo em memória
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Salva aba 1
            colunas_desl = ['Matrícula', 'Nome', 'Cargo', 'Classificação de Risco', 'Data Desligamento', 'Data de Bloqueio', 'Data de Último Login']
            df_falhas_desl[colunas_desl].to_excel(writer, sheet_name='Risco_Desligamentos', index=False)
            
            # Salva aba 2
            colunas_transf = ['Matrícula', 'Nome', 'Cargo Destino', 'Área Origem', 'Área Destino', 'Módulo', 'Classificação de Risco']
            df_falhas_transf[colunas_transf].to_excel(writer, sheet_name='Risco_Transferencias', index=False)
            
        # Botão de Download Mágico do Streamlit
        st.download_button(
            label="📊 Baixar Relatório Master (Excel)",
            data=buffer.getvalue(),
            file_name="Parecer_Auditoria_ZeroTrust.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )