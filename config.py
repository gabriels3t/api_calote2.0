# config.py
import chave
SQLALCHEMY_DATABASE_URI = "sqlite:///caloteiro.sqlite3"
SECRET_KEY = 'vm3NubT992grKgsqY35rf2nG'  # session 

MAIL_SETTINGS = {
    "MAIL_SERVER": "smtp-relay.brevo.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USE_SSL": False,
    "MAIL_USERNAME": chave.email,  # Certifique-se de substituir isso pelo seu próprio valor
    "MAIL_PASSWORD": chave.senha  # Certifique-se de substituir isso pelo seu próprio valor
}
