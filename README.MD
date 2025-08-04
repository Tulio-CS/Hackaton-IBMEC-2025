# MentorIA Carreiras IBMEC - MVP com IA

## Descrição do Projeto

O " CarreirAI" é um aplicativo web inovador que utiliza Inteligência Artificial da OpenAI para auxiliar alunos dos primeiros períodos dos cursos de Engenharia de Software, Engenharia de Computação e Ciência de Dados do IBMEC a explorarem suas afinidades com diferentes carreiras na área de tecnologia. Através de um chatbot dinâmico e conversacional, a aplicação busca entender os interesses e soft skills do aluno, gerando ao final um "prontuário" personalizado com insights e sugestões de carreira. Este prontuário é útil tanto para o aluno quanto para a equipe de Carreiras do IBMEC.

## Índice

* [Funcionalidades Principais](#funcionalidades-principais)
* [Tecnologias Utilizadas](#tecnologias-utilizadas)
* [Estrutura do Projeto](#estrutura-do-projeto)
* [Pré-requisitos](#pré-requisitos)
* [Configuração da API OpenAI](#configuração-da-api-openai)
* [Configuração e Instalação Local](#configuração-e-instalação-local)
* [Executando a Aplicação](#executando-a-aplicação)
* [Como Usar a Aplicação](#como-usar-a-aplicação)
* [Entendendo e Modificando o Comportamento da IA](#entendendo-e-modificando-o-comportamento-da-ia)
* [Principais Arquivos do Projeto](#principais-arquivos-do-projeto)
* [Contribuição](#contribuição)
* [Próximos Passos / Melhorias Futuras](#próximos-passos--melhorias-futuras)
* [License](#license)

## Funcionalidades Principais

* **Chatbot Inteligente e Dinâmico:** Interface de chat onde as perguntas são geradas e adaptadas em tempo real pela API da OpenAI com base na conversa.
* **Análise de Interesses e Soft Skills:** A IA é instruída para identificar afinidades técnicas e soft skills do aluno durante o diálogo.
* **Geração de "Prontuário do Aluno" em JSON:** Ao final da conversa, a IA gera um perfil detalhado em formato JSON contendo:
    * Interesses principais identificados.
    * Objetivos de carreira inferidos e/ou declarados.
    * Soft skills com evidências da conversa.
    * Hard skills mencionadas ou de interesse.
    * Sugestões de desenvolvimento e carreiras iniciais.
    * Observações gerais sobre a interação.
* **Relatórios Personalizados:**
    * **Relatório do Aluno:** Apresentação dos insights gerados pela IA de forma lúdica e orientadora.
    * **Relatório do Consultor de Carreiras:** Visão detalhada do prontuário gerado pela IA para auxiliar no aconselhamento.
* **Armazenamento de Perfis:** Os prontuários JSON gerados pela IA são salvos em um banco de dados SQLite.
* **"Salvar como PDF":** Os relatórios são páginas web que podem ser facilmente salvas como PDF.

## Tecnologias Utilizadas

* **Backend:** Python 3.x com Micro-framework Flask
* **Inteligência Artificial:** OpenAI (modelo GPT-4o-mini ou equivalente)
* **SDK da IA:** `openai`
* **Banco de Dados:** SQLite 3 (para armazenar os perfis gerados pela IA)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla/Puro)
* **Gerenciamento de Sessão:** Flask Sessions
* **Gerenciamento de Variáveis de Ambiente:** `python-dotenv`
* **Controle de Versão:** Git e GitHub

## Pré-requisitos

* Python 3.7 ou superior
* `pip` (gerenciador de pacotes Python)
* Git (para clonar o repositório)
* Uma chave de API válida da OpenAI.

## Configuração da API OpenAI

Antes de rodar o projeto localmente, você precisa obter uma chave de API da OpenAI:

1. Crie uma conta ou acesse [https://platform.openai.com/](https://platform.openai.com/) e gere uma chave de API.
2. Guarde essa chave de forma segura; ela será utilizada no arquivo `.env`.

## Configuração e Instalação Local

1.  **Clone o Repositório:**
    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_NO_GITHUB>
    cd mentoria-carreiras-ibmec 
    ```
    (Substitua `<URL_DO_SEU_REPOSITORIO_NO_GITHUB>` e `mentoria-carreiras-ibmec` se necessário).

2.  **Crie e Ative um Ambiente Virtual:**
    ```bash
    python -m venv venv
    # No Windows: .\venv\Scripts\activate
    # No macOS/Linux: source venv/bin/activate
    ```

3.  **Crie o Arquivo `.env`:**
    Na raiz do projeto, crie um arquivo chamado `.env` e adicione a seguinte variável, substituindo pelo seu valor:
    ```env
    OPENAI_API_KEY="SUA_CHAVE_OPENAI_AQUI"
    ```
    **IMPORTANTE:** Adicione `.env` ao seu arquivo `.gitignore`!

4.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    Seu `requirements.txt` deve incluir `Flask`, `openai`, `python-dotenv`.

5.  **Configure a Chave Secreta do Flask em `app.py`:**
    * Abra `app.py` e altere a linha `app.secret_key = '...'` para uma chave longa, aleatória e segura.

6.  **Banco de Dados:**
    * O arquivo `chatbot_com_ia.db` e a tabela `student_ai_profiles` serão criados automaticamente ao iniciar `app.py` pela primeira vez, devido à função `init_db()`.

## Executando a Aplicação

1.  Certifique-se de que seu ambiente virtual está ativo e as variáveis no `.env` estão corretas.
2.  No terminal, na raiz do projeto, execute:
    ```bash
    python app.py
    ```
3.  Acesse `http://127.0.0.1:5000/` no seu navegador.

## Deploy no Railway

1. Crie uma conta em [Railway](https://railway.app/) e conecte este repositório no painel web ou via [Railway CLI](https://docs.railway.app/reference/cli).
2. Ao criar o serviço, o Railway instalará automaticamente as dependências de `requirements.txt` e usará o `Procfile` para iniciar o servidor com `gunicorn`.
3. Defina as variáveis de ambiente necessárias no projeto (`OPENAI_API_KEY` e `FLASK_SECRET_KEY`). O Railway fornecerá automaticamente a variável `PORT`.
4. Inicie o deploy; após a conclusão, a aplicação estará disponível na URL gerada pelo Railway.

## Como Usar a Aplicação

1.  Acesse a URL no navegador.
2.  A saudação inicial do "GuIA Carreiras IBMEC" aparecerá.
3.  Responda às perguntas geradas dinamicamente pela IA. A conversa é aberta e visa explorar seus interesses.
4.  Quando a IA julgar que tem informações suficientes (ou você indicar que quer finalizar), ela perguntará se você deseja ver um resumo/perfil.
5.  Ao confirmar, seu perfil detalhado será gerado pela IA e você será redirecionado para a página de relatório.
6.  O relatório pode ser salvo em PDF usando a função "Imprimir" do navegador (escolha "Salvar como PDF").

## Entendendo e Modificando o Comportamento da IA

O comportamento do chatbot e a qualidade do perfil gerado são fortemente influenciados pelos "prompts de sistema" definidos em `openai_client.py`:

* **`DEFAULT_SYSTEM_INSTRUCTION_CAREER_GUIDE`:** Define a persona, o tom, os objetivos da conversa e como o GuIA deve interagir e fazer perguntas. Modificar este prompt altera a dinâmica do chat.
* **`SYSTEM_INSTRUCTION_JSON_GENERATOR`:** Instrui o modelo a gerar o perfil final estritamente no formato JSON especificado. Alterar os campos ou descrições aqui muda a estrutura do "prontuário do aluno".
* **Engenharia de Prompt:** Melhorar esses prompts é um processo iterativo. Teste diferentes formulações para otimizar a qualidade das interações e do perfil gerado.


## Principais Arquivos do Projeto

* **`app.py`**: Backend Flask, gerencia sessões, rotas da API, e orquestra chamadas ao `openai_client.py`.
* **`openai_client.py`**: Contém toda a lógica de interação com a API da OpenAI, incluindo inicialização, prompts de sistema, e as funções `conversar_com_openai` e `gerar_prontuario_com_openai`.
* **`.env`**: Armazena sua chave de API da OpenAI e configurações locais (NÃO DEVE SER VERSIONADO).
* **`static/script.js`**: Lógica do frontend para o chat, chamadas AJAX para o backend.
* **`templates/index.html`**: Interface do chat.
* **`templates/report.html`**: Página que exibe o perfil gerado pela IA.
* **`requirements.txt`**: Dependências Python.



## Próximos Passos / Melhorias Futuras

* Aprimorar continuamente os prompts de sistema para o modelo da OpenAI.
* Implementar uma interface de administração para visualizar os perfis salvos no banco de dados.
* Adicionar mais contexto ou conhecimento específico do IBMEC à IA (ex: via RAG - Retrieval Augmented Generation, se aplicável).
* Permitir que o aluno salve/exporte seu perfil de forma mais direta.
* Expandir as análises e os tipos de insights gerados.
* Testes automatizados.
* Deploy em ambiente de produção (ex: Google Cloud Run).


---
