from flask import jsonify, request, session, Blueprint,url_for , current_app
from model.models import Usuario
from lib import hash_email
from itsdangerous import BadSignature, URLSafeTimedSerializer 
from flask_mail import Mail, Message

blueprint_user = Blueprint("usuario",__name__)


#serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
mail =  Mail()

@blueprint_user.route("/")
def get_usuario():
    if 'email_usuario' in session:
        email = session["email_usuario"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            return jsonify({
                "email": usuario.email,
                "nome": usuario.nome,
                "amigos": [amigo.nome for amigo in usuario.listar_amigos()]
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

    email = hash_email(data['email'])
    senha = data['senha']
    usuario = Usuario.query.filter_by(email=email).first()
    if usuario and usuario.check_senha(senha):
        session['email_usuario'] = email
        return jsonify({'message': 'Login bem-sucedido', 'usuario': usuario.serialize()}), 200
    else:
        return jsonify({"message": "Nome de usuário ou senha incorretos"}), 401

@blueprint_user.route("/logout",methods=["POST","GET"])
def logout():
    session.pop('email_usuario', None)
    return jsonify({"message": "Logout bem-sucedido"}), 200


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
        return jsonify({"message": "Usuário adicionado com sucesso", "usuer_email": usuario.email}), 201
    except Exception as e:
        return jsonify({"message": "Erro ao adicionar usuário", "error": str(e)}), 500


serializer = None

@blueprint_user.record_once
def on_load(state):
    global serializer
    app = state.app
    with app.app_context():
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

@blueprint_user.route("/forgot_password", methods=["POST"])
def forgot_password():
    
   with current_app.app_context():
        if request.method == "POST":
            para_enviar = request.args.get('email')
            if not para_enviar:
                return jsonify({"error": "O campo de e-mail é obrigatório"}), 400
            
            #email = hash_email(para_enviar)
            email = para_enviar
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                token = serializer.dumps(email)
                reset_url = url_for('usuario.reset_password', token=token, _external=True)
                message = Message('Password Reset Request', 
                                   sender=current_app.config.get("MAIL_USERNAME"), 
                                   recipients=[para_enviar],
                                   body=f'Para redefinir sua senha, clique no link a seguir: {reset_url}')
              
                mail.send(message)
                return jsonify({"message": 'Um e-mail com as instruções para redefinir a senha foi enviado para o seu endereço de e-mail.'}), 200
            return jsonify({"error": "E-mail não encontrado na base de dados."}), 404

@blueprint_user.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    with current_app.app_context():
        try:
            email = serializer.loads(token, max_age=900)  # Expira em 15 minutos 
            usuario = Usuario.query.filter_by(email=email).first()
            if usuario:
                senha = request.args.get('senha')
                if senha:
                    usuario.alterar_senha(senha)
                    return jsonify({"message": "Senha alterada com sucesso."}), 200
                else:
                    return jsonify({"error": "Senha não fornecida."}), 400
            else:
                return jsonify({"error": "Usuário não encontrado."}), 404
        except BadSignature:
            return jsonify({"error": "O link de redefinição de senha é inválido ou expirou."}), 400
