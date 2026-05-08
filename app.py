import streamlit as st
import time
import pandas as pd
import io
import plotly.express as px

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
    st.markdown("Faça o upload de todas as bases para gerar o parecer consolidado e caçar Contas Fantasmas.")
    
    arquivo_desligados = st.sidebar.file_uploader("Base de Desligados (TXT)", type=['txt'])
    arquivo_transferidos = st.sidebar.file_uploader("Base de Transferidos (TXT)", type=['txt'])
    arquivo_ativos = st.sidebar.file_uploader("Base de Ativos (TXT)", type=['txt']) # O 4º Arquivo!
    arquivo_usuarios = st.sidebar.file_uploader("Acessos do Sistema (TXT)", type=['txt'])

    if arquivo_desligados and arquivo_transferidos and arquivo_ativos and arquivo_usuarios:
        with st.spinner("Processando Motor Zero Trust e rastreando contas fantasmas..."):
            inicio = time.time()
            
            # Importa o novo orquestrador
            from pipeline.orchestrator import rodar_auditoria_fantasmas
            
            # REBOBINA OS ARQUIVOS E RODA AUDITORIA 1
            arquivo_desligados.seek(0)
            arquivo_usuarios.seek(0)
            df_resultado_desligados = rodar_auditoria(arquivo_desligados, arquivo_usuarios)
            
            # REBOBINA E RODA AUDITORIA 2
            arquivo_transferidos.seek(0)
            arquivo_usuarios.seek(0)
            df_resultado_transferidos = rodar_auditoria_transferencias(arquivo_transferidos, arquivo_usuarios)
            
            # REBOBINA E RODA AUDITORIA 3 (A CAÇA AOS FANTASMAS)
            arquivo_ativos.seek(0)
            arquivo_desligados.seek(0)
            arquivo_usuarios.seek(0)
            df_falhas_fantasmas = rodar_auditoria_fantasmas(arquivo_ativos, arquivo_desligados, arquivo_usuarios)
            
            # Filtra apenas as falhas dos dois primeiros (o de fantasmas já traz só as falhas)
            df_falhas_desl = df_resultado_desligados[df_resultado_desligados['Classificação de Risco'] != '🟢 OK']
            df_falhas_transf = df_resultado_transferidos[df_resultado_transferidos['Classificação de Risco'] != '🟢 OK']
            
            tempo_execucao = time.time() - inicio

        st.success(f"✅ Auditoria Master concluída em {tempo_execucao:.3f} segundos.")
        
        # Resumo Executivo com 3 colunas agora!
        col1, col2, col3 = st.columns(3)
        col1.metric("🚨 Falhas de Desligamentos", len(df_falhas_desl))
        col2.metric("🚨 Conflitos de Transferência", len(df_falhas_transf))
        col3.metric("👻 Contas Fantasmas", len(df_falhas_fantasmas))
        
        st.divider()
        st.subheader("📊 Mapa de Calor de Riscos por Área")
        
        # Unificando falhas para o gráfico
        df_todas_falhas = pd.concat([
            df_falhas_desl[['Area_Risco', 'Classificação de Risco']],
            df_falhas_transf[['Area_Risco', 'Classificação de Risco']],
            df_falhas_fantasmas[['Area_Risco', 'Classificação de Risco']]
        ])
        
        if not df_todas_falhas.empty:
            # Agrupando dados para o gráfico
            chart_data = df_todas_falhas.groupby(['Area_Risco', 'Classificação de Risco']).size().reset_index(name='Quantidade')
            
            fig = px.bar(chart_data, x='Area_Risco', y='Quantidade', color='Classificação de Risco',
                         title="Concentração de Riscos por Departamento",
                         labels={'Area_Risco': 'Departamento', 'Quantidade': 'Nº de Incidentes'},
                         barmode='stack', color_discrete_sequence=["#D32F2F", "#F57C00"])
            
            st.plotly_chart(fig, use_container_width=True)
            
            # INSIGHT PARA O LÍDER ( Storytelling Genial)
            area_perigosa = chart_data.groupby('Area_Risco')['Quantidade'].sum().idxmax()
            st.warning(f"⚠️ **Insight para Liderança:** O departamento de **{area_perigosa}** apresenta o maior volume de inconformidades. Recomenda-se revisão imediata dos processos de aprovação desta área.")
        else:
            st.success("Nenhum risco detectado nas áreas analisadas.")
        # GERADOR DO EXCEL MULTI-ABAS
        st.subheader("📥 Exportar Parecer de Auditoria")
        st.markdown("Baixe o relatório consolidado em Excel contendo as 3 abas de risco.")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Aba 1
            colunas_desl = ['Matrícula', 'Nome', 'Cargo', 'Classificação de Risco', 'Data Desligamento', 'Data de Bloqueio', 'Data de Último Login']
            df_falhas_desl[colunas_desl].to_excel(writer, sheet_name='Risco_Desligamentos', index=False)
            
            # Aba 2
            colunas_transf = ['Matrícula', 'Nome', 'Cargo Destino', 'Área Origem', 'Área Destino', 'Módulo', 'Classificação de Risco']
            df_falhas_transf[colunas_transf].to_excel(writer, sheet_name='Risco_Transferencias', index=False)
            
            # Aba 3 (Nova)
            colunas_fantasma = ['ID', 'Módulo', 'Data de Último Login', 'Status', 'Classificação de Risco']
            df_falhas_fantasmas[colunas_fantasma].to_excel(writer, sheet_name='Risco_Fantasmas', index=False)
            
        st.download_button(
            label="📊 Baixar Relatório Master (Excel)",
            data=buffer.getvalue(),
            file_name="Parecer_Auditoria_ZeroTrust.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )