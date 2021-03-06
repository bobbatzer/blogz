from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://capstone-project:capstone-project@localhost:3306/capstone-project'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '95U60TmQqa3coPJC'

class Estimate(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    estimates = db.relationship('Estimate', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','index', 'estimate']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error = ""
        password_error = ""
        verify_error = ""

        if username == "" or " " in username:
            username_error = "Username Field must have characters"
            username = ""
        elif len(username) < 3:
            username_error = "Username must be at least 3 characters"
            username = ""

        if password == "" or " " in username:
            password_error = "Password Field must have characters"
            password = ""
        elif len(password) < 3:
            password_error = "Password must be at least 3 characters"
            password = ""
        elif password != verify:
                verify_error = "The Passwords do not match"

        if username_error or password_error or verify_error:
            return render_template('signup.html', username=username, username_error=username_error, 
                password_error=password_error, verify_error=verify_error)

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')   #redirect to the '/newpost' page with username being stored in a session
        else:
            username_error = "This username already exists"
            return render_template('signup.html', username=username, username_error=username_error)
    return render_template('signup.html')



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        elif not user:
            no_user_error = "That username does not exist"
            return render_template('login.html',username_error=no_user_error)
        elif user.password != password:
            verify = "That is not the correct password"
            return render_template('login.html',username=username, password_error=verify)

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')




@app.route('/estimate', methods=['POST', 'GET'])
def estimate():

    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_estimates = Estimate.query.filter_by(owner=user).all()
        return render_template("singleuser.html", page_title = user.username + "'s Posts!", 
                                                      user_estimates=user_estimates)
    
    single_post = request.args.get("id")
    if single_post:
        estimate = Estimate.query.get(single_post)
        return render_template("singleposting.html", estimate=estimate)

    else:
        estimates = Estimate.query.all()
        return render_template('estimate.html', estimates=estimates)


@app.route('/newpost', methods=['POST', 'GET'])
def add_post():

    if request.method == 'GET':
        return render_template('newposting.html')

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title and not body:
            return render_template('newposting.html', 
                                    title_error='Please enter a title', 
                                    body_error='Please enter your estimate')

        elif not title:
            return render_template('newposting.html', 
                                    title_error='Please enter a title', body=body)
        
        elif not body:
            return render_template('newposting.html', title=title, 
                                    body_error='Please enter your estimate')
            
        else:
            owner = User.query.filter_by(username=session['username']).first()
            new_post = Estimate(title, body, owner)
            db.session.add(new_post)
            db.session.commit()

            estimate = Estimate.query.get(new_post.id)
            return render_template('singleposting.html', estimate=estimate)
        users = User.query.all()
        return render_template('index.html', users=users)

@app.route('/',  methods=['POST', 'GET'])
def index():    
    users = User.query.all()
    return render_template('index.html', users=users)

    
if __name__ == '__main__':
    app.run() 