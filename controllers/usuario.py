from flask import jsonify, request, session, Blueprint
from model.models import Usuario
from lib import hash_email


blueprint_user =Blueprint("usuario",__name__)


@blueprint_user.route("/")
def get_usuario():
    if 'email_usuario' in session:
        email = session["email_usuario"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            return jsonify({
                "email": usuario.email,
                "nome": usuario.nome,
                "amigos": [amigo.nome for amigo in usuario.amigos]
            }), 200
        else:
            return jsonify({"message": "Usuário não encontrado"}), 404
    else:
        return jsonify({"message": "Sessão não encontrada"}), 401

@blueprint_user.route("/login", methods=["POST"])
def login():
    data = {
        'email': request.args.get('email'),
        'senha': request.args.get('senha')

    }
    if not data or 'email' not in data or 'senha' not in data:
        return jsonify({"message": "Dados de login incompletos"}), 400

    #email = hash_email(data['email'])
    senha = data['senha']
    email =data['email']
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.check_senha(data['senha']):
        session['email_usuario'] = email
        return jsonify({'message': 'Login bem-sucedido', 'usuario': usuario.serialize()}), 200
    else:
        return jsonify({"message": "Nome de usuário ou senha incorretos"}), 401



@blueprint_user.route("/add", methods=["POST"])
def add_usuario():
    data = {
        'email': request.args.get('email'),
        'userName': request.args.get('userName'),
        'senha': request.args.get('senha')

    }
    if not data or 'email' not in data or 'senha' not in data or 'userName' not in data:
        return jsonify({"message": "Dados de usuário incompletos"}), 400

    email = data['email']
    nome = data['userName']
    senha = data['senha']

    try:
        usuario = Usuario.cadastrar(email, nome, senha)
        return jsonify({"message": "Usuário adicionado com sucesso", "usuario_id": usuario.email}), 201
    except Exception as e:
        return jsonify({"message": "Erro ao adicionar usuário", "error": str(e)}), 500