from flask import jsonify, request, Blueprint,url_for , current_app
from model.models import Amizade, Usuario
from lib import hash_email
from itsdangerous import BadSignature, URLSafeTimedSerializer 
from flask_mail import Mail, Message

blueprint_friend = Blueprint("amigos",__name__)

serializer = None
mail =  Mail()

@blueprint_friend.record_once
def on_load(state):
    global serializer
    app = state.app
    with app.app_context():
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])


@blueprint_friend.route("/enviar_convite", methods=["POST"])
def enviar_convite():
    with current_app.app_context():
        if request.method == "POST":
            email_user = request.args.get('email_user') 
            user_name = request.args.get('user_name')
            enviar_email = request.args.get('email_amigo')
            email_amigo = hash_email(enviar_email)

            amigo = Usuario.query.filter_by(email=email_amigo).with_entities(Usuario.email, Usuario.nome).all()
            if amigo:
                token = serializer.dumps({'email_user': email_user, 'email_amigo': email_amigo})
                invite_url = url_for('amigos.aceitar_convite', token=token, _external=True)
                message = Message(f'{user_name} esta te convidando para se tornar amigo', 
                                sender=current_app.config.get("MAIL_USERNAME"), 
                                recipients=[enviar_email],
                                body=f'Ola {amigo[0].nome} \n tudo bem ? \n Você recebeu um convite para se tornar amigo! de {user_name} Clique no link a seguir para aceitar: {invite_url} \n')
                mail.send(message)
                return  jsonify({"message": "Email enviado"}), 201 

            else:
                return jsonify({"message": "Amigo não cadastrado "}), 401 

@blueprint_friend.route("/aceitar_convite/<token>",methods=["POST","GET"])
def aceitar_convite(token):
    with current_app.app_context():

        try:
            data = serializer.loads(token,max_age=3600) # valido por 1 hora 
            data = {
            'email_user': request.args.get('email_user'),
            'email_amigo': request.args.get('email_amigo'),
            }
            email_user = data['email_user']
            email_amigo = data['email_amigo']
            data = serializer.loads(token,max_age=3600)
            email_user = data['email_user']
            email_amigo = data['email_amigo']
            _ = Amizade.cadastrar(email_user,email_amigo)
            _ = Amizade.cadastrar(email_amigo,email_user)
        
            return jsonify({"message": "Amizade Cadastrada"}), 201

        except BadSignature as e:
            return jsonify({"message": "O link de redefinição de senha é inválido ou expirou.", "error": str(e)}), 500
