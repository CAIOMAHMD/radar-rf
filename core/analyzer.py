def classificar_oportunidade(titulo):
    """
    Lógica adaptada dos seus critérios de Renda Variável
    """
    # 1. Filtro de Qualidade (Emissor/Rating)
    if titulo['quality'] < 7 or titulo['rating_score'] < 3: # 3 = A-
        return "Descarte"

    # 2. Lógica de 'Forte Compra' (Baseada no Yield)
    # Exemplo para títulos IPCA+
    if titulo['tipo'] == 'IPCA+':
        if titulo['taxa'] >= 0.062 and titulo['prazo_anos'] <= 5:
            return "Forte Compra"
        elif titulo['taxa'] >= 0.058:
            return "Compra"
            
    # Exemplo para títulos Pós-Fixados (CDB/LC)
    if titulo['tipo'] == 'CDI':
        if titulo['percentual_cdi'] >= 1.15: # 115% do CDI
            return "Forte Compra"
        elif titulo['percentual_cdi'] >= 1.10:
            return "Compra"

    return "Aguardar"