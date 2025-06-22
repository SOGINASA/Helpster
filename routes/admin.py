import datetime
from flask import flash, jsonify, redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required
from db_models import Event, EventParticipant, db, User
from werkzeug.utils import secure_filename
import os
import babel.dates

admin_bp = Blueprint('admin', __name__)


UPLOAD_FOLDER ='/home/ivanchik322/Helpster/view/static/uploads/events'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_required
def create_event():
    if not current_user.is_admin:
        flash("Доступ запрещён", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':

        title = request.form.get('title')
        description = request.form.get('description')
        location = request.form.get('location')
        category = request.form.get('category')
        date_str = request.form.get('date')
        image = request.files.get('image')
        max_participants = request.form.get('max_participants')
        chat_link = request.form.get('chat_link')

        # Валидация
        if not all([title, date_str, category]):
            flash("Заполните обязательные поля: Название, Дата и Категория", "warning")
            return redirect(request.referrer)

        # Парсинг даты
        try:
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            flash("Неверный формат даты", "danger")
            return redirect(request.referrer)

        # Загрузка изображения
        image_path = None
        if image and allowed_file(image.filename):
            filename = secure_filename(f"{datetime.datetime.utcnow().timestamp()}_{image.filename}")
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = f"uploads/events/{filename}"
        elif image:
            flash("Недопустимый формат изображения", "danger")
            return redirect(request.referrer)

        # Создание события
        new_event = Event(
            title=title,
            description=description,
            date=event_date,
            location=location,
            category=category,
            image_path=image_path,
            admin_id=current_user.id,
            max_participants=max_participants,
            chat_link = chat_link,
        )
        db.session.add(new_event)
        db.session.commit()

        flash("Мероприятие успешно создано", "success")
        return redirect(url_for('admin.create_event'))  # Переход после создания

    return render_template('create_event.html')  # Форма для создания нового события




@login_required
def get_events_json():
    user_id = request.args.get('user_id', type=int)
    user = User.query.get(user_id) if user_id else None  # Проверка наличия пользователя

    events = Event.query.order_by(Event.date.asc()).all()
    result = []

    for event in events:
        formatted_date = babel.dates.format_date(event.date, format='d MMMM', locale='ru')

        # Проверка на наличие пользователя
        if user:
            # Проверка присоединения пользователя к событию
            is_joined = EventParticipant.query.filter_by(event_id=event.id, user_id=user.id).first() is not None
        else:
            is_joined = False  # Если пользователя нет, то по умолчанию присоединение не происходит

        # Подсчет участников через EventParticipant
        participants_count = db.session.query(EventParticipant).filter_by(event_id=event.id).count()

        result.append({
            "id": event.id,
            "title": event.title,
            "date": formatted_date,
            "participants": participants_count,
            "max_participants": event.max_participants,
            "category": event.category,
            "img": url_for('static', filename=event.image_path) if event.image_path else None,
            "description": event.description,
            "location": event.location,
            "created_at": event.created_at.isoformat(),
            "admin_email": event.admin.email if event.admin else None,
            "joined": is_joined
        })

    return jsonify({"events": result})



@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user.dashboard'))

    # Получаем все мероприятия
    events = Event.query.all()

    # Статистика:
    active_events = Event.query.filter(Event.date == datetime.datetime.utcnow()).count()  # Активные мероприятия
    completed_events = Event.query.filter(Event.date <= datetime.datetime.utcnow()).count()  # Завершённые мероприятия
    average_rating = db.session.query(db.func.avg(EventParticipant.rating)).scalar()  # Средний рейтинг мероприятий

    # Список пользователей
    users = User.query.all()

    return render_template('admin_main.html',
                           events=events,
                           active_events=active_events,
                           completed_events=completed_events,
                           average_rating=average_rating,
                           users=users)

@login_required
def admin_events():
    events = Event.query.all()
    return render_template('admin_events.html', events=events)

def admin_complaints():
    complaints = Complaint.query.all()
    return render_template('admin_complaints.html', complaints=complaints)

def statistics():
    avg_rating = db.session.query(db.func.avg(EventParticipant.rating)).scalar()
    people_come = db.session.query(db.func.sum(Event.people_come)).scalar()
    return render_template('statistics.html', avg_rating=avg_rating, people_come=people_come)

def messages():
    return render_template('messages.html')

def user_statistics():
    return render_template('user_statistics.html')

def test_create():
    return render_template('test_create.html')

admin_bp.add_url_rule('/events/create', view_func=create_event, methods=['GET', 'POST'])
admin_bp.add_url_rule('/events/json', view_func=get_events_json, methods=['GET'])
admin_bp.add_url_rule('/dashboard', view_func=admin_dashboard, methods=['GET'])
admin_bp.add_url_rule('/events', view_func=admin_events, methods=['GET'])
admin_bp.add_url_rule('/complaints', view_func=admin_complaints, methods=['GET'])
admin_bp.add_url_rule('/statistic', view_func=statistics, methods=['GET'])
admin_bp.add_url_rule('/messages', view_func=messages, methods=['GET'])
admin_bp.add_url_rule('/user_statistics', view_func=user_statistics, methods=['GET'])
admin_bp.add_url_rule('/tests/create', view_func=test_create, methods=['GET'])