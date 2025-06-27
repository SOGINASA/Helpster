import datetime
from flask import flash, jsonify, redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required
from db_models import Event, EventParticipant, db, User, Complaint
from werkzeug.utils import secure_filename
import os
import babel.dates

admin_bp = Blueprint('admin', __name__)


UPLOAD_FOLDER = '/home/ivanchik322/Helpster/view/static/uploads/events'
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
        points_prize = request.form.get('price')

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
            points_prize = points_prize
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

    average_rating = db.session.query(db.func.avg(EventParticipant.rating)).scalar()  # Средний рейтинг мероприятий

    # Список пользователей
    users = User.query.all()

    return render_template('admin_main.html', 
                           events=events,
                           active_events=Event.query.filter_by(status="coming").count(),
                           average_rating=average_rating,
                           users=users,
                           total_users=User.query.count(),
                           total_compaints=Complaint.query.count()
                           )

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
    total_events = Event.query.count()
    total_users = User.query.count()
    active_events = Event.query.filter(Event.status.in_(["coming", "active"])).count()
    eco_events = Event.query.filter_by(category="Экология").count()
    animals_events = Event.query.filter_by(category="Животные").count()
    social_events = Event.query.filter_by(category="Социальные").count()
    raids_events = Event.query.filter_by(category="рейды").count()
    lectures_events = Event.query.filter_by(category="лекции").count()
    flashmobs_events = Event.query.filter_by(category="флэшмобы").count()
    events = Event.query.all()

    # Получаем топ участников, их имя и сумму очков
    top_users = User.query.order_by(User.points.desc()).limit(3).all()

    return render_template(
        'user_statistics.html',
        total_events=total_events,
        total_users=total_users,
        active_events=active_events,
        eco_events=eco_events,
        animals_events=animals_events,
        social_events=social_events,
        raids_events=raids_events,
        lectures_events=lectures_events,
        flashmobs_events=flashmobs_events,
        events=events,
        top_users=top_users
    )



def test_create():
    return render_template('test_create.html')

def change_event_status(event_id, new_status):
    event = Event.query.get_or_404(event_id)
    event.status = new_status

    db.session.commit()
    return redirect(url_for('admin.admin_events'))

def event():
    event_id = request.args.get('event_id', type=int)
    event = Event.query.get_or_404(event_id)
    users = User.query.join(EventParticipant).filter(EventParticipant.event_id == event_id).all()
    return render_template('admin_event_details.html', event=event, users=users)

def mark_attended():
    # Получаем данные из тела запроса
    data = request.get_json()
    user_id = data.get('user_id')
    event_id = data.get('event_id')

    # Получаем пользователя и событие
    user = User.query.get_or_404(user_id)
    event = Event.query.get_or_404(event_id)

    # Проверяем, есть ли участник в этом мероприятии
    participant = EventParticipant.query.filter_by(user_id=user_id, event_id=event_id).first()
    
    if not participant:
        return jsonify({"error": "User is not part of this event"}), 404

    if f'Участие в {event.title}' in user.achievements.split(', '):
        return jsonify({"message": "User already marked"}), 200

    #начисляем очки
    user.points += event.points_prize

    # Добавим ачивку
    achievement_name = f'Участие в {event.title}'
    user.add_achievement(achievement_name)
    db.session.commit()
    # Вернем успешный ответ
    return jsonify({"message": f"User {user.login} marked as attended, added {event.points_prize} level", "achievement": achievement_name}), 200

admin_bp.add_url_rule('/events/create', view_func=create_event, methods=['GET', 'POST'])
admin_bp.add_url_rule('/events/json', view_func=get_events_json, methods=['GET'])
admin_bp.add_url_rule('/dashboard', view_func=admin_dashboard, methods=['GET'])
admin_bp.add_url_rule('/events', view_func=admin_events, methods=['GET'])
admin_bp.add_url_rule('/complaints', view_func=admin_complaints, methods=['GET'])
admin_bp.add_url_rule('/statistic', view_func=statistics, methods=['GET'])
admin_bp.add_url_rule('/messages', view_func=messages, methods=['GET'])
admin_bp.add_url_rule('/user_statistics', view_func=user_statistics, methods=['GET'])
admin_bp.add_url_rule('/tests/create', view_func=test_create, methods=['GET'])
admin_bp.add_url_rule('/events/<int:event_id>/status/<string:new_status>', view_func=lambda event_id, new_status: change_event_status(event_id, new_status), methods=['POST'])
admin_bp.add_url_rule('/event', view_func=event, methods=['GET'])   
admin_bp.add_url_rule('/mark_attended', view_func=mark_attended, methods=['POST'])