import requests
import pandas as pd
from datetime import datetime

def buscar_dados_tesouro():
    # URL da API simplificada (B3)
    url = "https://www.tesourodireto.com.br/json/br/com/b3/tesourodireto/service/api/treasurybondsinfo.json"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        df = pd.DataFrame(data['response']['TrsrBondLts'])
        return df[['nm', 'anulYield', 'dtVct']]
    except:
        return pd.DataFrame()

def main():
    print(f"🛰️ RADAR RF | {datetime.now().strftime('%d/%m/%Y')}")
    df = buscar_dados_tesouro()
    if not df.empty:
        print(df.head())
    else:
        print("⚠️ O servidor local não conseguiu acessar os dados. Tentando via GitHub Actions...")

if __name__ == "__main__":
    main()