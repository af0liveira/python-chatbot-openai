from flask import Flask,render_template, request
import os
import openai
import dotenv

app = Flask(__name__)
app.secret_key = 'alura'
    
dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods = ['POST'])
def chat():
    prompt = request.json['msg']
    resposta = bot(prompt = prompt)

if __name__ == "__main__":
    app.run(debug = True)
