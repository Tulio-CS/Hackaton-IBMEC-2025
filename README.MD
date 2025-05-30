# MentorIA Carreiras IBMEC - MVP com IA

## Descrição do Projeto

O "MentorIA Carreiras IBMEC" é um aplicativo web inovador que utiliza Inteligência Artificial (Vertex AI Gemini do Google Cloud) para auxiliar alunos dos primeiros períodos dos cursos de Engenharia de Software, Engenharia de Computação e Ciência de Dados do IBMEC a explorarem suas afinidades com diferentes carreiras na área de tecnologia. Através de um chatbot dinâmico e conversacional, a aplicação busca entender os interesses e soft skills do aluno, gerando ao final um "prontuário" personalizado com insights e sugestões de carreira. Este prontuário é útil tanto para o aluno quanto para a equipe de Carreiras do IBMEC.

## Índice

* [Funcionalidades Principais](#funcionalidades-principais)
* [Tecnologias Utilizadas](#tecnologias-utilizadas)
* [Estrutura do Projeto](#estrutura-do-projeto)
* [Pré-requisitos](#pré-requisitos)
* [Configuração do Ambiente Google Cloud (Vertex AI)](#configuração-do-ambiente-google-cloud-vertex-ai)
* [Configuração e Instalação Local](#configuração-e-instalação-local)
* [Executando a Aplicação](#executando-a-aplicação)
* [Como Usar a Aplicação](#como-usar-a-aplicação)
* [Entendendo e Modificando o Comportamento da IA](#entendendo-e-modificando-o-comportamento-da-ia)
* [Principais Arquivos do Projeto](#principais-arquivos-do-projeto)
* [Contribuição](#contribuição)
* [Próximos Passos / Melhorias Futuras](#próximos-passos--melhorias-futuras)
* [License](#license)

## Funcionalidades Principais

* **Chatbot Inteligente e Dinâmico:** Interface de chat onde as perguntas são geradas e adaptadas em tempo real pela Vertex AI (Gemini) com base na conversa.
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
* **Inteligência Artificial:** Google Cloud Vertex AI (Modelo Gemini Pro/Flash)
* **SDK da IA:** `google-cloud-aiplatform`
* **Banco de Dados:** SQLite 3 (para armazenar os perfis gerados pela IA)
* **Frontend:** HTML5, CSS3, JavaScript (Vanilla/Puro)
* **Gerenciamento de Sessão:** Flask Sessions
* **Gerenciamento de Variáveis de Ambiente:** `python-dotenv`
* **Controle de Versão:** Git e GitHub

## Pré-requisitos

* Python 3.7 ou superior
* `pip` (gerenciador de pacotes Python)
* Git (para clonar o repositório)
* Uma conta Google Cloud com um projeto configurado e faturamento habilitado.
* Uma Conta de Serviço (Service Account) no GCP com permissões para a Vertex AI e a chave JSON baixada.

## Configuração do Ambiente Google Cloud (Vertex AI)

Antes de rodar o projeto localmente, você precisa configurar seu ambiente no Google Cloud:

1.  **Crie/Selecione um Projeto GCP.**
2.  **Habilite o Faturamento** para o projeto.
3.  **Habilite a API "Vertex AI API"** no seu projeto.
4.  **Crie uma Conta de Serviço:**
    * Vá em "IAM e Admin" > "Contas de Serviço".
    * Crie uma nova conta ou use uma existente.
    * Atribua o papel **"Usuário da Vertex AI" (Vertex AI User)** a esta conta.
    * Crie uma **chave JSON** para esta conta de serviço e faça o download para sua máquina. Guarde este arquivo em um local seguro.

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
    Na raiz do projeto, crie um arquivo chamado `.env` e adicione as seguintes variáveis, substituindo pelos seus valores:
    ```env
    GCP_PROJECT_ID="SEU_ID_DE_PROJETO_GCP"
    GCP_REGION="sua-regiao-gcp-ex-southamerica-east1"
    GOOGLE_APPLICATION_CREDENTIALS="/caminho/completo/para/seu/arquivo-chave-service-account.json"
    ```
    **IMPORTANTE:** Adicione `.env` ao seu arquivo `.gitignore`!

4.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```
    Seu `requirements.txt` deve incluir `Flask`, `google-cloud-aiplatform`, `python-dotenv`.

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

## Como Usar a Aplicação

1.  Acesse a URL no navegador.
2.  A saudação inicial do "GuIA Carreiras IBMEC" aparecerá.
3.  Responda às perguntas geradas dinamicamente pela IA. A conversa é aberta e visa explorar seus interesses.
4.  Quando a IA julgar que tem informações suficientes (ou você indicar que quer finalizar), ela perguntará se você deseja ver um resumo/perfil.
5.  Ao confirmar, seu perfil detalhado será gerado pela IA e você será redirecionado para a página de relatório.
6.  O relatório pode ser salvo em PDF usando a função "Imprimir" do navegador (escolha "Salvar como PDF").

## Entendendo e Modificando o Comportamento da IA

O comportamento do chatbot e a qualidade do perfil gerado são fortemente influenciados pelos "prompts de sistema" definidos em `gemini_client.py`:

* **`DEFAULT_SYSTEM_INSTRUCTION_CAREER_GUIDE`:** Define a persona, o tom, os objetivos da conversa e como o GuIA deve interagir e fazer perguntas. Modificar este prompt altera a dinâmica do chat.
* **`SYSTEM_INSTRUCTION_JSON_GENERATOR`:** Instrui o modelo a gerar o perfil final estritamente no formato JSON especificado. Alterar os campos ou descrições aqui muda a estrutura do "prontuário do aluno".
* **Engenharia de Prompt:** Melhorar esses prompts é um processo iterativo. Teste diferentes formulações para otimizar a qualidade das interações e do perfil gerado.

O arquivo `questions.json` do MVP anterior não é mais usado para o fluxo principal de perguntas, que agora é dinâmico.

## Principais Arquivos do Projeto

* **`app.py`**: Backend Flask, gerencia sessões, rotas da API, e orquestra chamadas ao `gemini_client.py`.
* **`gemini_client.py`**: Contém toda a lógica de interação com a Vertex AI (Gemini), incluindo inicialização, prompts de sistema, e as funções `conversar_com_gemini` e `gerar_prontuario_com_gemini`.
* **`.env`**: Armazena suas credenciais e configurações do GCP (NÃO DEVE SER VERSIONADO).
* **`static/script.js`**: Lógica do frontend para o chat, chamadas AJAX para o backend.
* **`templates/index.html`**: Interface do chat.
* **`templates/report.html`**: Página que exibe o perfil gerado pela IA.
* **`requirements.txt`**: Dependências Python.

## Contribuição

* Para novas ideias ou grandes mudanças, discuta com o grupo.
* Use branches do Git para desenvolvimento (`git checkout -b sua-feature`).
* Faça commits claros e descritivos.
* Teste suas alterações.
* Abra Pull Requests para revisão.
* Mantenha a documentação (este README) atualizada.

## Próximos Passos / Melhorias Futuras

* Aprimorar continuamente os prompts de sistema para o Gemini.
* Implementar uma interface de administração para visualizar os perfis salvos no banco de dados.
* Adicionar mais contexto ou conhecimento específico do IBMEC à IA (ex: via RAG - Retrieval Augmented Generation, se aplicável).
* Permitir que o aluno salve/exporte seu perfil de forma mais direta.
* Expandir as análises e os tipos de insights gerados.
* Testes automatizados.
* Deploy em ambiente de produção (ex: Google Cloud Run).


---