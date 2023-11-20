from flask import Flask, request, Response
from time import sleep
import os
import openai
import dotenv
import tiktoken

app = Flask(__name__)
app.secret_key = 'alura'

from views import *
    
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Carrega os dados do e-commerce
with open('./dados_ecommerce.txt', 'rb') as fp:
    dados_ecommerce = fp.read()


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


if __name__ == "__main__":
    app.run(debug = True)
