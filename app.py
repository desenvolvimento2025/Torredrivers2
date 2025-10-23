import streamlit as st
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime, timedelta
import time
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="Sistema de Motoristas",
    page_icon="🚗",
    layout="wide"
)

# Classe para gerenciamento de dados
class GerenciadorMotoristas:
    def __init__(self):
        self.arquivo_excel = "tabela-motoristas.xlsx"
        self.ultima_atualizacao = None
        self.dados = None
        self.colunas_principais = [
            'nome', 'usuario', 'grupo', 'empresa', 'filial', 'status', 
            'categoria', 'placa1', 'placa2', 'placa3', 'localiz-atual'
        ]
        
    def carregar_dados(self):
        """Carrega dados do arquivo Excel"""
        try:
            if os.path.exists(self.arquivo_excel):
                self.dados = pd.read_excel(self.arquivo_excel, sheet_name='motoristas')
                self.ultima_atualizacao = datetime.now()
                return True
            else:
                # Cria dataframe vazio com a estrutura correta
                colunas = [
                    'nome', 'usuario', 'grupo', 'empresa', 'filial', 'status', 'status1', 'status2', 'status3',
                    'com-atend', 'sem-atend', 'com-veiculo', 'sem-veiculo', 'com-check', 'sem-check', 'dirigindo', 'parado',
                    'parado-ate1h', 'parado1ate2h', 'parado-acima2h', 'jornada-acm80', 'jornada-exced', 'sem-folga-acm7d',
                    'sem-folga-acm12d', 'categoria', 'doc-vencendo', 'doc-vencido', 'localiz-atual', 'agenda-pro',
                    'agenda-anda', 'agenda-con', 'projeto-pro', 'projeto-anda', 'projeto-con', 'interj-menor8',
                    'interj-maior8', 'placa1', 'placa2', 'placa3', 'status-log1', 'status-log2'
                ]
                self.dados = pd.DataFrame(columns=colunas)
                self.salvar_dados()
                return True
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return False
    
    def salvar_dados(self):
        """Salva dados no arquivo Excel"""
        try:
            with pd.ExcelWriter(self.arquivo_excel, engine='openpyxl') as writer:
                self.dados.to_excel(writer, sheet_name='motoristas', index=False)
                # Cria sheet de logs vazia
                pd.DataFrame().to_excel(writer, sheet_name='logs', index=False)
            return True
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")
            return False
    
    def adicionar_motorista(self, dados_motorista):
        """Adiciona novo motorista"""
        try:
            novo_registro = pd.DataFrame([dados_motorista])
            self.dados = pd.concat([self.dados, novo_registro], ignore_index=True)
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao adicionar motorista: {e}")
            return False
    
    def atualizar_motorista(self, index, dados_motorista):
        """Atualiza motorista existente"""
        try:
            for coluna, valor in dados_motorista.items():
                self.dados.at[index, coluna] = valor
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao atualizar motorista: {e}")
            return False
    
    def excluir_motorista(self, index):
        """Exclui motorista"""
        try:
            self.dados = self.dados.drop(index).reset_index(drop=True)
            return self.salvar_dados()
        except Exception as e:
            st.error(f"Erro ao excluir motorista: {e}")
            return False

# Inicialização do gerenciador
@st.cache_resource
def get_gerenciador():
    return GerenciadorMotoristas()

gerenciador = get_gerenciador()

# Sidebar para navegação
st.sidebar.title("🚗 Sistema de Motoristas")
pagina = st.sidebar.selectbox(
    "Navegação",
    ["📊 Dashboard", "👥 Cadastrar Motorista", "✏️ Editar Motorista", "🗑️ Excluir Motorista", "📋 Lista Completa"]
)

# Auto-atualização a cada 1 hora
if 'ultima_atualizacao' not in st.session_state:
    st.session_state.ultima_atualizacao = datetime.now()

tempo_decorrido = datetime.now() - st.session_state.ultima_atualizacao
if tempo_decorrido.total_seconds() > 3600:  # 1 hora
    st.session_state.ultima_atualizacao = datetime.now()
    gerenciador.carregar_dados()
    st.rerun()

# Carrega dados
if gerenciador.dados is None:
    gerenciador.carregar_dados()

# Página: Dashboard
if pagina == "📊 Dashboard":
    st.title("📊 Dashboard de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_motoristas = len(gerenciador.dados)
            st.metric("Total de Motoristas", total_motoristas)
        
        with col2:
            ativos = len(gerenciador.dados[gerenciador.dados['status'] == 'Ativo'])
            st.metric("Motoristas Ativos", ativos)
        
        with col3:
            com_veiculo = len(gerenciador.dados[gerenciador.dados['com-veiculo'] == 'Sim'])
            st.metric("Com Veículo", com_veiculo)
        
        with col4:
            doc_vencido = len(gerenciador.dados[gerenciador.dados['doc-vencido'] == 'Sim'])
            st.metric("Docs Vencidos", doc_vencido)
        
        # Gráficos e estatísticas
        st.subheader("📈 Estatísticas")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'empresa' in gerenciador.dados.columns:
                empresa_count = gerenciador.dados['empresa'].value_counts()
                st.bar_chart(empresa_count)
        
        with col2:
            if 'status' in gerenciador.dados.columns:
                status_count = gerenciador.dados['status'].value_counts()
                st.bar_chart(status_count)
        
        # Tabela resumo
        st.subheader("📋 Resumo dos Motoristas")
        if not gerenciador.dados.empty:
            dados_resumo = gerenciador.dados[gerenciador.colunas_principais]
            st.dataframe(dados_resumo, use_container_width=True)
    
    else:
        st.info("Nenhum motorista cadastrado ainda.")

# Página: Cadastrar Motorista
elif pagina == "👥 Cadastrar Motorista":
    st.title("👥 Cadastrar Novo Motorista")
    
    with st.form("form_cadastro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo*")
            usuario = st.text_input("Usuário*")
            grupo = st.text_input("Grupo")
            empresa = st.text_input("Empresa*")
            filial = st.text_input("Filial")
        
        with col2:
            status = st.selectbox("Status*", ["Ativo", "Inativo", "Férias", "Afastado"])
            categoria = st.selectbox("Categoria CNH", ["A", "B", "C", "D", "E"])
            placa1 = st.text_input("Placa Principal")
            placa2 = st.text_input("Placa Secundária")
            placa3 = st.text_input("Placa Terciária")
        
        st.subheader("Informações Adicionais")
        col3, col4 = st.columns(2)
        
        with col3:
            com_veiculo = st.selectbox("Com Veículo", ["Sim", "Não"])
            doc_vencendo = st.selectbox("Documentação Vencendo", ["Sim", "Não"])
            doc_vencido = st.selectbox("Documentação Vencida", ["Sim", "Não"])
            localiz_atual = st.text_input("Localização Atual")
        
        with col4:
            dirigindo = st.selectbox("Dirigindo", ["Sim", "Não"])
            parado = st.selectbox("Parado", ["Sim", "Não"])
            com_atend = st.selectbox("Com Atendimento", ["Sim", "Não"])
            sem_atend = st.selectbox("Sem Atendimento", ["Sim", "Não"])
        
        submitted = st.form_submit_button("💾 Cadastrar Motorista")
        
        if submitted:
            if nome and usuario and empresa:
                dados_motorista = {
                    'nome': nome,
                    'usuario': usuario,
                    'grupo': grupo,
                    'empresa': empresa,
                    'filial': filial,
                    'status': status,
                    'categoria': categoria,
                    'placa1': placa1,
                    'placa2': placa2,
                    'placa3': placa3,
                    'com-veiculo': com_veiculo,
                    'doc-vencendo': doc_vencendo,
                    'doc-vencido': doc_vencido,
                    'localiz-atual': localiz_atual,
                    'dirigindo': dirigindo,
                    'parado': parado,
                    'com-atend': com_atend,
                    'sem-atend': sem_atend,
                    # Campos com valores padrão
                    'status1': '',
                    'status2': '',
                    'status3': '',
                    'sem-veiculo': 'Não' if com_veiculo == 'Sim' else 'Sim',
                    'com-check': 'Não',
                    'sem-check': 'Não',
                    'parado-ate1h': 'Não',
                    'parado1ate2h': 'Não',
                    'parado-acima2h': 'Não',
                    'jornada-acm80': 'Não',
                    'jornada-exced': 'Não',
                    'sem-folga-acm7d': 'Não',
                    'sem-folga-acm12d': 'Não',
                    'agenda-pro': '',
                    'agenda-anda': '',
                    'agenda-con': '',
                    'projeto-pro': '',
                    'projeto-anda': '',
                    'projeto-con': '',
                    'interj-menor8': '',
                    'interj-maior8': '',
                    'status-log1': '',
                    'status-log2': ''
                }
                
                if gerenciador.adicionar_motorista(dados_motorista):
                    st.success("✅ Motorista cadastrado com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Erro ao cadastrar motorista")
            else:
                st.warning("⚠️ Preencha os campos obrigatórios (Nome, Usuário, Empresa)")

# Página: Editar Motorista
elif pagina == "✏️ Editar Motorista":
    st.title("✏️ Editar Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        motorista_selecionado = st.selectbox(
            "Selecione o motorista para editar",
            gerenciador.dados['nome'].tolist()
        )
        
        if motorista_selecionado:
            index = gerenciador.dados[gerenciador.dados['nome'] == motorista_selecionado].index[0]
            motorista_data = gerenciador.dados.iloc[index]
            
            with st.form("form_edicao"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nome = st.text_input("Nome completo*", value=motorista_data.get('nome', ''))
                    usuario = st.text_input("Usuário*", value=motorista_data.get('usuario', ''))
                    grupo = st.text_input("Grupo", value=motorista_data.get('grupo', ''))
                    empresa = st.text_input("Empresa*", value=motorista_data.get('empresa', ''))
                    filial = st.text_input("Filial", value=motorista_data.get('filial', ''))
                
                with col2:
                    status = st.selectbox(
                        "Status*", 
                        ["Ativo", "Inativo", "Férias", "Afastado"],
                        index=["Ativo", "Inativo", "Férias", "Afastado"].index(motorista_data.get('status', 'Ativo'))
                    )
                    categoria = st.selectbox(
                        "Categoria CNH", 
                        ["A", "B", "C", "D", "E"],
                        index=["A", "B", "C", "D", "E"].index(motorista_data.get('categoria', 'B'))
                    )
                    placa1 = st.text_input("Placa Principal", value=motorista_data.get('placa1', ''))
                    placa2 = st.text_input("Placa Secundária", value=motorista_data.get('placa2', ''))
                    placa3 = st.text_input("Placa Terciária", value=motorista_data.get('placa3', ''))
                
                st.subheader("Informações Atuais")
                col3, col4 = st.columns(2)
                
                with col3:
                    com_veiculo = st.selectbox(
                        "Com Veículo", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('com-veiculo') == 'Sim' else 1
                    )
                    doc_vencendo = st.selectbox(
                        "Documentação Vencendo", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('doc-vencendo') == 'Sim' else 1
                    )
                    doc_vencido = st.selectbox(
                        "Documentação Vencida", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('doc-vencido') == 'Sim' else 1
                    )
                    localiz_atual = st.text_input("Localização Atual", value=motorista_data.get('localiz-atual', ''))
                
                with col4:
                    dirigindo = st.selectbox(
                        "Dirigindo", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('dirigindo') == 'Sim' else 1
                    )
                    parado = st.selectbox(
                        "Parado", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('parado') == 'Sim' else 1
                    )
                    com_atend = st.selectbox(
                        "Com Atendimento", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('com-atend') == 'Sim' else 1
                    )
                    sem_atend = st.selectbox(
                        "Sem Atendimento", 
                        ["Sim", "Não"],
                        index=0 if motorista_data.get('sem-atend') == 'Sim' else 1
                    )
                
                submitted = st.form_submit_button("💾 Atualizar Motorista")
                
                if submitted:
                    if nome and usuario and empresa:
                        dados_atualizados = {
                            'nome': nome,
                            'usuario': usuario,
                            'grupo': grupo,
                            'empresa': empresa,
                            'filial': filial,
                            'status': status,
                            'categoria': categoria,
                            'placa1': placa1,
                            'placa2': placa2,
                            'placa3': placa3,
                            'com-veiculo': com_veiculo,
                            'doc-vencendo': doc_vencendo,
                            'doc-vencido': doc_vencido,
                            'localiz-atual': localiz_atual,
                            'dirigindo': dirigindo,
                            'parado': parado,
                            'com-atend': com_atend,
                            'sem-atend': sem_atend,
                            'sem-veiculo': 'Não' if com_veiculo == 'Sim' else 'Sim'
                        }
                        
                        if gerenciador.atualizar_motorista(index, dados_atualizados):
                            st.success("✅ Motorista atualizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Erro ao atualizar motorista")
                    else:
                        st.warning("⚠️ Preencha os campos obrigatórios")
    else:
        st.info("Nenhum motorista cadastrado para editar.")

# Página: Excluir Motorista
elif pagina == "🗑️ Excluir Motorista":
    st.title("🗑️ Excluir Motorista")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        motorista_selecionado = st.selectbox(
            "Selecione o motorista para excluir",
            gerenciador.dados['nome'].tolist()
        )
        
        if motorista_selecionado:
            index = gerenciador.dados[gerenciador.dados['nome'] == motorista_selecionado].index[0]
            motorista_data = gerenciador.dados.iloc[index]
            
            st.warning("⚠️ Confirma a exclusão deste motorista?")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.write(f"**Nome:** {motorista_data.get('nome', '')}")
                st.write(f"**Usuário:** {motorista_data.get('usuario', '')}")
                st.write(f"**Empresa:** {motorista_data.get('empresa', '')}")
                st.write(f"**Status:** {motorista_data.get('status', '')}")
            
            col1, col2, col3 = st.columns(3)
            with col2:
                if st.button("🗑️ Confirmar Exclusão", type="primary"):
                    if gerenciador.excluir_motorista(index):
                        st.success("✅ Motorista excluído com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao excluir motorista")
    else:
        st.info("Nenhum motorista cadastrado.")

# Página: Lista Completa
elif pagina == "📋 Lista Completa":
    st.title("📋 Lista Completa de Motoristas")
    
    if gerenciador.dados is not None and not gerenciador.dados.empty:
        # Filtros
        st.subheader("🔍 Filtros")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            filtro_empresa = st.selectbox(
                "Empresa",
                ["Todas"] + gerenciador.dados['empresa'].unique().tolist()
            )
        
        with col2:
            filtro_status = st.selectbox(
                "Status",
                ["Todos"] + gerenciador.dados['status'].unique().tolist()
            )
        
        with col3:
            filtro_categoria = st.selectbox(
                "Categoria",
                ["Todas"] + gerenciador.dados['categoria'].unique().tolist()
            )
        
        with col4:
            filtro_veiculo = st.selectbox(
                "Com Veículo",
                ["Todos", "Sim", "Não"]
            )
        
        # Aplicar filtros
        dados_filtrados = gerenciador.dados.copy()
        
        if filtro_empresa != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['empresa'] == filtro_empresa]
        
        if filtro_status != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['status'] == filtro_status]
        
        if filtro_categoria != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados['categoria'] == filtro_categoria]
        
        if filtro_veiculo != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados['com-veiculo'] == filtro_veiculo]
        
        st.subheader(f"📊 Resultados ({len(dados_filtrados)} motoristas)")
        st.dataframe(dados_filtrados, use_container_width=True)
        
        # Botão de download
        if not dados_filtrados.empty:
            csv = dados_filtrados.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"motoristas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
    else:
        st.info("Nenhum motorista cadastrado.")

# Informações de atualização no sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("🔄 Atualização")
if gerenciador.ultima_atualizacao:
    st.sidebar.write(f"Última atualização: {gerenciador.ultima_atualizacao.strftime('%d/%m/%Y %H:%M')}")

if st.sidebar.button("🔄 Atualizar Agora"):
    gerenciador.carregar_dados()
    st.session_state.ultima_atualizacao = datetime.now()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("Sistema atualizado automaticamente a cada 1 hora")