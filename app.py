from flask import Flask, render_template, request, Response
from time import sleep
import os
import openai
import dotenv
import tiktoken


app = Flask(__name__)
app.secret_key = 'alura'
    
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_file = './chat_history.txt'

# Carrega os dados do e-commerce
with open('./dados_ecommerce.txt', 'rb') as fp:
    dados_ecommerce = fp.read()


def count_tokens(prompt):
    encoder = tiktoken.encoding_for_model('gpt-3.5-turbo')
    tokens = encoder.encode(prompt)
    return len(tokens)

def bot(prompt, chat_history):
    max_repetition = 1
    repetition = 0
    while True:
        try:
            model='gpt-3.5-turbo'
            system_prompt = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!

            #### Dados do e-commerce
            {dados_ecommerce}

            #### Histórico
            {chat_history}
            """
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                stream=True,
                temperature=1,
                max_tokens=256,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
            )
            return response
        except Exception as err:
            repetition += 1
            if repetition >= max_repetition:
                return f"Erro no GPT3: {err}"
            print(f"Erro de comunicação com OpenAI: {err}")
            sleep(1)

@app.route("/")
def home():
    return render_template("index.html")

def constrain_chat_history(chat_history):
    max_tokens = 2_000
    tokens_count = 0
    partial_history = ""
    for line in reversed(chat_history.split('\n')):
        tokens_count += count_tokens(line)
        if tokens_count > max_tokens:
            break
        partial_history = f'{line}' + partial_history
    return partial_history

def process_response(prompt, chat_history):
    partial_response = ""
    partial_history = constrain_chat_history(chat_history)
    print("PARTIAL", flush=True)
    print(partial_history, flush=True)
    response = bot(prompt, partial_history)
    for chunk in response:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text:
            partial_response += chunk_text
            yield chunk_text
    with open(chat_file, 'a') as fp:
        fp.write(f"Usuário: {prompt}\n")
        fp.write(f"IA: {partial_response}\n")

@app.route("/chat", methods=['POST'])
def chat():
    prompt = request.json['msg']
    try:
        with open(chat_file, 'r') as fp:
            chat_history = fp.read()
    except FileNotFoundError as err:
        chat_history = ""
    return Response(process_response(prompt, chat_history),
                    mimetype='text/event-stream')

@app.route("/limparhistorico", methods=['POST'])
def clear_history():
    try:
        os.remove(chat_file)
    except FileNotFoundError as err:
        print(f"Nothing to do! File {chat_file} not found.")
    else:
        print(f"File removed: {chat_file}")
    return {}


if __name__ == "__main__":
    app.run(debug = True)
