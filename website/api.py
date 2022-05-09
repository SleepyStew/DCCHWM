from dataclasses import replace
from re import sub
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
import requests
import bs4
import json
from .models import Note, User
from . import db

api = Blueprint('api', __name__)  

# Returns basic 5 subject "today" timetable | STRING(HTML)
def get_timetable(current_user):

    friendly_subject_names = {
        "Homegroup": "Homegroup",
        "Art": "Art",
        "ComL": "ComLife",
        "Dram": "Drama",
        "Elec": "Electronics",
        "Eng": "English",
        "Farm": "Farming",
        "Food": "Food Tech",
        "Germ": "German",
        "Huma": "Humanities",
        "Math": "Maths",
        "Medi": "Media",
        "Musi": "Music",
        "OuEd": "Outdoor Ed",
        "PE": "PE",
        "RS": "Research Science",
        "Sci": "Science",
        "Sport": "Sport",
        "Vis": "VisCom",
        "Community Life": "ComLife"
    }

    cookies = {
        'PHPSESSID': f'{current_user.sbCookie}',
    }

    response = requests.get("https://schoolbox.donvale.vic.edu.au", cookies=cookies)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    elements = []

    for tag in soup.find_all(attrs={'class': 'timetable-subject'}):

        if len(tag.find_all()) == 2:
            tag.append(soup.new_tag("br"))
        
        tag.find_all()[0]['style'] = "display: inline; text-decoration: none;"
        tag.find_all()[0]['target'] = "_blank"
        for subject, subject_value in friendly_subject_names.items():
            if subject in tag.find_all()[0].text:
                tag.find_all()[0].string.replace_with(subject_value)
                break
        try:
            tag.find_all()[0]['href'] = "https://schoolbox.donvale.vic.edu.au" + tag.find_all()[0]['href']
        except:
            pass
        elements.append(tag)

    if "userNameInput.placeholder = 'Sample.User@donvale.vic.edu.au';" in response.text:
        return "logout"
    return ''.join(map(str, elements))

# Returns whether a note is valid or not | BOOLEAN
def note_is_valid(note):
    if len(note) < 1 or note.isspace():
        flash("A note can not be empty.", category="error")
        return False
    elif len(note) > 256:
        flash("This note is too long.", category="error")
        return False
    return True

def setting_is_valid(setting):
    if setting == "True" or setting == "False":
        return True
    if setting == "low" or setting == "medium" or setting == "high":
        return True
    return False

#########################################
# Function above this | Endpoints below #
#########################################

# Endpoint for deleting notes
@api.route('/delete-note', methods=['POST'])
def delete_note():
    note_id = json.loads(request.data)['note_id']
    note = Note.query.get(note_id)
    if note:
        if note.userID == current_user.sbID:
            db.session.delete(note)
            db.session.commit()
            flash("Note successfully deleted.", category="success")
            return json.dumps({'success': True})
    return json.dumps({'success': False})

# Endpoint for editing notes
@api.route('/edit-note', methods=['POST'])
def edit_note():
    note_id = json.loads(request.data)['note_id']
    note_content = json.loads(request.data)['note_content']
    note = Note.query.get(note_id)
    if note:
        if note.userID == current_user.sbID:
            if note_is_valid(note_content):
                Note.query.filter_by(id=note_id).update(dict(content=note_content))
                db.session.commit()
                flash("Note successfully edited.", category="success")
                return json.dumps({'success': True})
    return json.dumps({'success': False})

# Endpoint for creating notes
@api.route('/create-note', methods=['POST'])
def create_note():
    note = request.form.get('note')

    if note_is_valid(note):
        new_note = Note(content=note, userID=current_user.sbID)
        db.session.add(new_note)
        db.session.commit()
        flash("Successfully saved note.", category="success")
    return redirect(url_for('views.quicknotes'))

@api.route('/update-setting', methods=['POST'])
def update_setting():
    setting_type = request.form.get('setting_type')
    new_setting = request.form.get('new_setting')
    print(setting_type)
    print(new_setting)
    if setting_is_valid(new_setting):
        print("1")
        if setting_type == "alerts":
            print("2")
            User.query.filter_by(id=current_user.sbID).update(dict(setting_alerts=new_setting))
            db.session.commit()
            print("3")
    return redirect(url_for('views.settings'))