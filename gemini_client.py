# gemini_client.py
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Content, FinishReason
from dotenv import load_dotenv
import json

load_dotenv()

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
LOCATION = os.environ.get("GCP_REGION")
# ATENÇÃO: Verifique se este é um nome de modelo válido e disponível em sua GCP_REGION
MODEL_NAME = "gemini-2.0-flash" # Ou "gemini-1.5-flash-001", "gemini-1.0-pro-002", etc.

DEFAULT_SYSTEM_INSTRUCTION_CAREER_GUIDE = Part.from_text("""
nao use emojis                                                         
Você é o "GuIA Carreiras IBMEC", um conselheiro de carreira empático, experiente e perspicaz, especialista em identificar interesses técnicos, soft skills e aspirações de carreira em alunos universitários.
Seus objetivos principais são:
1.  Ajudar o aluno a explorar e articular seus verdadeiros interesses, paixões, atividades preferidas e o que o motiva em relação à tecnologia e ao trabalho em geral.
2.  Identificar afinidades com diferentes áreas e tipos de desafios tecnológicos.
3.  Perceber e destacar soft skills relevantes demonstradas ou mencionadas pelo aluno durante a conversa.
4.  Descobrir, de forma natural e se apropriado durante o diálogo, se o aluno já possui alguma visão mais clara sobre seu futuro profissional, como uma "empresa dos sonhos", um cargo específico que almeja, ou objetivos de carreira definidos.
o aluno ira comecar informando seu curso e periodo, logo apos pergunte sobre a materia favorita dele e use isso como um ponto para gerar o perfil da pessoa e
Para atingir esses objetivos:
- Conduza uma conversa aberta, natural e direcionada. Inicie de forma ampla e vá afunilando conforme as respostas do aluno.
- Formule perguntas abertas, curiosas, reflexivas e sugestivas que encorajem o aluno a se expressar livremente e aprofundar seus pensamentos.
- Explore sutilmente as preferências do aluno por diferentes tipos de trabalho (ex: criar, analisar, proteger, otimizar), ambientes (ex: colaborativo, focado) e desafios.
- Se a conversa levar a temas como "onde aplicar meus interesses" ou "tipos de empresas", aproveite a oportunidade para perguntar sobre aspirações específicas de forma contextualizada (ex: "Isso que você descreveu te faz pensar em algum tipo de empresa ou projeto que seria ideal para você no futuro?"). Não force esta questão se o aluno parecer incerto.
- Evite jargões técnicos complexos, a menos que o aluno demonstre familiaridade e os utilize primeiro.
- Mantenha um tom profissional, mas extremamente amigável, paciente, positivo e encorajador. Use uma linguagem acessível e inspiradora.
REGRA CRÍTICA PARA ALUNOS COM DIFICULDADE: Se o aluno parecer perdido, confuso, responder de forma muito vaga, monossilábica ou demonstrar baixa confiança, sua prioridade é torná-lo confortável.
- Adapte sua abordagem: refraseie a pergunta anterior de forma mais simples, ofereça exemplos concretos e relacionáveis, sugira categorias de pensamento para ajudá-lo a estruturar suas ideias, ou simplifique o tópico.
- Em último caso, como um recurso para destravar a conversa se o diálogo aberto estiver muito difícil, você pode oferecer uma pergunta com 2-3 opções claras para ele escolher, mas retorne rapidamente para perguntas abertas assim que possível. O objetivo principal é uma conversa fluida e exploratória.
COLETA DE INFORMAÇÕES E FINALIZAÇÃO:
- Seu objetivo é coletar informações suficientes para traçar um perfil preliminar que seja útil e revelador para o aluno.
- Após uma quantidade razoável de interações (ex: 3 a 5 trocas de mensagens significativas que tenham explorado diferentes facetas, ou se o aluno indicar que deseja concluir, ou se você sentir que já tem um bom panorama inicial que inclua, se possível, alguma indicação sobre suas aspirações), você deve indicar que informações suficientes foram coletadas.
- Faça isso emitindo a frase EXATA: "Ok, acho que temos informações valiosas para começar a traçar um perfil. Gostaria de ver um resumo agora?"
- Não gere o resumo JSON ou qualquer análise detalhada diretamente nesta fase da conversa; apenas sinalize a prontidão para o resumo e aguarde a confirmação.
""")

SYSTEM_INSTRUCTION_JSON_GENERATOR = Content(parts=[Part.from_text("""
Você é um assistente especialista em analisar transcrições de conversas e gerar perfis de carreira estruturados em formato JSON.
Siga estritamente o formato JSON solicitado. Retorne APENAS o JSON, sem nenhum texto adicional, comentários ou explicações antes ou depois do objeto JSON.
""")])

main_model = None
try:
    if not PROJECT_ID or not LOCATION:
        raise ValueError("As variáveis de ambiente GCP_PROJECT_ID e GCP_REGION precisam estar definidas.")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    main_model = GenerativeModel(MODEL_NAME, system_instruction=DEFAULT_SYSTEM_INSTRUCTION_CAREER_GUIDE)
    print(f"Vertex AI SDK inicializado. Modelo Gemini ('{MODEL_NAME}') carregado com instrução de sistema padrão.")
except Exception as e:
    print(f"ERRO CRÍTICO ao inicializar Vertex AI ou carregar main_model Gemini: {e}")
    print(f"Verifique: ID do Projeto ('{PROJECT_ID}'), Localização ('{LOCATION}'), Nome do Modelo ('{MODEL_NAME}'), e GOOGLE_APPLICATION_CREDENTIALS.")


def _converter_historico_simples_para_gemini(historia_simples: list):
    gemini_history = []
    if not historia_simples:
        return gemini_history
    for turno in historia_simples:
        role = turno.get("role")
        parts_text_list = turno.get("parts")
        if role and isinstance(parts_text_list, list):
            gemini_parts = [Part.from_text(p_text) for p_text in parts_text_list if isinstance(p_text, str)]
            if gemini_parts:
                gemini_history.append(Content(role=role, parts=gemini_parts))
        else:
            print(f"AVISO: Turno do histórico simples ignorado por formato inválido: {turno}")
    return gemini_history

def conversar_com_gemini(conversation_log_simples: list, nova_mensagem_aluno_texto: str):
    if not main_model:
        error_msg = "Desculpe, o serviço de IA principal não está disponível no momento."
        conversation_log_simples.append({"role": "user", "parts": [nova_mensagem_aluno_texto]})
        conversation_log_simples.append({"role": "model", "parts": [error_msg]})
        return error_msg, conversation_log_simples

    conteudo_para_api = _converter_historico_simples_para_gemini(conversation_log_simples)
    conteudo_para_api.append(Content(role="user", parts=[Part.from_text(nova_mensagem_aluno_texto)]))
    
    try:
        response = main_model.generate_content(
            contents=conteudo_para_api,
            generation_config={"temperature": 0.75, "max_output_tokens": 800},
            safety_settings={}
        )
        
        resposta_modelo_texto = ""
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            if response.candidates[0].finish_reason != FinishReason.SAFETY:
                 resposta_modelo_texto = response.candidates[0].content.parts[0].text
            else:
                resposta_modelo_texto = "Minha resposta foi bloqueada por questões de segurança. Poderia reformular?"
                print(f"Resposta bloqueada: {response.candidates[0].finish_reason} / {response.candidates[0].safety_ratings}")
        elif hasattr(response, 'text'): 
            resposta_modelo_texto = response.text
        else:
            resposta_modelo_texto = "Não consegui gerar uma resposta clara."
            print(f"Resposta inesperada: {response}")

        conversation_log_simples.append({"role": "user", "parts": [nova_mensagem_aluno_texto]})
        conversation_log_simples.append({"role": "model", "parts": [resposta_modelo_texto]})
        
        return resposta_modelo_texto, conversation_log_simples
    
    except Exception as e:
        print(f"Erro ao interagir com o Gemini (conversar_com_gemini): {e}")
        error_msg = "Desculpe, tive um problema ao processar sua resposta. Tente novamente."
        conversation_log_simples.append({"role": "user", "parts": [nova_mensagem_aluno_texto]})
        conversation_log_simples.append({"role": "model", "parts": [error_msg]})
        return error_msg, conversation_log_simples

def gerar_prontuario_com_gemini(conversation_log_simples: list):
    # Para esta função, é mais robusto criar uma nova instância de modelo
    # configurada especificamente com a system instruction para JSON.
    json_model_instance = None
    try:
        # Se main_model carregou, vertexai.init() já foi chamado.
        # Não precisamos de 'if not vertexai.generative_models._initialized:'
        if not PROJECT_ID or not LOCATION: # Redundante se main_model carregou, mas seguro
             return "{\"error\": \"Configuração de Projeto/Localização ausente para modelo JSON.\"}"
        
        json_model_instance = GenerativeModel(MODEL_NAME, system_instruction=SYSTEM_INSTRUCTION_JSON_GENERATOR)
        # print("Modelo para JSON criado com sucesso.") # Opcional para debug
    except Exception as e:
        print(f"Erro ao criar modelo específico para JSON (json_model_instance): {e}")
        return "{\"error\": \"Falha ao configurar modelo de IA para gerar prontuário.\"}"

    if not json_model_instance: # Verificação adicional
        return "{\"error\": \"Modelo de IA para JSON não pôde ser inicializado.\"}"

    prompt_final_json_str = """
    Baseado em toda a nossa conversa até agora, por favor, gere um perfil de carreira detalhado para o aluno no formato JSON.
Inclua os seguintes campos:

- "interesses_principais": string (uma frase concisa resumindo os principais interesses técnicos e temas que surgiram, como áreas de tecnologia, tipos de problemas que gosta de resolver, etc.)
- "objetivos_carreira_inferidos": string (objetivos de carreira de curto ou longo prazo que você inferiu da conversa, mesmo que não tenham sido explicitamente declarados pelo aluno)
- "aspiracoes_declaradas": objeto opcional contendo os seguintes subcampos (se o aluno mencionou explicitamente alguma aspiração, preencha os campos correspondentes; se nenhuma aspiração clara foi declarada, você pode omitir o objeto "aspiracoes_declaradas" ou deixar seus subcampos como null ou string vazia):
    - "empresa_sonhos_mencionada": string (nome da empresa ou tipo de empresa que o aluno mencionou como ideal ou dos sonhos)
    - "cargo_desejado_mencionado": string (nome do cargo ou tipo de papel que o aluno mencionou desejar)
    - "outros_objetivos_claros_mencionados": string (quaisquer outros objetivos de carreira específicos e claros que o aluno verbalizou)
- "soft_skills_identificadas_com_evidencia": array de objetos, onde cada objeto tem os campos {"skill": "nome_da_skill_identificada_pela_IA", "evidencia": "uma frase ou breve resumo da parte da conversa que indica essa skill"}
- "hard_skills_mencionadas_ou_desejadas": array de strings (tecnologias específicas, ferramentas, linguagens de programação ou áreas de conhecimento técnico que o aluno mencionou conhecer, ter interesse em aprender, ou que foram inferidas como relevantes)
- "areas_de_potencial_desenvolvimento_sugeridas": string (sugestões concisas de áreas ou habilidades que o aluno poderia focar para desenvolvimento futuro e cite empresas que trabalham com isso , baseado na conversa e nos seus interesses/objetivos)
- "sugestoes_de_carreira_inicial_exploratoria": array de strings (2-3 sugestões de tipos de carreira ou áreas de atuação para o aluno pesquisar mais e empresas que trabalham com isso, alinhadas com os interesses e skills identificados)
- "observacoes_gerais_sobre_interacao": string (sua análise geral sobre o engajamento do aluno durante a conversa, seu nível de clareza sobre seus objetivos, e quaisquer pontos de atenção ou destaque para um orientador de carreira)


    Certifique-se de que a saída seja um objeto JSON válido e completo, começando com '{' e terminando com '}'.
    Retorne APENAS o JSON, sem nenhum texto explicativo, markdown, ou qualquer caractere fora do objeto JSON.
    """
    
    conteudo_para_json = _converter_historico_simples_para_gemini(conversation_log_simples)
    conteudo_para_json.append(Content(role="user", parts=[Part.from_text(prompt_final_json_str)]))

    try:
        response = json_model_instance.generate_content( # Usa o json_model_instance
            contents=conteudo_para_json,
            generation_config={"temperature": 0.1, "max_output_tokens": 2048},
            safety_settings={}
        )
        
        resposta_json_texto = ""
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            if response.candidates[0].finish_reason != FinishReason.SAFETY:
                resposta_json_texto = response.candidates[0].content.parts[0].text
            else:
                resposta_json_texto = "{\"error\": \"Geração do prontuário bloqueada por segurança.\"}"
                print(f"Geração de JSON bloqueada por segurança: {response.candidates[0].finish_reason} / {response.candidates[0].safety_ratings}")
        elif hasattr(response, 'text'):
             resposta_json_texto = response.text
        else:
            resposta_json_texto = "{\"error\": \"Não foi possível gerar o prontuário em formato JSON.\"}"
            print(f"Resposta inesperada do modelo ao gerar JSON: {response}")
            
        return resposta_json_texto.strip()
    
    except Exception as e:
        print(f"Erro ao gerar prontuário JSON com o Gemini: {e}")
        return "{\"error\": \"Falha crítica ao gerar o resumo do perfil via IA.\"}"

# Bloco if __name__ == '__main__' para teste local
if __name__ == '__main__':
    if main_model: # Verifica se o modelo principal (de chat) foi carregado
        print("\n--- Teste Interativo do GuIA Carreiras IBMEC (com histórico simples) ---")
        print(f"Usando modelo: {MODEL_NAME} em {LOCATION} para o projeto {PROJECT_ID}")
        print("Digite 'sair', 'finalizar' ou 'resumir' para encerrar e gerar o prontuário.")
        
        

        turn_count = 0
        max_turns_before_summary_prompt = 5 # Exemplo: sugerir resumo após 5 turnos do usuário

        while True:
            user_input = input("Você: ").strip()
            
            if user_input.lower() in ['sair', 'finalizar', 'resumir']:
                log_simples_teste.append({"role": "user", "parts": [user_input]})
                log_simples_teste.append({"role": "model", "parts": ["Entendido! Vou preparar um resumo da nossa conversa."]})
                print(f"GuIA: {log_simples_teste[-1]['parts'][0]}")
                break
            
            if not user_input:
                print("GuIA: Parece que você não digitou nada. Poderia me contar um pouco mais?")
                # Não adicionamos ao histórico, apenas um prompt visual
                continue

            turn_count += 1
            bot_resp, log_simples_teste = conversar_com_gemini(log_simples_teste, user_input)
            print(f"GuIA: {bot_resp}")

            # Verifica se o bot indicou que está pronto para resumir ou se atingiu o número de turnos
            if "gostaria de ver um resumo agora?" in bot_resp.lower() or turn_count >= max_turns_before_summary_prompt:
                if not ("gostaria de ver um resumo agora?" in bot_resp.lower()): # Se foi por contagem de turnos
                    print("GuIA: Já conversamos bastante! Gostaria de ver um resumo agora?")
                    log_simples_teste.append({"role": "model", "parts": ["Já conversamos bastante! Gostaria de ver um resumo agora?"]})


                confirmacao = input("Você (digite 'sim' para gerar o perfil, ou qualquer outra coisa para continuar): ").strip().lower()
                log_simples_teste.append({"role": "user", "parts": [confirmacao]})
                if confirmacao == 'sim':
                    msg_confirmacao_bot = "Ótimo! Preparando seu resumo..."
                    print(f"GuIA: {msg_confirmacao_bot}")
                    log_simples_teste.append({"role": "model", "parts": [msg_confirmacao_bot]})
                    break 
                else:
                    msg_continuar_conversa = "Sem problemas! Sobre o que mais gostaria de conversar?"
                    print(f"GuIA: {msg_continuar_conversa}")
                    log_simples_teste.append({"role": "model", "parts": [msg_continuar_conversa]})
                    turn_count = 0 # Reseta a contagem de turnos para continuar a conversa

        print("\n--- Gerando Prontuário (com histórico simples) ---")
        json_prontuario = gerar_prontuario_com_gemini(log_simples_teste)
        
        print("\n--- Resposta Bruta do Prontuário JSON ---")
        print(json_prontuario)
        
        try:
            parsed = json.loads(json_prontuario)
            print("\n--- Prontuário JSON (Formatado e Validado) ---")
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as json_err:
            print(f"ERRO: O prontuário retornado não é um JSON válido: {json_err}")
            print("Isso geralmente requer ajuste no prompt de geração do JSON ou na instrução de sistema do 'json_model_instance'.")
    else:
        print("Modelo principal (main_model) não carregado. Encerrando teste do cliente.")