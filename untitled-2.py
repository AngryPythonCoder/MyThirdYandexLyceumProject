from flask import request, Flask, render_template, redirect, session
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
 
 
class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    
    
class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
    

class AddTopicForm(FlaskForm):
    title = StringField('Название темы', validators=[DataRequired()])
    content = TextAreaField('Описание темы', validators=[DataRequired()])
    submit = SubmitField('Добавить')
    
    
class AddMessageForm(FlaskForm):
    text = TextAreaField('Текст', validators=[DataRequired()])
    submit = SubmitField('Добавить')

 
app = Flask(__name__)  
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '<User {} {} {}>'.format(self.id, self.username, self.password)
    
    
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(2000), unique=False, nullable=False)
    author = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return '<Topic {} {} {}>'.format(self.id, self.name, self.description)    
    
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(2000), unique=False, nullable=False)
    
    def __repr__(self):
        return '<Message {} {} {} {}>'.format(self.id, self.author, self.topic, self.text)   


db.create_all()

@app.route('/add_topic', methods=['GET', 'POST'])
def add_topic():
    if 'username' not in session:
        return redirect('/login')
    form = AddTopicForm()
    if form.validate_on_submit():
        name = form.title.data
        description = form.content.data
        author = session['user_id']
        topic = Topic(name=name, description=description, author=author)
        db.session.add(topic)
        db.session.commit()
        print(Topic.query.all())
        return redirect('/index')
    return render_template('add_topic.html', title='Добавление новости', 
                           username=session['username'], form=form)

@app.route('/delete_topic/<int:topic_id>', methods=['GET'])
def delete_topic(topic_id):
    if 'username' not in session:
        return redirect('/login')
    for message in Message.query.filter_by(topic=topic_id).all():
        db.session.delete(message)
    db.session.delete(Topic.query.get(topic_id))
    db.session.commit()
    return redirect('/index')

@app.route('/topic/<int:topic_id>', methods=['GET', 'POST'])
def topic(topic_id):
    form = AddMessageForm()
    if 'username' not in session:
        return redirect('/login')
    if form.validate_on_submit():
        text = form.text.data
        message = Message(author=session['user_id'], topic=topic_id, text=text)
        db.session.add(message)
        db.session.commit()
        redirect('/index')
    topic = Topic.query.filter_by(id=topic_id).first()
    messages = [[i.id, i.author, i.topic, i.text] 
                for i in Message.query.filter_by(topic=topic_id).all()]
    return render_template('topic.html', 
                           topic=[topic.id, topic.name, topic.description, topic.author],
                           messages=messages, form=form)

@app.route('/delete_message/<int:topic_id>/<int:message_id>', methods=['GET'])
def message_topic(topic_id, message_id):
    if 'username' not in session:
        return redirect('/login')
    db.session.delete(Message.query.get(message_id))
    db.session.commit()
    return redirect('/topic/' + str(topic_id))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
        if user:
            session['username'] = form.username.data
            session['user_id'] = user.id
            return redirect('/index')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.username.data
        pas = form.password.data
        email = form.email.data
        user = User(username=name, password=pas, email=email)
        db.session.add(user)
        db.session.commit()
        session['username'] = form.username.data
        session['user_id'] = user.id        
        return redirect('/index')
    return render_template('register.html', title='Register', form=form)

@app.route('/index')
def index():
    if 'username' in session:
        user = session['username']
    else:
        return redirect('/login')
    topic=[[i.id, i.name, i.description, i.author] for i in Topic.query.all()]
    return render_template('index.html', title='Домашняя страница',
                           username=user, topics=topic)

@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')