from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import json

app = Flask(__name__)

# Diretório para uploads e para dados JSON
UPLOAD_FOLDER = 'uploads'
DATA_FOLDER = 'data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DATA_FOLDER'] = DATA_FOLDER

# Criando os diretórios, se não existirem
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Função para ler dados de JSON
def read_data():
    data_file = os.path.join(app.config['DATA_FOLDER'], 'files.json')
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    return []

# Função para escrever dados em JSON
def write_data(data):
    data_file = os.path.join(app.config['DATA_FOLDER'], 'files.json')
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_file', methods=['POST'])
def add_file():
    tenant_id = request.form['tenant_id']
    username = request.form['username']
    email = request.form['email']
    
    # Processar o upload de arquivo
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    
    if file:
        # Criar um diretório por tenant se não existir
        tenant_folder = os.path.join(app.config['UPLOAD_FOLDER'], tenant_id)
        if not os.path.exists(tenant_folder):
            os.makedirs(tenant_folder)
        
        # Salvar o arquivo no diretório do tenant
        filename = file.filename
        file_path = os.path.join(tenant_folder, filename)
        file.save(file_path)
        
        # URL do arquivo no sistema local
        file_url = url_for('uploaded_file', tenant_id=tenant_id, filename=filename)
        
        # Inserir dados no arquivo JSON
        data = read_data()
        data.append({
            'tenant_id': tenant_id,
            'username': username,
            'email': email,
            'file_name': filename,
            'file_url': file_url
        })
        write_data(data)
        
        return redirect(url_for('user_files', tenant_id=tenant_id))

# Rota para listar os arquivos do usuário
@app.route('/files/<tenant_id>')
def user_files(tenant_id):
    data = read_data()
    user_files = [file for file in data if file['tenant_id'] == tenant_id]
    return render_template('user_files.html', files=user_files, tenant_id=tenant_id)

# Rota para servir os arquivos
@app.route('/uploads/<tenant_id>/<filename>')
def uploaded_file(tenant_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], tenant_id), filename)

if __name__ == '__main__':
    app.run(debug=True)
