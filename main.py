import requests
import pandas as pd

# Configurações de critérios (Baseado no seu perfil de Renda Variável)
CRITERIOS = {
    'FORTE_COMPRA_IPCA': 0.062, # 6.2% acima da inflação
    'COMPRA_IPCA': 0.058,       # 5.8% acima da inflação
    'QUALITY_MIN': 7            # Nota de qualidade para o Tesouro (Sempre 10)
}

def buscar_dados_tesouro():
    """Consome a API oficial do Tesouro Direto"""
    url = "https://www.tesourotransparente.gov.br/ckan/dataset/df5611b2-adfd-4fd5-940a-f5578f847737/resource/afc19704-591d-4c0f-950a-4df6c3cba072/download/TesouroDireto.csv"
    # Lendo o CSV diretamente do portal da transparência
    df = pd.read_csv(url, sep=';', decimal=',')
    return df

def filtrar_ultimas_taxas(df):
    """Pega apenas as taxas mais recentes de cada título"""
    df['Data Base'] = pd.to_datetime(df['Data Base'], dayfirst=True)
    ultima_data = df['Data Base'].max()
    return df[df['Data Base'] == ultima_data]

def classificar_oportunidade(row):
    """Sua lógica de decisão adaptada"""
    taxa = row['Taxa Compra Manha'] / 100
    nome = row['Tipo Titulo']
    
    if "IPCA" in nome:
        if taxa >= CRITERIOS['FORTE_COMPRA_IPCA']:
            return "🔥 FORTE COMPRA"
        elif taxa >= CRITERIOS['COMPRA_IPCA']:
            return "✅ COMPRA"
    
    return "⏳ AGUARDAR"

# --- Execução Principal ---
print("🛰️ Iniciando Radar de Renda Fixa...")
dados_brutos = buscar_dados_tesouro()
radar = filtrar_ultimas_taxas(dados_brutos)

# Aplicando a classificação
radar['Recomendacao'] = radar.apply(classificar_oportunidade, axis=1)

# Exibindo o que importa
colunas_foco = ['Tipo Titulo', 'Data Vencimento', 'Taxa Compra Manha', 'Recomendacao']
print(radar[colunas_foco].sort_values(by='Taxa Compra Manha', ascending=False))