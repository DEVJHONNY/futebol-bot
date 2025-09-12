from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar a API do Gemini
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def extract_json_from_text(text):
    """Tenta extrair JSON do texto retornado pelo Gemini"""
    try:
        # Tenta encontrar um objeto JSON no texto
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"error": "Não foi possível extrair dados JSON da resposta"}
    except json.JSONDecodeError:
        return {"error": "Resposta em formato inválido"}

@app.route('/api/team-info', methods=['POST'])
def get_team_info():
    try:
        data = request.get_json()
        team = data.get('team')
        
        if not team:
            return jsonify({"error": "Time não especificado"}), 400
        
        # Verificar se a API key está configurada
        if not os.environ.get('GEMINI_API_KEY'):
            return jsonify({"error": "API key não configurada"}), 500
        
        # Usar o modelo Gemini para obter informações
        model = genai.GenerativeModel('gemini-pro')
        
        # Prompt para informações do time
        prompt = f"""
        Como especialista em futebol brasileiro, forneça informações completas sobre o time {team} no Campeonato Brasileiro.
        
        Retorne APENAS um JSON com a seguinte estrutura:
        {{
          "next_match": {{
            "date": "data",
            "time": "horário",
            "stadium": "estádio",
            "opponent": "adversário",
            "championship": "campeonato"
          }},
          "last_matches": [
            {{
              "date": "data",
              "opponent": "adversário",
              "result": "resultado",
              "competition": "competição"
            }}
          ],
          "probable_lineup": {{
            "formation": "formação",
            "players": ["jogador1", "jogador2", ...]
          }},
          "news": [
            {{
              "title": "título",
              "summary": "resumo",
              "date": "data",
              "source": "fonte"
            }}
          ]
        }}
        
        Forneça informações reais e atualizadas sobre o {team}.
        """
        
        response = model.generate_content(prompt)
        result = extract_json_from_text(response.text)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "gemini_configured": bool(os.environ.get('GEMINI_API_KEY'))})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)