from flask import redirect, render_template, request, session, url_for, Blueprint
from flask_login import login_required, login_user, logout_user
from db_models import Admin, db, User

user_bp = Blueprint('user', __name__)


def dashboard():
    return render_template('main.html')


user_bp.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])