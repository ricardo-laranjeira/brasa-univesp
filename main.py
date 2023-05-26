from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5433/brasa'
app.secret_key = 'my-secret-key'

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__: str = 'user'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.fullname


class Enterprise(db.Model):
    __tablename__: str = 'enterprise'
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Enterprise %r>' % self.name


def insert_user(fullname, email, password):
    user = User(fullname=fullname, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    if user.id:
        return True
    else:
        return False


def insert_enterprise(cnpj, name, address, email, password):
    enterprise = Enterprise(cnpj=cnpj, name=name, address=address, email=email, password=password)
    db.session.add(enterprise)
    db.session.commit()
    if enterprise.id:
        return True
    else:
        return False


# delete records from a table
# db.session.delete(user)
# db.session.commit()

# retrieves all records (corresponding to SELECT queries) from the table.
# model.query.all ()


def valid_login(email, password):
    ret = 0
    result = db.session.query(User).filter(User.email.like(email), User.password.like(password))
    for row in result:
        ret = 1
    if ret == 0:
        result = db.session.query(Enterprise).filter(Enterprise.email.like(email), Enterprise.password.like(password))
        for row in result:
            ret = 2
    return ret


@app.route('/add_user', methods=['POST'])
def add_user():
    if insert_user(request.form['user-fullname'],
                   request.form['user-email'],
                   request.form['user-password']):
        return render_template('success.html', send='User', result='add with success')
    else:
        render_template('success.html', send='User', result='not add.')


@app.route('/add_enterprise', methods=['POST'])
def add_enterprise():
    if insert_enterprise(request.form['enterprise-cnpj'],
                         request.form['enterprise-name'],
                         request.form['enterprise-address'],
                         request.form['enterprise-email'],
                         request.form['enterprise-password']):
        return render_template('success.html', send='Enterprise', result='add with success')
    else:
        render_template('success.html', send='Enterprise', result='not add.')


@app.route('/login')
@app.route('/login', methods=['POST'])
def login():
    error = None
    if request.method == 'POST':
        valid = valid_login(request.form['email'],
                            request.form['password'])
        if valid == 1:
            user = db.session.query(User).filter(User.email.like(request.form['email']),
                                                 User.password.like(request.form['password'])).first()
            return redirect(url_for('home_user', id=user.id))
        elif valid == 2:
            enterprise = db.session.query(Enterprise).filter(Enterprise.email.like(request.form['email']),
                                                             Enterprise.password.like(request.form['password'])).first()
            return redirect(url_for('home_enterprise', id=enterprise.id))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)


@app.route('/home/user/list_enterprises/<id>')
def list_enterprises(id=None):
    enterprises = db.session.query(Enterprise)
    return render_template('list_enterprises.html', enterprises=enterprises, id=id)


@app.route('/home/enterprise/list_users/<id>')
def list_users(id=None):
    users = db.session.query(User)
    return render_template('list_users.html', users=users, id=id)


@app.route('/home/user/<id>')
def home_user(id=None):
    user = User.query.get(id)
    return render_template('home-user.html', user=user)


@app.route('/home/enterprise/<id>')
def home_enterprise(id= None):
    enterprise = Enterprise.query.get(id)
    return render_template('home-enterprise.html', enterprise=enterprise)


@app.route('/')
def index():
    return render_template('home.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
