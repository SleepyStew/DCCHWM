from dataclasses import replace
from re import sub
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
        "Vis": "VisCom"
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
        
        tag.find_all()[0]['style'] = "display: inline;"
        tag.find_all()[0]['target'] = "_blank"
        for subject in friendly_subject_names:
            if subject in tag.find_all()[0].text:
                tag.find_all()[0].text.replace_with(subject)
                break
        try:
            tag.find_all()[0]['href'] = "https://schoolbox.donvale.vic.edu.au" + tag.find_all()[0]['href']
        except:
            pass
        elements.append(tag)

    if len(elements) == 0:
        return "logout"
    return ''.join(map(str, elements))

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
            Note.query.filter_by(id=note_id).update(dict(content=note_content))
            db.session.commit()
            flash("Note successfully edited.", category="success")
            return json.dumps({'success': True})
    return json.dumps({'success': False})

