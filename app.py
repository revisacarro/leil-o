from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# Arquivos
ARQUIVO_COMPRAS = "compras.json"
ARQUIVO_PRODUTOS = "produtos.json"

# Funções para carregar e salvar produtos/compras
def carregar_compras():
    if os.path.exists(ARQUIVO_COMPRAS):
        with open(ARQUIVO_COMPRAS, "r") as f:
            return json.load(f)
    return []

def salvar_compras(compras):
    with open(ARQUIVO_COMPRAS, "w") as f:
        json.dump(compras, f, indent=2)

def carregar_produtos():
    if os.path.exists(ARQUIVO_PRODUTOS):
        with open(ARQUIVO_PRODUTOS, "r") as f:
            return json.load(f)
    return []

# Mensagens por produto (em memória)
produto_mensagens = {}

# Rotas
@app.route("/")
def index():
    produtos = carregar_produtos()
    # Adiciona lista de mensagens se não existir
    for p in produtos:
        if p['id'] not in produto_mensagens:
            produto_mensagens[p['id']] = []
        p['mensagens'] = produto_mensagens[p['id']]
    return render_template("index.html", produtos=produtos)

@app.route("/nova_mensagem/<int:produto_id>", methods=["POST"])
def nova_mensagem(produto_id):
    data = request.get_json()
    texto = data.get("texto","")
    if produto_id not in produto_mensagens:
        produto_mensagens[produto_id] = []
    
    produto_mensagens[produto_id].append({"autor":"usuario","texto":texto})
    # Limite de 3 mensagens
    produto_mensagens[produto_id] = produto_mensagens[produto_id][-3:]
    return jsonify(produto_mensagens[produto_id])

@app.route("/comprar/<int:produto_id>", methods=["GET", "POST"])
def finalizar_compra(produto_id):
    produtos = carregar_produtos()
    produto = next((p for p in produtos if p['id']==produto_id), None)
    if not produto:
        return "Produto não encontrado", 404

    if request.method == "POST":
        numero = request.form['whatsapp']
        compras = carregar_compras()
        compras.append({"produto_id": produto_id, "numero": numero})
        salvar_compras(compras)
        return redirect(url_for('agradecimento'))

    return render_template("compra.html", produto=produto)

@app.route("/agradecimento")
def agradecimento():
    return render_template("agradecimento.html")

if __name__ == "__main__":
    app.run(debug=True)
