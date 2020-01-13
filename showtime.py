import re

import requests
from bs4 import BeautifulSoup


def fetch_cinema_and_session_id(data: dict) -> list:
    """Getting CinemaID, sessionID from the link provided"""

    request = requests.get(data.get('link')).content

    soup = BeautifulSoup(request, 'html.parser')
    cinema_num = ""
    for _ in soup.find_all('li'):
        if data.get('date') in str(_):
            cinema_num = _

    result = re.search(r'''data-selector="[0-9]*"''', str(cinema_num))

    data_anchor = re.search(r'\d+', result.group()).group()

    session_data = ''
    for _ in soup.find_all('div', {'data-anchor': data_anchor}):
        if data.get('time') in str(_):
            session_data = _

    result = re.search(r'\d+-\d+', str(session_data))
    session_data = result.group().split('-')
    link = f"https://gate.multiplex.ua/site/seats.html?CinemaId=" \
           f"{session_data[0]}&SessionId={session_data[1]}&anchor=" \
           f"{data_anchor}&back_url={data.get('link')}"

    session_data.append(link)

    return session_data
