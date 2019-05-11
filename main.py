from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'difhishfuserladjaklds'
db = SQLAlchemy(app)



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(120))

    body = db.Column(db.Text)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))



    def __init__(self, title, body, owner):

        self.title = title

        self.body = body

        self.owner = owner




class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(120))

    blogs = db.relationship('Blog', backref='owner')



    def __init__(self, username, password):

        self.username = username

        self.password = password





@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', '/', 'signup', 'singleposts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)



@app.route('/login', methods=['POST','GET'])
def login():

    if request.method == 'GET':
        if 'username' not in session:
            return render_template("login.html", page_title='Login')
        else:
            return redirect('/new_post')

 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/new_post')

        if user and user.password != password:
            password_error = "Incorrect Password"
            return render_template('login.html', password_error=password_error)

        if not user:
            username_error = "Incorrect Username"
            return render_template('login.html', username_error=username_error)

    else:
        return render_template('login.html')



@app.route('/register', methods=['POST', 'GET'])

def signup():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        verify = request.form['verify']

        exist = User.query.filter_by(username=username).first()



        username_error = ""

        password_error = ""

        verify_error = ""



        if username == "":

            username_error = "Please enter a username."

        elif len(username) <= 3 or len(username) > 20:

            username_error = "Username must be between 3 and 20 characters long."

        elif " " in username:

            username_error = "Username cannot contain any spaces."

        if password == "":

            password_error = "Please enter a password."

        elif len(password) <= 3:

            password_error = "Password must be greater than 3 characters long."

        elif " " in password:

            password_error = "Password cannot contain any spaces."

        if password != verify or verify == "":

            verify_error = "Passwords do not match."

        if exist:

            username_error = "Username already taken."



        if len(username) > 3 and len(password) > 3 and password == verify and not exist:

            new_user = User(username, password)

            db.session.add(new_user)

            db.session.commit()

            session['username'] = username

            return redirect('/new_post')

        else:

            return render_template('signup.html',

            username=username,

            username_error=username_error,

            password_error=password_error,

            verify_error=verify_error

            )



    return render_template('signup.html')





@app.route('/blog', methods=['POST', 'GET'])
def blog():
    post_id = request.args.get('id')
    user_id = request.args.get('userid')
    blogs = Blog.query.all()

    if post_id:
        blog_posts = Blog.query.filter_by(id=post_id).first()
        return render_template('single_entry.html', blog_posts=blog_posts, username=blog_posts.owner.username)
    if user_id:
        entries = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('singleUser.html', entries=entries)
    return render_template('all_entries.html', blogs=blogs)







@app.route('/new_post')

def post():

    return render_template('new_entry_form.html', title="New Post")





@app.route('/new_post', methods=['POST', 'GET'])

def newpost():
    title = request.form['title']
    body = request.form["body"]
    owner = User.query.filter_by(username=session['username']).first()


    title_error = ""

    body_error = ""



    if title == "":
        title_error = "Title required."

    if body == "":
        body_error = "Content required."



    if not title_error and not body_error:

        owner = User.query.filter_by(username=session['username']).first()
        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()
        page_id = new_post.id
        return redirect("/blog?id={0}".format(page_id))

    else:

        return render_template("new_entry_form.html",
            title = title,
            body = body,
            title_error = title_error,
            body_error = body_error
        )



@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')



if __name__ == '__main__':
    app.run()