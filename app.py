# app.py - CÓDIGO COMPLETO PARA STREAMLIT CLOUD
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Organograma Motoristas Online",
    page_icon="🚚",
    layout="wide"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown('<div class="main-header">🚚 ORGANOGRAMA DE MOTORISTAS ONLINE</div>', unsafe_allow_html=True)
st.success("✅ **Sistema funcionando na nuvem!**")

# Inicializar banco de dados
def init_database():
    conn = sqlite3.connect('motoristas.db')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS motoristas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            situacao TEXT NOT NULL,
            status_trabalho TEXT,
            estado_motorista TEXT,
            categoria_cnh TEXT,
            localizacao TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Dados de exemplo
    motoristas_exemplo = [
        ('João Silva', 'TRABALHANDO', 'C/ATEND', 'DIRIGINDO', 'D', 'Base Centro'),
        ('Maria Santos', 'INTERJORNADA', 'S/ATEND', 'PARADO', 'E', 'Casa'),
        ('Pedro Oliveira', 'TRABALHANDO', 'C/VEICULO', 'Parado até 1h', 'C', 'Base Norte'),
        ('Ana Costa', 'TRABALHANDO', 'S/VEICULO', 'DIRIGINDO', 'B', 'Base Sul')
    ]
    
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR IGNORE INTO motoristas (nome, situacao, status_trabalho, estado_motorista, categoria_cnh, localizacao)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', motoristas_exemplo)
    
    conn.commit()
    return conn

# Interface principal
def main():
    conn = init_database()
    
    # Menu lateral
    st.sidebar.title("🎛️ Menu")
    opcao = st.sidebar.radio(
        "Navegação:",
        ["📊 Dashboard", "➕ Adicionar Motorista", "📈 Estatísticas"]
    )
    
    # Filtro
    filtro_situacao = st.sidebar.selectbox(
        "Filtrar por situação:",
        ["TODOS", "TRABALHANDO", "INTERJORNADA"]
    )
    
    if opcao == "📊 Dashboard":
        mostrar_dashboard(conn, filtro_situacao)
    elif opcao == "➕ Adicionar Motorista":
        adicionar_motorista(conn)
    elif opcao == "📈 Estatísticas":
        mostrar_estatisticas(conn)

def mostrar_dashboard(conn, filtro):
    st.header("📊 Dashboard de Motoristas")
    
    # Buscar dados
    query = "SELECT * FROM motoristas"
    if filtro != "TODOS":
        query += f" WHERE situacao = '{filtro}'"
    
    df_motoristas = pd.read_sql(query, conn)
    
    # Mostrar cards
    for _, motorista in df_motoristas.iterrows():
        cor = "#2ecc71" if motorista['situacao'] == 'TRABALHANDO' else "#3498db"
        
        st.markdown(f"""
        <div class="card" style="border-left-color: {cor}">
            <h3>🚗 {motorista['nome']}</h3>
            <strong>Situação:</strong> {motorista['situacao']} | 
            <strong>Status:</strong> {motorista['status_trabalho']}<br>
            <strong>Estado:</strong> {motorista['estado_motorista']} | 
            <strong>CNH:</strong> {motorista['categoria_cnh']}<br>
            <strong>Localização:</strong> {motorista['localizacao']}
        </div>
        """, unsafe_allow_html=True)

def adicionar_motorista(conn):
    st.header("➕ Adicionar Novo Motorista")
    
    with st.form("form_motorista"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo")
            situacao = st.selectbox("Situação", ["TRABALHANDO", "INTERJORNADA"])
            status_trabalho = st.selectbox("Status", ["C/ATEND", "S/ATEND", "C/VEICULO", "S/VEICULO"])
        
        with col2:
            estado = st.selectbox("Estado", ["DIRIGINDO", "PARADO", "Parado até 1h", "Parado até 2h"])
            categoria_cnh = st.selectbox("CNH", ["A", "B", "C", "D", "E"])
            localizacao = st.text_input("Localização")
        
        if st.form_submit_button("💾 Salvar Motorista"):
            if nome:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO motoristas (nome, situacao, status_trabalho, estado_motorista, categoria_cnh, localizacao)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (nome, situacao, status_trabalho, estado, categoria_cnh, localizacao))
                conn.commit()
                st.success(f"✅ Motorista {nome} adicionado com sucesso!")
            else:
                st.error("❌ Preencha o nome do motorista")

def mostrar_estatisticas(conn):
    st.header("📈 Estatísticas")
    
    df_motoristas = pd.read_sql("SELECT * FROM motoristas", conn)
    
    if not df_motoristas.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(df_motoristas)
        trabalhando = len(df_motoristas[df_motoristas['situacao'] == 'TRABALHANDO'])
        interjornada = len(df_motoristas[df_motoristas['situacao'] == 'INTERJORNADA'])
        
        col1.metric("Total Motoristas", total)
        col2.metric("Trabalhando", trabalhando)
        col3.metric("Interjornada", interjornada)
        col4.metric("Disponibilidade", f"{(trabalhando/total*100):.1f}%")
        
        # Gráfico de distribuição
        st.subheader("📊 Distribuição por Situação")
        dist_situacao = df_motoristas['situacao'].value_counts()
        st.bar_chart(dist_situacao)
        
        # Gráfico de CNH
        st.subheader("🚦 Distribuição por Categoria CNH")
        dist_cnh = df_motoristas['categoria_cnh'].value_counts()
        st.bar_chart(dist_cnh)
    else:
        st.warning("Nenhum motorista cadastrado.")

if __name__ == '__main__':
    main()