import pandas as pd

class AnalisadorCredito:
    def __init__(self):
        # Aqui você carregaria o CSV do Banco Central (IF.DATA)
        # Para o exemplo, vamos usar um dicionário que simula a base de dados
        self.base_bancos = {
            'Itaú': {'basileia': 14.7, 'imobilizacao': 18.5, 'lucro': True},
            'Banco Master': {'basileia': 11.2, 'imobilizacao': 12.0, 'lucro': True},
            'Banco XP': {'basileia': 18.0, 'imobilizacao': 5.0, 'lucro': True},
            'Banco ABC': {'basileia': 15.5, 'imobilizacao': 1.0, 'lucro': True},
        }

    def calcular_quality(self, nome_banco):
        if nome_banco not in self.base_bancos:
            return 0 # Banco desconhecido = Risco máximo (Score 0)
        
        dados = self.base_bancos[nome_banco]
        score = 0
        
        # --- Critério 1: Índice de Basileia (Segurança de Capital) ---
        # Mínimo exigido pelo BC é 11%
        if dados['basileia'] > 15:
            score += 5
        elif dados['basileia'] >= 11:
            score += 3
            
        # --- Critério 2: Índice de Imobilização (Liquidez do Patrimônio) ---
        # Menos é melhor (ideal abaixo de 50%)
        if dados['imobilizacao'] < 20:
            score += 3
        elif dados['imobilizacao'] < 50:
            score += 1
            
        # --- Critério 3: Lucratividade ---
        if dados['lucro']:
            score += 2
            
        return score

    def filtrar_forte_compra(self, nome_banco, taxa_oferecida, benchmark_cdi):
        quality = self.calcular_quality(nome_banco)
        
        # Aplicando seus critérios de 'Forte Compra'
        # Quality >= 7 e Taxa atraente (Ex: 120% do CDI)
        if quality >= 7 and taxa_oferecida >= (benchmark_cdi * 1.20):
            return "🔥 FORTE COMPRA (High Quality + Premium)"
        elif quality >= 7 and taxa_oferecida >= (benchmark_cdi * 1.10):
            return "✅ COMPRA (Safe Choice)"
        elif quality < 7 and taxa_oferecida >= (benchmark_cdi * 1.30):
            return "⚠️ ESPECULATIVO (High Yield / Low Quality)"
        
        return "⏳ AGUARDAR"

# Testando o motor de busca
if __name__ == "__main__":
    analisador = AnalisadorCredito()
    resultado = analisador.filtrar_forte_compra('Banco ABC', 1.25, 1.0) # 125% do CDI
    print(f"Resultado para Banco ABC: {resultado}")