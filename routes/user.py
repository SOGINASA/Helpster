from flask import redirect, render_template, request, session, url_for, Blueprint
from flask_login import login_required, login_user, logout_user
from db_models import Admin, db, User

user_bp = Blueprint('user', __name__, template_folder='templates')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('main.html')


@user_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@user_bp.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@user_bp.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')


# если нужно, добавьте редирект с корня на дашборд
@user_bp.route('/')
def index():
    return redirect(url_for('user.dashboard'))
