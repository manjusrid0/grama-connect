from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os, json
from app import app, db
from models import User

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        # Update description
        current_user.description = request.form.get("description")

        # Handle profile photo upload
        if "profile_photo" in request.files:
            photo = request.files["profile_photo"]
            if photo.filename != "":
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                current_user.profile_photo = filename

        # Handle skills (name:level pairs)
        skill_names = request.form.getlist("skill_name")
        skill_levels = request.form.getlist("skill_level")
        skills_dict = {}
        for name, level in zip(skill_names, skill_levels):
            if name.strip():
                skills_dict[name] = int(level)
        current_user.skills = skills_dict

        # Handle experience
        exp_titles = request.form.getlist("exp_title")
        exp_companies = request.form.getlist("exp_company")
        exp_start = request.form.getlist("exp_start")
        exp_end = request.form.getlist("exp_end")
        exp_desc = request.form.getlist("exp_desc")

        experiences = []
        for t, c, s, e, d in zip(exp_titles, exp_companies, exp_start, exp_end, exp_desc):
            if t.strip():
                experiences.append({
                    "title": t,
                    "company": c,
                    "start_date": s,
                    "end_date": e,
                    "description": d
                })
        current_user.experience = experiences

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("edit_profile.html", user=current_user)
