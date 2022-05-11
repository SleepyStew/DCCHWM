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
import markdown
import re

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

def convert_to_markdown(note):
    note = markdown.markdown(note)
    soup = bs4.BeautifulSoup(note, 'html.parser')
    elements = []
    for tag in soup.findAll():
        tag['style'] = "display: inline;"
        elements.append(tag)
    note = ''.join(map(str, elements))
    note = note.replace("\n", "<br>")
    return note

#########################################
# Function above this | Endpoints below #
#########################################

# Endpoint for deleting notes
@api.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note_id = json.loads(request.data)['note_id']
    note = Note.query.get(note_id)
    if note and note.userID == current_user.sbID:
        db.session.delete(note)
        db.session.commit()
        if current_user.setting_alerts == "high":
            flash("Note successfully deleted.", category="success")
        return json.dumps({'success': True})
    return json.dumps({'success': False})

# Endpoint for editing notes
@api.route('/edit-note', methods=['POST'])
@login_required
def edit_note():
    note_id = json.loads(request.data)['note_id']
    note_content = convert_to_markdown(json.loads(request.data)['note_content'].strip())
    note = Note.query.get(note_id)
    if note and note.userID == current_user.sbID and note_is_valid(note_content):
        Note.query.filter_by(id=note_id).update(dict(content=note_content))
        db.session.commit()
        if current_user.setting_alerts == "high":
            flash("Note successfully edited.", category="success")
        return json.dumps({'success': True})
    return json.dumps({'success': False})

# Endpoint for creating notes
@api.route('/create-note', methods=['POST'])
@login_required
def create_note():
    note = convert_to_markdown(request.form.get('note').strip())

    if note_is_valid(note):
        new_note = Note(content=note, userID=current_user.sbID)
        db.session.add(new_note)
        db.session.commit()
        if current_user.setting_alerts == "high":
            flash("Successfully saved note.", category="success")
    return redirect(url_for('views.quicknotes'))

@api.route('/update-setting', methods=['POST'])
@login_required
def update_setting():
    setting_type = request.form.get('setting_type')
    new_setting = request.form.get('new_setting')

    valid_setting = False

    if setting_type == "alerts":
        if new_setting == "low" or new_setting == "high":
            valid_setting = True
            User.query.filter_by(sbID=current_user.sbID).update(dict(setting_alerts=new_setting))
            db.session.commit()
    
    if valid_setting and current_user.setting_alerts == "high":
        flash("Successfully updated setting.", category="success")

    return redirect(url_for('views.settings'))
