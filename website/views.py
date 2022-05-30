import re
from unicodedata import category
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import flask_login
from regex import P
from sqlalchemy import false
from .api import get_upcoming_due_work
from . import db
from .models import User, Note
from .api import get_timetable
from .auth import logout_current_user
from flask_admin import AdminIndexView
from flask_admin.contrib import sqla as flask_admin_sqla
from .api import note_is_valid
from . import app
import requests
from . import socketio
from flask_socketio import SocketIO
import sys
import json

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
    cookies = { 
        'PHPSESSID': f'{current_user.sbCookie}',
    }
    response = requests.get("https://schoolbox.donvale.vic.edu.au", cookies=cookies)
    timetable = get_timetable(response, current_user)
    duework = get_upcoming_due_work(response, current_user)
    if timetable == "logout" or duework == "logout":
        flash("Your Schoolbox session has expired, please log back in.", category="error")
        logout_current_user()
        return redirect(url_for('auth.login'))
    timetable_headers = ["<div class=\"timetable-top\">Homegroup<br>8:40am-8:55am</div>", "<div class=\"timetable-top\">Period 1<br>9:00am-10:10am</div>", "<div class=\"timetable-top\">Period 2<br>10:30am-11:40am</div>", "<div class=\"timetable-top\">Period 3<br>11:45am-12:55pm</div>", "<div class=\"timetable-top\">Period 4<br>1:50pm-3:05pm</div>"]
    return render_template("dashboard.html", user=current_user, timetable=zip(timetable, timetable_headers), duework=duework)

@views.route('/information')
def information():
    return render_template("information.html", user=current_user)

@views.route('/quick-notes', methods=['GET'])
@login_required
def quicknotes():
    return render_template("notes.html", user=current_user)

@views.route('/chatroom', methods=['GET'])
@login_required
def chatroom():
    recent_messages = []
    with open('chatlog.txt', 'r') as f:
        for message in f.readlines()[-100:]:
            recent_messages.append(json.loads(message.replace("'", "\"")))
    return render_template("chatroom.html", user=current_user, recent_messages=recent_messages)

@views.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template("usersettings.html", user=current_user)

@app.errorhandler(429)
def too_many_requests(e):
    return render_template("ratelimit.html", user=current_user)

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
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", category="success")
            return redirect(url_for('auth.login'))

        flash("You do not have access to this page.", category="error")
        return redirect(url_for('views.root'))

class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        try:
            return current_user.sbID == 5350
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", category="success")
            return redirect(url_for('auth.login'))
            
        flash("You do not have access to this page.", category="error")
        return redirect(url_for('views.root'))