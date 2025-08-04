# app.py (Versão Enxuta com Integração OpenAI)
import sqlite3
import uuid
import json
import os # Para carregar variáveis de ambiente
from flask import Flask, jsonify, render_template, request, session
from dotenv import load_dotenv # Para carregar o .env

# Carrega variáveis de ambiente do arquivo .env no início
load_dotenv()

# Importa as funções do nosso cliente OpenAI
try:
    from openai_client import conversar_com_openai, gerar_prontuario_com_openai, client as openai_client
    if not openai_client:
        print("AVISO em app.py: Cliente OpenAI não foi carregado pelo openai_client. Funcionalidades de IA podem estar desabilitadas.")
except ImportError:
    print("ERRO CRÍTICO em app.py: Não foi possível importar openai_client.py. Funcionalidades de IA estarão desabilitadas.")
    conversar_com_openai = None
    gerar_prontuario_com_openai = None
    openai_client = None

app = Flask(__name__)
# Carrega a Chave Secreta do Flask de uma variável de ambiente
# Defina FLASK_SECRET_KEY no seu arquivo .env
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "uma-chave-secreta-padrao-muito-forte-se-nao-definida")
if app.secret_key == "uma-chave-secreta-padrao-muito-forte-se-nao-definida":
    print("AVISO: FLASK_SECRET_KEY não definida no ambiente. Usando chave padrão (NÃO SEGURO PARA PRODUÇÃO).")


DATABASE = 'chatbot_ai_data.db' # Nome do banco de dados focado na IA

# --- Funções de Banco de Dados ---
def get_db():
    db_conn = sqlite3.connect(DATABASE)
    db_conn.row_factory = sqlite3.Row # Permite acesso às colunas por nome
    return db_conn

def init_db():
    db_conn = None
    try:
        db_conn = get_db()
        cursor = db_conn.cursor()
        # Tabela para armazenar o prontuário JSON gerado pela IA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_ai_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL, 
                profile_json TEXT, -- Armazena o JSON completo como texto
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db_conn.commit()
        print(f"Banco de dados '{DATABASE}' e tabela 'student_ai_profiles' inicializados/verificados.")
    except sqlite3.Error as e:
        print(f"Erro ao inicializar o banco de dados '{DATABASE}': {e}")
    finally:
        if db_conn:
            db_conn.close()

# --- Rotas da Aplicação ---
@app.route('/')
def index():
    return render_template('index.html') # Página principal do chatbot

@app.route('/api/start_session', methods=['GET'])
def start_session():
    if not openai_client or not conversar_com_openai:
        return jsonify({"error": "Desculpe, o serviço de IA está temporariamente indisponível."}), 503

    session.clear() # Limpa qualquer sessão anterior
    session['session_id'] = uuid.uuid4().hex
    
    # Mensagem inicial do bot (pode ser customizada ou até gerada por uma chamada inicial ao OpenAI se desejado)

    saudacao_inicial_bot = "Olá! Seja bem vindo ao CarreirAi. Meu nome é Aline, e vou conduzir a nossa conversa! Para começarmos, me conte seu curso e qual perido você esta."
    
    # Histórico na sessão Flask armazena 'parts' como lista de strings
    session['conversation_history'] = [{"role": "model", "parts": [saudacao_inicial_bot]}]
    session.modified = True # Garante que a sessão seja salva

    print(f"Nova sessão IA iniciada: {session['session_id']}, Histórico inicial: {session['conversation_history']}")
    return jsonify({"initial_message": saudacao_inicial_bot})

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    if not openai_client or not conversar_com_openai:
        return jsonify({"error": "Serviço de IA indisponível no momento."}), 503

    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Mensagem não fornecida."}), 400

    user_message = data['message']

    if 'session_id' not in session or 'conversation_history' not in session:
        print("AVISO: Sessão inválida ou histórico não encontrado em /api/chat, reiniciando sessão.")
        start_response_data = start_session().get_json() # Chama a função para obter dados da nova sessão
        return jsonify({
            "bot_response": start_response_data.get("initial_message", "Sessão reiniciada. Olá! Como posso ajudar?"),
            "session_restarted": True, # Sinalizador para o frontend
            "error_message": "Sua sessão anterior não foi encontrada. Uma nova conversa foi iniciada."
        }), 200 

    current_simple_history = session.get('conversation_history', [])
    
    # openai_client.conversar_com_openai aceita e retorna o histórico no formato simples
    bot_response_text, updated_simple_history = conversar_com_openai(current_simple_history, user_message)
    
    session['conversation_history'] = updated_simple_history
    session.modified = True

    # Verifica se o bot indicou que está pronto para gerar o prontuário
    # (conforme instruído no system_prompt do openai_client)
    trigger_phrase_resumo = "gostaria de ver um resumo agora?" # Mantenha esta frase EXATA e em minúsculas
    if trigger_phrase_resumo in bot_response_text.lower():
        return jsonify({
            "bot_response": bot_response_text,
            "end_of_quiz_phase_reached": True # Sinaliza ao frontend para perguntar se quer o resumo
        })
    else:
        return jsonify({"bot_response": bot_response_text})

@app.route('/api/generate_profile', methods=['POST'])
def generate_profile_route():
    if not openai_client or not gerar_prontuario_com_openai:
        return jsonify({"error": "Serviço de IA indisponível para gerar perfil."}), 503

    if 'session_id' not in session or not session.get('conversation_history'):
        return jsonify({"error": "Sessão inválida ou histórico não encontrado para gerar perfil."}), 400

    current_simple_history = session['conversation_history']
    
    # Opcional: Adicionar um turno do usuário confirmando o desejo de gerar o perfil,
    # se o frontend não o adicionar ao histórico antes desta chamada.
    # if current_simple_history and current_simple_history[-1]["role"] == "model" and \
    #    "gostaria de ver um resumo agora?" in current_simple_history[-1]["parts"][0].lower():
    #    current_simple_history.append({"role": "user", "parts": ["Sim, por favor, gere o resumo."]})

    print(f"Histórico SIMPLES para geração de prontuário (sessão {session['session_id']}): {current_simple_history[-3:] if len(current_simple_history) > 2 else current_simple_history}")

    prontuario_json_text = gerar_prontuario_com_openai(current_simple_history)
    
    cleaned_json_text = prontuario_json_text
    if cleaned_json_text.strip().startswith("```json"):
        cleaned_json_text = cleaned_json_text.strip()[len("```json"):].strip()
    elif cleaned_json_text.strip().startswith("```"):
         cleaned_json_text = cleaned_json_text.strip()[len("```"):].strip()
    if cleaned_json_text.strip().endswith("```"):
        cleaned_json_text = cleaned_json_text.strip()[:-len("```")].strip()
    
    try:
        profile_result = json.loads(cleaned_json_text)
        if isinstance(profile_result, dict) and "error" in profile_result: 
            print(f"Erro retornado pelo OpenAI na geração do prontuário: {profile_result['error']}")
            return jsonify({"error": f"IA reportou um erro na geração do perfil: {profile_result['error']}" }), 500
    except json.JSONDecodeError as e:
        print(f"ERRO CRÍTICO: OpenAI não retornou um JSON válido mesmo após limpeza: '{cleaned_json_text}'. Erro de parse: {e}")
        print(f"Texto original do OpenAI (antes da limpeza): '{prontuario_json_text}'")
        return jsonify({"error": "Falha ao processar o perfil gerado pela IA (formato inválido)."}), 500

    session['profile_analysis_result'] = profile_result 
    session.modified = True

    db_conn = None
    try:
        db_conn = get_db()
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO student_ai_profiles (session_id, profile_json) VALUES (?, ?)",
            (session['session_id'], json.dumps(profile_result)) # Salva como string JSON
        )
        db_conn.commit()
        print(f"Perfil AI salvo no BD para sessão {session['session_id']}")
    except sqlite3.Error as e:
        print(f"Erro ao salvar perfil AI no BD: {e}")
        # Não retorna erro crítico ao cliente por isso, mas registra no log do servidor.
    finally:
        if db_conn:
            db_conn.close()
            
    return jsonify({
        "message": "Seu perfil personalizado foi gerado com sucesso!",
        "profile_generation_complete": True
    })

@app.route('/report')
def report():
    profile_data = session.get('profile_analysis_result')
    if not profile_data:
        return "Resultado da análise não encontrado. Por favor, complete o questionário primeiro. <a href='/'>Voltar ao início</a>"
    
    # O template 'report.html' precisa ser adaptado para ler as chaves do JSON gerado pelo OpenAI.
    # Exemplo: profile.interesses_principais, profile.soft_skills_identificadas_com_evidencia, etc.
    return render_template('report.html', profile=profile_data)

if __name__ == '__main__':
    init_db() # Garante que a tabela student_ai_profiles seja criada/verificada.
    app.run(debug=True, port=5000)
