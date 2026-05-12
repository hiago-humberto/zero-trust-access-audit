import pandas as pd

print("⏳ Fabricando massa de dados corrompida para teste de Auditoria...")

ativos = pd.DataFrame({
    "Matrícula": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    "Nome": ["Carlos Silva", "Maria Souza", "João Perez", "Ana Costa", "Lucas Almeida", "Fernanda Lima", "Pedro Rocha", "Juliana Mendes", "Roberto Alves", "Camila Ribeiro"],
    "Cargo": ["Gerente", "Analista", "Diretor", "Coordenador", "Estagiário", "Analista", "Assistente", "Gerente", "Diretor", "Coordenador"],
    "Área": ["Vendas", "RH", "Operações", "TI", "Marketing", "Financeiro", "Contábil", "Tributário", "TI", "Vendas"],
    "Data de Admissão": ["10/01/2015", "15/03/2018", "20/05/2010", "11/11/2019", "01/02/2023", "10/04/2020", "15/06/2021", "20/08/2016", "05/09/2012", "12/12/2018"]
})

desligados = pd.DataFrame({
    "Matrícula": [2001, 2002, 2003, 2004, 2005],
    "Nome": ["Marcos Gomes", "Luciana Faria", "Paulo Castro", "Beatriz Nunes", "Ricardo Dias"],
    "Cargo": ["Analista", "Assistente", "Gerente", "Estagiário", "Diretor"],
    "Área": ["TI", "RH", "Financeiro", "Vendas", "Operações"],
    "Data Desligamento": ["01/10/2023", "15/10/2023", "20/10/2023", "05/11/2023", "10/11/2023"]
})

transferidos = pd.DataFrame({
    "Matrícula": [3001, 3002, 3003, 3004, 3005],
    "Nome": ["Sandra Lopes", "Diego Martins", "Tatiana Silva", "Vitor Hugo", "Aline Barros"],
    "Cargo Origem": ["Analista", "Assistente", "Gerente", "Coordenador", "Estagiário"],
    "Área Origem": ["Tributário", "Vendas", "Operações", "Contábil", "RH"],
    "Data Transferência": ["01/09/2023", "15/09/2023", "20/09/2023", "05/10/2023", "10/10/2023"],
    "Cargo Destino": ["Analista", "Assistente", "Gerente", "Coordenador", "Assistente"],
    "Área Destino": ["Financeiro", "Marketing", "TI", "Tributário", "RH"]
})

usuarios = pd.DataFrame({
    "ID": ["TI1001", "RH1002", "TI2001", "RH2002", "FN2003", "TR3001", "VD3002", "TI9991", "VD9992"],
    "Módulo": ["RH;VENDAS", "RH", "RH;TI", "RH", "RH;FINANCEIRO", "RH;TRIBUTÁRIO;FINANCEIRO", "RH;MARKETING", "TI;FINANCEIRO;ADMIN", "VENDAS;RH"],
    "Status": ["Ativo", "Ativo", "Ativo", "Inativo", "Inativo", "Ativo", "Ativo", "Ativo", "Ativo"],
    "Data de Bloqueio": ["-", "-", "-", "30/10/2023", "21/10/2023", "-", "-", "-", "-"],
    "Data de Último Login": ["01/12/2023", "05/12/2023", "05/10/2023", "15/10/2023", "20/10/2023", "02/12/2023", "03/12/2023", "10/12/2023", "11/12/2023"]
})

# O segredo está aqui: sep='\t' garante que os arquivos nasçam com as abas corretas!
ativos.to_csv("Ativos_Teste_Sistema.txt", sep='\t', index=False)
desligados.to_csv("Desligados_Teste_Sistema.txt", sep='\t', index=False)
transferidos.to_csv("Transferidos_Teste_Sistema.txt", sep='\t', index=False)
usuarios.to_csv("Acessos_Teste_Sistema.txt", sep='\t', index=False)

print("✅ 4 Arquivos TXT gerados com sucesso na sua pasta!")