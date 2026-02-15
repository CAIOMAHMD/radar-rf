from google import genai
import os

# Substitua pela sua chave do Google AI Studio
# Dica: No Mac, você pode usar os.environ.get("GEMINI_API_KEY") para segurança
client = genai.Client(api_key="AIzaSyBz1sbjbY8KHt_e7wl10ysOmRwjJ01gqDo ")

def avaliar_clima_politico():
    prompt = """
    Analise o cenário político e fiscal do Brasil hoje (Fevereiro de 2026).
    Foque em: notícias do Copom, falas do Ministro da Fazenda e riscos no Congresso.
    Responda estritamente com uma palavra:
    'ESTRESSE' (se houver instabilidade ou risco fiscal alto)
    'ESTAVEL' (se o clima estiver sob controle)
    """
    
    try:
        # Usando o Gemini 2.0 Flash (mais rápido para análise de texto)
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        resultado = response.text.strip().upper()
        return "ALTA" if "ESTRESSE" in resultado else "BAIXA"
        
    except Exception as e:
        print(f"⚠️ Erro na IA: {e}")
        return "BAIXA" # Fallback de segurança