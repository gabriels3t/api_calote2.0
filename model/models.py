
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

from flask_bcrypt import Bcrypt
from lib import hash_email

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
    nome_devedor = db.Column(db.String(255), db.ForeignKey('usuario.email'),nullable=False)
    nome_receptor = db.Column(db.String(255), db.ForeignKey('usuario.email'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    descricao = db.Column(db.String(255))
    pago = db.Column(db.Boolean, nullable=False)
