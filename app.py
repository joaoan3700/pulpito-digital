from flask import Flask, render_template, url_for, flash, redirect, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from config import Config
from models import db, User, Post, Slide
from forms import LoginForm, PostForm, SlideForm, UserForm
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

migrate = Migrate(app, db)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin():
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('03041826', method='pbkdf2:sha256')
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe.")

with app.app_context():
    db.create_all()
    create_admin()

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
    return render_template('login.html', form=form)

@app.route("/")
def index():
    posts = Post.query.all()
    for post in posts:
        post.image_url = url_for('static', filename='images/' + post.image_file)

    slides = Slide.query.order_by(Slide.date_posted.desc()).limit(10).all()
    for slide in slides:
        slide.image_url = url_for('static', filename='images/' + slide.image_file_desktop)

    return render_template('index.html', posts=posts, slides=slides)

@app.route("/posts")
@login_required
def posts():
    if current_user.username != 'admin':
        abort(403)
    posts = Post.query.all()
    return render_template('posts.html', posts=posts)

@app.route("/create_post", methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        picture_file = 'default.jpg'
        if form.picture.data:
            picture_file = secure_filename(form.picture.data.filename)
            form.picture.data.save(os.path.join('static/images', picture_file))
        post = Post(title=form.title.data, content=form.content.data, image_file=picture_file, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post criado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', form=form)

@app.route("/edit_post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('Você não tem autorização para editar este post.', 'danger')
        return redirect(url_for('index'))

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.picture.data:
            picture_file = secure_filename(form.picture.data.filename)
            form.picture.data.save(os.path.join('static/images', picture_file))
            post.image_file = picture_file
        db.session.commit()
        flash('Post atualizado com sucesso!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('edit_post.html', form=form, post=post)

@app.route("/delete_post/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        flash('Você não tem autorização para deletar este post.', 'danger')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deletado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'success')
    return redirect(url_for('login'))

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    post.image_url = url_for('static', filename='images/' + post.image_file)
    return render_template("post_detail.html", post=post)

# -------- Slides -----------

@app.route('/slides')
@login_required
def slides():
    if current_user.username != 'admin':
        abort(403)
    slides = Slide.query.order_by(Slide.date_posted.desc()).limit(10).all()
    return render_template('slides.html', slides=slides)

@app.route('/create_slide', methods=['GET', 'POST'])
@login_required
def create_slide():
    if current_user.username != 'admin':
        abort(403)
    form = SlideForm()
    if form.validate_on_submit():
        picture_file_desktop = 'default_slide_desktop.jpg'
        picture_file_mobile = 'default_slide_mobile.jpg'

        if form.picture_desktop.data:
            picture_file_desktop = secure_filename(form.picture_desktop.data.filename)
            form.picture_desktop.data.save(os.path.join('static/images', picture_file_desktop))

        if form.picture_mobile.data:
            picture_file_mobile = secure_filename(form.picture_mobile.data.filename)
            form.picture_mobile.data.save(os.path.join('static/images', picture_file_mobile))

        slide = Slide(
            title=form.title.data,
            description=form.description.data,
            image_file_desktop=picture_file_desktop,
            image_file_mobile=picture_file_mobile,
            author=current_user
        )
        db.session.add(slide)
        db.session.commit()
        flash('Slide criado com sucesso!', 'success')
        return redirect(url_for('slides'))
    return render_template('create_slide.html', form=form)

@app.route('/edit_slide/<int:slide_id>', methods=['GET', 'POST'])
@login_required
def edit_slide(slide_id):
    if current_user.username != 'admin':
        abort(403)
    slide = Slide.query.get_or_404(slide_id)
    form = SlideForm()
    if form.validate_on_submit():
        slide.title = form.title.data
        slide.description = form.description.data

        if form.picture_desktop.data:
            picture_file_desktop = secure_filename(form.picture_desktop.data.filename)
            form.picture_desktop.data.save(os.path.join('static/images', picture_file_desktop))
            slide.image_file_desktop = picture_file_desktop

        if form.picture_mobile.data:
            picture_file_mobile = secure_filename(form.picture_mobile.data.filename)
            form.picture_mobile.data.save(os.path.join('static/images', picture_file_mobile))
            slide.image_file_mobile = picture_file_mobile

        db.session.commit()
        flash('Slide atualizado com sucesso!', 'success')
        return redirect(url_for('slides'))
    elif request.method == 'GET':
        form.title.data = slide.title
        form.description.data = slide.description
    return render_template('edit_slide.html', form=form, slide=slide)

@app.route('/delete_slide/<int:slide_id>', methods=['POST'])
@login_required
def delete_slide(slide_id):
    if current_user.username != 'admin':
        abort(403)
    slide = Slide.query.get_or_404(slide_id)
    db.session.delete(slide)
    db.session.commit()
    flash('Slide deletado com sucesso!', 'success')
    return redirect(url_for('slides'))


# Lista todos os usuários (admin only)
@app.route('/users')
@login_required
def users():
    if current_user.username != 'admin':
        abort(403)
    users_list = User.query.all()
    return render_template('users.html', users=users_list)

# Criar usuário (admin only)
@app.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.username != 'admin':
        abort(403)
    form = UserForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Usuário criado com sucesso!', 'success')
        return redirect(url_for('users'))
    return render_template('create_user.html', form=form)

# Editar usuário (admin only)
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.username != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    form = UserForm()
    if form.validate_on_submit():
        user.username = form.username.data
        if form.password.data:
            user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        db.session.commit()
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('users'))
    elif request.method == 'GET':
        form.username.data = user.username
    return render_template('edit_user.html', form=form, user=user)

# Deletar usuário (admin only)
@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.username != 'admin':
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Não é permitido deletar o usuário admin.', 'danger')
        return redirect(url_for('users'))
    db.session.delete(user)
    db.session.commit()
    flash('Usuário deletado com sucesso!', 'success')
    return redirect(url_for('users'))

#Terços
@app.route('/tercos')
def tercos():
    return render_template('tercos.html')

@app.route('/tercos/terco_mariano')
def terco_mariano():
    return render_template('tercos/terco_mariano.html')

@app.route('/tercos/terco_misericordia')
def terco_misericordia():
    return render_template('tercos/terco_misericordia.html')

# Novenas
@app.route('/novenas')
def novenas():
    return render_template('novenas.html')

# Orações
@app.route('/oracoes')
def oracoes():
    return render_template('oracoes.html')

# Rosário
@app.route('/rosario')
def rosario():
    return render_template('rosario.html')

# Salmos
@app.route('/salmos')
def salmos():
    return render_template('salmos.html')


if __name__ == "__main__":
    app.run(debug=True)
