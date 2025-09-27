# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(150))
    skills = db.Column(db.Text)
    password_hash = db.Column(db.String(200))
    profile_pic = db.Column(db.String(300), default="default.png")

    # Relationships
    products_for_sale = db.relationship("Product", backref="seller", foreign_keys="Product.seller_id", lazy=True)
    products_bought = db.relationship("Product", backref="buyer", foreign_keys="Product.buyer_id", lazy=True)
    jobs_posted = db.relationship("Job", backref="poster", foreign_keys="Job.user_id", lazy=True)
    classes_posted = db.relationship("ClassPost", backref="owner", foreign_keys="ClassPost.owner_id", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)

class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))
    image_filename = db.Column(db.String(200))
    price = db.Column(db.String(20))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # poster
    joined_jobs = db.relationship('JoinedJob', backref='job', lazy=True)

class JoinedJob(db.Model):
    __tablename__ = "joined_job"
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'))  # points to job.id

class ClassPost(db.Model):
    __tablename__ = "class_post"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_type = db.Column(db.String(20), nullable=False)  # 'video_link', 'upload_video', 'offline'
    video_link = db.Column(db.String(200), nullable=True)  # YouTube / DIKSHA
    file_name = db.Column(db.String(200), nullable=True)   # Uploaded video/file path
    location = db.Column(db.String(100), nullable=True)    # Offline location
    date_time = db.Column(db.String(100), nullable=True)   # Offline date/time
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationship: One class → many joined users
    joined_classes = db.relationship("JoinedClass", backref="parent_class", lazy=True)

class JoinedClass(db.Model):
    __tablename__ = "joined_class"

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    class_ref = db.Column(db.Integer, db.ForeignKey("class_post.id"), nullable=False)

class Upload(db.Model):
    __tablename__ = "upload"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_type = db.Column(db.String(20), nullable=False)  # 'video' or 'image'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MentorshipRequest(db.Model):
    __tablename__ = "mentorship_request"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    need = db.Column(db.Text)

class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.String(50), default="general")
