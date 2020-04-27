from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_restful import Api
from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired

from api_item import ItemListResource, ItemResource
from data import db_session, items, users, basket

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
count_items = 0
category = 'phones&laptop'


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
    display = TextAreaField('Экран')
    processor = TextAreaField('Процессор')
    videoadapter = TextAreaField('Видеокарта')
    ram = TextAreaField('ОЗУ')
    battery = TextAreaField('Батарея и автономность')
    category = SelectField('Категория', validators=[DataRequired()], choices=[('1', 'laptop'),
                                                                              ('2', "phones")])
    count = IntegerField('Количество')
    submit = SubmitField('Применить')


class EditForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    price = StringField('Цена')
    count = IntegerField('Количество')
    submit = SubmitField('Применить')


class LengthError(Exception):
    error = 'Пароль должен состоять не менее чем из 8 символов!'


class SymbolError(Exception):
    error = 'В пароле должен быть хотя бы один символ!'


class LetterError(Exception):
    error = 'В пароле должна быть хотя бы одна большая и маленькая буква!'


class DigitError(Exception):
    error = 'В пароле должна быть хотя бы одна цифра!'


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/index')


def reformat(s):
    return '\n'.join([s[i].strip() + ': ' + s[i + 1].strip() for i in range(0, len(s) - 1, 2)])


@app.route('/items', methods=['GET', 'POST'])
@login_required
def add_items():
    global count_items
    form = ItemsForm()
    if form.validate_on_submit():
        sessions = db_session.create_session()
        item = items.Items()
        item.title = form.title.data
        item.content = form.content.data
        item.count = form.count.data
        item.display = reformat(form.display.data.split('\n'))
        item.processor = reformat(form.processor.data.split('\n'))
        item.ram = reformat(form.ram.data.split('\n'))
        item.videoadapter = reformat(form.videoadapter.data.split('\n'))
        item.battery = reformat(form.battery.data.split('\n'))
        item.main_characteristics = form.main_characteristics.data
        if form.category.data == '1':
            item.category = 'laptop'
        else:
            item.category = 'phones'
        item.price = form.price.data
        f = request.files['file']
        if f:
            f.save('static/images/image' + str(count_items) + '.png')
            item.photo = '/static/images/image' + str(count_items) + '.png'
        sessions.add(item)
        sessions.commit()
        count_items += 1
        return redirect('/index')
    return render_template('items.html', title='Добавление товара', form=form)


@app.route('/items_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def items_delete(id):
    global count_items
    sessions = db_session.create_session()
    item = sessions.query(items.Items).filter(items.Items.id == id).first()
    if item:
        count_items -= 1
        sessions.delete(item)
        sessions.commit()
    else:
        abort(404)
    return redirect('/index')


@app.route('/')
def categories():
    return render_template('categories.html', title='Категории')


@app.route('/buy/<int:id>')
def buy(id):
    sessions = db_session.create_session()
    item = sessions.query(items.Items).get(id)
    basket_item = sessions.query(basket.Basket).get(id)
    sessions.delete(basket_item)
    sessions.commit()
    return render_template('purchase_page.html', title='Покупка товара', item=item)


@app.route('/items/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_items(id):
    form = EditForm()
    if request.method == 'GET':
        sessions = db_session.create_session()
        item = sessions.query(items.Items).filter(items.Items.id == id).first()
        form.title.data = item.title
        form.price.data = item.price
        form.count.data = item.count
    if form.validate_on_submit():
        sessions = db_session.create_session()
        item = sessions.query(items.Items).filter(items.Items.id == id).first()
        item.title = form.title.data
        item.price = form.price.data
        item.count = form.count.data
        sessions.commit()
        return redirect('/index')
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
            return redirect('/index')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/index/<type_item>')
@app.route('/index')
def index(type_item=False):
    global category
    if type_item:
        category = type_item
    else:
        category = 'phones&laptop'
    sessions = db_session.create_session()
    item = sessions.query(items.Items)
    search = request.args.get('s', default="", type=str).lower()
    if search:
        return render_template("index.html", items=item, search=search, category=category)
    return render_template("index.html", items=item, search="", category=category)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        result = check_password(form.password.data)
        if result != 'OK':
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form, email_error="OK", again_password_error="OK",
                                   password_error=result)
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form, email_error="OK", password_error="OK",
                                   again_password_error="Пароли не совпадают")
        sessions = db_session.create_session()
        if sessions.query(users.User).filter(users.User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   password_error="OK", again_password_error="OK",
                                   email_error="Такой пользователь уже есть")
        user = users.User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        sessions.add(user)
        sessions.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, email_error="OK",
                           password_error="OK", again_password_error="OK")


def test_password(password):
    flagki = [0, 0, 0, 0]
    for element in password:
        if element.isdigit():
            flagki[0] = 1
        elif element.isalpha():
            if element.isupper():
                flagki[1] = 1
            else:
                flagki[2] = 1
        else:
            flagki[3] = 1
    if flagki[2] * flagki[1] == 0:
        raise LetterError
    if flagki[0] == 0:
        raise DigitError
    if flagki[3] == 0:
        raise SymbolError
    return 'ok'


def check_password(password):
    try:
        if len(password) < 8:
            raise LengthError
        test_password(password)
        return 'OK'
    except (LengthError, SymbolError, LetterError, DigitError) as ex:
        return ex.error


@app.route("/basket")
def add_basket():
    sessions = db_session.create_session()
    item = sessions.query(basket.Basket)
    return render_template("basket.html", basket=item)


@app.route("/basket/<int:id>/<int:flag>")
def edit_basket(id, flag):
    sessions = db_session.create_session()
    basket_item = True
    for item in sessions.query(basket.Basket):
        if id == item.item_id and current_user.id == item.user_id:
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
        return redirect('/index')
    return redirect('/about_item/' + str(id))


@app.route('/basket_delete/<int:id>', methods=['GET', 'POST'])
def basket_delete(id):
    sessions = db_session.create_session()
    item = sessions.query(basket.Basket).get(id)
    items_id = item.item_id
    item_basket = sessions.query(items.Items).get(items_id)
    if item:
        if item.count == 1:
            sessions.delete(item)
        else:
            item.count -= 1
        item_basket.count += 1
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
    api.add_resource(ItemListResource, '/api/v2/item')
    api.add_resource(ItemResource, '/api/v2/item/<int:item_id>')
    sessions.close()
    app.run()


if __name__ == '__main__':
    main()
