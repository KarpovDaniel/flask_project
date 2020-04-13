from flask import Flask, render_template, redirect, request, abort, session
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired

from data import db_session, items, users, basket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
count_items = 0


@login_manager.user_loader
def load_user(user_id):
    sessions = db_session.create_session()
    return sessions.query(users.User).get(user_id)


class RegisterForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField("Почта", validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ItemsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    main_characteristics = TextAreaField('Главные характеристики')
    content = TextAreaField('Описание товара')
    price = StringField('Цена')
    specifications = TextAreaField('Характеристики')
    count = IntegerField('Количество')
    submit = SubmitField('Применить')


class EditForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    price = StringField('Цена')
    count = IntegerField('Количество')
    submit = SubmitField('Применить')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/items', methods=['GET', 'POST'])
@login_required
def add_items():
    global count_items
    form = ItemsForm()
    if request.method == 'POST':
        f = request.files['file']
        item = items.Items()
        f.save('static/images/image' + str(count_items) + '.png')
        if form.validate_on_submit():
            sessions = db_session.create_session()
            item = items.Items()
            item.title = form.title.data
            item.content = form.content.data
            item.count = form.count.data
            item.specifications = form.specifications.data
            item.photo = '/static/images/image' + str(count_items) + '.png'
            current_user.items.append(item)
            sessions.merge(current_user)
            sessions.commit()
            count_items += 1
            return redirect('/')
    return render_template('items.html', title='Добавление товара', form=form)


@app.route('/items_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def items_delete(id):
    global count_items
    sessions = db_session.create_session()
    item = sessions.query(items.Items).filter(items.Items.id == id,
                                              items.Items.user == current_user).first()
    if item:
        count_items -= 1
        sessions.delete(item)
        sessions.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/items/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_items(id):
    form = EditForm()
    if request.method == 'GET':
        sessions = db_session.create_session()
        item = sessions.query(items.Items).filter(items.Items.id == id,
                                                  items.Items.user == current_user).first()
        if item:
            form.title.data = item.title
        else:
            abort(404)
    if form.validate_on_submit():
        sessions = db_session.create_session()
        item = sessions.query(items.Items).filter(items.Items.id == id,
                                                  items.Items.user == current_user).first()
        if item:
            item.title = form.title.data
            item.price = form.price.data
            item.count = form.count.data
            sessions.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('editor.html', title='Редактирование товара', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        user = sessions.query(users.User).filter(users.User.email ==
                                                 form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/")
def index():
    sessions = db_session.create_session()
    item = sessions.query(items.Items)
    if request.method == 'POST':
        session['tag'] = request.form['search']
        return redirect('/')
    return render_template("index.html", items=item)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        sessions = db_session.create_session()
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = users.User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route("/basket")
def add_basket():
    sessions = db_session.create_session()
    item = sessions.query(basket.Basket)
    return render_template("basket.html", basket=item)



@app.route("/basket/<int:id>/<int:flag>")
def edit_basket(id, flag):
    sessions = db_session.create_session()
    basket_item = True
    basket_id = basket.Basket()
    for item in sessions.query(basket.Basket):
        if id == item.item_id and current_user.id == basket_id.user_id:
            item.count += 1
            basket_item = False
    item = sessions.query(items.Items).get(id)
    if basket_item:
        basket_item = basket.Basket()
        basket_item.item_id = id
        basket_item.user_id = current_user.id
        basket_item.photo = item.photo
        basket_item.title = item.title
        sessions.add(basket_item)
    item.count -= 1
    sessions.commit()
    if not flag:
        return redirect('/')
    return redirect('/about_item/' + str(id))


@app.route('/basket_delete/<int:id>', methods=['GET', 'POST'])
def basket_delete(id):
    sessions = db_session.create_session()
    item = sessions.query(basket.Basket).get(id)
    items_id = item.item_id
    item_basket = sessions.query(items.Items).get(items_id)
    if item:
        item_basket.count += item.count
        sessions.delete(item)
        sessions.commit()
    else:
        abort(404)
    return redirect('/basket')


@app.route('/about_item/<int:id>', methods=['GET', 'POST'])
def about_item(id):
    sessions = db_session.create_session()
    item = sessions.query(items.Items).get(id)
    return render_template("single_item.html", item=item)


def main():
    global count_items
    db_session.global_init("db/blogs.sqlite")
    sessions = db_session.create_session()
    count_items += len(list(sessions.query(items.Items)))
    sessions.close()
    app.run()


if __name__ == '__main__':
    main()
