// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chatMessages');
    const inputControls = document.getElementById('inputControls');
    let esperandoConfirmacaoResumo = false; // Controla se o app está aguardando a confirmação Sim/Não para gerar o resumo.

    function addMessage(messageText, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender === 'bot' ? 'bot-message' : 'user-message');
        const paragraphElement = document.createElement('p');
        paragraphElement.innerHTML = messageText.replace(/\n/g, '<br>'); // Permite quebras de linha do Gemini
        messageElement.appendChild(paragraphElement);
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function renderTextInput(placeholder = 'Digite sua resposta aqui...') {
        inputControls.innerHTML = ''; 
        const inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.id = 'userInput';
        inputField.placeholder = placeholder;
        const sendButton = document.createElement('button');
        sendButton.id = 'sendButton';
        sendButton.textContent = 'Enviar';
        
        sendButton.addEventListener('click', handleSendMessage);
        inputField.addEventListener('keypress', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // Evita o comportamento padrão do Enter
                handleSendMessage();
            }
        });
        inputControls.appendChild(inputField);
        inputControls.appendChild(sendButton);
        if (document.activeElement !== inputField) { // Evita roubar foco desnecessariamente
            inputField.focus();
        }
    }

    function renderConfirmationButtons() {
        inputControls.innerHTML = '';
        // A mensagem do bot que contém a pergunta "Gostaria de ver um resumo agora?" já foi exibida.
        // Aqui apenas adicionamos os botões de confirmação.

        const buttonContainer = document.createElement('div');
        buttonContainer.style.display = 'flex';
        buttonContainer.style.justifyContent = 'center';
        buttonContainer.style.gap = '10px';
        buttonContainer.style.padding = '10px';

        const yesButton = document.createElement('button');
        yesButton.textContent = 'Sim, gerar meu perfil!';
        yesButton.classList.add('option-button');
        yesButton.addEventListener('click', () => {
            addMessage('Sim, por favor!', 'user'); 
            handleProfileGenerationRequest();
        });

        const noButton = document.createElement('button');
        noButton.textContent = 'Ainda não, conversar mais';
        noButton.classList.add('option-button');
        noButton.addEventListener('click', () => {
            const userResponseToContinue = 'Ainda não, gostaria de conversar um pouco mais.';
            addMessage(userResponseToContinue, 'user'); 
            esperandoConfirmacaoResumo = false; // Usuário fez uma escolha, não está mais esperando esta confirmação.
            handleApiChatMessage(userResponseToContinue); // Envia esta intenção para a IA continuar a conversa.
        });

        buttonContainer.appendChild(yesButton);
        buttonContainer.appendChild(noButton);
        inputControls.appendChild(buttonContainer);
    }
    
    async function handleApiChatMessage(text) {
        setChatInputDisabled(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: text }),
            });
            
            setChatInputDisabled(false); 

            if (!response.ok) {
                const errorData = await response.json();
                addMessage(errorData.error || `Erro HTTP: ${response.status}`, 'bot');
                renderTextInput("Ocorreu um erro. Tente novamente ou recarregue.");
                return; 
            }

            const data = await response.json();

            if (data.bot_response) {
                addMessage(data.bot_response, 'bot');
            }

            if (data.session_restarted) {
                renderTextInput("Sua sessão foi reiniciada. Como posso ajudar?");
                esperandoConfirmacaoResumo = false;
            } else if (data.end_of_quiz_phase_reached) {
                esperandoConfirmacaoResumo = true;
                // A pergunta do bot (data.bot_response) já foi exibida.
                // Agora renderizamos os botões Sim/Não para essa pergunta.
                renderConfirmationButtons();
            } else {
                renderTextInput(); 
            }

        } catch (error) {
            console.error('Erro em handleApiChatMessage:', error);
            addMessage(`Erro na comunicação com o servidor: ${error.message}. Tente recarregar a página.`, 'bot');
            setChatInputDisabled(false);
            renderTextInput();
        }
    }

    async function handleSendMessage() {
        const userInputField = document.getElementById('userInput');
        if (!userInputField || userInputField.disabled) return;
        const text = userInputField.value.trim();
        if (text === '') return;

        addMessage(text, 'user'); 

        userInputField.value = ''; 
        
        if(esperandoConfirmacaoResumo){
            // Se o usuário digitar em vez de usar os botões de confirmação,
            // resetamos o flag e enviamos o texto para a IA.
            esperandoConfirmacaoResumo = false; 
        }
        handleApiChatMessage(text);
    }

    async function handleProfileGenerationRequest() {
        esperandoConfirmacaoResumo = false; // Sai do estado de espera de confirmação
        inputControls.innerHTML = '<p style="text-align:center; padding:10px;">Gerando seu perfil personalizado, aguarde um momento...</p>';
        setChatInputDisabled(true); 

        try {
            const response = await fetch('/api/generate_profile', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // O backend usa o histórico da sessão, não é necessário enviar corpo.
            });

            if (!response.ok) {
                const errorData = await response.json();
                addMessage(errorData.error || `Falha ao gerar perfil (HTTP ${response.status})`, 'bot');
                setChatInputDisabled(false); 
                renderTextInput("Houve um problema. Tentar gerar o perfil novamente ou conversar mais?");
                return;
            }
            const data = await response.json();

            if (data.profile_generation_complete) {
                addMessage(data.message, 'bot');
                setTimeout(() => { window.location.href = '/report'; }, 2000); // Atraso para o usuário ler a mensagem
            } else {
                // Caso o backend retorne 200 OK mas com um erro no payload JSON
                addMessage(data.error || "Houve um problema inesperado ao gerar seu perfil.", 'bot');
                setChatInputDisabled(false);
                renderTextInput("Houve um problema ao gerar. Tentar novamente ou conversar mais?");
            }
        } catch (error) {
            console.error('Erro ao solicitar geração de perfil:', error);
            addMessage(`Erro crítico ao gerar seu perfil: ${error.message}.`, 'bot');
            setChatInputDisabled(false);
            renderTextInput("Houve um erro crítico. Tente recarregar ou contate o suporte.");
        }
    }
    
    function setChatInputDisabled(disabled) {
        const userInput = document.getElementById('userInput');
        const sendButton = document.getElementById('sendButton');
        if (userInput) userInput.disabled = disabled;
        if (sendButton) sendButton.disabled = disabled;
        document.querySelectorAll('.option-button').forEach(button => { button.disabled = disabled; });
    }

    async function startChat() {
        setChatInputDisabled(true);
        inputControls.innerHTML = '<p style="text-align:center; padding:10px;">Iniciando o GuIA Carreiras IBMEC...</p>';
        try {
            const response = await fetch('/api/start_session');
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro HTTP: ${response.status}`);
            }
            const data = await response.json();
            addMessage(data.initial_message, 'bot'); 
            renderTextInput(); 
            setChatInputDisabled(false);
        } catch (error) {
            console.error('Erro ao iniciar chat:', error);
            addMessage(`Não consegui iniciar nossa conversa: ${error.message}.`, 'bot');
            inputControls.innerHTML = '<p style="text-align:center; padding:10px;">Falha ao iniciar. Tente recarregar a página.</p>';
        }
    }
    startChat();
});