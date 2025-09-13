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

# Variável global para verificar se a API foi configurada
gemini_configured = False

try:
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        gemini_configured = True
        print("✅ Gemini API configurada com sucesso")
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
        if not gemini_configured:
            return jsonify({"error": "API Gemini não configurada"}), 500
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados não fornecidos"}), 400
            
        team = data.get('team')
        
        if not team:
            return jsonify({"error": "Time não especificado"}), 400
        
        # Usar o modelo Gemini para obter informações
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Prompt para informações do time
        prompt = f"""
        Como especialista em futebol brasileiro, forneça informações REAIS sobre o time {team} no Campeonato Brasileiro.
        
        Retorne APENAS um JSON com a seguinte estrutura:
        {{
          "next_match": {{
            "date": "data real",
            "time": "horário real", 
            "stadium": "estádio real",
            "opponent": "adversário real",
            "championship": "campeonato"
          }},
          "last_matches": [
            {{
              "date": "data real",
              "opponent": "adversário real", 
              "result": "resultado real",
              "competition": "competição real"
            }},
            {{
              "date": "data real",
              "opponent": "adversário real",
              "result": "resultado real", 
              "competition": "competição real"
            }}
          ],
          "probable_lineup": {{
            "formation": "formação tática",
            "players": ["jogador1", "jogador2", "jogador3", "jogador4", "jogador5", "jogador6", "jogador7", "jogador8", "jogador9", "jogador10", "jogador11"]
          }},
          "news": [
            {{
              "title": "título real de notícia",
              "summary": "resumo real da notícia",
              "date": "data da notícia",
              "source": "fonte da notícia"
            }}
          ]
        }}
        
        Forneça informações VERDADEIRAS e ATUALIZADAS sobre o {team}.
        """
        
        response = model.generate_content(prompt)
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
        "message": "Acesse https://console.cloud.google.com/ para verificar sua API Key"
    })

@app.route('/test-gemini', methods=['GET'])
def test_gemini():
    """Rota para testar a conexão com a API Gemini"""
    try:
        if not gemini_configured:
            return jsonify({"error": "API Gemini não configurada"}), 500
            
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Me responda apenas 'OK' se estiver funcionando")
        
        return jsonify({
            "status": "success",
            "response": response.text,
            "message": "Conexão com Gemini API bem-sucedida"
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
    app.run(host='0.0.0.0', port=port)