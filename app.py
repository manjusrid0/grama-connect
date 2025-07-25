from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os
from werkzeug.utils import secure_filename
import sqlite3
import os



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.secret_key = 'secretkey'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'
if not os.path.exists("database"):
    os.makedirs("database")

# Connect to the database
conn = sqlite3.connect("database/grama.db")
cursor = conn.cursor()

# Create the jobs table
cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    location TEXT NOT NULL
)
''')
# Mentorship Request Table
# -------------------------------
class MentorshipRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    need = db.Column(db.Text)

# -------------------------------
# Skill Badge Activity Table (for future use if you want dynamic badge)
# -------------------------------
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    videos_uploaded = db.Column(db.Integer, default=0)
    classes_joined = db.Column(db.Integer, default=0)
    jobs_posted = db.Column(db.Integer, default=0)


# Insert sample jobs (optional)
sample_jobs = [
    ("Teacher", "Theni"),
    ("Electrician", "Madurai"),
    ("Handloom Weaver", "Kanchipuram"),
    ("Agri Consultant", "Trichy")
]

cursor.executemany("INSERT INTO jobs (title, location) VALUES (?, ?)", sample_jobs)

# Commit and close
conn.commit()
conn.close()

print("✅ grama.db created with sample job data.")

# ------------------- MODELS -------------------

class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(300))
    image_filename = db.Column(db.String(100))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)


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

# Home route
@app.route('/')
def home():
    return render_template("home.html")

# Admin login page (GET)
@app.route("/admin", methods=["GET"])
def admin_login_page():
    return render_template("admin_login.html")

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
        location = request.form['location']

        con = sqlite3.connect("database/grama.db")
        cur = con.cursor()
        cur.execute("INSERT INTO jobs (title, location) VALUES (?, ?)", (title, location))
        con.commit()
        con.close()

        flash("Job added successfully")
        return redirect(url_for('view_jobs'))

    return render_template("add_job.html")


@app.route("/admin/view_jobs")
def view_jobs():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))

    con = sqlite3.connect("database/grama.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM jobs")
    jobs = cur.fetchall()
    con.close()

    return render_template("view_jobs.html", jobs=jobs)

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
        image = request.files['image']

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product = Product(
                name=name,
                description=description,
                image=filename,
                seller_id=current_user.id
            )
            db.session.add(product)
            db.session.commit()
            flash("Product posted successfully!")
            return redirect(url_for('dashboard'))

    return render_template('sell.html')
@app.route('/debug/jobs')
def debug_jobs():
    import sqlite3
    con = sqlite3.connect("database/grama.db")
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
            flash('Product purchased successfully! The seller has been notified.')
        else:
            flash('This product is already purchased.')
    products = Product.query.filter_by(buyer_id=None).all()
    return render_template('buy.html', products=products)
@app.route('/my-products')
@login_required
def my_products():
    products = Product.query.filter_by(seller_id=current_user.id).all()
    return render_template('my_products.html', products=products)

@app.route('/post_class', methods=['GET', 'POST'])
@login_required
def post_class():
    if request.method == 'POST':
        # Add logic for storing class data
        flash("Class posted successfully!")
        return redirect(url_for('dashboard'))
    return render_template('post_class.html')
@app.route('/join_class', methods=['GET', 'POST'])
@login_required
def join_class():
    if request.method == 'POST':
        class_code = request.form.get('class_code')
        # You can validate class_code if needed
        flash(f'You have joined the class with code: {class_code}', 'success')
        return redirect(url_for('dashboard'))
    return render_template('join_class.html')
@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_job = Job(title=title, description=description, user_id=current_user.id)
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!')
        return redirect(url_for('jobs'))

    all_jobs = Job.query.all()
    return render_template('jobs.html', jobs=all_jobs)

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