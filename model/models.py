
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from flask_bcrypt import Bcrypt
from lib import hash_email
from sqlalchemy.dialects.mysql import TINYINT
from flask import jsonify
db = SQLAlchemy()
bcrypt = Bcrypt()

class Amizade(db.Model):
    __tablename__ = 'amizade'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_email = db.Column(db.String(255), db.ForeignKey('usuario.email'), nullable=False)
    amigo_email = db.Column(db.String(255), db.ForeignKey('usuario.email'), nullable=False)

    def __init__(self,usuario_email,amigo_email):
        
        self.usuario_email = usuario_email
        self.amigo_email = amigo_email

    def cadastrar(usuario_email,amigo_email):
        amizade = Amizade(usuario_email=usuario_email,amigo_email=amigo_email)
        db.session.add(amizade)
        db.session.commit()
        return amizade

class Usuario(db.Model):
    __tablename__ = 'usuario'
    email = db.Column(db.String(255), primary_key=True)
    nome = db.Column(db.String(255))
    senha = db.Column(db.String(255))
    amigos = relationship("Usuario",
                          secondary="amizade",
                          primaryjoin=(email == Amizade.usuario_email),
                          secondaryjoin=(email == Amizade.amigo_email),
                          backref="amigos_devedores")
    
    def __init__(self, email, nome, senha):
        self.email = hash_email(email)
        self.nome = nome
        self.senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    def cadastrar(email, nome, senha):
        novo_usuario = Usuario(email=email, nome=nome, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        return novo_usuario
    
    def check_senha(self, senha):
        return bcrypt.check_password_hash(self.senha, senha)

    def serialize(self):
        return {
            'email': self.email,
            'nome': self.nome
        }
    def alterar_senha(self, nova_senha):
        
        self.senha = bcrypt.generate_password_hash(nova_senha).decode('utf-8')
        db.session.commit()
    
    def listar_amigos(self):
        return self.amigos

class Devendo(db.Model):
    __tablename__ = 'devendo'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email_devedor = db.Column(db.String(255), db.ForeignKey('usuario.email'),nullable=False)
    email_receptor = db.Column(db.String(255), db.ForeignKey('usuario.email'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    pago = db.Column(db.Boolean, nullable=False,default=False)

    def __init__(self,email_devedor,email_receptor,valor,descricao):
        self.email_devedor = email_devedor
        self.email_receptor= email_receptor
        self.valor = float(valor)
        self.descricao = descricao
        self.pago = False

    def cadastrar( email_devedor,email_receptor, valor, descricao):
        nova_divida = Devendo(email_devedor=email_devedor, email_receptor=email_receptor, valor=valor, descricao=descricao)
        db.session.add(nova_divida)
        db.session.commit()
        return nova_divida

 
    
    def consultar_dividas(email_devedor, email_receptor):
        
        usuario = Usuario.query.filter_by(email=email_receptor).first()
        amigo = Usuario.query.filter_by(email=email_devedor).first()
        if not usuario or not amigo:
            return jsonify({'message': 'usuario não encontrado'}), 404
             
        devendos_pendentes = Devendo.query.filter_by(
            email_devedor=email_devedor,
            email_receptor=email_receptor,
            pago=False
        ).all()

        valor_receptor = Devendo.query.filter_by(
            email_devedor=email_receptor,
            email_receptor=email_devedor,
            pago = False
        ).with_entities(func.sum(Devendo.valor)).scalar() or 0

        total = Devendo.query.filter_by(
            email_devedor=email_devedor,
            email_receptor=email_receptor,
            pago=False
        ).with_entities(func.sum(Devendo.valor)).scalar() or 0

        valor_a_pagar = valor_receptor - total  
        return devendos_pendentes,valor_a_pagar,usuario,amigo, total 

   
