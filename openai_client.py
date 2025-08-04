import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

MODEL_NAME = "gpt-4o-mini"

DEFAULT_SYSTEM_INSTRUCTION_CAREER_GUIDE = """
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
- Em último caso, como um recurso para destravar a conversa se o diálogo aberto estiver muito difícil, você pode oferecer uma pergunta com topicos com os quais ele nao se identifica considerando areas,atividades,perfis profissionais e ambiente empresariais, mas retorne rapidamente para perguntas de topicos da preferencia dele assim que possível. O objetivo principal é uma conversa fluida e exploratória.
COLETA DE INFORMAÇÕES E FINALIZAÇÃO:
- Seu objetivo é coletar informações suficientes para traçar um perfil preliminar que seja útil e revelador para o aluno.
- Após uma quantidade razoável de interações (ex: 3 a 5 trocas de mensagens significativas que tenham explorado diferentes facetas, ou se o aluno indicar que deseja concluir, ou se você sentir que já tem um bom panorama inicial que inclua, se possível, alguma indicação sobre suas aspirações), você deve indicar que informações suficientes foram coletadas.
- Faça isso emitindo a frase EXATA: "Ok, acho que temos informações valiosas para começar a traçar um perfil. Gostaria de ver um resumo agora?"
- Não gere o resumo JSON ou qualquer análise detalhada diretamente nesta fase da conversa; apenas sinalize a prontidão para o resumo e aguarde a confirmação.
"""

SYSTEM_INSTRUCTION_JSON_GENERATOR = """
Você é um assistente especialista em analisar transcrições de conversas e gerar perfis de carreira estruturados em formato JSON.
Siga estritamente o formato JSON solicitado. Retorne APENAS o JSON, sem nenhum texto adicional, comentários ou explicações antes ou depois do objeto JSON.
"""

client = None
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    print("Cliente OpenAI inicializado.")
except Exception as e:
    print(f"ERRO CRÍTICO ao inicializar OpenAI: {e}")
    client = None


def _converter_historico_simples_para_openai(historia_simples: list):
    messages = []
    if not historia_simples:
        return messages
    for turno in historia_simples:
        role = turno.get("role")
        parts_text_list = turno.get("parts")
        if role and isinstance(parts_text_list, list):
            content = "\n".join(p for p in parts_text_list if isinstance(p, str))
            if role == "model":
                role = "assistant"
            messages.append({"role": role, "content": content})
        else:
            print(f"AVISO: Turno do histórico simples ignorado por formato inválido: {turno}")
    return messages


def conversar_com_openai(conversation_log_simples: list, nova_mensagem_aluno_texto: str):
    if not client:
        error_msg = "Desculpe, o serviço de IA principal não está disponível no momento."
        conversation_log_simples.append({"role": "user", "parts": [nova_mensagem_aluno_texto]})
        conversation_log_simples.append({"role": "model", "parts": [error_msg]})
        return error_msg, conversation_log_simples

    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_INSTRUCTION_CAREER_GUIDE}
    ]
    messages.extend(_converter_historico_simples_para_openai(conversation_log_simples))
    messages.append({"role": "user", "content": nova_mensagem_aluno_texto})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.75,
            max_tokens=800,
        )
        resposta_modelo_texto = response.choices[0].message["content"]
        conversation_log_simples.append({"role": "user", "parts": [nova_mensagem_aluno_texto]})
        conversation_log_simples.append({"role": "model", "parts": [resposta_modelo_texto]})
        return resposta_modelo_texto, conversation_log_simples
    except Exception as e:
        print(f"Erro ao interagir com o OpenAI (conversar_com_openai): {e}")
        error_msg = "Desculpe, tive um problema ao processar sua resposta. Tente novamente."
        conversation_log_simples.append({"role": "user", "parts": [nova_mensagem_aluno_texto]})
        conversation_log_simples.append({"role": "model", "parts": [error_msg]})
        return error_msg, conversation_log_simples


def gerar_prontuario_com_openai(conversation_log_simples: list):
    if not client:
        return "{\"error\": \"Configuração de API ausente.\"}"

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
- "soft_skills_que estao faltando para a area": array de objetos, onde cada objeto tem os campos {"skill": "nome_da_skill_identificada_pela_IA", "evidencia": "uma frase ou breve resumo da parte da conversa que indica essa falta de skill necessaria"}
- "hard_skills_mencionadas_ou_desejadas": array de strings (tecnologias específicas, ferramentas, linguagens de programação ou áreas de conhecimento técnico que o aluno mencionou conhecer, ter interesse em aprender, ou que foram inferidas como relevantes)
- "areas_de_potencial_desenvolvimento_sugeridas": string (sugestões concisas de áreas ou habilidades que o aluno poderia focar para desenvolvimento futuro e cite empresas que trabalham com isso , baseado na conversa e nos seus interesses/objetivos)
- "sugestoes_de_carreira_inicial_exploratoria": array de strings (2-3 sugestões de tipos de carreira ou áreas de atuação para o aluno pesquisar mais e empresas que trabalham com isso, alinhadas com os interesses e skills identificados)
- "observacoes_gerais_sobre_interacao": string (sua análise geral sobre o engajamento do aluno durante a conversa, seu nível de clareza sobre seus objetivos, e quaisquer pontos de atenção ou destaque para um orientador de carreira)


    Certifique-se de que a saída seja um objeto JSON válido e completo, começando com '{' e terminando com '}'.
    Retorne APENAS o JSON, sem nenhum texto explicativo, markdown, ou qualquer caractere fora do objeto JSON.
    """

    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION_JSON_GENERATOR}
    ]
    messages.extend(_converter_historico_simples_para_openai(conversation_log_simples))
    messages.append({"role": "user", "content": prompt_final_json_str})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=2048,
        )
        resposta_json_texto = response.choices[0].message["content"]
        return resposta_json_texto.strip()
    except Exception as e:
        print(f"Erro ao gerar prontuário JSON com o OpenAI: {e}")
        return "{\"error\": \"Falha crítica ao gerar o resumo do perfil via IA.\"}"
