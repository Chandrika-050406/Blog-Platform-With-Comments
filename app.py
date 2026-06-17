from flask import Flask, render_template, redirect, request, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# USER TABLE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# POST TABLE
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# COMMENT TABLE
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        user = User(
            username=request.form['username'],
            password=request.form['password']
        )

        db.session.add(user)
        db.session.commit()

        flash("Registered Successfully")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            login_user(user)
            return redirect('/')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():

    if request.method == 'POST':

        post = Post(
            title=request.form['title'],
            content=request.form['content'],
            user_id=current_user.id
        )

        db.session.add(post)
        db.session.commit()

        return redirect('/')

    return render_template('create_post.html')


@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):

    post = Post.query.get_or_404(id)

    comments = Comment.query.filter_by(post_id=id).all()

    if request.method == 'POST':

        comment = Comment(
            text=request.form['comment'],
            post_id=id,
            user_id=current_user.id
        )

        db.session.add(comment)
        db.session.commit()

        return redirect(url_for('post', id=id))

    return render_template(
        'post.html',
        post=post,
        comments=comments
    )


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):

    post = Post.query.get_or_404(id)

    if request.method == 'POST':

        post.title = request.form['title']
        post.content = request.form['content']

        db.session.commit()

        return redirect('/')

    return render_template('edit_post.html', post=post)


@app.route('/delete/<int:id>')
@login_required
def delete_post(id):

    post = Post.query.get_or_404(id)

    db.session.delete(post)
    db.session.commit()

    return redirect('/')


if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)