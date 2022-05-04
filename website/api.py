from dataclasses import replace
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
import requests
import bs4
import json
from .models import Note
from . import db

api = Blueprint('api', __name__)  

def get_timetable(current_user):

    cookies = {
        'PHPSESSID': f'{current_user.sbCookie}',
    }

    response = requests.get("https://schoolbox.donvale.vic.edu.au", cookies=cookies)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    elements = []

    for tag in soup.find_all(attrs={'class': 'timetable-subject'}):
        tag['style'] += " width: 200px; padding: 10px; margin: 3px; display: inline-block; height: auto;"
        tag.find_all()[0]['style'] = "display: inline;"
        tag.find_all()[0]['href'] = "https://schoolbox.donvale.vic.edu.au" + tag.find_all()[0]['href']
        elements.append(tag)
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
def delete_note():
    note_id = json.loads(request.data)['note_id']
    note_content = json.loads(request.data)['note_content']
    note = Note.query.get(note_id)
    if note:
        if note.userID == current_user.sbID:
            db.session.delete(note)
            db.session.commit()
            flash("Note successfully edited.", category="success")
            return json.dumps({'success': True})
    return json.dumps({'success': False})

