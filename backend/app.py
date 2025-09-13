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
        
        # Prompt para informações do time - ESPECIFICANDO 2025
        prompt = f"""
        Como especialista em futebol brasileiro, forneça informações REAIS e ATUALIZADAS sobre o time {team}.
        
        IMPORTANTE: Estamos em {current_year}. Forneça informações ATUAIS de {current_year}, não de 2024.
        
        Retorne APENAS um JSON com a seguinte estrutura:
        {{
          "next_match": {{
            "date": "data real do próximo jogo em 2025",
            "time": "horário real", 
            "stadium": "estádio real",
            "opponent": "adversário real",
            "championship": "campeonato"
          }},
          "last_matches": [
            {{
              "date": "data real de um jogo recente em 2025",
              "opponent": "adversário real", 
              "result": "resultado real",
              "competition": "competição real"
            }},
            {{
              "date": "data real de um jogo recente em 2025", 
              "opponent": "adversário real",
              "result": "resultado real", 
              "competition": "competição real"
            }}
          ],
          "probable_lineup": {{
            "formation": "formação tática atual",
            "players": ["jogador1 atual", "jogador2 atual", "jogador3 atual", "jogador4 atual", "jogador5 atual", "jogador6 atual", "jogador7 atual", "jogador8 atual", "jogador9 atual", "jogador10 atual", "jogador11 atual"]
          }},
          "news": [
            {{
              "title": "título real de notícia RECENTE de {current_year}",
              "summary": "resumo real da notícia",
              "date": "data da notícia em 2025",
              "source": "fonte da notícia"
            }}
          ]
        }}
        
        Forneça informações VERDADEIRAS e ATUALIZADAS de {current_year} sobre o {team}.
        Não use informações de 2024 ou anos anteriores.
        """
        
        response = gemini_model.generate_content(prompt)
        print("✅ Resposta do Gemini recebida")
        
        result = extract_json_from_text(response.text)
        print(f"✅ Resultado extraído: {json.dumps(result, indent=2)}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Erro interno: {str(e)}")
        return jsonify({"error": f"Erro interno do servidor: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "gemini_configured": gemini_configured,
        "model": "gemini-2.0-flash" if gemini_configured else "none",
        "current_year": datetime.now().year
    })

@app.route('/test-gemini', methods=['GET'])
def test_gemini():
    """Rota para testar a conexão com a API Gemini"""
    try:
        if not gemini_configured or not gemini_model:
            return jsonify({"error": "API Gemini não configurada"}), 500
            
        response = gemini_model.generate_content(f"Em que ano estamos? Responda apenas com o ano atual.")
        
        return jsonify({
            "status": "success",
            "response": response.text,
            "message": "Conexão com Gemini API bem-sucedida",
            "model": "gemini-2.0-flash",
            "current_year": datetime.now().year
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Erro ao conectar com Gemini API. Verifique sua chave API."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Servidor iniciando na porta {port}")
    print(f"🔑 Gemini Configurado: {gemini_configured}")
    if gemini_configured:
        print(f"🤖 Modelo: gemini-2.0-flash")
    print(f"📅 Ano atual: {datetime.now().year}")
    app.run(host='0.0.0.0', port=port)