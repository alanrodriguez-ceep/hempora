from flask import Flask, render_template, request, redirect, url_for, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

DATA_PATH = "data"
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

CHAT_CSV = os.path.join(DATA_PATH, "chat_mensagens.csv")

def salvar_csv(nome_arquivo, dados, cabecalho):
    caminho = os.path.join(DATA_PATH, nome_arquivo)
    precisa_cabecalho = not os.path.isfile(caminho) or os.stat(caminho).st_size == 0
    with open(caminho, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cabecalho)
        if precisa_cabecalho:
            writer.writeheader()
        writer.writerow(dados)

def salvar_mensagem_chat(texto, tipo='usuario'):
    dados = {
        "texto": texto,
        "tipo": tipo,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S")
    }
    
    cabecalho = ["texto", "tipo", "timestamp", "data", "hora"]
    salvar_csv("chat_mensagens.csv", dados, cabecalho)

def carregar_mensagens_chat():
    try:
        caminho = os.path.join(DATA_PATH, "chat_mensagens.csv")
        if not os.path.exists(caminho):
            return []
        
        mensagens = []
        with open(caminho, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                mensagens.append({
                    'texto': row['texto'],
                    'tipo': row['tipo'],
                    'timestamp': row['timestamp']
                })
        return mensagens
    except Exception as e:
        print(f"Erro ao carregar mensagens: {e}")
        return []

def registrar_clique_material(titulo, url, ip_usuario):
    """Registra cada clique nos materiais didáticos"""
    dados = {
        "titulo": titulo,
        "url": url,
        "ip_usuario": ip_usuario,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": datetime.now().strftime("%Y-%m-%d"),
        "hora": datetime.now().strftime("%H:%M:%S")
    }
    
    cabecalho = ["titulo", "url", "ip_usuario", "timestamp", "data", "hora"]
    salvar_csv("materiais.csv", dados, cabecalho)

@app.route('/')
def index():
    return render_template('index.html', pagina_atual='index')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', pagina_atual='cadastro')

@app.route('/sobre_o_projeto')
def sobre_o_projeto():
    return render_template('sobre_o_projeto.html', pagina_atual='sobre_o_projeto')

@app.route('/processo_legal')
def processo_legal():
    return render_template('processo_legal.html', pagina_atual='processo_legal')

@app.route('/chat')
def chat():
    return render_template('chat.html', pagina_atual='chat')

@app.route('/material_didatico')
def material_didatico():
    return render_template('material_didatico.html', pagina_atual='material_didatico')

@app.route('/listagem')
def listagem():
    return render_template('listagem.html', pagina_atual='listagem')

@app.route('/feedback')
def feedback():
    return render_template('feedback.html', pagina_atual='feedback')

@app.route('/registrar_clique', methods=['POST'])
def registrar_clique():
    """Rota para registrar cliques nos materiais"""
    data = request.get_json()
    if data and 'titulo' in data and 'url' in data:
        titulo = data['titulo']
        url = data['url']
        ip_usuario = request.remote_addr
        
        registrar_clique_material(titulo, url, ip_usuario)
        return jsonify({'status': 'success', 'message': 'Clique registrado com sucesso'})
    
    return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400

@app.route('/api/mensagens', methods=['GET', 'POST'])
def api_mensagens():
    if request.method == 'GET':
        mensagens = carregar_mensagens_chat()
        return jsonify({'mensagens': mensagens})
    
    elif request.method == 'POST':
        data = request.get_json()
        if data and 'texto' in data:
            texto = data['texto'].strip()
            if texto:
                salvar_mensagem_chat(texto, 'usuario')
                
                resposta_texto = "Obrigado pela sua mensagem! Nossa equipe responderá em breve."
                salvar_mensagem_chat(resposta_texto, 'outro')
                
                return jsonify({'status': 'success'})
        
        return jsonify({'status': 'error', 'message': 'Dados inválidos'}), 400

@app.route('/cadastrar_form', methods=['POST'])
def cadastrar_form():
    dados = {
        "nome": request.form.get("nome"),
        "idade": request.form.get("idade"),
        "telefone": request.form.get("telefone"),
        "cpf": request.form.get("cpf"),
        "email": request.form.get("email"),
        "etnia": request.form.get("etnia"),
        "genero": request.form.get("genero"),
        "condicoes": request.form.get("condicoes"),
        "tratamento": request.form.get("tratamento"),
        "esta_tratando": request.form.get("esta_tratando"),
        "consultou": request.form.get("consultou"),
        "contraindicacao": request.form.get("contraindicacao"),
        "data_cadastro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    campos = list(dados.keys())
    salvar_csv("usuarios.csv", dados, campos)
    return redirect(url_for('cadastro'))

@app.route('/enviar_feedback', methods=['POST'])
def enviar_feedback():
    dados = {
        "id_usuario": request.form.get("id_usuario", ""),
        "tipo": request.form.get("tipo"),
        "descricao": request.form.get("descricao"),
        "data_envio": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    campos = ["id_usuario", "tipo", "descricao", "data_envio"]
    salvar_csv("feedbacks.csv", dados, campos)
    
    return render_template('feedback.html', mensagem="Feedback enviado com sucesso!", pagina_atual='feedback')

@app.route('/admin/chat')
def admin_chat():
    mensagens = carregar_mensagens_chat()
    return render_template('admin_chat.html', mensagens=mensagens, pagina_atual='admin_chat')

@app.route('/cadastro_concluido')
def cadastro_concluido():
    return render_template('cadastro_concluido.html', pagina_atual='cadastro_concluido')

@app.route('/admin/materiais')
def admin_materiais():
    """Página admin para visualizar os cliques nos materiais"""
    try:
        caminho = os.path.join(DATA_PATH, "materiais.csv")
        if not os.path.exists(caminho):
            materiais = []
        else:
            with open(caminho, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                materiais = list(reader)
        
        return render_template('admin_materiais.html', materiais=materiais, pagina_atual='admin_materiais')
    except Exception as e:
        print(f"Erro ao carregar materiais: {e}")
        return render_template('admin_materiais.html', materiais=[], pagina_atual='admin_materiais')

if __name__ == '__main__':
    app.run(debug=True)