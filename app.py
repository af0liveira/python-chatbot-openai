from flask import Flask, render_template, request, Response
from time import sleep
import os
import openai
import dotenv


app = Flask(__name__)
app.secret_key = 'alura'
    
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def bot(prompt):
    max_repetition = 1
    repetition = 0
    while True:
        try:
            model='gpt-3.5-turbo'
            system_prompt = f"""
            Você é um chatbot de atendimento a clientes de um e-commerce.
            Você não deve responder perguntas que não sejam dados do ecommerce informado!
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

def process_response(prompt):
    partial_response = ""
    response = bot(prompt)
    for chunk in response:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text:
            partial_response += chunk_text
            yield chunk_text

@app.route("/chat", methods=['POST'])
def chat():
    prompt = request.json['msg']
    return Response(process_response(prompt), mimetype='text/event-stream')


if __name__ == "__main__":
    app.run(debug = True)
