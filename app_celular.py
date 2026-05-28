import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Leitor WorldFree", page_icon="📱", layout="centered")

# --- CONEXÃO COM O GOOGLE SHEETS ---
@st.cache_resource
def conectar_google_sheets():
    try:
        escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', escopo)
        cliente = gspread.authorize(creds)
        
        # ⚠️ COLE O SEU LINK DA PLANILHA DENTRO DAS ASPAS ABAIXO:
        link_da_planilha = "https://docs.google.com/spreadsheets/d/1ZotMEJ4gdwWb47xedQqI83g0fpADxkCjp-H8FWN47jE/edit?usp=drive_link"
        
        planilha = cliente.open_by_url(link_da_planilha).worksheet("Bipes_Celular")
        return planilha
    except Exception as e:
        st.error(f"Erro ao conectar com a nuvem: {e}")
        return None

planilha = conectar_google_sheets()

# --- VARIÁVEIS DE SESSÃO PARA SALVAR A TELA ---
if 'bipes' not in st.session_state:
    st.session_state.bipes = []
if 'chave_salva' not in st.session_state:
    st.session_state.chave_salva = ""

# --- INTERFACE DO APLICATIVO ---
st.title("📦 WorldFree - Coletor")

# Lista de lojas (A mesma do sistema principal)
lista_lojas = [
    "CARREFOUR GALERIA(2)", "BANGU SHOPPING(3)", "RIO SHOPPING(4)", "GRANDE RIO SHOPPING(6)", 
    "PARK SHOPPING(8)", "NOVA AMERICA(9)", "TERESOPOLIS(10)", "BARRA SHOPPING(11)", 
    "PLAZA SHOPPING(12)", "MADUREIRA SHOPPING(14)", "ILHA PLAZA(16)", "LUXE(17)", 
    "NITEROI PLAZA(18)", "TIJUCA(19)", "PARK JACAREPAGUA(20)", "LUXE DIAMOND(21)", 
    "OUTLET SHOPPING(22)", "NS WORLD(23)", "LEBLON(24)", "LUXE RIBEIRÃO(25)"
]

loja = st.selectbox("Selecione sua Loja:", lista_lojas)

# Se já tiver uma chave digitada antes, mantém na tela
chave_nota = st.text_input("Chave da Nota Fiscal (44 dígitos):", value=st.session_state.chave_salva, max_chars=44)
st.session_state.chave_salva = chave_nota

st.divider()

st.subheader("📷 Leitura de Produtos")
st.info("💡 DICA: Toque no campo abaixo e use o ícone de 'Câmera/Escanear' do seu teclado para ler o código de barras super rápido!")

with st.form(key="form_bipe", clear_on_submit=True):
    ean = st.text_input("Código de Barras (EAN):")
    btn_enviar = st.form_submit_button("➕ Enviar Produto", use_container_width=True)

    if btn_enviar:
        if not chave_nota or len(chave_nota) != 44:
            st.warning("⚠️ Preencha a chave da nota corretamente (44 dígitos) antes de bipar!")
        elif not ean:
            st.warning("⚠️ O código de barras não pode estar vazio!")
        else:
            agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            novo_bipe = [agora, loja, chave_nota, ean]
            
            if planilha is not None:
                try:
                    # Envia para a aba "Bipes_Celular" na nuvem na mesma hora
                    planilha.append_row(novo_bipe)
                    
                    # Guarda na tela para a gerente ver que deu certo
                    st.session_state.bipes.append(ean)
                    st.success(f"✅ EAN {ean} guardado com sucesso!")
                    st.balloons() # Efeito visual de sucesso
                    
                except Exception as e:
                    st.error(f"❌ Erro ao enviar os dados. Tente novamente: {e}")
            else:
                st.error("❌ O sistema não conseguiu conectar à planilha. Verifique o link no código.")

# --- MOSTRAR RESUMO NA TELA ---
if st.session_state.bipes:
    st.success(f"📊 Total de peças lidas: {len(st.session_state.bipes)}")
    with st.expander("Ver itens já bipados"):
        for item in reversed(st.session_state.bipes):
            st.write(f"🛒 {item}")