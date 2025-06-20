from flask import redirect, render_template, request, session, url_for, Blueprint
from flask_login import login_required, login_user, logout_user
from db_models import Admin, db, User



auth_bp = Blueprint('auth', __name__)


def login():
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


    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        city = request.form.get('city')
        phone = request.form.get('phone')
        iin = request.form.get('iin')

        existing_user = User.query.filter_by(login=login).first()
        existing_admin = Admin.query.filter_by(login=login).first()
        if existing_user or existing_admin:
            return render_template('register.html', error="Пользователь уже существует")

        # Получение координат города
        
        new_user = User(
            login=login,
            email=email,
            full_name=full_name,
            city=city,
            phone=phone,
            iin=iin
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
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        email = request.form.get('email')
        
        # Проверка, существует ли пользователь
        existing_user = User.query.filter_by(login=login).first()
        existing_admin = Admin.query.filter_by(login=login).first()
        if existing_user or existing_admin:
            return render_template('register_admin.html')
        
        # Создание нового пользователя
        new_admin = Admin(login=login, email=email)
        new_admin.set_password(password)
        
        db.session.add(new_admin)
        db.session.commit()

        
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