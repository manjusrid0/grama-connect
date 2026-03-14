🌾 **Grama Connect – Empowering Rural Communities with Digital Solutions**

Grama Connect is a **Flask-based digital platform** designed to bridge the gap between rural talent and modern digital opportunities.
The platform helps **students, self-employed individuals, and rural communities** access jobs, education, mentorship, and local commerce in one unified system.

The goal of this project is simple: **connect rural skills to real opportunities using technology.**

---

## 🚀 Features

### 👤 User System

* User registration and login
* Profile management with skills and profession
* Profile picture upload
* Activity tracking

### 💼 Job Portal

* Post local job opportunities
* Join available jobs
* Employer can view applicants
* Email notification when someone applies

### 🛒 Local Marketplace

* Users can post products for sale
* Buy products from other users
* Sellers receive email notifications when a product is purchased
* Buyer list visible to sellers

### 🎓 Learning & Classes

* Post educational classes
* Join online or offline classes
* Support for:

  * Video link classes
  * Uploaded video classes
  * Offline training sessions
* Automatic redirect to class content after joining

### 📚 Free Course Suggestions

Connects users with free government learning platforms like:

* Skill India
* NPTEL
* SWAYAM
* DIKSHA

### 🧠 Mentorship Requests

Users can request guidance or support from mentors.

Admin receives email notifications when a mentorship request is submitted.

### 📈 Income Estimator

Helps self-employed users estimate monthly income based on:

* Skill type
* Working hours
* Days worked

### 🛠️ Self Employment Ideas

Provides business ideas for rural communities such as:

* Goat farming
* Tailoring
* Pickle business
* Paper bag manufacturing
* Mobile recharge services

### 🌐 Multi-Language Support

Users can switch between languages:

* English
* Tamil
* Hindi
* Malayalam
* Telugu

### 🔔 Notification System

Automatic notifications for:

* Job applications
* Product purchases
* Class enrollments
* Mentorship requests

### 🛡️ Admin Dashboard

Admin can manage:

* Job postings
* Mentorship requests
* Uploaded learning content
* Platform activity

---

## 🛠️ Tech Stack

💻 **Frontend**

* HTML
* CSS
* Bootstrap
* Jinja2 Templates

⚙️ **Backend**

* Python
* Flask Framework

🗃️ **Database**

* SQLite
* SQLAlchemy ORM

🔐 **Authentication**

* Flask-Login

🌍 **Localization**

* Flask-Babel (Multi-language support)

📧 **Email Notifications**

* SMTP (Gmail)

📂 **File Upload**

* Image uploads
* Video uploads
* Profile picture uploads

---

## 📦 Project Structure

```
grama_connect/
│
├── app.py
│
├── database/
│   └── grama_main.db
│
├── static/
│   ├── uploads/
│   ├── profile_pic/
│   └── css/
│
├── templates/
│   ├── home.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── jobs.html
│   ├── join_job.html
│   ├── add_product.html
│   ├── buy.html
│   ├── post_class.html
│   ├── join_class.html
│   ├── request_mentorship.html
│   ├── income_estimator.html
│   └── admin_dashboard.html
│
└── README.md
```

---

## ⚙️ How to Run Locally

### 1️⃣ Clone the Repository

```
git clone https://github.com/yourusername/grama-connect.git
cd grama-connect
```

### 2️⃣ Create Virtual Environment

Windows

```
python -m venv venv
venv\Scripts\activate
```

Mac/Linux

```
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

### 4️⃣ Run the Application

```
python app.py
```

### 5️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

## 🔑 Admin Login

Username

```
admin
```

Password

```
admin123
```

Admin Panel URL

```
http://127.0.0.1:5000/admin
```

---

## 🌟 Project Highlights

✔ Built specifically for **rural empowerment**
✔ Supports **jobs, education, commerce, and mentorship** in one platform
✔ **Multi-language interface** for accessibility
✔ Designed for **students, villagers, and self-employed individuals**
✔ Simple and practical UI for real-world users

---

## 🌐 Live Project

https://grama-connect.onrender.com/

---

## 👩‍💻 Developer

**Manjusri D**

📍 Cuddalore, Tamil Nadu
📧 [manjusrid0@gmail.com](mailto:manjusrid0@gmail.com)
💼 LinkedIn: https://www.linkedin.com/in/manjusri-d

---

## 📜 License

This project is developed for educational and community development purposes.
