from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ----------------- USER -----------------
class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(150))
    skills = db.Column(db.Text)
    password = db.Column(db.String(200))
    profile_pic = db.Column(db.String(300), default="default.png")
    profession = db.Column(db.String(100))
    status = db.Column(db.String(100))
    courses = db.Column(db.Text)

    # Relationships
    products_for_sale = db.relationship("Product", backref="seller", lazy=True)
    purchases = db.relationship("Purchase", backref="buyer", lazy=True)
    jobs_posted = db.relationship("Job", backref="poster", lazy=True)
    classes_posted = db.relationship("ClassPost", backref="owner", lazy=True)
    notifications = db.relationship("Notification", backref="user", lazy=True)
    activities = db.relationship("Activity", backref="user", lazy=True)
    joined_classes = db.relationship("JoinedClass", backref="user", lazy=True)
    joined_jobs = db.relationship("JoinedJob", backref="user", lazy=True)

# ----------------- PRODUCTS -----------------
class Product(db.Model):
    __tablename__ = "product"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    image_filename = db.Column(db.String(200))
    price = db.Column(db.String(20))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # All purchases of this product
    purchases = db.relationship("Purchase", backref="product", lazy=True)

    # Helper: Number of buyers
    @property
    def buyer_count(self):
        return len(self.purchases)

# ----------------- PURCHASE -----------------
class Purchase(db.Model):
    __tablename__ = "purchase"
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- JOBS -----------------
class Job(db.Model):
    __tablename__ = "job"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    joined_jobs = db.relationship("JoinedJob", backref="job", lazy=True)

class JoinedJob(db.Model):
    __tablename__ = "joined_job"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- CLASSES -----------------
class ClassPost(db.Model):
    __tablename__ = "class_post"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_type = db.Column(db.String(20), nullable=False)  # video_link / upload_video / offline
    video_url = db.Column(db.String(200))
    video_filename = db.Column(db.String(200))
    location = db.Column(db.String(100))
    date_time = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Students joined
    joined_classes = db.relationship("JoinedClass", backref="parent_class", lazy=True)

    # Helper: Number of attendees
    @property
    def attendee_count(self):
        return len(self.joined_classes)

class JoinedClass(db.Model):
    __tablename__ = "joined_class"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey("class_post.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- UPLOADS -----------------
class Upload(db.Model):
    __tablename__ = "upload"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_type = db.Column(db.String(20), nullable=False)  # video or image
    uploader_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer, default=0)  # optional: store file size in bytes

# ----------------- MENTORSHIP -----------------
class MentorshipRequest(db.Model):
    __tablename__ = "mentorship_request"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    need = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ----------------- NOTIFICATIONS -----------------
class Notification(db.Model):
    __tablename__ = "notification"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(50), default="general")

# ----------------- ACTIVITIES -----------------
class Activity(db.Model):
    __tablename__ = "activity"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
