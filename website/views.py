from unicodedata import category
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, request, flash
from flask_login import login_user, login_required, logout_user, current_user
import flask_login
from . import db
from .models import User, Note
from .api import get_timetable

views = Blueprint('views', __name__)  

@views.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@views.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@views.route('/dashboard')
@login_required
def dashboard():
    timetable = get_timetable(current_user)
    return render_template("dashboard.html", user=current_user, timetable=timetable)

@views.route('/information')
def information():
    return render_template("information.html", user=current_user)

@views.route('/quick-notes', methods=['GET', 'POST'])
@login_required
def quicknotes():
    if request.method == "POST":
        note = request.form.get('note')

        if len(note) < 1:
            flash("You must enter a note to save.", category="error")
        else:
            new_note = Note(content=note, userID=current_user.sbID)
            db.session.add(new_note)
            db.session.commit()
            flash("Note saved.", category="success")
            return redirect(url_for('views.quicknotes'))

    return render_template("notes.html", user=current_user)