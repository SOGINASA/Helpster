import os
from flask import current_app, flash, redirect, render_template, request, session, url_for, Blueprint, jsonify
from flask_login import current_user, login_required, login_user, logout_user
from db_models import Admin, Complaint, Idea, db, User, Event, EventParticipant
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

AVATAR_FOLDER = '/home/ivanchik322/Helpster/view/static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
def dashboard():
    return render_template('main.html')


@login_required
def profile():
    user = current_user

    if request.method == 'POST':
        # print("📥 Обновление профиля")
        user.email = request.form.get('email')
        user.full_name = request.form.get('full_name')
        user.phone = request.form.get('phone')
        user.city = request.form.get('city')
        user.iin = request.form.get('iin')

        avatar = request.files.get('avatar')
        if avatar and allowed_file(avatar.filename):
            os.makedirs(AVATAR_FOLDER, exist_ok=True)

            ext = avatar.filename.rsplit('.', 1)[-1].lower()  # получаем расширение
            filename = secure_filename(f"{user.login}.{ext}")      # создаём безопасное имя

            path = os.path.join(AVATAR_FOLDER, filename)
            avatar.save(path)

            avatar_path = f"uploads/avatars/{filename}"
            user.avatar_path = avatar_path

        try:
            db.session.commit()
            # print("✅ Профиль успешно обновлен")
            flash('Профиль успешно обновлен', 'success')
        except Exception as e:
            print("❌ Ошибка при обновлении профиля:", e)
            db.session.rollback()
            flash('Ошибка сохранения: ' + str(e), 'danger')

        return redirect(url_for('user.profile'))

    lvl = user.points // 100
    points_left = user.points % 100

    top_users = User.query.order_by(User.points.desc()).limit(3).all()

    return render_template('profile.html', user=user, lvl=lvl, points_left=points_left, top_users=top_users)


@login_required
def chatbot():
    return render_template('chatbot.html')


@login_required
def calendar():
    return render_template('calendar.html')

@user_bp.route('/')
def index():
    return redirect(url_for('user.dashboard'))

@login_required
def education():
    return render_template('education.html')

@login_required
def ideas():
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']

        new_idea = Idea(
            title=title,
            message=message,
            user_id=current_user.id  # Привязываем идею к текущему пользователю
        )

        try:
            db.session.add(new_idea)
            db.session.commit()
            flash('Идея успешно отправлена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при отправке идеи: {str(e)}', 'danger')

        return redirect(url_for('user.ideas'))  # Перенаправляем обратно на страницу

    # Получаем все идеи из базы данных
    ideas = Idea.query.order_by(Idea.created_at.desc()).all()

    return render_template('ideas.html', ideas=ideas)

@login_required
def complaints():
    if request.method == 'POST':
        violation_type = request.form['violationType']
        organization = request.form['organization']
        description = request.form['description']
        evidence = request.form.get('evidence')  # Доказательства (необязательно)
        incident_date = request.form['incidentDate']
        location = request.form['location']

        # Валидация
        if not all([violation_type, organization, description, incident_date, location]):
            flash("Заполните все обязательные поля", "warning")
            return redirect(request.referrer)

        # Создание новой жалобы
        new_complaint = Complaint(
            violationType=violation_type,
            organization=organization,
            description=description,
            evidence=evidence,  # Доказательства (если есть)
            incidentDate=incident_date,
            location=location
        )

        try:
            db.session.add(new_complaint)
            db.session.commit()
            flash('Жалоба успешно отправлена!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при отправке жалобы: {str(e)}', 'danger')

        return redirect(url_for('user.complaints'))  # Перенаправляем обратно на страницу

    # Получаем все жалобы из базы данных
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    return render_template('complaints.html', complaints=complaints)

def event_details(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('event_details.html', event=event)

@login_required
def join_event():
    data = request.get_json()
    event_id = data.get('event_id')

    # Проверка, что пользователь уже участвует в событии
    existing_participant = EventParticipant.query.filter_by(event_id=event_id, user_id=current_user.id).first()

    if existing_participant:
        # Если пользователь уже участвует, возвращаем успешный ответ
        return jsonify({'message': 'Вы уже зарегестрированны', 'participants': existing_participant.event.people_come}), 200

    # Добавляем нового участника
    new_participant = EventParticipant(event_id=event_id, user_id=current_user.id)
    db.session.add(new_participant)
    db.session.commit()

    event = Event.query.get(event_id)
    event.people_come += 1
    db.session.commit()

    return jsonify({'message': 'Вы успешно зарегестрированны', 'participants': event.people_come}), 200

def create_complaint():
    violation_type = request.form.get('violationType')
    organization = request.form.get('organization')
    description = request.form.get('description')
    evidence = request.form.get('evidence')
    incident_date = request.form.get('incidentDate')
    location = request.form.get('location')
    
    # Убедитесь, что обязательные поля заполнены
    if not violation_type or not description:
        return render_template('error.html', error_message="Заполните обязательные поля")

    # Создайте объект жалобы
    new_complaint = Complaint(
        violationType=violation_type,
        organization=organization,
        description=description,
        evidence=evidence,
        incidentDate=incident_date,
        location=location
    )

    # Сохраняем в базе данных
    db.session.add(new_complaint)
    db.session.commit()

    # Перенаправляем на страницу с жалобами
    return redirect('/')

user_bp.add_url_rule('/dashboard', view_func=dashboard, methods=['GET'])
user_bp.add_url_rule('/calendar', view_func=calendar, methods=['GET'])
user_bp.add_url_rule('/profile', view_func=profile, methods=['GET', 'POST'])
user_bp.add_url_rule('/chatbot', view_func=chatbot, methods=['GET'])
user_bp.add_url_rule('/education', view_func=education, methods=['GET'])
user_bp.add_url_rule('/complaints', view_func=create_complaint, methods=['POST'])
user_bp.add_url_rule('/event/<int:event_id>', view_func=lambda event_id: event_details(event_id), methods=['GET'])
user_bp.add_url_rule('/ideas', view_func=ideas, methods=['GET', 'POST'])
user_bp.add_url_rule('/complaints', view_func=complaints, methods=['GET', 'POST'])
user_bp.add_url_rule('/event/join', view_func=join_event, methods=['POST'])