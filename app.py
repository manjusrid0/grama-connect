# app.py
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.utils import secure_filename
from flask_babel import Babel, get_locale
from flask_mail import Mail
from email.mime.text import MIMEText
import smtplib

# -------------------- Flask App --------------------


app = Flask(__name__)
app.secret_key = "supersecretkey"

# Dummy class to simulate your Product object (no DB change needed)
class DummyProduct:
    def __init__(self, id, name, description, price, quantity, image_filename):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity
        self.image_filename = image_filename



# -------------------- Multi-language --------------------
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['LANGUAGES'] = {'en':'English','ta':'தமிழ்','hi':'हिन्दी','ml':'മലയാളം','te':'తెలుగు'}
babel = Babel(app)
def select_locale(): return session.get('lang', request.accept_languages.best_match(app.config['LANGUAGES'].keys()))
@app.context_processor
def inject_globals(): return dict(get_locale=get_locale)

# -------------------- Database --------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'database', 'grama_main.db')
os.makedirs(os.path.dirname(db_path), exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------- Models --------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(150))
    skills = db.Column(db.Text)
    password = db.Column(db.String(150))
    profile_pic = db.Column(db.String(300), default="default.png")
    profession = db.Column(db.String(150))
    status = db.Column(db.String(150))
    courses = db.Column(db.String(300))
    classes = db.relationship('ClassPost', backref='owner', lazy=True)
    

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    image_filename = db.Column(db.String(200))
    price = db.Column(db.String(20))
    quantity = db.Column(db.Integer, default=1)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purchases = db.relationship('Purchase', backref='product', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    buyer = db.relationship('User', backref='purchases')

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
    poster = db.relationship('User', backref='posted_jobs', lazy=True, foreign_keys=[user_id])

class JoinedJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    job_ref = db.Column(db.Integer, db.ForeignKey('job.id'))

class ClassPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    class_type = db.Column(db.String(20), nullable=False)
    video_url = db.Column(db.String(200), nullable=True)
    video_filename = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    date_time = db.Column(db.String(100), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    joined_classes = db.relationship("JoinedClass", backref="parent_class", lazy=True)

class JoinedClass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    class_ref = db.Column(db.Integer, db.ForeignKey("class_post.id"), nullable=False)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    filename = db.Column(db.String(200))
    upload_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class MentorshipRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    need = db.Column(db.Text)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('activities', lazy=True))

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    type = db.Column(db.String(50), default="general")

# -------------------- DB Init --------------------
with app.app_context():
    db.create_all()

# -------------------- Login --------------------
login_manager = LoginManager()
login_manager.login_view = 'user_login'
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id): return User.query.get(int(user_id))

# -------------------- Upload Settings --------------------
UPLOAD_FOLDER = os.path.join('static', 'uploads')
PROFILE_PIC_FOLDER = os.path.join('static', 'profile_pic')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROFILE_PIC_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROFILE_PIC_FOLDER'] = PROFILE_PIC_FOLDER

# -------------------- Admin --------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# -------------------- Utilities --------------------
def allowed_file(filename): return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def send_notification(recipient, subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = app.config['MAIL_USERNAME']
        msg["To"] = recipient
        with smtplib.SMTP("smtp.gmail.com",587) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(app.config['MAIL_USERNAME'], recipient, msg.as_string())
    except Exception as e: print("❌ Email error:", e)

# -------------------- ROUTES --------------------
@app.route('/')
def home(): 
    return render_template("home.html")
@app.route('/about')
def about(): 
    return render_template("about.html")
@app.route('/set_language/<language>')
def set_language(language): session['lang']=language; return redirect(request.referrer or url_for('home'))

# -------------------- Admin Routes --------------------
@app.route("/admin", methods=["GET"])
def admin_login_page(): 
    return render_template("admin_login.html")
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method=="GET": return redirect(url_for('admin_login_page'))
    username = request.form.get("username"); password = request.form.get("password")
    if username==ADMIN_USERNAME and password==ADMIN_PASSWORD:
        session['admin_logged_in']=True; return redirect(url_for('admin_dashboard'))
    flash("Invalid admin credentials"); return redirect(url_for('admin_login_page'))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))
    
    # Fetch all jobs
    jobs = Job.query.all()
    
    # Fetch all mentorship requests
    mentorship_requests = MentorshipRequest.query.order_by(MentorshipRequest.id.desc()).all()
    
    return render_template(
        "admin_dashboard.html",
        jobs=jobs,
        mentorship_requests=mentorship_requests
    )


@app.route("/admin/logout")
def admin_logout(): 
    session.pop('admin_logged_in',None); return redirect(url_for('admin_login_page'))

@app.route("/admin/add_jobs",methods=["GET","POST"])
def admin_add_job():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login_page'))
    if request.method=="POST":
        job = Job(title=request.form['title'],description=request.form['description'],location=request.form['location'],
                  salary=request.form['salary'],contact=request.form['contact'],job_type=request.form['job_type'])
        db.session.add(job); db.session.commit(); flash("Job added successfully"); return redirect(url_for('admin_view_jobs'))
    return render_template("jobs.html")

@app.route("/admin/jobs")
def admin_view_jobs():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login_page'))
    jobs = Job.query.all(); return render_template("join_job.html", jobs=jobs)

@app.route("/admin/post_upload",methods=["GET","POST"])
def post_upload():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login_page'))
    if request.method=="POST":
        file=request.files.get('file')
        if file:
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            new_upload=Upload(filename=filename,title=filename,upload_type='video')
            db.session.add(new_upload); db.session.commit()
            flash("Upload posted successfully","success"); return redirect(url_for('admin_view_upload'))
        flash("Please select a file","danger")
    return render_template("post_upload.html")

@app.route('/admin/view_uploads')
def admin_view_uploads():
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login_page'))
    uploads = Upload.query.order_by(Upload.created_at.desc()).all()
    return render_template('view_all_uploads.html', uploads=uploads)

@app.route("/admin/delete_upload/<int:upload_id>",methods=["POST","GET"])
def delete_upload(upload_id):
    if not session.get('admin_logged_in'): return redirect(url_for('admin_login_page'))
    upload=Upload.query.get_or_404(upload_id)
    file_path=os.path.join(app.config['UPLOAD_FOLDER'],upload.filename)
    if os.path.exists(file_path): os.remove(file_path)
    db.session.delete(upload); db.session.commit(); flash("Upload deleted successfully")
    return redirect(url_for('admin_view_uploads'))
@app.route('/admin/mentorship_requests')
def admin_view_mentorship():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login_page'))
    
    # Fetch all mentorship requests
    requests = MentorshipRequest.query.order_by(MentorshipRequest.id.desc()).all()
    
    return render_template('admin_mentorship_requests.html', requests=requests)

# -------------------- User Auth --------------------
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=request.form.get('name'); email=request.form.get('email'); password=request.form.get('password')
        if not name or not email or not password: flash("Please fill all fields"); return redirect(url_for('register'))
        if User.query.filter_by(email=email).first(): flash("Email exists"); return redirect(url_for('register'))
        user=User(name=name,email=email,password=password)
        db.session.add(user); db.session.commit(); flash("Registration successful"); return redirect(url_for('user_login'))
    return render_template("register.html")

@app.route('/login',methods=['GET','POST'])
def user_login():
    if request.method=='POST':
        identifier=request.form.get('username_or_email'); password=request.form.get('password')
        user=User.query.filter((User.email==identifier)|(User.name==identifier)).first()
        if user and user.password==password: login_user(user); flash(f"Welcome {user.name}"); return redirect(url_for('dashboard'))
        flash("Invalid credentials"); return redirect(url_for('user_login'))
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('user_login'))

# -------------------- Dashboard --------------------
@app.route('/dashboard')
@login_required
def dashboard():
    products = Product.query.all()  # fetch all products
    return render_template("dashboard.html", products=products)


# -------------------- Profile --------------------
@app.route('/profile')
@login_required
def profile(): return render_template('profile.html',user=current_user)

@app.route('/profile/<int:user_id>')

@login_required
def view_profile(user_id):
    user=User.query.get_or_404(user_id)
    activities=Activity.query.filter_by(user_id=user.id).order_by(Activity.timestamp.desc()).all()
    return render_template('profile.html',user=user,activities=activities)

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    user=current_user
    if request.method=='POST':
        user.name=request.form.get('name'); user.phone=request.form.get('phone')
        user.location=request.form.get('location'); user.skills=request.form.get('skills')
        for field in ['profession','status','courses']: setattr(user,field,request.form.get(field))
        file=request.files.get('profile_pic')
        if file and file.filename!='':
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            user.profile_pic=f'uploads/{filename}'
        db.session.commit(); flash("Profile updated"); return redirect(url_for('profile'))
    return render_template('edit_profile.html',user=user)

# -------------------- Search --------------------
@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('dashboard'))

    # --- Users ---
    users = User.query.filter(User.name.ilike(f"%{query}%")).all()

    # --- Jobs ---
    jobs = Job.query.filter(
        (Job.title.ilike(f"%{query}%")) | (Job.description.ilike(f"%{query}%"))
    ).all()

    # --- Products ---
    products = Product.query.filter(
        (Product.name.ilike(f"%{query}%")) | (Product.description.ilike(f"%{query}%"))
    ).all()

    # --- Classes ---
    classes = ClassPost.query.filter(
        (ClassPost.title.ilike(f"%{query}%")) | (ClassPost.description.ilike(f"%{query}%"))
    ).all()

    # --- Uploads ---
    uploads = Upload.query.filter(Upload.title.ilike(f"%{query}%")).all()

    # --- Courses ---
    courses = []
    for c in [
        {'title':'Skill India Digital – Free Govt Courses','link':'https://www.skillindiadigital.gov.in/home'},
        {'title':'NPTEL – Free Engineering & Vocational Training','link':'https://nptel.ac.in/'},
        {'title':'SWAYAM – Online Education Platform','link':'https://swayam.gov.in/'},
        {'title':'DIKSHA – Teacher and Skill Development','link':'https://diksha.gov.in/'}
    ]:
        if query.lower() in c['title'].lower():
            courses.append(c)

    return render_template(
        'search_result.html',
        query=query,
        users=users,
        jobs=jobs,
        products=products,
        classes=classes,
        uploads=uploads,
        courses=courses
    )


# -------------------- Add Product --------------------

# ---------- Products ----------
@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
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
        flash("✅ Product posted successfully!")
        return redirect(url_for('add_product'))

    # Fetch products of current seller
    products = Product.query.filter_by(seller_id=current_user.id).all()

    # Prepare buyers for each product: product_id -> list of buyer names
    buyers_dict = {}
    for product in products:
        buyers_dict[product.id] = [p.buyer.name for p in product.purchases]

    return render_template('add_product.html', products=products, buyers_dict=buyers_dict)


@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        product = Product.query.get(product_id)
        if product:
            existing_purchase = Purchase.query.filter_by(
                product_id=product.id,
                buyer_id=current_user.id
            ).first()

            if not existing_purchase:
                new_purchase = Purchase(
                    buyer_id=current_user.id,
                    product_id=product.id
                )
                db.session.add(new_purchase)
                db.session.commit()
                flash('✅ Purchase successful!')

                # Notify seller
                seller = User.query.get(product.seller_id)
                if seller:
                    send_notification(
                        seller.email,
                        "Your Product Has a New Buyer!",
                        f"Hi {seller.name},\n\nYour product '{product.name}' was bought by {current_user.name}.\n\n-Grama Connect"
                    )
            else:
                flash('⚠️ You already purchased this product.')
        else:
            flash('⚠️ Product not found.')

    products = Product.query.all()
    purchased_products = [
        p.product_id for p in Purchase.query.filter_by(buyer_id=current_user.id).all()
    ]
    sellers = {p.id: User.query.get(p.seller_id) for p in products}

    # Build purchased list here instead of using {% do %}
    purchased_list = [p for p in products if p.id in purchased_products]

    return render_template(
        'buy.html',
        products=products,
        purchased_products=purchased_products,
        sellers=sellers,
        purchased_list=purchased_list  # ✅ pass it directly
    )


# -------------------- Add Job --------------------
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
        contact = None
        duration = None

        if delivery_mode == 'video_link':
            video_url = request.form.get('video_link')
        elif delivery_mode == 'upload_video':
            video_file = request.files.get('video_file')
            if video_file and video_file.filename != '':
                filename = secure_filename(video_file.filename)
                video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                video_filename = filename
        elif delivery_mode == 'offline':
            location = request.form.get('offline_place')
            date = request.form.get('offline_date')
            time = request.form.get('offline_time')
            contact = request.form.get('offline_contact')
            duration = request.form.get('offline_duration')

            # Combine offline info into description
            offline_info = f"Location: {location}\nDate: {date}\nTime: {time}\nContact Info: {contact}\nDuration: {duration}"
            description = f"{description}\n\n{offline_info}"

        new_class = ClassPost(
            title=title,
            description=description,
            class_type=delivery_mode,
            video_url=video_url,
            video_filename=video_filename,
            location=location,
            owner_id=current_user.id,
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

@app.route('/confirm_join_class/<int:class_id>', methods=['GET', 'POST'])
@login_required
def confirm_join_class(class_id):
    selected_class = ClassPost.query.get_or_404(class_id)

    if request.method == 'POST':
        # Save user join info
        joined = JoinedClass(
            user_name=current_user.name,
            email=current_user.email,
            phone=request.form.get('phone'),
            class_ref=selected_class.id
        )
        db.session.add(joined)
        db.session.commit()

        # Notify class owner
        send_notification(
            subject="New Class Join",
            recipient=selected_class.owner.email,
            body=f"{current_user.name} has joined your class '{selected_class.title}'."
        )

        # ✅ Redirect automatically based on class type
        if selected_class.class_type in ['video_link', 'upload_video']:
            return redirect(url_for('show_class_content', class_id=selected_class.id))
        elif selected_class.class_type == 'offline':
            return redirect(url_for('show_class_content', class_id=selected_class.id))

    return render_template('join_class.html', step='confirm', selected_class=selected_class)

@app.route('/show_class/<int:class_id>')
@login_required
def show_class_content(class_id):
    cls = ClassPost.query.get_or_404(class_id)

    if cls.class_type == 'offline':
        return render_template('offline_class_details.html', class_info=cls)

    elif cls.class_type == 'video_link':
        return render_template('join_class.html', step='video_link', video_url=cls.video_url)
    elif cls.class_type == 'upload_video':
        return render_template('join_class.html', step='video', video_file=cls.video_filename)

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
    flash("class deleted successfully!")
    return redirect(url_for("post_class"))

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



# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True)