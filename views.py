from app import app, bot
from flask import render_template, request, Response
import os 
from helpers import *
from conta_tokens import *

def limita_historico(historico,limite_maximo_de_tokens):
    total_de_tokens = 0
    historico_parcial = ''
    for linha in reversed(historico.split('\n')):
        tokens_da_linha = conta_tokens(linha)
        total_de_tokens = total_de_tokens + tokens_da_linha
        if (total_de_tokens > limite_maximo_de_tokens):
            break
        historico_parcial = linha + historico_parcial
    return historico_parcial

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat",methods = ['POST'])
def chat():
    prompt = request.json['msg']
    nome_do_arquivo = 'historico_ecomart'
    historico = ''
    if os.path.exists(nome_do_arquivo):
        historico = carrega(nome_do_arquivo)
    return Response(trata_resposta(prompt,historico,nome_do_arquivo), mimetype = 'text/event-stream')

def trata_resposta(prompt,historico,nome_do_arquivo):
    resposta_parcial = ''
    limite_maximo_de_tokens = 2000
    historico_parcial = limita_historico(historico,limite_maximo_de_tokens)
    for resposta in bot(prompt,historico_parcial):
        pedaco_da_resposta = resposta.choices[0].delta.get('content','')
        if len(pedaco_da_resposta):
            resposta_parcial += pedaco_da_resposta
            yield pedaco_da_resposta 
    conteudo = f"""
    Historico: {historico_parcial}
    Usuário: {prompt}
    IA: {resposta_parcial}    
    """
    salva(nome_do_arquivo,conteudo)

@app.route('/limparhistorico', methods = ['POST'])
def limpar_historico():
    nome_do_arquivo = 'historico_ecomart'
    if os.path.exists(nome_do_arquivo):
        os.remove(nome_do_arquivo)
        print("Arquivo removido!")
    else: 
        print("Não foi possivel remover esse arquivo")
    return {}