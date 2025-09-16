from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.utils import secure_filename
from flask_babel import Babel, _
import os
from datetime import datetime
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText


# -------------------- Flask App Setup --------------------
app = Flask(__name__)
app.secret_key = 'secretkey'

# Upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database', 'grama_main.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)  # ensure folder exists

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "your_email@gmail.com"   # sender email
app.config['MAIL_PASSWORD'] = "your_app_password"      # app password, not Gmail login
app.config['MAIL_DEFAULT_SENDER'] = "your_email@gmail.com"

mail = Mail(app)
# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

# Babel / Multi-language setup
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'ta': 'தமிழ்',
    'hi': 'हिन्दी',
    'ml': 'മലയാളം',
    'te': 'తెలుగు'
}
babel = Babel(app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_locale():
    return session.get('lang', request.accept_languages.best_match(['en', 'ta', 'hi', 'te', 'ml']))

babel.init_app(app, locale_selector=get_locale)

def send_notification(to_email, subject, body):
    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[to_email])
    msg.body = body
    mail.send(msg)

def send_notification(subject, recipient, body):
    sender_email = "your_outlook_email@outlook.com"   # change here
    sender_password = "your_password"                 # change here

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient

    try:
        with smtplib.SMTP("smtp.office365.com", 587) as server:  # if Outlook
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient, msg.as_string())
        print("✅ Email sent successfully")
    except Exception as e:
        print("❌ Error:", e)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.String(50), default="general")

    def __init__(self, message, user_id=None, type="general"):
        self.message = message
        self.user_id = user_id
        self.type = type

    @staticmethod
    def create_notification(message, user, type="general", send_email=False):
        notif = Notification(message=message, user_id=user.id, type=type)
        db.session.add(notif)
        db.session.commit()

        # Send email if required
        if send_email and user.email:
            try:
                msg = Message(
                    subject="Grama Connect Notification",
                    recipients=[user.email],
                    body=message
                )
                mail.send(msg)
            except Exception as e:
                print("Email sending failed:", e)

        return notif

@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

# -------------------- Models --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(150))
    skills = db.Column(db.Text)
    password = db.Column(db.String(150))
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))
    image_filename = db.Column(db.String(100))
    price = db.Column(db.String(20))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    seller = db.relationship("User", foreign_keys=[seller_id])
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(200), nullable=False)  # video or image
    upload_type = db.Column(db.String(20), nullable=False)  # 'video' or 'image'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    location = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    contact = db.Column(db.String(50))
    job_type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    joined_jobs = db.relationship('JoinedJob', backref='job', lazy=True)
class JoinedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    job_ref = db.Column(db.Integer, db.ForeignKey('job.id'))

class ClassPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    delivery_mode = db.Column(db.String(20))  # 'video_link', 'upload_video', 'offline'
    video_link = db.Column(db.String(200))
    file_name = db.Column(db.String(200))
    location = db.Column(db.String(100))
    date_time = db.Column(db.String(100))

    # ✅ Add owner link
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    owner = db.relationship("User", backref="classes")


class JoinedClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    class_ref = db.Column(db.Integer, db.ForeignKey('class_post.id'))
    joined_class = db.relationship('ClassPost', backref='joined_users')

class MentorshipRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    need = db.Column(db.Text)

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    videos_uploaded = db.Column(db.Integer, default=0)
    classes_joined = db.Column(db.Integer, default=0)
    jobs_posted = db.Column(db.Integer, default=0)

# Create all tables
with app.app_context():
    db.create_all()

# -------------------- Login Manager --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Admin --------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# -------------------- Routes --------------------
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(request.referrer or url_for('home'))

# ---------- Admin Routes ----------
@app.route("/admin", methods=["GET"])
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == 'GET':
        return redirect(url_for('admin_login_page'))
    username = request.form.get("username")
    password = request.form.get("password")
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Invalid admin credentials")
        return redirect(url_for('admin_login_page'))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))
    
    jobs = Job.query.all()  # Fetch all jobs
    return render_template("admin_dashboard.html", jobs=jobs)


@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login_page'))

@app.route("/admin/add_jobs", methods=["GET", "POST"])
def admin_add_job():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))
    if request.method == "POST":
        job = Job(
            title=request.form['title'],
            description=request.form['description'],
            location=request.form['location'],
            salary=request.form['salary'],
            contact=request.form['contact'],
            job_type=request.form['job_type']
        )
        db.session.add(job)
        db.session.commit()
        flash("Job added successfully")
        return redirect(url_for('admin_view_jobs'))
    return render_template("jobs.html")

@app.route("/admin/jobs")
def admin_view_jobs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))
    jobs = Job.query.all()
    return render_template("join_job.html", jobs=jobs)
@app.route("/admin/delete_upload/<int:upload_id>", methods=["POST", "GET"])
def delete_upload(upload_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    upload = Upload.query.get_or_404(upload_id)

    # Remove file from static/uploads if it exists
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], upload.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Delete record from database
    db.session.delete(upload)
    db.session.commit()

    flash("🗑️ Upload deleted successfully")
    return redirect(url_for('admin_view_uploads'))

@app.route("/admin/post_upload", methods=["GET", "POST"])
def post_upload():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    if request.method == "POST":
        file = request.files.get('file')
        description = request.form.get('description')

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Save file
            file.save(filepath)

            # Save to DB
            new_upload = Upload(filename=filename, description=description)
            db.session.add(new_upload)
            db.session.commit()

            flash("✅ Upload posted successfully", "success")
            return redirect(url_for('admin_view_uploads'))
        else:
            flash("⚠️ Please select a file", "danger")

    return render_template("post_upload.html")




@app.route('/admin/view_uploads')
def admin_view_uploads():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    uploads = Upload.query.order_by(Upload.created_at.desc()).all()
    return render_template('view_all_uploads.html', uploads=uploads)

# ---------- User Registration/Login ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not name or not email or not password:
            flash("Please fill in all fields")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for('register'))

        user = User(name=name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for('user_login'))

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        identifier = request.form.get('username_or_email')
        password = request.form.get('password')

        if not identifier or not password:
            flash("⚠️ Please enter both username/email and password", "warning")
            return redirect(url_for('user_login'))

        # Login check (plain password, or hash later)
        user = User.query.filter(
            (User.email == identifier) | (User.name == identifier)
        ).first()

        if user and user.password == password:
            login_user(user)
            flash(f"✅ Welcome back, {user.name}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("❌ Invalid credentials", "danger")
            return redirect(url_for('user_login'))

    return render_template("login.html")



@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")
@app.route('/dashboard/uploads')
@login_required
def user_view_uploads():
    uploads = Upload.query.filter_by(upload_type='video').order_by(Upload.created_at.desc()).all()
    return render_template('user_view_uploads.html', uploads=uploads)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_login'))

# ---------- Profile ----------
@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.name = request.form['name']
        current_user.phone = request.form['phone']
        current_user.location = request.form['location']
        current_user.skills = request.form['skills']
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for("profile"))
    return render_template("edit_profile.html")

# ---------- Products ----------
@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        image = request.files['image']
        filename = secure_filename(image.filename) if image else None
        if image and allowed_file(image.filename):
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            image_filename=filename,
            seller_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('sell', success='1'))
    success = request.args.get('success') == '1'
    return render_template('add_product.html', success=success)

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        if product and not product.buyer_id:
            product.buyer_id = current_user.id
            db.session.commit()
            flash('Product purchased successfully!')

            # Notify seller
            send_notification(
                product.seller.email,   # seller is a User object
                "Your Product Has Been Sold!",
                f"Hi {product.seller.name},\n\nYour product '{product.name}' was bought by {current_user.name}.\n\n-Grama Connect"
            )

        else:
            flash('Product not available or already sold.')


    available_products = Product.query.filter_by(buyer_id=None).all()
    purchased_products = Product.query.filter_by(buyer_id=current_user.id).all()

    return render_template('buy.html', products=available_products, purchased=purchased_products)



# ---------- Jobs ----------
# Route to post a job
@app.route("/user/add_jobs", methods=["GET", "POST"])
@login_required
def view_jobs():
    if request.method == "POST":
        job = Job(
            title=request.form['title'],
            description=request.form['description'],
            location=request.form['location'],
            salary=request.form['salary'],
            contact=request.form['contact'],
            job_type=request.form['job_type'],
            user_id=current_user.id
        )
        db.session.add(job)
        db.session.commit()
        flash("Job added successfully!")
        return redirect(url_for('view_jobs'))
    
    # Show all jobs including the newly added ones
    jobs = Job.query.all()
    return render_template("jobs.html", jobs=jobs)

# Route to join a job
@app.route("/jobs", methods=["POST"])
@login_required
def add_jobs():
    job_id = int(request.form['job_id'])
    joined = JoinedJob(
        user_name=request.form['name'],
        email=request.form['email'],
        phone=request.form['phone'],
        job_ref=job_id
    )
    db.session.add(joined)
    db.session.commit()
    flash("Successfully joined the job! Employer will contact you.")
    return redirect(url_for('view_jobs'))

@app.route("/jobs", methods=["GET", "POST"])
@login_required
def user_view_jobs():
    jobs = Job.query.all()
    message = None
    if request.method == "POST":
        job_id = int(request.form['job_id'])
        joined = JoinedJob(
            user_name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            job_ref=job_id
        )
        db.session.add(joined)
        db.session.commit()
        job = Job.query.get(job_id)

        # Notify job poster
        send_notification(
            job.poster.email,
            "New Job Application",
            f"Hi {job.poster.name},\n\n{current_user.name} ({current_user.email}) has applied for your job '{job.title}'.\n\n-Grama Connect"
        )

        message = "Successfully joined the job! The employer will contact you."
    return render_template('join_job.html', jobs=jobs, message=message)

@app.route("/user/view_applicants/<int:job_id>")
@login_required
def view_applicants(job_id):
    job = Job.query.get_or_404(job_id)

    # Make sure only the job poster can see applicants
    if job.user_id != current_user.id:
        flash("You are not authorized to view this job's applicants")
        return redirect(url_for('add_job'))

    applicants = job.joined_jobs  # All JoinedJob entries for this job
    return render_template("view_applicants.html", job=job, applicants=applicants)

# ---------- Classes ----------
@app.route('/post_class', methods=['GET', 'POST'])
def post_class():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        delivery_mode = request.form['delivery_mode']
        video_url = None
        video_filename = None
        location = None
        date = None
        time = None

        if delivery_mode == 'video_link':
            video_url = request.form.get('video_link')
        elif delivery_mode == 'upload_video':
            video_file = request.files.get('video_file')
            if video_file and video_file.filename != '':
                filename = secure_filename(video_file.filename)
                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                video_filename = filename
        elif delivery_mode == 'offline':
            location = request.form.get('offline_details')

        new_class = ClassPost(
            title=title,
            description=description,
            class_type=delivery_mode,
            video_url=video_url,
            video_filename=video_filename,
            location=location,
            date=date,
            owner_id=current_user.id,
            time=time
        )
        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('post_class'))

    classes = ClassPost.query.all()

    return render_template("post_class.html", classes=classes)

@app.route('/join_class')
def join_class():
    classes = ClassPost.query.all()
    return render_template('join_class.html', step='list', classes=classes)


@app.route('/confirm_join/<int:class_id>', methods=['GET', 'POST'])
@login_required
def confirm_join_class(class_id):
    selected_class = ClassPost.query.get_or_404(class_id)

    if request.method == 'POST':
        # ✅ Send email to class owner
        send_notification(
            subject="New Class Join",
            recipient=selected_class.owner.email,
            body=f"Hi {selected_class.owner.name}, {current_user.name} has joined your class '{selected_class.title}'."
        )
        flash("You have successfully joined the class!")
        return redirect(url_for('join_class'))

    return render_template('join_class.html', step='confirm', selected_class=selected_class)

@app.route('/show_class/<int:class_id>')
def show_class_content(class_id):
    cls = ClassPost.query.get_or_404(class_id)
    if cls.class_type == 'video_link':
        return redirect(cls.video_url)
    elif cls.class_type == 'upload_video':
        return render_template('join_class.html', step='video', video_file=cls.video_filename)
    elif cls.class_type == 'offline':
        return render_template('join_class.html', step='offline', class_info=cls)
    return "Invalid class type."

@app.route('/edit_class/<int:class_id>', methods=['GET', 'POST'])
def edit_class(class_id):
    cls = ClassPost.query.get_or_404(class_id)
    if request.method == 'POST':
        cls.title = request.form['title']
        cls.description = request.form['description']
        cls.class_type = request.form['delivery_mode']
        cls.video_url = None
        cls.video_filename = None
        cls.location = None
        if cls.class_type == 'video_link':
            cls.video_url = request.form.get('video_link')
        elif cls.class_type == 'upload_video':
            video_file = request.files.get('video_file')
            if video_file and video_file.filename != '':
                filename = secure_filename(video_file.filename)
                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cls.video_filename = filename
        elif cls.class_type == 'offline':
            cls.location = request.form.get('offline_details')
        db.session.commit()
        return redirect(url_for('post_class'))
    return render_template('edit_class.html', cls=cls)

@app.route('/delete_class/<int:class_id>')
def delete_class(class_id):
    cls = ClassPost.query.get_or_404(class_id)
    db.session.delete(cls)
    db.session.commit()
    return redirect(url_for('post_class'))

@app.route('/video/<filename>')
def uploaded_video(filename):
    return render_template('video_page.html', filename=filename)

# ---------- Mentorship ----------
@app.route('/request_mentorship', methods=['GET', 'POST'])
@login_required
def request_mentorship():
    success = False
    if request.method == 'POST':
        req = MentorshipRequest(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            need=request.form['need']
        )
        db.session.add(req)
        db.session.commit()
        success = True

        # Always notify admin
        send_notification(
            "manjusrid0@gmail.com",  # admin email
            "New Mentorship Request",
            f"Hi Admin,\n\n{current_user.name} ({current_user.email}) has requested mentorship.\n\nDetails: {req.need}\n\n-Grama Connect"
        )

        flash("Mentorship request submitted. Admin will contact you soon.")

    return render_template('request_mentorship.html', success=success)


# ---------- Income Estimator ----------
@app.route('/income_estimator', methods=['GET', 'POST'])
def income_estimator():
    estimated_income = None
    if request.method == 'POST':
        skill = request.form.get('skill')
        try:
            hours = int(request.form.get('hours', 0))
            days = int(request.form.get('days', 0))
        except ValueError:
            hours = 0
            days = 0

        # Add more skills if needed
        rates = {
            'Tailoring': 60,
            'Farming': 40,
            'Masonry': 80,
            'Welding': 100,
            'Tutoring': 50,
            'Handicrafts': 50,
            'Jewelry Making': 70,
            'Cooking': 45
        }

        if skill in rates:
            estimated_income = rates[skill] * hours * days * 4  # 4 weeks in a month

    return render_template('income_estimator.html', estimated_income=estimated_income)


# ---------- Self Employment ----------
@app.route('/self_employment_board')
def self_employment_board():
    ideas = [
        {'title':'Goat Farming','description':'Start with 2 goats, sell milk, manure, and kids. Can earn ₹8,000–₹12,000/month.','link':'https://youtu.be/1RwPCtSAr-4'},
        {'title':'Home-based Pickle Business','description':'Use local ingredients, low investment. Package and sell to neighbors or online.','link':'https://www.skillindiadigital.gov.in/home'},
        {'title':'Paper Bag Making','description':'Eco-friendly product idea. Sell to small shops, markets, and schools.','link':'https://youtu.be/mnY1x2vIp58'},
        {'title':'Basic Tailoring Service','description':'Use one sewing machine and offer mending/alterations for daily income.','link':''},
        {'title':'Mobile Recharge & UPI Agent','description':'Provide digital services in rural area with a smartphone. No huge setup needed.','link':'https://youtu.be/xnmsbBqbsQU'}
    ]
    return render_template('self_employment_board.html', ideas=ideas)

# ---------- Free Courses ----------
# ---------- Free Courses ----------
@app.route('/free_courses')
def free_courses():
    courses = [
        {'title':'Skill India Digital – Free Govt Courses',
         'description':'Thousands of certified courses for self-employment, from tailoring to tech.',
         'link':'https://www.skillindiadigital.gov.in/home'},
        {'title':'NPTEL – Free Engineering & Vocational Training',
         'description':'IIT-level learning with certification in various engineering and vocational subjects.',
         'link':'https://nptel.ac.in/'},
        {'title':'SWAYAM – Online Education Platform',
         'description':'Free courses in arts, science, management, technology with certifications.',
         'link':'https://swayam.gov.in/'},
        {'title':'DIKSHA – Teacher and Skill Development',
         'description':'Platform offering courses and resources for educators and skill development.',
         'link':'https://diksha.gov.in/'}
    ]
    return render_template('free_courses.html', courses=courses)

# ---------- Error Handlers ----------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True)
