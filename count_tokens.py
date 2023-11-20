import tiktoken


def count_tokens(prompt):
    encoder = tiktoken.encoding_for_model('gpt-3.5-turbo')
    tokens = encoder.encode(prompt)
    return len(tokens)
