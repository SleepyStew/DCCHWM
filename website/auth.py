from flask import Blueprint, render_template, request, flash, redirect
import requests
import os

auth = Blueprint('auth', __name__)  

@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print(request.method)         
        data = request.form
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
                id = login.text.split('= {"id":')[1].split("\"")[0][:-1]
                external_id = login.text.split('= {"id":')[1].split("\"")[3]
                flash(f"Sucessfully authenticated. This had no effect. ID: {id}, External ID: {external_id}.", category='success')
            else:
                flash("An error occured.", category="error")

    return render_template("login.html")

@auth.route('/logout')
def logout():
    return 'Logout'
