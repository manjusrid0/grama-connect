from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os
import sqlite3
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, session, redirect, url_for
from flask_babel import Babel, _
from datetime import datetime
import random
import string


# --------------- Flask App Setup ------------------
app = Flask(__name__)
app.secret_key = 'secretkey'
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grama_main.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {
    'en': 'English',
    'ta': 'தமிழ்',
    'hi': 'हिन्दी',
    'ml': 'മലയാളം',
    'te': 'తెలుగు'
}
babel = Babel()



# --------------- Database + Migrate Init ------------------# --------------- Flask-Login ------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

# --------------- Helper ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------- MODELS -------------------

# ---------- User Table ----------
class User(UserMixin, db.Model):
 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# ---------- Product Table ----------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))
    image_filename = db.Column(db.String(100))
    price = db.Column(db.String(20))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    seller = db.relationship("User", foreign_keys=[seller_id])

# ---------- Job Table ----------
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
class JoinedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    job_ref = db.Column(db.Integer, db.ForeignKey('job.id'))

# ---------- Class Posting ----------
class ClassPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_type = db.Column(db.String(20), nullable=False)
    
    # For Video Link
    video_url = db.Column(db.String(500))
    
    # For Uploaded Video
    video_filename = db.Column(db.String(200))
    
    # For Offline/Live Class
    location = db.Column(db.String(100))
    date = db.Column(db.String(20))
    time = db.Column(db.String(20))

# ---------- Class Joining ----------
# ---------- Class Joining ----------
class JoinedClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    class_ref = db.Column(db.Integer, db.ForeignKey('class_post.id'))  # Link to ClassPost
    
    joined_class = db.relationship('ClassPost', backref='joined_users')

# ---------- Mentorship Request ----------
class MentorshipRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    need = db.Column(db.Text)

# ---------- Skill Badge System ----------
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    videos_uploaded = db.Column(db.Integer, default=0)
    classes_joined = db.Column(db.Integer, default=0)
    jobs_posted = db.Column(db.Integer, default=0)

# Create all tables before altering anything
with app.app_context():
    db.create_all()

# THEN try to add columns
def safe_add_column(table, column, col_type):
    db_path = os.path.join(os.getcwd(), 'grama_main.db')  # or use instance path if needed
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [info[1] for info in cursor.fetchall()]
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        print(f"✅ Column '{column}' added to '{table}'")
    else:
        print(f"ℹ️ Column '{column}' already exists in '{table}'")
    conn.close()

# Now run this AFTER tables are created


# ------------------- LOGIN MANAGER -------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# ---------------- ADMIN CREDENTIAL -------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def get_locale():
    return session.get('lang', 'en')
@app.context_processor
def inject_locale():
    return dict(get_locale=get_locale)

# Home route
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/set_language/<language>')
def set_language(language):
    session['lang'] = language
    return redirect(request.referrer or url_for('home'))


# Admin login page (GET)
@app.route("/admin", methods=["GET"])
def admin_login_page():
    return render_template("admin_login.html")
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")
# Admin login form POST handler
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

# Admin dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))
    return render_template("admin_dashboard.html")

# Admin logout
@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login_page'))

@app.route("/admin/add_jobs", methods=["GET", "POST"])
def add_job():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']

        con = sqlite3.connect("instance/grama_main.db")
        cur = con.cursor()
        cur.execute("INSERT INTO job (title, description) VALUES (?, ?)", (title, description))
        con.commit()
        con.close()

        flash("Job added successfully")
        return redirect(url_for('jobs'))

    return render_template("jobs.html")


@app.route("/admin/view_jobs")
def view_jobs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    con = sqlite3.connect("instance/grama_main")
    cur = con.cursor()
    
    jobs = Job.query.all()
    message = None

    if request.method == 'POST':
        job_id = int(request.form['job_id'])
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        joined = JoinedJob(
            user_name=name,
            email=email,
            phone=phone,
            job_ref=job_id
        )
        db.session.add(joined)
        db.session.commit()

        message = "Successfully joined the job! The employer will contact you."

    return render_template('join_job.html', jobs=jobs, message=message)

@app.route("/admin/view_uploads")
def view_all_uploads():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    con = sqlite3.connect("database/grama.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM videos")
    videos = cur.fetchall()

    cur.execute("SELECT * FROM classes")
    classes = cur.fetchall()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    con.close()

    return render_template("view_all_uploads.html", videos=videos, classes=classes, products=products)

# ------------------- USER LOGIN/REGISTER -------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists!")
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please login.")
        return redirect(url_for('user_login'))
    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
    return render_template("login.html")

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user_login'))
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

    # Fetch activity record
    activity = UserActivity.query.filter_by(user_id=current_user.id).first()
    badge = None

    if activity:
        score = activity.videos_uploaded + activity.classes_joined + activity.jobs_posted

        if score >= 5:
            badge = "Gold Contributor"
        elif score >= 3:
            badge = "Silver Contributor"
        elif score >= 1:
            badge = "Bronze Contributor"

    return render_template('profile.html', badge=badge)

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product = Product(
                name=name,
                description=description,
                image_filename=filename,
                price=price,
                seller_id=current_user.id
            )
            db.session.add(product)
            db.session.commit()

            # ✅ Redirect with success flag
            return redirect(url_for('sell', success='1'))

    # ✅ Get flash message only if redirected with ?success=1
    success = request.args.get('success') == '1'
    return render_template('add_product.html', success=success)

@app.route('/debug/jobs')
def debug_jobs():
    import sqlite3
    con = sqlite3.connect("instance/grama_main.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM jobs")
    data = cur.fetchall()
    con.close()
    return "<br>".join([f"{d[0]} - {d[1]} - {d[2]}" for d in data])



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

    available_products = Product.query.filter_by(buyer_id=None).all()
    purchased_products = Product.query.filter_by(buyer_id=current_user.id).all()
    return render_template('buy.html', products=available_products, purchased=purchased_products)






@app.route('/post_class', methods=['GET', 'POST'])

def post_class():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        delivery_mode = request.form['delivery_mode']  # ✅ was class_type

        video_url = None
        video_filename = None
        location = None
        date = None
        time = None

        if delivery_mode == 'video_link':
            video_url = request.form.get('video_link')

        elif delivery_mode == 'upload_video':
            video_file = request.files['video_file']
            if video_file:
                filename = secure_filename(video_file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video_file.save(filepath)
                video_filename = filename

        elif delivery_mode == 'offline':
            location = request.form.get('offline_details')
            # If you're collecting date/time separately, uncomment below:
            # date = request.form.get('date')
            # time = request.form.get('time')

        new_class = ClassPost(
            title=title,
            description=description,
            class_type=delivery_mode,  # save it into DB field `class_type`
            video_url=video_url,
            video_filename=video_filename,
            location=location,
            date=date,
            time=time
        )

        db.session.add(new_class)
        db.session.commit()
        return redirect(url_for('post_class'))

    classes = ClassPost.query.all()
    return render_template("post_class.html", classes=classes)

# Step 1: Show all available classes
@app.route('/join_class')
def join_class():
    classes = ClassPost.query.all()
    return render_template('join_class.html', step='list', classes=classes)

# Step 2: Confirm Join
@app.route('/confirm_join/<int:class_id>', methods=['GET', 'POST'])
def confirm_join(class_id):
    selected_class = ClassPost.query.get_or_404(class_id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        joined = JoinedClass(
            user_name=name,
            email=email,
            phone=phone,
            class_ref=class_id
        )
        db.session.add(joined)
       

        return redirect(url_for('show_class_content', class_id=class_id))

    return render_template('join_class.html', step='confirm', selected_class=selected_class)

# Step 3: Show Content
@app.route('/show_class/<int:class_id>')
def show_class_content(class_id):
    selected_class = ClassPost.query.get_or_404(class_id)

    if selected_class.class_type == 'video_link':

        return redirect(selected_class.video_url)

    elif selected_class.class_type == 'upload_video':
        return render_template('join_class.html', step='video', video_file=selected_class.video_filename)

    elif selected_class.class_type == 'offline_class':
        return render_template('join_class.html', step='offline', class_info=selected_class)

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
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video_file.save(filepath)
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


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        salary = request.form['salary']
        contact = request.form['contact']
        job_type = request.form['job_type']
        new_job = Job(title=title, description=description, user_id=current_user.id)
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!')
        return redirect(url_for('jobs'))

    all_jobs = Job.query.all()
    return render_template('jobs.html', jobs=all_jobs)
@app.route('/join-job', methods=['GET', 'POST'])
def join_job():
    jobs = Job.query.all()
    message = None

    if request.method == 'POST':
        job_id = int(request.form['job_id'])
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        joined = JoinedJob(
            user_name=name,
            email=email,
            phone=phone,
            job_ref=job_id
        )
        db.session.add(joined)
        db.session.commit()

        message = "Successfully joined the job! The employer will contact you."

    return render_template('join_job.html', jobs=jobs, message=message)

@app.route('/income_estimator', methods=['GET', 'POST'])
def income_estimator():
    estimated_income = None
    if request.method == 'POST':
        skill = request.form['skill']
        hours = int(request.form['hours'])
        days = int(request.form['days'])

        # Base income estimation table (in INR/hour)
        income_rates = {
            'Tailoring': 60,
            'Farming': 40,
            'Masonry': 80,
            'Welding': 100,
            'Tutoring': 50
        }

        if skill in income_rates:
            rate = income_rates[skill]
            weekly_income = rate * hours * days
            estimated_income = weekly_income * 4  # Approx. monthly

    return render_template('income_estimator.html', estimated_income=estimated_income)

@app.route('/self_employment_board')
def self_employment_board():
    ideas = [
        {
            'title': 'Goat Farming',
            'description': 'Start with 2 goats, sell milk, manure, and kids. Can earn ₹8,000–₹12,000/month.',
            'link': 'https://youtu.be/1RwPCtSAr-4'
        },
        {
            'title': 'Home-based Pickle Business',
            'description': 'Use local ingredients, low investment. Package and sell to neighbors or online.',
            'link': 'https://www.skillindiadigital.gov.in/home'
        },
        {
            'title': 'Paper Bag Making',
            'description': 'Eco-friendly product idea. Sell to small shops, markets, and schools.',
            'link': 'https://youtu.be/mnY1x2vIp58'
        },
        {
            'title': 'Basic Tailoring Service',
            'description': 'Use one sewing machine and offer mending/alterations for daily income.',
            'link': ''
        },
        {
            'title': 'Mobile Recharge & UPI Agent',
            'description': 'Provide digital services in rural area with a smartphone. No huge setup needed.',
            'link': 'https://youtu.be/xnmsbBqbsQU'
        }
    ]
    return render_template('self_employment_board.html', ideas=ideas)

@app.route('/free_courses')
def free_courses():
    courses = [
        {
            'title': 'Skill India Digital – Free Govt Courses',
            'description': 'Thousands of certified courses for self-employment, from tailoring to tech.',
            'link': 'https://www.skillindiadigital.gov.in/home'
        },
        {
            'title': 'NPTEL – Free Engineering & Vocational Training',
            'description': 'IIT-level learning with certification. Great for youth and students.',
            'link': 'https://onlinecourses.nptel.ac.in/'
        },
        {
            'title': 'eSkillIndia Platform',
            'description': 'Free digital literacy, retail, agriculture, and soft skills.',
            'link': 'https://eskillindia.org/'
        },
        {
            'title': 'PMKVY – Government Training Centres',
            'description': 'Visit PMKVY centres nearby to learn offline & get job-ready.',
            'link': 'https://www.pmkvyofficial.org/'
        },
        {
            'title': 'YouTube – Hand Skill Tutorials',
            'description': 'Thousands of free tutorials on tailoring, craft, farming & more.',
            'link': 'https://www.youtube.com/results?search_query=rural+skills+training'
        }
    ]
    return render_template('free_courses.html', courses=courses)
@app.route('/request_mentorship', methods=['GET', 'POST'])
def request_mentorship():
    success = False
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        need = request.form['need']

        new_request = MentorshipRequest(name=name, email=email, phone=phone, need=need)
        db.session.add(new_request)
        db.session.commit()
        success = True

    return render_template('request_mentorship.html', success=success)


# ------------------- MAIN -------------------
if __name__ == '__main__':
    if not os.path.exists('database'):
        os.makedirs('database')
    with app.app_context():
        db.create_all()
    app.run(debug=True)