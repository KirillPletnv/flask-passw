from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
import sqlalchemy as sa
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from prometheus_flask_exporter import PrometheusMetrics



app = Flask(__name__)
metrics = PrometheusMetrics(app)
db = SQLAlchemy(app)
app.secret_key = "super secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///finals.db'


bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(0)
    if form.validate_on_submit():
        print(1)
        user = User.query.filter_by(username=form.username.data).first()
        print(user)
        if user:
            session['us'] = user.username
            print(2)
            if user:
                print(3)
                if bcrypt.check_password_hash(user.password, form.password.data):
                    print(4)
                    login_user(user)
                    print(5)
                    return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def form_registration():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        print(hashed_password)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('registration.html', form=form)

@app.route("/", methods=['GET', 'POST'])
@login_required
def retr():
    return redirect(url_for('/index'))


@app.route("/index", methods=['GET', 'POST'])
@login_required
def index():
    create = False
    inserts = False
    if request.method == 'GET':
        # if not name:
        #    return render_template('auth_bad.html')
        return render_template("home.html")
    if request.method == 'POST':
        site = request.form.get('site')
        login = request.form.get('login')
        passw = request.form.get('password')
        us = session['us']
        site_f, login_f, passw_f, inserts, create = workeds(us, site, login, passw, inserts)
        print(site_f)
        print(login_f)
        print(passw_f)
        return render_template("home.html", inserts=inserts, create=create, site=site_f, us=us, login=login_f, passw=passw_f)


def workeds(us, one, two, three, inserts):

    create = inserts
    s1, s2, s3 = 'сохранено', 'сохранено', 'сохранено'
    worked = True
    while worked:
        conn = sa.create_engine('sqlite:///finals.db')
        conn.execute(''' CREATE TABLE IF NOT EXISTS SITE_FINAL(us VARCHAR(30), sites VARCHAR(30), login VARCHAR(30), pssw VARCHAR(30))  ''')
        sites = one
        if sites != 'exits':
            sql_answs = f'SELECT * from site_final where sites = "{sites}" and us = "{us}"'
            prov = conn.execute(sql_answs)
            f = False
            for row in prov:
                if row:
                    f = True
                    s0 = row[0]
                    s1 = row[1]
                    s2 = row[2]
                    s3 = row[3]

                    print('Уже есть аккаунт на ' + str(row[1]))
                    print('login: ' + str(row[2]))
                    print('password: ' + str(row[3]))
                    inserts = True
                    worked = False
            if not f:
                create = True
                s1 = one
                s2 = two
                s3 = three
                ins = 'INSERT INTO site_final (us, sites, login, pssw) VALUES (?, ?, ?, ?)'
                conn.execute(ins, us, s1, s2, s3)
                worked = False

        else:
            worked = False
    return str(s1), str(s2), str(s3), inserts, create



@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    db.create_all()
    app.run(port=5000, host='0.0.0.0', debug=False)
