let chat = document.querySelector('#chat');
let input = document.querySelector('#input');
let botaoEnviar = document.querySelector('#botao-enviar');

async function enviarMensagem() {
    if(input.value == "" || input.value == null) return;
    let mensagem = input.value;
    input.value = "";

    let novaBolha = criaBolhaUsuario();
    novaBolha.innerHTML = mensagem;
    chat.appendChild(novaBolha);

    let novaBolhaBot = criaBolhaBot();
    chat.appendChild(novaBolhaBot);
    vaiParaFinalDoChat();
    
    // Envia requisição com a mensagem para a API do ChatBot
    const resposta = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
        },
        body: JSON.stringify({'msg':mensagem}),
    });

    const decoder = new TextDecoder();
    const responseReader = resposta.body.getReader();
    let partialResponse = "";
    while (true) {
        // Wait and receive next response chunck from the API
        const {done: completed, value: responseChunk} = await responseReader.read();
        if (completed) break;

        // Append new partial response and refresh screen
        partialResponse += decoder.decode(responseChunk).replace(/\n/g, "<br>");
        novaBolhaBot.innerHTML = partialResponse;
        vaiParaFinalDoChat();
    }

    const textoDaResposta = await resposta.text();
    novaBolhaBot.innerHTML = textoDaResposta;
    vaiParaFinalDoChat();
}

function criaBolhaUsuario() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--usuario';
    return bolha;
}

function criaBolhaBot() {
    let bolha = document.createElement('p');
    bolha.classList = 'chat__bolha chat__bolha--bot';
    return bolha;
}

function vaiParaFinalDoChat() {
    chat.scrollTop = chat.scrollHeight;
}

function clearChat(){
    const limpar = fetch("http://127.0.0.1:5000/limparhistorico", {
        method: "POST"
    });
    chat.innerHTML = "<p class='chat__bolha chat__bolha--bot'>Olá! Eu sou o assistente virtual da EcoMart ~<br/><br/>Como posso te ajudar?</p>";
}


botaoEnviar.addEventListener('click', enviarMensagem);
input.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        botaoEnviar.click();
    }
});