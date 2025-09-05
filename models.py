from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    description = db.Column(db.Text, nullable=True)
    profile_photo = db.Column(db.String(200), nullable=True)

    # Store as JSON in DB (string)
    skills = db.Column(db.Text, nullable=True, default="{}")
    experience = db.Column(db.Text, nullable=True, default="[]")

    # Convert JSON string -> Python dict/list
    def get_skills(self):
        return json.loads(self.skills) if self.skills else {}

    def get_experience(self):
        return json.loads(self.experience) if self.experience else []
