from dataclasses import replace
from re import sub
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
import requests
import bs4
import json
from .models import Note
from . import db

api = Blueprint('api', __name__)  

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

    if len(elements) == 0:
        return "logout"
    return ''.join(map(str, elements))

def note_is_valid(note):
    if len(note) < 1 or note.isspace():
        flash("A note can not be empty.", category="error")
        return False
    elif len(note) > 256:
        flash("This note is too long.", category="error")
        return False
    return True

#########################################
# Function above this | Endpoints below #
#########################################

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

@api.route('/create-note', methods=['POST'])
def create_note():
    note = request.form.get('note')

    if note_is_valid(note):
        new_note = Note(content=note, userID=current_user.sbID)
        db.session.add(new_note)
        db.session.commit()
        flash("Successfully saved note.", category="success")
    return redirect(url_for('views.quicknotes'))
