"""
This file declares URLs that are intended to be accessed by regular browser navigation.
It handles login, logout, signup and various pages of the site via templates.
"""

from flask import request, redirect, url_for, render_template
from flask.ext.login import login_user, logout_user, login_required, current_user
from . import app, login_manager, models, forms, db

# Required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return models.User.query.filter_by(id=user_id).first()

@app.route('/')
def index():
    photos = models.Photo.query.all()
    return render_template('index.html', photos=photos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = forms.LoginForm()

    if form.validate_on_submit():
        login_user(form.user)

        next_page = request.args.get('next')

        return redirect(next_page or url_for('index'))

    return render_template('login.html', form=form, signup=False)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = forms.SignupForm()

    if form.validate_on_submit():
        user = models.User(username=form.username.data)
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        return redirect(url_for('index'))

    return render_template('login.html', form=form, signup=True)

@app.route('/users')
def users():
    users = models.User.query.all()

    return render_template('users.html', users=users)

@app.route('/photo/<int:id>')
def photo(id):
    photo = models.Photo.query.get_or_404(id)

    return render_template('photo.html', photo=photo)

@app.route('/user/<int:id>')
def user(id):
    user = models.User.query.get_or_404(id)

    return render_template('user.html', user=user)

@app.route('/myfeed')
@login_required
def myfeed():
    return render_template('myfeed.html')

@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html')
