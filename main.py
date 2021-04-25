import os
from flask import Flask, render_template, redirect, request
from data import db_session
from forms.user import LoginForm, RegisterForm, AddingForm, AccauntForm, RecipeForm
from data.users import User
from data.recipes import Recipe
from flask_login import LoginManager, login_user, login_required, logout_user
import flask_login


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    recipes = db_sess.query(Recipe).filter(Recipe.is_private == False)
    return render_template("index.html", recipes=recipes)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/')
@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    form = AddingForm()
    if form.validate_on_submit():
        user_id = flask_login.current_user.id
        recipe = Recipe(
            title=form.Title.data,
            ingridients=form.Ingridients.data,
            text=form.Text.data,
            is_private=form.is_private.data,
            user_id=user_id
            )
        db_sess = db_session.create_session()
        db_sess.add(recipe)
        db_sess.commit()
        return redirect('/')
    return render_template('adding.html', title='Регистрация', form=form)


@app.route('/')
@app.route('/accaunt')
def accaunt():
    form = LoginForm()
    db_sess = db_session.create_session()
    user_id = flask_login.current_user.id
    user = db_sess.query(User).filter(User.id == user_id).first()
    recipes = db_sess.query(Recipe).filter(Recipe.user_id == user_id)
    return render_template('my_accaunt.html', title='Регистрация', form=form, recipes=recipes, user=user)


@app.route('/')
@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
    form = RecipeForm()
    db_sess = db_session.create_session()
    recipe_id = int(recipe_id[1:-1])
    recipe = db_sess.query(Recipe).filter(Recipe.id == recipe_id).first()
    return render_template('recipe.html', title='Регистрация', form=form, recipe=recipe, other_accaunt=False)


@app.route('/')
@app.route('/other_accaunts/<user_id>')
def other_accaunts(user_id):
    form = AccauntForm()
    db_sess = db_session.create_session()
    user_id = int(user_id[1:-1])
    user = db_sess.query(User).filter(User.id == user_id).first()
    recipes = db_sess.query(Recipe).filter(Recipe.user_id == user_id and Recipe.is_private == False)
    return render_template('accaunt.html', title='Регистрация', form=form, recipes=recipes, user=user, other_accaunt=True)


if __name__ == '__main__':
    main()
