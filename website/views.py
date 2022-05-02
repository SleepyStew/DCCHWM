from flask import Blueprint, render_template, redirect, url_for, send_from_directory
from flask_login import login_user, login_required, logout_user, current_user
import flask_login
from .models import User
from .api import get_timetable

views = Blueprint('views', __name__)  

@views.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@views.route('/')
def home():
    if not isinstance(current_user, flask_login.AnonymousUserMixin):
        return redirect(url_for('views.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@views.route('/dashboard')
@login_required
def dashboard():
    timetable = get_timetable(current_user)
    return render_template("dashboard.html", logged_in=not isinstance(current_user, flask_login.AnonymousUserMixin), timetable=timetable)

@views.route('/information')
def information():
    return render_template("information.html", logged_in=not isinstance(current_user, flask_login.AnonymousUserMixin))