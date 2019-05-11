from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'difhishfuserladjaklds'
db = SQLAlchemy(app)




class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    body = db.Column(db.String(1000))



    def __init__(self, title, body ):
        self.title = title
        self.body = body



    def is_valid(self):

        if self.title and self.body:
            return True
        else:
            return False



@app.route("/")
def index():

    return redirect("/blog")


@app.route("/blog")
def display_blog_posts():

    entry_id = request.args.get('id')
    if (entry_id):
        entry = Entry.query.get(entry_id)
        return render_template('single_entry.html', title="Blog Entry", entry=entry)



    all_entries = Entry.query.all()   
    return render_template('all_entries.html', title="All Entries", all_entries=all_entries)



@app.route('/new_post', methods=['GET', 'POST'])
def new_post():

    if request.method == 'POST':
        new_post_title = request.form['title']
        new_post_body = request.form['body']
        new_post = Entry(new_post_title, new_post_body)


        if new_post.is_valid():
            db.session.add(new_post)
            db.session.commit()


            url = "/blog?id=" + str(new_post.id)
            return redirect(url)
        elif len(new_post_title) == 0 and len(new_post_body) == 0:
            flash("You must add a title and body to your entry.")
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_post_title=new_post_title,
                new_post_body=new_post_body)
        elif len(new_post_title) == 0:
            flash("You must add a title to your entry.")
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_post_title=new_post_title,
                new_post_body=new_post_body)
        elif len(new_post_body) == 0:  
            flash("You must add a body message to your entry.")  
            return render_template('new_entry_form.html',
                title="Create new blog entry",
                new_post_title=new_post_title,
                new_post_body=new_post_body)



    else:
        return render_template('new_entry_form.html', title="Create new blog entry")


@app.route('/delete-post', methods=['POST'])
def entry():

    entry_id = int(request.form['entry-id'])
    entry = Entry.query.get(entry_id)
    db.session.delete(entry)
    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run()