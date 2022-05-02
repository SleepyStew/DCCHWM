from flask import Blueprint, render_template, redirect, url_for
from markupsafe import Markup
from flask_login import login_user, login_required, logout_user, current_user
import flask_login
from .models import User

views = Blueprint('views', __name__)  

@views.route('/')
@login_required
def home():
    return redirect(url_for('views.dashboard'))

@views.route('/dashboard')
@login_required
def dashboard():
    print(current_user.sbCookie)
    return render_template("dashboard.html", logged_in=not isinstance(current_user, flask_login.AnonymousUserMixin), text=Markup('<strong>The HTML String</strong>'))