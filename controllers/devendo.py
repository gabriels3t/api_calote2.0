from flask import jsonify, request, Blueprint
from model.models import Devendo, Usuario
from sqlalchemy import func

blueprint_owing = Blueprint("devendo",__name__)


@blueprint_owing.route("/add",methods=["POST"])
def add():    
    data = {
        'email_receptor': request.args.get('email_receptor'),
        'email_devedor': request.args.get('email_devedor'),
        'valor': request.args.get('valor'),
        'descricao': request.args.get('descricao')

    }
    if not data or 'email_receptor' not in data or 'email_devedor' not in data or 'valor' not in data or 'descricao' not in data:
        return jsonify({"message": "Dados de usuário incompletos"}), 400

    email_receptor = data['email_receptor']
    email_devedor = data['email_devedor']
    valor = data['valor']
    descricao = data['descricao']

    try:
        devedor = Devendo.cadastrar(email_devedor, email_receptor, valor, descricao)
        return jsonify({"message": "Divida cadastrada", "usuer_email": devedor.id}), 201

    except Exception as e:
        return jsonify({"message": "Erro ao cadastrada Divida", "error": str(e)}), 500


@blueprint_owing.route("/consult",methods=["POST"])
def consulta():
    data = {
        'email_receptor': request.args.get('email_receptor'),
        'email_devedor': request.args.get('email_devedor')
        }
    email_devedor = data['email_receptor']
    email_receptor = data['email_devedor']

    if not email_devedor or not email_receptor:
         return jsonify({'message': 'Um ou ambos os usuários não foram encontrados'}), 404
    # Retorna None para as variáveis que não puderam ser encontradas
    
    
    devendos_pendentes ,valor_a_pagar,usuario,amigo,total = Devendo.consultar_dividas(email_devedor,email_receptor)

    return jsonify({
        'nome_devedor': amigo.nome,
        'nome_receptor': usuario.nome,
        'Valor': [devendo.valor for devendo in devendos_pendentes],
        'Descricao': [devendo.descricao for devendo in devendos_pendentes],
        'total': total,
        'pagar': valor_a_pagar,
        'email_receptor': usuario.email,
        'email_amigo': amigo.email
    })


@blueprint_owing.route("/consultas", methods=["POST"])
def consultar():
    # Obtém os dados da solicitação
    data = {
        'email_receptor': request.args.get('email_receptor'),
        'email_devedor': request.args.get('email_devedor')
    }
    
    # Valida se os dados estão presentes e são válidos
    if not data or 'email_receptor' not in data or 'email_devedor' not in data:
        return jsonify({"message": "Dados de usuário incompletos"}), 400
    
    try:
        # Chama a função para consultar as dívidas
        devendos_pendentes = Devendo.query.all()
        
        # Retorna os resultados em formato JSON
        return jsonify({
            "devendos_pendentes": [devendo.pago for devendo in devendos_pendentes],
            
        })
    except Exception as e:
        return jsonify({"message": "Erro ao consultar as dívidas", "error": str(e)}), 500




