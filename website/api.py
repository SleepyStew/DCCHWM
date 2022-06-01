from dataclasses import replace
from re import S, sub
from unicodedata import category
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, make_response
from flask_login import login_user, login_required, logout_user, current_user
import requests
import bs4
import json
from .models import Note, User, Message
from . import db
import markdown
import re
from flask_socketio import SocketIO, emit
from . import socketio
import sys
from . import app
from dateutil import tz
from datetime import datetime

api = Blueprint('api', __name__)  

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
    "Outdoor Edu": "Outdoor Ed",
    "PE": "PE",
    "RS": "Research Science",
    "Sci": "Science",
    "Sport": "Sport",
    "Vis": "VisCom",
    "Community Life": "ComLife"
}

# Returns basic 5 subject "today" timetable | LIST(HTML)
def get_timetable(response, current_user):

    if "userNameInput.placeholder = 'Sample.User@donvale.vic.edu.au';" in response.text:
        return "logout"

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
            elements.append(tag)
        except:
            elements.append(tag)

    return map(str, elements)

# Returns upcoming due work found on the homepage | LIST(HTML)
def get_upcoming_due_work(response, current_user):

    if "userNameInput.placeholder = 'Sample.User@donvale.vic.edu.au';" in response.text:
        return "logout"

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    elements = []
    
    for tag in soup.find(attrs={'id': 'component52396'}).find("div").find("div").find("section").find("ul").find_all("li"):
        tag.name = "div"
        tag.find("div")["style"] = "padding: 10px; margin-bottom: 10px;"
        tag.find("div").find_all()[0]["style"] = "font-size: 22px;"
        tag.find("div").find_all()[1]["style"] = "font-size: 18px;"
        tag.find("div").find_all()[2]["style"] = "font-size: 15px;"

        tag.find("div").find_all()[0].find("a")['href'] = "https://schoolbox.donvale.vic.edu.au" + tag.find("div").find_all()[0].find("a")['href']
        tag.find("div").find_all()[0].find("a")['style'] = "text-decoration: none;"
        tag.find("div").find_all()[0].find("a")['target'] = "_blank"

        for subject, subject_value in friendly_subject_names.items():
            if subject in tag.find("div").find_all()[2].text:
                tag.find("div").find_all()[0].string.replace_with(subject_value + " - " + tag.find("div").find_all()[0].text)
                break

        if "homework" in tag.find("div").find_all()[2].text.lower():
            tag.find("div").find_all()[2].clear()
            tag.find("div").find_all()[2].append("Homework")
        elif "assessment" in tag.find("div").find_all()[2].text.lower():
            tag.find("div").find_all()[2].clear()
            tag.find("div").find_all()[2].append("Assessment Task")
        else:
            tag.find("div").find_all()[2].clear()
            tag.find("div").find_all()[2].append("Other")

        elements.append(tag)

    return map(str, elements)

# Returns whether a note is valid or not | BOOLEAN
def note_is_valid(note):
    if len(note) < 1 or note.isspace():
        flash("A note can not be empty.", category="error")
        return False
    elif len(note) > 1024:
        flash("This note is too long.", category="error")
        return False
    return True

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
    note_content = json.loads(request.data)['note_content'].strip()
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
    note = request.form.get('note').strip()

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
    if setting_type == "deleted-messages":
        if new_setting == "hide" or new_setting == "show":
            valid_setting = True
            User.query.filter_by(sbID=current_user.sbID).update(dict(setting_deleted_messages=new_setting))
            db.session.commit()
    
    if valid_setting and current_user.setting_alerts == "high":
        flash("Successfully updated setting.", category="success")

    return redirect(url_for('views.settings'))

@socketio.on('chatmessage')
def chat_message(message):
    if current_user.is_authenticated and message['message']:
        if len(message['message']) > 1024:
            flash("This message is too long.", category="error")
            return
        if message['message'] == "" or str(message['message']).isspace():
            return
        message['message'] = message['message'].replace('\n', ' ')
        message_store = Message(username=current_user.sbName, content=message['message'])
        db.session.add(message_store)
        db.session.commit()
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        utc = Message.query.filter_by(id=message_store.id).first().date
        utc = utc.replace(tzinfo=from_zone)
        central = utc.astimezone(to_zone)
        emit('chatmessage', {"id": message_store.id, "message": message['message'], "username": current_user.sbName, "datetime": central.strftime('%H:%M')}, broadcast=True)

@socketio.on('deletemessage')
def delete_message(id):
    if current_user.is_authenticated:
        message = Message.query.get(id)
        if message and message.username == current_user.sbName:
            Message.query.filter_by(id=message.id).update(dict(content="[message deleted]", deleted=True))
            db.session.commit()
            emit('deletemessage', {"id": id}, broadcast=True)

@api.route("/get-more-messages", methods=['GET'])
@login_required
def get_more_messages():
    args = request.args
    if not args or not args.get("amount") or not args.get("from"):
        return json.dumps({'success': False, 'error': 'invalid arguments'})
    recent_messages = []
    amount = args.get("amount")
    start_from = args.get("from")
    if len(Message.query.all()) + int(amount) < int(start_from):
        return json.dumps({})
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    for message in Message.query.all()[-int(start_from):][:int(amount)]:
        if message.username == current_user.sbName:
            utc = Message.query.filter_by(id=message.id).first().date
            utc = utc.replace(tzinfo=from_zone)
            central = utc.astimezone(to_zone)
            if central.date() == datetime.now().date():
                central = central.strftime('%H:%M')
            else:
                central = central.strftime('%d/%m/%Y')
            recent_messages.append({"id": message.id, "message": message.content, "username": message.username, "mine": True, "deleted": message.deleted, "datetime": central})
        else:
            utc = Message.query.filter_by(id=message.id).first().date
            utc = utc.replace(tzinfo=from_zone)
            central = utc.astimezone(to_zone)
            if central.date() == datetime.now().date():
                central = central.strftime('%H:%M')
            else:
                central = central.strftime('%d/%m/%Y')
            recent_messages.append({"id": message.id, "message": message.content, "username": message.username, "mine": False, "deleted": message.deleted, "datetime": central})
    response = make_response(json.dumps(recent_messages), 200)
    response.mimetype = "text/plain"
    return response