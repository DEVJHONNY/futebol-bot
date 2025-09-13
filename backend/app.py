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

# Configurar CORS para permitir todas as origens (para desenvolvimento)
CORS(app)

# Configurar a API do Gemini
try:
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
except Exception as e:
    print(f"Erro ao configurar Gemini: {str(e)}")

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
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        team = data.get('team')
        
        if not team:
            return jsonify({"error": "Time não especificado"}), 400
        
        # Verificar se a API key está configurada
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("GEMINI_API_KEY não configurada")
            return jsonify({"error": "API não configurada"}), 500
        
        # Usar o modelo Gemini para obter informações
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prompt para informações do time
        prompt = f"""
        Como especialista em futebol brasileiro, forneça informações sobre o time {team}.
        Forneça dados fictícios mas realistas para demonstração.
        
        Retorne APENAS um JSON com a seguinte estrutura:
        {{
          "next_match": {{
            "date": "01/12/2023",
            "time": "16:00",
            "stadium": "Maracanã",
            "opponent": "Fluminense",
            "championship": "Brasileirão Série A"
          }},
          "last_matches": [
            {{
              "date": "25/11/2023",
              "opponent": "Palmeiras",
              "result": "2x1",
              "competition": "Brasileirão"
            }},
            {{
              "date": "19/11/2023",
              "opponent": "Corinthians",
              "result": "0x0",
              "competition": "Brasileirão"
            }}
          ],
          "probable_lineup": {{
            "formation": "4-3-3",
            "players": ["Santos", "Danilo", "Gustavo Gómez", "Murilo", "Piquerez", "Zé Rafael", "Gabriel Menino", "Raphael Veiga", "Dudu", "Rony", "Endrick"]
          }},
          "news": [
            {{
              "title": "Time se prepara para último jogo do campeonato",
              "summary": "O {team} treinou strong focado para o último jogo do Brasileirão",
              "date": "28/11/2023",
              "source": "Site do Clube"
            }}
          ]
        }}
        """
        
        response = model.generate_content(prompt)
        print("Resposta do Gemini recebida")
        
        result = extract_json_from_text(response.text)
        print(f"Resultado extraído: {result}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Erro interno: {str(e)}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    api_key_configured = bool(os.environ.get('GEMINI_API_KEY'))
    return jsonify({
        "status": "healthy", 
        "gemini_configured": api_key_configured
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)