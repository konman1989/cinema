import re

import requests
from bs4 import BeautifulSoup


def fetch_cinema_and_session_id(data: dict) -> list:
    """Getting CinemaID, sessionID from the link provided"""

    request = requests.get(data.get('link')).content

    soup = BeautifulSoup(request, 'html.parser')

    # fetching cinema_id using cinema name
    result = soup.find('div', {'data-name': data.get('cinema')})
    cinema_id = re.search(r'\d+', str(result)).group()

    # fetching data id using date provided
    data_selector = ""
    for _ in soup.find_all('li'):
        if data.get('date') in str(_):
            data_selector = _

    result = re.search(r'''data-selector="[0-9]*"''', str(data_selector))

    data_anchor = re.search(r'\d+', result.group()).group()

    # fetching session id and data id
    session_data = ''
    for _ in soup.find_all('div', {'data-anchor': data_anchor}):
        if data.get('time') in str(_) and cinema_id in str(_):
            session_data = _

    result = re.search(r'\d+-\d+', str(session_data))
    session_data = result.group().split('-')

    link = f"https://gate.multiplex.ua/site/seats.html?CinemaId=" \
           f"{session_data[0]}&SessionId={session_data[1]}&anchor=" \
           f"{data_anchor}&back_url={data.get('link')}"

    session_data.append(link)

    return session_data
