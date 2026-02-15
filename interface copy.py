import streamlit as st
import pandas as pd
import datetime
import br_api
import motor_analista
import ia_analista

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Radar RF Dinâmico", page_icon="🛰️", layout="wide")

# --- BUSCA DE DADOS INICIAL ---
with st.spinner("Sincronizando taxas de mercado..."):
    mercado = br_api.buscar_dados_mercado()
    dados_t = mercado['tesouro']

# --- HEADER ---
st.title("🛰️ Radar de Oportunidades Inteligente")
st.markdown(f"**Status das Taxas:** {mercado['status']} | Atualizado em: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")

# --- DASHBOARD DE INDICADORES ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Selic Atual", f"{mercado['selic']}%")
with col2:
    st.metric("IPCA Mensal", f"{mercado['ipca_mensal']}%")
with col3:
    if st.button("🤖 IA: Analisar Cenário"):
        st.session_state.clima = ia_analista.avaliar_clima_politico()
    clima = st.session_state.get('clima', 'BAIXA')
    st.metric("Risco Brasil", "🔥 ALTO" if clima == "ALTA" else "✅ ESTÁVEL")
with col4:
    v_invest = st.number_input("Valor do Aporte (R$)", value=1000.0, step=500.0)

st.divider()

# --- GRADE DE OPORTUNIDADES (DINÂMICA) ---
st.subheader("💡 Prateleira de Oportunidades (Baseada no Tesouro Nacional)")
st.caption("As taxas abaixo são carregadas automaticamente. Você pode ajustar conforme o que ver na sua corretora.")

# Se for a primeira vez, carrega os dados dinâmicos da API
if 'grade_viva' not in st.session_state:
    st.session_state.grade_viva = pd.DataFrame([
        {'Ativo': 'Tesouro Selic', 'Taxa %': 100.0 + dados_t['selic_bonus'], 'Tipo': 'POS (CDI)', 'Quality': 10},
        {'Ativo': 'Tesouro Prefixado', 'Taxa %': dados_t['pre'], 'Tipo': 'PRE', 'Quality': 10},
        {'Ativo': 'Tesouro IPCA+', 'Taxa %': dados_t['ipca_fixo'], 'Tipo': 'IPCA_MAIS', 'Quality': 10},
        {'Ativo': 'CDB Oportunidade (Ex: 110% CDI)', 'Taxa %': 110.0, 'Tipo': 'POS (CDI)', 'Quality': 8},
        {'Ativo': 'LCI/LCA Isenta (Ex: 92% CDI)', 'Taxa %': 92.0, 'Tipo': 'ISENTO (CDI)', 'Quality': 9}
    ])

# Editor de dados permite que o Caio altere se achar algo melhor no app
df_editado = st.data_editor(
    st.session_state.grade_viva, 
    use_container_width=True, 
    num_rows="dynamic",
    column_config={
        "Tipo": st.column_config.SelectboxColumn(
            "Tipo", options=["POS (CDI)", "ISENTO (CDI)", "PRE", "IPCA_MAIS", "ISENTO_IPCA"]
        )
    }
)
st.session_state.grade_viva = df_editado # Salva alterações da sessão

p_dias = st.select_slider("Prazo do Investimento (Dias)", options=[180, 360, 720, 1080], value=360)

# --- PROCESSAMENTO ---
if st.button("🚀 CALCULAR RENTABILIDADE REAL", use_container_width=True):
    def calcular_ir(d):
        if d <= 180: return 0.225
        if d <= 360: return 0.20
        if d <= 720: return 0.175
        return 0.15

    ir_v = calcular_ir(p_dias)
    resultados = []

    for _, row in df_editado.iterrows():
        if pd.isna(row['Ativo']): continue
        
        # Lógica de Rentabilidade Anual
        if "CDI" in str(row['Tipo']):
            t_anual = (row['Taxa %'] * mercado['selic'] / 100)
        elif row['Tipo'] == "PRE":
            t_anual = row['Taxa %']
        else: # IPCA_MAIS
            inf_anual = ((1 + (mercado['ipca_mensal']/100))**12 - 1) * 100
            t_anual = row['Taxa %'] + inf_anual

        # Cálculo de impostos e valores
        isento = "ISENTO" in str(row['Tipo'])
        aliquota = 0 if isento else ir_v
        v_bruto = v_invest * ((1 + (t_anual / 100)) ** (p_dias / 360))
        v_liquido = v_bruto - ((v_bruto - v_invest) * aliquota)
        
        # Juro Real e Veredito (Usando seus outros arquivos .py)
        j_real = motor_analista.calcular_juro_real(t_anual, mercado['ipca_mensal'])
        veredito = motor_analista.calcular_status_ativo(row, mercado, clima)

        resultados.append({
            'Ativo': row['Ativo'],
            'Juro Real (aa)': f"{j_real}%",
            'Valor Líquido': v_liquido,
            'Lucro Limpo': v_liquido - v_invest,
            'Veredito': veredito
        })

    df_final = pd.DataFrame(resultados).sort_values(by='Valor Líquido', ascending=False)

    # --- RESULTADOS VISUAIS ---
    st.divider()
    res1, res2 = st.columns([2, 1])
    with res1:
        st.subheader("📊 Ranking de Retorno")
        st.dataframe(
            df_final.style.format({'Valor Líquido': 'R$ {:.2f}', 'Lucro Limpo': 'R$ {:.2f}'})
            .highlight_max(subset=['Valor Líquido'], color='#095a33'),
            use_container_width=True
        )
    with res2:
        st.subheader("🏆 Onde você ganha mais?")
        st.bar_chart(df_final.set_index('Ativo')['Lucro Limpo'])