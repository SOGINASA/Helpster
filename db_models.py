import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    iin = db.Column(db.String(12), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    achievements = db.Column(db.Text, default="")
    avatar_path = db.Column(db.String(255), nullable=True)
    event_associations = db.relationship('EventParticipant', back_populates='user')

    is_admin = False
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return f"user:{self.login}"

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    avatar_path = db.Column(db.String(255), nullable=True)
    is_admin = True
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return f"admin:{self.login}"

class EventParticipant(db.Model):
    __tablename__ = 'event_participants'

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    rating = db.Column(db.Integer)  # рейтинг от 1 до 5

    event = db.relationship('Event', back_populates='user_associations')
    user = db.relationship('User', back_populates='event_associations')

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    category = db.Column(db.String(50), nullable=False)
    image_path = db.Column(db.String(200), nullable=True)
    max_participants = db.Column(db.Integer, default=100)
    points_prize = db.Column(db.Integer, default=0)
    ststus = db.Column(db.String(50), nullable=False, default="coming") # "active" or "completed" or "coming"
    people_come = db.Column(db.Integer, default=0)
    chat_link = db.Column(db.String(200), nullable=True)


    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    admin = db.relationship('Admin', backref='events')
    user_associations = db.relationship('EventParticipant', back_populates='event')

    def average_rating(self):
        ratings = [assoc.rating for assoc in self.user_associations if assoc.rating]
        if ratings:
            return round(sum(ratings) / len(ratings), 2)
        return 0.0

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    violationType = db.Column(db.String(50), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.Text)
    incidentDate = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)

if __name__ == '__main__':
    db.create_all()