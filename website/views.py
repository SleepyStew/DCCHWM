import requests
from flask import Blueprint, render_template, redirect, url_for, send_from_directory, flash
from flask_admin import AdminIndexView
from flask_admin.contrib import sqla as flask_admin_sqla
from flask_login import login_required, current_user

from . import app
from . import db
from .api import check_if_down
from .api import get_recent_messages
from .api import get_timetable
from .api import get_upcoming_due_work
from .auth import logout_current_user
from .models import User, Note

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
    schoolbox_is_down = not check_if_down(response)
    duework = get_upcoming_due_work(response, current_user)
    if timetable == "logout" or duework == "logout":
        flash("Your Schoolbox session has expired, please log back in.", category="error")
        logout_current_user()
        return redirect(url_for('auth.login'))
    timetable_headers = ["<div class=\"timetable-top\">Homegroup<br>8:40am-8:55am</div>", "<div class=\"timetable-top\">Period 1<br>9:00am-10:10am</div>",
                         "<div class=\"timetable-top\">Period 2<br>10:30am-11:40am</div>", "<div class=\"timetable-top\">Period 3<br>11:45am-12:55pm</div>",
                         "<div class=\"timetable-top\">Period 4<br>1:50pm-3:05pm</div>"]
    ziptable = zip(timetable, timetable_headers)
    return render_template("dashboard.html", timetable=ziptable, duework=duework, schoolbox_is_down=schoolbox_is_down)


@views.route('/information')
def information():
    return render_template("information.html")


@views.route('/quick-notes', methods=['GET'])
@login_required
def quicknotes():
    notes = Note.query.filter_by(userID=current_user.sbID).order_by(Note.displayOrder.asc()).all()
    return render_template("notes.html", notes=notes)


@views.route('/discussion', methods=['GET'])
@login_required
def chatroom():
    recent_messages = get_recent_messages(current_user)
    return render_template("chatroom.html", recent_messages=recent_messages)


@views.route('/settings', methods=['GET'])
@login_required
def settings():
    return render_template("usersettings.html")


@views.route("/recover", methods=['GET'])
@login_required
def recover():
    lines = []
    customjs = User.query.filter_by(sbID=current_user.sbID).first().customJavascript
    for line in customjs.splitlines():
        lines.append("// " + line)

    User.query.filter_by(sbID=current_user.sbID).update(dict(customJavascript="\n".join(lines)))
    db.session.commit()
    flash("Your custom Javascript has been commented out.", category="success")
    return redirect(url_for('views.settings'))


@app.errorhandler(429)
def too_many_requests(e):
    return render_template("ratelimit.html")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


class DefaultModelView(flask_admin_sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        try:
            return current_user.isAdmin
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
            User.query.filter_by(sbID=5350).update(dict(isAdmin=True))
            db.session.commit()
            return current_user.isAdmin
        except:
            return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        if not current_user.is_authenticated:
            flash("Please log in to access this page.", category="success")
            return redirect(url_for('auth.login'))

        flash("You do not have access to this page.", category="error")
        return redirect(url_for('views.root'))
