from flask import Blueprint, render_template, redirect, url_for, request

views = Blueprint('views', __name__)  

@views.route('/')
def home():
    return redirect(url_for('auth.login'))