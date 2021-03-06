import json

import bs4
import requests
from dateutil import tz
from flask import Blueprint, request, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from flask_socketio import emit

from . import db
from . import socketio
from .models import Note, User, Message

api = Blueprint('api', __name__)

friendly_subject_names = {
    "Homegroup": "Homegroup",
    "Art": "Art",
    "ComL": "ComLife",
    "Dram": "Drama",
    "Elec": "Electronics",
    "Eng": "English",
    "Farm": "Farming",
    "Huma": "Humanities",
    "Food": "Food Tech",
    "Germ": "German",
    "Math": "Maths",
    "Medi": "Media",
    "Musi": "Music",
    "OuEd": "Outdoor Ed",
    "Outdoor Edu": "Outdoor Ed",
    "PE": "PE",
    "Research": "Research Science",
    "RS": "Research Science",
    "Sci": "Science",
    "Sport": "Sport",
    "Vis": "VisCom",
    "Commerce": "Commerce",
    "Community Life": "ComLife"
}


# Returns basic 5 subject "today" timetable | LIST(HTML)
def get_timetable(response, current_user):
    if check_if_logged_out(response):
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

    if len(elements) == 0:
        return []

    return map(str, elements)


# Returns upcoming due work found on the homepage | LIST(HTML)
def get_upcoming_due_work(response, current_user):
    if check_if_logged_out(response):
        return "logout"

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    elements = []

    try:
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
            elif "class work" in tag.find("div").find_all()[2].text.lower():
                tag.find("div").find_all()[2].clear()
                tag.find("div").find_all()[2].append("Class Work")
            else:
                tag.find("div").find_all()[2].clear()
                tag.find("div").find_all()[2].append("Other")

            elements.append(tag)
        if len(elements) == 0:
            return None
        return map(str, elements)
    except AttributeError:
        return None


def check_if_logged_out(response):
    if "userNameInput.placeholder = 'Sample.User@donvale.vic.edu.au';" in response.text:
        return True
    return False


def check_if_down(response):
    if "<img src=\"/portrait.php?id=" in response.text:
        return True
    return False


# Returns whether a note is valid or not | BOOLEAN
def note_is_valid(note):
    if len(note) < 1 or note.isspace():
        flash("A note can not be empty.", category="error")
        return False
    elif len(note) > 1024:
        flash("This note is too long.", category="error")
        return False
    return True


def get_recent_messages(current_user):
    recent_messages = []
    for message in Message.query.all()[-100:]:
        if message.username == current_user.sbName:
            dates = convert_date(Message.query.filter_by(id=message.id).first().date)
            datetime = dates[0]
            fulldate = dates[1]
            recent_messages.append(
                {"id": message.id, "message": message.content, "username": message.username, "mine": True, "deleted": message.deleted, "datetime": datetime,
                 "fulldate": fulldate})
        else:
            dates = convert_date(Message.query.filter_by(id=message.id).first().date)
            datetime = dates[0]
            fulldate = dates[1]
            recent_messages.append(
                {"id": message.id, "message": message.content, "username": message.username, "mine": False, "deleted": message.deleted, "datetime": datetime,
                 "fulldate": fulldate})
    return recent_messages


from_zone = tz.tzutc()
to_zone = tz.tzlocal()


def convert_date(date):
    date = date.replace(tzinfo=from_zone)
    datetime = date.astimezone(to_zone)
    fulldate = datetime.strftime('%A, %-d %B %Y - %H:%M:%S')
    if datetime.date() == datetime.now().date():
        if current_user.setting_timestamp_hour_type == "24":
            datetime = datetime.strftime('%-H:%M')
        else:
            datetime = datetime.strftime('%-I:%M%p')
    else:
        datetime = datetime.strftime('%d/%m/%Y')
    return [datetime, fulldate]


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

    if len(Note.query.filter_by(userID=current_user.sbID).all()) >= 50:
        flash("You have reached the maximum of 50 notes.", category="error")
    elif note_is_valid(note):
        display_order = Note.query.filter_by(userID=current_user.sbID).count() + 1
        new_note = Note(content=note, userID=current_user.sbID, displayOrder=display_order)
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
    if setting_type == "timestamp-hour-type":
        if new_setting == "24" or new_setting == "12":
            valid_setting = True
            User.query.filter_by(sbID=current_user.sbID).update(dict(setting_timestamp_hour_type=new_setting))
            db.session.commit()
    if setting_type == "custom-javascript":
        if len(new_setting) < 2048:
            valid_setting = True
            User.query.filter_by(sbID=current_user.sbID).update(dict(customJavascript=new_setting.replace("\\n", "\n")))
            db.session.commit()
        else:
            flash("Custom Javascript can not be longer than 2048 characters.", category="error")

    if valid_setting and current_user.setting_alerts == "high":
        flash("Successfully updated setting.", category="success")

    return redirect(url_for('views.settings'))


@socketio.on('chatmessage', namespace='/discussion')
def chat_message(message):
    if current_user.is_authenticated and message['message']:
        if len(message['message']) > 1024:
            flash("This message is too long.", category="error")
            return
        if message['message'] == "" or str(message['message']).isspace():
            return
        message_store = Message(username=current_user.sbName, content=message['message'])
        db.session.add(message_store)
        db.session.commit()
        dates = convert_date(Message.query.filter_by(id=message_store.id).first().date)
        datetime = dates[0]
        fulldate = dates[1]
        emit('chatmessage', {"id": message_store.id, "message": message['message'], "username": current_user.sbName, "datetime": datetime, "fulldate": fulldate},
             broadcast=True)

        for connection in connections:
            if "@" + connection['sbName'].lower() in message['message'].lower():
                socketio.emit('messageAlert', {'mentioner': current_user.sbName}, room=connection['id'])


@socketio.on('deletemessage', namespace='/discussion')
def delete_message(id):
    if current_user.is_authenticated:
        message = Message.query.get(id)
        if message and message.username == current_user.sbName:
            Message.query.filter_by(id=message.id).update(dict(content="[message deleted]", deleted=True))
            db.session.commit()
            emit('deletemessage', {"id": id}, broadcast=True)


connections = []


@socketio.on('connect')
def connect():
    if current_user.is_authenticated:
        connections.append({'sbName': current_user.sbName, 'id': request.sid, 'sbID': current_user.sbID})


@socketio.on('disconnect')
def disconnect():
    for connection in connections:
        if connection['id'] == request.sid:
            connections.pop(connections.index(connection))


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
    for message in Message.query.all()[-int(start_from):][:int(amount)]:
        dates = convert_date(Message.query.filter_by(id=message.id).first().date)
        datetime = dates[0]
        fulldate = dates[1]
        recent_messages.append(
            {"id": message.id, "message": message.content, "username": message.username, "mine": message.username == current_user.sbName, "deleted": message.deleted,
             "datetime": datetime, "fulldate": fulldate})
    response = make_response(json.dumps(recent_messages), 200)
    response.mimetype = "text/plain"
    return response


@api.route("/update-note-display-order", methods=['POST'])
@login_required
def move_note():
    new_order = list(json.loads(request.data)['order'])
    legit_request = True
    for note in new_order:
        if Note.query.filter_by(id=note).first().userID != current_user.sbID:
            legit_request = False
    if legit_request:
        for i in range(len(new_order)):
            Note.query.filter_by(id=new_order[i]).update(dict(displayOrder=i + 1))
        db.session.commit()
        return json.dumps({'success': True})
    return json.dumps({'success': False})


@api.route("/get-alerts", methods=['GET'])
@login_required
def get_alerts():
    cookies = {
        'PHPSESSID': f'{current_user.sbCookie}',
    }

    response = requests.get("https://schoolbox.donvale.vic.edu.au/messages", cookies=cookies)

    if check_if_logged_out(response):
        return "logout"

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    elements = []

    for tag in soup.find(attrs={'id': 'content'}).find_all("li"):
        tag.name = "div"
        tag.find("div")["style"] = "padding: 10px; margin-bottom: 10px;"

        # remove the img tag
        tag.find("div").find("a").find("img").extract()

        # get parent of tag
        tag.find("div").find(attrs={'class': 'meta'}).find("time").string.replace_with(
            tag.parent.parent.find_previous_sibling('h2').string + " at " + tag.find("div").find(attrs={'class': 'meta'}).find("time").string)

        for atag in tag.find_all("a"):
            try:
                atag['href'] = "https://schoolbox.donvale.vic.edu.au" + atag['href']
                atag['style'] = "text-decoration: none;"
                atag['target'] = "_blank"
            except:
                continue

        elements.append(tag)
    if len(elements) == 0:
        return ""
    return "".join(list(map(str, elements)))
