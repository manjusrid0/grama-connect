from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    
    # Add these
    skills = db.Column(db.Text, nullable=True)        # can store JSON as string
    experience = db.Column(db.Text, nullable=True)
