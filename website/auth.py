from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import flask_login
import requests
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from . import limiter

auth = Blueprint('auth', __name__)  

@auth.route('/login', methods=['POST', 'GET'])
@limiter.limit("10 per minute")
def login():
    if not isinstance(current_user, flask_login.AnonymousUserMixin):
        flash('You are already logged in. Please logout from the dashboard to return to the login page.', category='success')
        return redirect(url_for('views.root'))
    if request.method == 'POST':        
        data = request.form

        # Error handling
        if data.get('username') == None:
            return redirect(url_for('auth.login'))
        if data.get('password') == None:
            return redirect(url_for('auth.login'))

        if len(data.get('username').split(" ")) < 2:
            flash('A first and last name is required.', category='error')
        elif len(data.get('password')) < 1:
            flash('A password is required.', category='error')
        else:
            requestdata = {
                'username': data.get('username').replace(" ", "."),
                'password': data.get('password')
            }

            login = requests.post("https://schoolbox.donvale.vic.edu.au/api/session", data=requestdata)

            if login.status_code == 400 or login.status_code == 401:
                flash("Incorrect username or password.", category='error')
            elif login.status_code == 200:
                sbid = login.text.split('= {"id":')[1].split("\"")[0][:-1]
                user = User.query.filter_by(sbID=sbid).first() is not None
                if user:
                    User.query.filter_by(sbID=sbid).update(dict(id=str(login.cookies.get('PHPSESSID'))))
                    User.query.filter_by(sbID=sbid).update(dict(sbCookie=str(login.cookies.get('PHPSESSID'))))
                    db.session.commit()
                    user_login = User.query.filter_by(sbID=sbid).first()
                else:
                    user_login = User(sbID=sbid, id = str(login.cookies.get('PHPSESSID')), sbCookie=str(login.cookies.get('PHPSESSID')))
                    db.session.add(user_login)
                    db.session.commit()
                    

                login_user(user_login, remember=True)
                flash(f"Sucessfully logged in. Welcome to the Dashboard.", category='success')
                return redirect(url_for('views.dashboard'))
            else:
                flash("An error occured.", category="error")

    return render_template("login.html", user=current_user)

@auth.route('/logout')
def logout():
    if current_user.is_authenticated:
        if current_user.setting_alerts == "high":
            flash('Sucessfully logged out.', category='success')
        logout_current_user()
    else:
        flash('You are not logged in.', category='success')
    return redirect(url_for('auth.login'))

def logout_current_user():
    if current_user.is_authenticated:
        User.query.filter_by(sbID=current_user.sbID).update(dict(id="Logged Out"))
        db.session.commit()
        logout_user()