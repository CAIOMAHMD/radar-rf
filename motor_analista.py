def analisar_cenario(dados):
    s = dados['selic']
    i = dados['ipca_mensal']
    
    # Sua Tabela de Oportunidades
    if s > 12:
        return "🔥 CDI ALTO: Foco em Pós-fixados. Bancos Médios (Quality >= 7) para maximizar taxa."
    elif i > 0.5:
        return "🛡️ INFLAÇÃO SUBINDO: Hora de olhar títulos IPCA+ para proteger o poder de compra."
    else:
        return "⚖️ CENÁRIO ESTÁVEL: Diversificar entre Pós e Isentos."

def calcular_status_ativo(ativo, mercado, volatilidade):
    quality = ativo.get('Quality', 0)
    taxa = ativo.get('Taxa %', 0)
    tipo = ativo.get('Tipo', '')
    
    # 1. Filtro de Segurança (Seu critério salvo)
    if quality < 7:
        return "❌ REJEITADO (Risco Alto)"
    
    # 2. Lógica de Isentos (CRA/CRI/LCI/LCA)
    if "ISENTO" in tipo:
        if taxa >= 95: return "🚀 EXCELENTE (Prêmio Alto)"
        if taxa >= 90: return "🔥 FORTE COMPRA"
        return "✅ OK (Isento)"

    # 3. Lógica de Pós-Fixados (CDB)
    if "POS" in tipo:
        if taxa >= 115: return "🚀 EXCELENTE (Taxa Rara)"
        if taxa >= 110: return "✅ COMPRA (Acima da Média)"
        if quality == 10 and taxa >= 100: return "🛡️ RESERVA (Seguro)"
        return "🕒 MONITORAR"

    # 4. Lógica de Inflação e Prefixados (Marcação a Mercado)
    if tipo == "IPCA_MAIS":
        if taxa >= 6.0: return "💎 PROTEÇÃO PREMIUM"
        return "⚖️ ESTRATÉGICO"
        
    if tipo == "PRE":
        if volatilidade == "ALTA": return "⚠️ RISCO PRE (Evitar)"
        if taxa >= 13.0: return "🎯 OPORTUNIDADE PRE"
        return "✅ OK (Pre)"

    return "✅ OK"
# Mantendo suas outras funções
def calcular_juro_real(taxa_nominal, ipca_mensal):
    ipca_anual = (1 + (ipca_mensal/100))**12 - 1
    juro_real = ((1 + (taxa_nominal/100)) / (1 + ipca_anual)) - 1
    return round(juro_real * 100, 2)


def calcular_juro_real(taxa_nominal, ipca_mensal):
    # Transforma o IPCA mensal em anual aproximado
    ipca_anual = (1 + (ipca_mensal/100))**12 - 1
    # Equação de Fisher: (1 + r) = (1 + i) / (1 + f)
    juro_real = ((1 + (taxa_nominal/100)) / (1 + ipca_anual)) - 1
    return round(juro_real * 100, 2)

def definir_alerta_estresse(volatilidade="BAIXA"):
    # Sua tabela: Cenário Político/Estresse -> Comprar na volatilidade
    if volatilidade == "ALTA":
        return "⚠️ ESTRESSE POLÍTICO: Prêmios de risco elevados. Foco em liquidez ou Prefixados longos."
    return "✅ CENÁRIO ESTÁVEL: Seguir estratégia de carrego."

def calcular_taxa_equivalente(taxa, tipo, prazo_dias):
    # Se já é um CDB (POS), a equivalente é ela mesma
    if "POS" in tipo:
        return taxa
    
    # Se for ISENTO, precisamos descobrir qual CDB seria necessário para bater essa taxa
    if "ISENTO" in tipo:
        def obter_ir(d):
            if d <= 180: return 0.225
            if d <= 360: return 0.20
            if d <= 720: return 0.175
            return 0.15
        
        ir = obter_ir(prazo_dias)
        # Fórmula: Taxa Isenta / (1 - IR)
        equivalente = taxa / (1 - ir)
        return round(equivalente, 2)
    
    return taxa