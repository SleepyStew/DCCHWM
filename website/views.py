import re
from unicodedata import category
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, request, flash
from flask_login import login_user, login_required, logout_user, current_user
import flask_login
from sqlalchemy import false
from . import db
from .models import User, Note
from .api import get_timetable
from .auth import logout_current_user
from flask_admin import AdminIndexView
from flask_admin.contrib import sqla as flask_admin_sqla

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
    if timetable == "logout":
        flash("Your Schoolbox session has expired, please log back in.", category="error")
        logout_current_user()
        return redirect(url_for('auth.login'))
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
            flash("A note can not be empty.", category="error")
        else:
            new_note = Note(content=note, userID=current_user.sbID)
            db.session.add(new_note)
            db.session.commit()
            flash("Successfully saved note.", category="success")
            return redirect(url_for('views.quicknotes'))

    return render_template("notes.html", user=current_user)

class DefaultModelView(flask_admin_sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        try:
            return current_user.sbID == 5350
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("You do not have access to this page.", category="error")
        return redirect(url_for('auth.login'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            return current_user.sbID == 5350
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("You do not have access to this page.", category="error")
        return redirect(url_for('auth.login'))