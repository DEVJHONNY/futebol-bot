from flask import Flask, request, jsonify
from flask_cors import CORS
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS para permitir todas as origens
CORS(app)

# Configurar a API do Gemini
gemini_configured = False
gemini_model = None

try:
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        gemini_model = GenerativeModel('gemini-2.0-flash')
        gemini_configured = True
        print("✅ Gemini API configurada com sucesso - usando gemini-2.0-flash")
    else:
        print("❌ GEMINI_API_KEY não encontrada")
except Exception as e:
    print(f"❌ Erro ao configurar Gemini: {str(e)}")

def extract_json_from_text(text):
    """Tenta extrair JSON do texto retornado pelo Gemini"""
    try:
        # Tenta encontrar um objeto JSON no texto
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"error": "Não foi possível extrair dados JSON da resposta"}
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {str(e)}")
        return {"error": "Resposta em formato inválido"}

@app.route('/api/team-info', methods=['POST'])
def get_team_info():
    try:
        if not gemini_configured or not gemini_model:
            return jsonify({"error": "API Gemini não configurada"}), 500
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        team = data.get('team')
        
        if not team:
            return jsonify({"error": "Time não especificado"}), 400
        
        # Obter o ano atual
        current_year = datetime.now().year
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        # Prompt para informações do time - MUITO ESPECÍFICO
        prompt = f"""
        Como especialista em futebol brasileiro, forneça informações COMPLETAMENTE ATUALIZADAS sobre o time {team}.
        
        DATA ATUAL: {current_date} ({current_year})
        
        CRITÉRIOS OBRIGATÓRIOS:
        1. Todas as informações devem ser da TEMPORADA ATUAL de 2025
        2. Escalação deve refletir os titulares ATUAIS do time
        3. Próximo jogo deve ser o próximo da temporada 2025
        4. Últimos jogos devem ser da temporada 2025
        5. Notícias devem ser RECENTES (2025)
        
        Retorne APENAS um JSON com a seguinte estrutura:
        {{
          "next_match": {{
            "date": "data real do próximo jogo em 2025 (formato DD/MM/AAAA)",
            "time": "horário real (formato HH:MM)", 
            "stadium": "estádio real",
            "opponent": "adversário real",
            "championship": "Campeonato Brasileiro 2025"
          }},
          "last_matches": [
            {{
              "date": "data real de jogo RECENTE em 2025",
              "opponent": "adversário real", 
              "result": "resultado real (ex: 2x1, 0x0, 1x3)",
              "competition": "Campeonato Brasileiro 2025"
            }},
            {{
              "date": "data real de jogo RECENTE em 2025",
              "opponent": "adversário real", 
              "result": "resultado real (ex: 2x1, 0x0, 1x3)",
              "competition": "Campeonato Brasileiro 2025"
            }}
          ],
          "probable_lineup": {{
            "formation": "formação tática atual (ex: 4-3-3, 4-2-3-1, 4-4-2)",
            "players": [
              "goleiro atual (ex: Santos)",
              "lateral direito atual",
              "zagueiro atual", 
              "zagueiro atual",
              "lateral esquerdo atual",
              "volante atual",
              "meia atual",
              "meia atual",
              "atacante atual",
              "atacante atual", 
              "centroavante atual"
            ]
          }},
          "news": [
            {{
              "title": "título de notícia REALMENTE RECENTE de {current_year}",
              "summary": "resumo real da notícia atual",
              "date": "data recente em 2025",
              "source": "fonte confiável (ex: GE, UOL, ESPN)"
            }}
          ]
        }}
        
        NÃO USE jogadores que não estejam mais no time.
        NÃO USE dados de 2024 ou temporadas anteriores.
        NÃO INVENTE informações - use apenas dados reais da temporada 2025.
        """
        
        response = gemini_model.generate_content(prompt)
        print("✅ Resposta do Gemini recebida")
        
        result = extract_json_from_text(response.text)
        print(f"✅ Resultado extraído: {json.dumps(result, indent=2)}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Erro interno: {str(e)}")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

@app.route('/api/lineup-only', methods=['POST'])
def get_lineup_only():
    """Endpoint específico apenas para escalações atualizadas"""
    try:
        if not gemini_configured or not gemini_model:
            return jsonify({"error": "API Gemini não configurada"}), 500
            
        data = request.get_json()
        team = data.get('team')
        
        if not team:
            return jsonify({"error": "Time não especificado"}), 400
        
        prompt = f"""
        Forneça APENAS a escalação ATUAL e ATUALIZADA do {team} para a temporada 2025 do Campeonato Brasileiro.
        
        Retorne APENAS um JSON com a estrutura:
        {{
          "formation": "formação tática atual",
          "players": [
            "goleiro ATUAL",
            "lateral direito ATUAL", 
            "zagueiro ATUAL",
            "zagueiro ATUAL",
            "lateral esquerdo ATUAL",
            "volante ATUAL",
            "meia ATUAL", 
            "meia ATUAL",
            "atacante ATUAL",
            "atacante ATUAL",
            "centroavante ATUAL"
          ]
        }}
        
        NÃO USE jogadores que não estejam mais no time.
        Use apenas jogadores atuais do elenco de 2025.
        """
        
        response = gemini_model.generate_content(prompt)
        result = extract_json_from_text(response.text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar escalação: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "gemini_configured": gemini_configured,
        "model": "gemini-2.0-flash" if gemini_configured else "none",
        "current_year": datetime.now().year,
        "current_date": datetime.now().strftime("%d/%m/%Y")
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor iniciando na porta {port}")
    print(f"🔑 Gemini Configurado: {gemini_configured}")
    if gemini_configured:
        print(f"🤖 Modelo: gemini-2.0-flash")
    print(f"📅 Data atual: {datetime.now().strftime('%d/%m/%Y')}")
    app.run(host='0.0.0.0', port=port)