from flask import redirect, render_template, request, session, url_for, Blueprint
from flask_login import current_user, login_required, login_user, logout_user
from db_models import Admin, db, User
import os
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

AVATAR_FOLDER = '/home/ivanchik322/Helpster/view/static/uploads/avatars'


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



def login():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        user = User.query.filter_by(login=login).first()

        admin = Admin.query.filter_by(login=login).first()

        if admin and admin.check_password(password):
            login_user(admin)
            session['login'] = login
            session['is_admin'] = True
            return redirect('/')

        if user and user.check_password(password):
            login_user(user)
            session['login'] = login
            session['is_admin'] = False
            return redirect('/')
        else:
            return render_template('login.html', error="Неверное имя пользователя или пароль")

    return render_template('login.html')

# Страница регистрации
def register():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        city = request.form.get('city')
        phone = request.form.get('phone')
        iin = request.form.get('iin')
        avatar = request.files.get('avatar')

        existing_user = User.query.filter_by(login=login).first()
        existing_admin = Admin.query.filter_by(login=login).first()
        if existing_user or existing_admin:
            return render_template('register.html', error="Пользователь уже существует")
        existing_user = User.query.filter_by(iin=iin).first()
        if existing_user:
            return render_template('register.html', error="Пользователь с таким ИИН уже существует.")


        os.makedirs(AVATAR_FOLDER, exist_ok=True)
        avatar_path = 'uploads/avatars/default.jpg'
        if avatar and allowed_file(avatar.filename):
            os.makedirs(AVATAR_FOLDER, exist_ok=True)

            ext = avatar.filename.rsplit('.', 1)[-1].lower()  # получаем расширение
            filename = secure_filename(f"{login}.{ext}")
            path = os.path.join(AVATAR_FOLDER, filename)
            avatar.save(path)



        new_user = User(
            login=login,
            email=email,
            full_name=full_name,
            city=city,
            phone=phone,
            iin=iin,
            avatar_path=avatar_path
        )
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при регистрации: {str(e)}", 500

        login_user(new_user)
        session['login'] = login
        session['is_admin'] = False
        return redirect('/')

    return render_template('register.html')


def register_admin():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        city = request.form.get('city')
        phone = request.form.get('phone')
        avatar = request.files.get('avatar')

        existing_user = User.query.filter_by(login=login).first()
        existing_admin = Admin.query.filter_by(login=login).first()
        if existing_user or existing_admin:
            return render_template('register.html', error="Пользователь уже существует")

        avatar_path = 'uploads/avatars/default.jpg'
        if avatar and allowed_file(avatar.filename):
            os.makedirs(AVATAR_FOLDER, exist_ok=True)

            ext = avatar.filename.rsplit('.', 1)[-1].lower()  # получаем расширение
            filename = secure_filename(f"{login}.{ext}")      # создаём безопасное имя

            path = os.path.join(AVATAR_FOLDER, filename)
            avatar.save(path)

            avatar_path = f"uploads/avatars/{filename}"


        new_admin = Admin(
            login=login,
            email=email,
            full_name=full_name,
            city=city,
            phone=phone,
            avatar_path=avatar_path
        )
        new_admin.set_password(password)

        try:
            db.session.add(new_admin)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Ошибка при регистрации: {str(e)}", 500

        login_user(new_admin)
        session['login'] = login
        session['is_admin'] = True
        return redirect('/')

    return render_template('register_admin.html')



# Выход

@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))


auth_bp.add_url_rule('/register', view_func=register, methods=['GET', 'POST'])
auth_bp.add_url_rule('/register_admin', view_func=register_admin, methods=['GET', 'POST'])
auth_bp.add_url_rule('/login', view_func=login, methods=['GET','POST'])
auth_bp.add_url_rule('/logout', view_func=logout, methods=['GET'])

if __name__ == '__main__':
    print('wrong file')