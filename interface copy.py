import streamlit as st
import pandas as pd
import datetime
import br_api
import motor_analista
import ia_analista

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Radar RF Terminal", page_icon="🏦", layout="wide")

# --- ESTILO CSS PROFISSIONAL (DARK MODE CUSTOM) ---
st.markdown("""
    <style>
    /* Fundo e Texto Geral */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Metricas / Cards */
    [data-testid="stMetric"] {
        background-color: #1c202a;
        border: 1px solid #2d323e;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-family: 'Courier New', monospace; }
    [data-testid="stMetricLabel"] { color: #808495 !important; font-size: 1rem; }

    /* Inputs e Tabelas */
    .stNumberInput, .stDataEditor {
        background-color: #1c202a !important;
        border-radius: 10px;
    }

    /* Botão Principal */
    .stButton>button {
        background: linear-gradient(135deg, #00ff88 0%, #00bd68 100%);
        color: #0e1117 !important;
        font-weight: bold;
        border: none;
        padding: 12px 30px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,255,136,0.3);
    }

    /* Divisores */
    hr { border: 0; height: 1px; background: linear-gradient(to right, #1c202a, #00ff88, #1c202a); }
    </style>
    """, unsafe_allow_html=True)

# --- CARREGAMENTO DE DADOS ---
@st.cache_data(ttl=3600) # Faz cache por 1 hora para não sobrecarregar a API
def carregar_dados():
    return br_api.buscar_dados_mercado()

mercado = carregar_dados()
dados_t = mercado['tesouro']

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🏦 Terminal de Oportunidades RF")
    st.caption(f"Sincronizado via Banco Central & Tesouro Direto | {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
with c2:
    v_invest = st.number_input("Capital para Aporte (R$)", value=10000.0, step=1000.0)

# --- DASHBOARD DE INDICADORES ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Taxa Selic", f"{mercado['selic']}%")
with col2:
    st.metric("Inflação IPCA", f"{mercado['ipca_mensal']}%")
with col3:
    if st.button("🤖 IA: SCANNER DE RISCO"):
        st.session_state.clima = ia_analista.avaliar_clima_politico()
    clima = st.session_state.get('clima', 'BAIXA')
    st.metric("Clima de Mercado", "⚠️ ESTRESSE" if clima == "ALTA" else "✅ ESTÁVEL")
with col4:
    p_dias = st.selectbox("Prazo Desejado (Dias)", [180, 360, 720, 1080], index=1)

st.divider()

# --- PRATELEIRA DINÂMICA ---
st.subheader("💡 Grade de Títulos (Taxas Atuais)")
if 'grade_viva' not in st.session_state:
    st.session_state.grade_viva = pd.DataFrame([
        {'Ativo': 'Tesouro Selic', 'Taxa %': 100.0 + dados_t['selic_bonus'], 'Tipo': 'POS (CDI)', 'Quality': 10},
        {'Ativo': 'Tesouro Prefixado', 'Taxa %': dados_t['pre'], 'Tipo': 'PRE', 'Quality': 10},
        {'Ativo': 'Tesouro IPCA+', 'Taxa %': dados_t['ipca_fixo'], 'Tipo': 'IPCA_MAIS', 'Quality': 10},
        {'Ativo': 'CDB Banco Digital', 'Taxa %': 110.0, 'Tipo': 'POS (CDI)', 'Quality': 8},
        {'Ativo': 'LCA/LCI Isenta', 'Taxa %': 92.0, 'Tipo': 'ISENTO (CDI)', 'Quality': 9},
        {'Ativo': 'CRA/CRI Corporativo', 'Taxa %': 94.0, 'Tipo': 'ISENTO (CDI)', 'Quality': 7}
    ])

df_editado = st.data_editor(st.session_state.grade_viva, use_container_width=True, num_rows="dynamic")
st.session_state.grade_viva = df_editado 

# --- CÁLCULOS E RESULTADOS ---
if st.button("🚀 PROCESSAR ANÁLISE QUANTITATIVA", use_container_width=True):
    def calcular_ir(d):
        if d <= 180: return 0.225
        if d <= 360: return 0.20
        if d <= 720: return 0.175
        return 0.15

    ir_v = calcular_ir(p_dias)
    analise = []

    for _, row in df_editado.iterrows():
        if pd.isna(row['Ativo']): continue
        
        # Lógica de Rentabilidade
        if "CDI" in str(row['Tipo']):
            t_anual = (row['Taxa %'] * mercado['selic'] / 100)
        elif row['Tipo'] == "PRE":
            t_anual = row['Taxa %']
        else:
            inf_anual = ((1 + (mercado['ipca_mensal']/100))**12 - 1) * 100
            t_anual = row['Taxa %'] + inf_anual

        isento = "ISENTO" in str(row['Tipo'])
        aliquota = 0 if isento else ir_v
        v_liquido = v_invest * ((1 + (t_anual / 100)) ** (p_dias / 360))
        v_liquido = v_liquido - ((v_liquido - v_invest) * aliquota)
        
        # Inteligência Adicional
        taxa_eq = motor_analista.calcular_taxa_equivalente(row['Taxa %'], row['Tipo'], p_dias)
        j_real = motor_analista.calcular_juro_real(t_anual, mercado['ipca_mensal'])
        veredito = motor_analista.calcular_status_ativo(row, mercado, clima)

        analise.append({
            'Ativo': row['Ativo'],
            'Equiv. CDB': f"{taxa_eq}% CDI",
            'Juro Real': f"{j_real}%",
            'Lucro (R$)': v_liquido - v_invest,
            'Valor Final': v_liquido,
            'Veredito': veredito
        })

    df_res = pd.DataFrame(analise).sort_values(by='Valor Final', ascending=False)

    st.divider()
    res1, res2 = st.columns([2, 1])
    
    with res1:
        st.subheader("📊 Ranking de Rentabilidade Líquida")
        st.dataframe(
            df_res.style.format({'Lucro (R$)': 'R$ {:.2f}', 'Valor Final': 'R$ {:.2f}'})
            .highlight_max(subset=['Valor Final'], color='#004d2b'),
            use_container_width=True
        )
    with res2:
        st.subheader("🏆 Gráfico de Lucro Limpo")
        st.bar_chart(df_res.set_index('Ativo')['Lucro (R$)'])

    st.success(f"Analise Finalizada: Imposto de Renda de {ir_v*100}% aplicado para o prazo de {p_dias} dias.")

# --- SEÇÃO DE LEGENDA E CONCEITOS ---
st.divider()
with st.expander("📖 Guia Rápido: O que são esses ativos?"):
    l1, l2, l3 = st.columns(3)
    
    with l1:
        st.markdown("""
        ### 🏢 Crédito Privado (CRA/CRI)
        * **O que é:** Empréstimo para empresas do setor Agrícola (CRA) ou Imobiliário (CRI).
        * **Risco:** Não tem FGC. Depende da saúde da empresa.
        * **Vantagem:** Isenção total de Imposto de Renda.
        """)
        
    with l2:
        st.markdown("""
        ### 🏦 Bancários (CDB/LCI/LCA)
        * **CDB:** Empréstimo para o banco. Tem Imposto de Renda.
        * **LCI/LCA:** Empréstimo para o setor imobiliário/agro via banco. **Isento de IR**.
        * **Garantia:** Protegidos pelo **FGC** até R$ 250 mil.
        """)
        
    with l3:
        st.markdown("""
        ### 🏛️ Títulos Públicos (Tesouro)
        * **Selic:** Acompanha os juros. Ideal para reserva.
        * **Prefixado:** Taxa travada. Bom se os juros caírem.
        * **IPCA+:** Ganho real. Protege seu poder de compra contra a inflação.
        """)