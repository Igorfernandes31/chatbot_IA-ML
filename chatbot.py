import numpy as np
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import threading
import string

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    stop_words = set(stopwords.words('portuguese'))
    words = word_tokenize(text.lower())
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return ' '.join(filtered_words)

def remover_pontuacao(texto):
    return texto.translate(str.maketrans('', '', string.punctuation))

data = {
    'cumprimento': ['olá', 'oi', 'como vai', 'bom dia', 'boa tarde', 'boa noite'],
    'despedida': ['tchau', 'até mais', 'adeus', 'se cuida'],
    'agradecimento': ['obrigado', 'muito obrigado', 'agradeço', 'valeu'],
    'seguranca': [
        'O que é phishing?',
        'Como se proteger contra malware?',
        'O que é um firewall?',
        'Como proteger minhas senhas?',
        'O que é autenticação de dois fatores?',
        'Como evitar ataques de phishing?',
        'O que é ransomware?',
        'Como se manter seguro online?',
        'O que é um antivírus?',
        'Como criar uma senha forte?',
        'O que é Segurança da Informação?'
    ],
    'sem resposta': [' ']
}

respostas_seguranca = {
    'phishing': 'Phishing é um tipo de ataque de engenharia social onde os atacantes enganam os usuários para fornecer informações sensíveis.',
    'malware': 'Use software antivírus, mantenha seu sistema atualizado e evite clicar em links suspeitos.',
    'firewall': 'Um firewall é um dispositivo de segurança de rede que monitora e filtra o tráfego de rede de entrada e saída com base em regras de segurança.',
    'senhas': 'Use senhas fortes e únicas para cada conta e considere usar um gerenciador de senhas.',
    'autenticação de dois fatores': 'A autenticação de dois fatores é uma camada extra de segurança usada para garantir que as pessoas que tentam acessar uma conta online sejam quem dizem ser.',
    'ransomware': 'Ransomware é um tipo de malware que criptografa os arquivos de um usuário e exige um pagamento de resgate para restaurar o acesso.',
    'segurança online': 'Use senhas fortes, habilite a autenticação de dois fatores, evite compartilhar informações pessoais e mantenha seu software atualizado.',
    'antivírus': 'Um antivírus é um software projetado para detectar e destruir vírus de computador.',
    'senha forte': 'Uma senha forte deve ter pelo menos 12 caracteres, incluir uma mistura de letras, números e símbolos, e não deve ser baseada em informações facilmente adivinháveis.',
    'segurança da informação': 'Segurança da informação é a prática de proteger informações contra acesso não autorizado, divulgação, interrupção, modificação ou destruição. Isso inclui a implementação de políticas, processos e controles para proteger a confidencialidade, integridade e disponibilidade da informação.'
}

categorias = list(data.keys())
todas_frases = []
rotulos = []

for categoria, frases in data.items():
    for frase in frases:
        todas_frases.append(preprocess_text(remover_pontuacao(frase)))
        rotulos.append(categoria)

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(todas_frases)
y = np.array(rotulos)


model = MultinomialNB()
model.fit(X, y)

def prever_categoria(texto):
    texto_processado = preprocess_text(remover_pontuacao(texto))
    vetor_texto = vectorizer.transform([texto_processado])
    previsao = model.predict(vetor_texto)
    return previsao[0]

def resposta_chatbot(input_usuario):
    input_usuario = input_usuario.lower()
    categoria = prever_categoria(input_usuario)
    if categoria == 'cumprimento':
        return "Olá! Como posso ajudar você hoje?"
    elif categoria == 'despedida':
        return "Adeus! Tenha um ótimo dia!"
    elif categoria == 'agradecimento':
        return "De nada!"
    elif categoria == 'seguranca':
        palavras_chave = respostas_seguranca.keys()
        for palavra in palavras_chave:
            if palavra in input_usuario:
                return respostas_seguranca[palavra]
        return "Não tenho certeza de como responder a essa pergunta específica, mas posso ajudar com perguntas gerais sobre segurança."
    else:
        return "Não tenho certeza de como responder a isso."

def enviar_mensagem():
    global timer
    mensagem_usuario = entrada_usuario.get()
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Você: " + mensagem_usuario + '\n', 'usuario')
    resposta = resposta_chatbot(mensagem_usuario)
    chat_log.insert(tk.END, "Iguinho: " + resposta + '\n', 'chatbot')
    chat_log.config(state=tk.DISABLED)
    entrada_usuario.delete(0, tk.END)
    reset_timer()

def timeout():
    global timer, inatividade
    inatividade = True
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Iguinho: Deseja continuar ou posso encerrar a sessão?\n", 'chatbot')
    chat_log.config(state=tk.DISABLED)
    timer = threading.Timer(60.0, finalizar_sessao)
    timer.start()

def finalizar_sessao():
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Iguinho: Obrigado! Espero ter te ajudado! Sessão encerrada..\n", 'chatbot')
    chat_log.config(state=tk.DISABLED)
    pedir_avaliacao()

def pedir_avaliacao():
    nota = simpledialog.askinteger("Avaliação", "Por favor, avalie o atendimento de 0 a 5:")
    if nota is not None:
        messagebox.showinfo("Avaliação", f"Obrigado pela sua avaliação de {nota}!")
    janela.destroy()

def reset_timer():
    global timer, inatividade
    if inatividade:
        chat_log.config(state=tk.NORMAL)
        resposta = entrada_usuario.get().strip().lower()
        if resposta in ['sim', 'sim!', 'desejo continuar', 'continuar']:
            chat_log.insert(tk.END, "Iguinho: Tudo bem, vamos continuar! Qual é sua outra dúvida sobre segurança da informação?\n", 'chatbot')
            inatividade = False
            chat_log.config(state=tk.DISABLED)
            reset_timer()
            return
        elif resposta in ['não', 'nao', 'não!', 'nao!', 'não desejo continuar', 'não desejo continuar!', 'nao desejo continuar', 'nao desejo continuar!', 'pode encerrar', 'encerrar']:
            finalizar_sessao()
            return
        else:
            chat_log.insert(tk.END, "Iguinho: Não entendi bem. Vamos continuar! Qual é sua dúvida sobre segurança da informação?\n", 'chatbot')
            inatividade = False
        chat_log.config(state=tk.DISABLED)
    if timer is not None:
        timer.cancel()
    timer = threading.Timer(60.0, timeout)
    timer.start()

def finalizar_sessao_botao():
    finalizar_sessao()

inatividade = False
timer = None

janela = tk.Tk()
janela.title("Chatbot de Segurança da Informação")
janela.geometry("500x550")

chat_log = scrolledtext.ScrolledText(janela, wrap=tk.WORD, bg="white", state=tk.DISABLED)
chat_log.place(x=6, y=6, height=486, width=488)

chat_log.tag_config('usuario', background="#D1E7DD", foreground="black")
chat_log.tag_config('chatbot', background="#6C757D", foreground="white")

entrada_usuario = tk.Entry(janela, bg="white")
entrada_usuario.place(x=6, y=500, height=40, width=300)

botao_enviar = tk.Button(janela, text="Enviar", command=enviar_mensagem)
botao_enviar.place(x=320, y=500, height=40, width=70)
botao_finalizar = tk.Button(janela, text="Finalizar Sessão", command=finalizar_sessao_botao)
botao_finalizar.place(x=400, y=500, height=40, width=90)

def mensagem_introducao():
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "Iguinho: Olá, eu sou o Iguinho, o seu amigo Bot que vai te ajudar com dúvidas sobre segurança da informação. Qual sua dúvida hoje?\n", 'chatbot')
    chat_log.config(state=tk.DISABLED)
    reset_timer()

mensagem_introducao()
janela.mainloop()