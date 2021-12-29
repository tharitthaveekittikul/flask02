from datetime import timedelta
from flask import Flask,render_template,request,session,g
from flask.helpers import url_for
from flask_mysqldb import MySQL
from werkzeug.utils import redirect
from loginform import LoginForm
# from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'

# Bootstrap(app)
mysql = MySQL(app)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(seconds=60)
    g.user = None
    g.role = None

    if 'username' in session:
        g.user = session['username']

    if 'role' in session:
        g.role = session['role']

@app.route('/')
def index():
    return render_template('index.html',user = g.user, role = g.role)


@app.route('/login', methods = ["GET","POST"])
def login():
    form = LoginForm()
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = form.username.data
        password = form.password.data

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM adminuser WHERE username = %s AND password = %s', (username,password))
        
        account = cursor.fetchone()
        # print(account)
        mysql.connect.commit()
        cursor.close()
        if account:
            session['loggedin'] = True
            session['username'] = account[1]
            session['role'] = account[5]
            # msg = 'Correct'
            if account[5] == 'admin':
                return redirect(url_for('dashboard'))
            elif account[5] == 'employee':
                return redirect(url_for('index'))

        else:
            msg = 'Incorrect'
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('login.html', form = form , msg = msg)


@app.route('/logout')
def logout():
    session.pop('username',None)
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('dashboard.html',user = g.user, role = g.role)

@app.route('/profile')
def profile():
    return render_template('profile.html',user = g.user, role = g.role)

@app.route('/about')
def about():
    return render_template('about.html',user = g.user, role = g.role)
    
@app.route('/contactprofile')
def contactprofile():
    return render_template('contactprofile.html',user = g.user, role = g.role)
if __name__ == "__main__":
    app.run(debug=True)