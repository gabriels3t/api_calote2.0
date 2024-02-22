# app.py

from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, MAIL_SETTINGS
from flask_mail import Mail, Message
from model.models import bcrypt,db


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.secret_key = SECRET_KEY
app.config.update(MAIL_SETTINGS)
db.init_app(app)
bcrypt.init_app(app)
mail = Mail(app)
    

from controllers.usuario import blueprint_user
app.register_blueprint(blueprint_user, url_prefix="/api/user/")
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(debug=True)
