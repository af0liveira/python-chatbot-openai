import os
from app import app, bot
from flask import render_template, request, Response
from count_tokens import count_tokens
from summarizer import summarizing

chat_file = './chat_history.txt'

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