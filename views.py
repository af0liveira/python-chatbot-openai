import os
from app import app, bot
from flask import (render_template, request, Response, redirect, url_for,
                   session, flash)
from count_tokens import count_tokens
from summarizer import summarizing
from models import usuarios


@app.route("/")
def home():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login'))
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


def process_response(prompt, chat_history, chat_file):
    partial_response = ""
    history_summary = summarizing(chat_history)
    response = bot(prompt, history_summary)
    for chunk in response:
        chunk_text = chunk.choices[0].delta.content
        if chunk_text:
            partial_response += chunk_text
            yield chunk_text
    with open(chat_file, 'w') as fp:
        fp.write(f"History: {history_summary}\n")
        fp.write(f"Usuário: {prompt}\n")
        fp.write(f"IA: {partial_response}\n")


@app.route("/chat", methods=['POST'])
def chat():
    prompt = request.json['msg']
    chat_file = session['usuario_logado']
    try:
        with open(chat_file, 'r') as fp:
            chat_history = fp.read()
    except FileNotFoundError as err:
        chat_history = ""
    return Response(process_response(prompt, chat_history, chat_file),
                    mimetype='text/event-stream')


@app.route("/limparhistorico", methods=['POST'])
def clear_history():
    chat_file = session['usuario_logado']
    try:
        os.remove(chat_file)
    except FileNotFoundError as err:
        print(f"Nothing to do! File {chat_file} not found.")
    else:
        print(f"File removed: {chat_file}")
    return {}


@app.route('/login')
def login():
    return render_template('login.html', proxima='/')

@app.route('/autenticar', methods=['POST',])
def autenticar():
    if request.form['usuario'] in usuarios:
        usuario = usuarios[request.form['usuario']]
        if request.form['senha'] == usuario.senha:
            session['usuario_logado'] = usuario.nickname
            flash(usuario.nickname + ' logado com sucesso!')
            return redirect(request.form['proxima'])
    else:
        flash('Usuário não logado.')
        return redirect(url_for('login'))
    

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('login'))
