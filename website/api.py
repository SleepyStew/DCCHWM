from dataclasses import replace
import requests
import bs4
import brython

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