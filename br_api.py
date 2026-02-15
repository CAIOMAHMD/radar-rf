import requests

def buscar_dados_mercado():
    try:
        # Busca Selic Real (SGS 1178)
        r_selic = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados/ultimos/1?formato=json", timeout=10)
        selic = float(r_selic.json()[0]['valor'])
        
        # Busca IPCA Mensal (SGS 433)
        r_ipca = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/1?formato=json", timeout=10)
        ipca = float(r_ipca.json()[0]['valor'])

        # Simulação de taxas do Tesouro baseadas na Selic (Dinâmico)
        # Em 2026, com Selic alta, os prefixados e IPCA acompanham a curva
        taxas_tesouro = {
            'pre': round(selic - 1.5, 2),  # Ex: Selic 14% -> Pre 12.5%
            'ipca_fixo': 6.25,             # Taxa fixa padrão de proteção
            'selic_bonus': 0.05            # Taxa adicional do Tesouro Selic
        }

        return {
            'selic': selic,
            'ipca_mensal': ipca,
            'tesouro': taxas_tesouro,
            'status': 'Online'
        }
    except Exception as e:
        # Fallback de segurança caso o site do BC caia
        return {
            'selic': 14.0, 
            'ipca_mensal': 0.40, 
            'tesouro': {'pre': 12.5, 'ipca_fixo': 6.10, 'selic_bonus': 0.05},
            'status': 'Offline (Dados Estimados)'
        }