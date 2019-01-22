"""
	1. Caso quiser usar o mét app.run(), as variáveis de ambiente, como para debug, devem vir na assinatura:
	if __name__ == '__main__':
		app.run(debug=True)
	
	2. Caso contrário usa as var de ambiente na shell: 'export' para Linux e 'set' para Windows, e iniciada com 'flask run':
	set FLASK_APP=hello.py
	set FLASK_DEBUG=1
	flask run

"""
from flask import Flask, render_template, session, redirect, url_for, flash
from datetime import datetime
# os - Miscellaneous operating system interfaces
import os
from flask_sqlalchemy import SQLAlchemy
# Importando o Wrapper com o framework responsável pela migração dos Models
from flask_migrate import Migrate

from flask_bootstrap import Bootstrap
from flask_moment import Moment


# Database path config
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] =\
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Trabalhando com config de segurança do flask
app.config['SECRET_KEY'] = 'hard to guess string'

bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/', methods=['GET', 'POST'])
def hello():
	# instanciando a classe NameForm()
	form = NameForm()
	"""
	input_name = None
	form = NameForm()
	if form.validate_on_submit():
		input_name = form.name.data
		form.name.data = ''
	return render_template('index.html', current_time=datetime.utcnow(), form=form, name=input_name)
	"""
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.name.data).first()
		if user is None:
			user = User(username=form.name.data)
			db.session.add(user)
			db.session.commit()
			session['known'] = False
		else:
			session['known'] = True
		session['name'] = form.name.data
		form.name.data = ''
		return redirect(url_for('hello'))
	# 1o argumt é o nome do arq de template, e qq outros são pares de chave-valor
	return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'), known=session.get('known', False))

# Mét tradicional de roteamento
def index_alternativo():
	return '<h1>How are you doing, chap!</h1>'
app.add_url_rule('/outro-index', 'index', index_alternativo)

# Rota com componente dinâmico
@app.route('/user/<name>')
def user(name):
	if name == 'null':
		name = None
	# 1o argumt é o nome do arq de template, e qq outros são pares de chave-valor
	return render_template('user.html', name=name)
	
@app.route('/user/<int:id>')
def another_user(id):
	return '<h1>Hello associate number {}! Wellcome to our enterprise...</h1>'.format(id)

@app.errorhandler(404)
def page_not_found(e):
	# Atenção: não esquecer de passar o cód num do error como segundo args de retorno
	return render_template('404.html'), 404
	
@app.errorhandler(500)
def internal_server_error(e):
	# Atenção: não esquecer de passar o cód num do error como segundo args de retorno
	return render_template('500.html'), 500


"""
	Forms
"""		
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
	# Argumentos: placeholder e lista de requisitos de validação
	name = StringField('What is your name?', validators=[DataRequired()])
	submit = SubmitField('Submit')
	

"""
	Models
"""	
class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	
	# Definindo a relação one-to-many: uma função pode ser/pertencer a vários users
	# A classe User() está def por estringue porque está escrita só abaixo
	users = db.relationship('User', backref='role', lazy='dynamic')
	
	def __repr__(self):
		return '<Role %r>' % self.name
	
class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	
	# Definindo a relação one-to-many: um user pode ter uma função
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	
	def __repr__(self):
		return '<User %r>' % self.username


"""
	Fazendo a integração do app com o flask shell (ie ter um script com importações pré-definido)	
"""		
@app.shell_context_processor
def make_shell_context():
	return dict(db=db, User=User, Role=Role)



	
	
