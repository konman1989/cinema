import json
import re
import requests

from requests_body import book_left_and_right_seat, book_seats_front_back

# link = 'https://gate.multiplex.ua/site/seats.html?CinemaId=0000000017&SessionId=140062&anchor=07012020&back_url=https://multiplex.ua/movie/353052#07012020'
link = "https://gate.multiplex.ua/site/seats.html?CinemaId=0000000003&SessionId=72214&anchor=07012020&back_url=https://multiplex.ua/movie/353052#07012020"
user_row = 5
user_seats = [10, 11, 12]


def fetch_cinema_and_session_id(url: str) -> list:
    """Getting CinemaID, sessionID from the link provided"""

    pattern = re.compile(r"[0-9]+")
    result = re.findall(pattern, url)
    return result


def fetch_seats_schema(url: str, row: int, seats: list) -> dict or None:
    """Finds left and right seats to the booked ones"""

    cinema_session_id = fetch_cinema_and_session_id(url)

    request_body = {
        "command": "getseatsplan",
        "params": "{'cinemas':%s,'sessions':%s}" % (cinema_session_id[0],
                                                    cinema_session_id[1]),
        "SessionId": None,
        "Client": "siteMX"
    }
    data = requests.post(url, json=request_body)

    seats_schema = {
        'cinema_id': cinema_session_id[0],
        'cinema_session_id': cinema_session_id[1],
        'user_session_id': data.json().get('SessionId'),
        'seats_dict': json.loads(data.json().get('Data'))
    }

    seats_list = []
    for dict_ in seats_schema['seats_dict']["SeatLayoutData"]["Areas"]:
        for item in dict_['Rows']:
            if item.get('PhysicalName') == str(row) and len(
                    dict_['Rows'][0].get("Seats")) > 3:
                seats_list.extend(item.get('Seats'))
                seats_schema['area_category'] = dict_.get("AreaCategoryCode")
                seats_schema['ticket_type'] = dict_.get("TicketTypeCode")

    for dict_ in seats_schema['seats_dict']['SessionTickets']:
        if dict_.get('AreaCategoryCode') == seats_schema['area_category'] \
                and dict_.get('PriceInCents') > 0:
            seats_schema['ticket_type'] = dict_.get("TicketTypeCode")

    try:
        seats_schema['first_seat'] = [i.get('Position') for i in seats_list
                                      if i.get('Id') == str(min(seats) - 1)][0]
        seats_schema['last_seat'] = [i.get('Position') for i in seats_list
                                     if i.get('Id') == str(max(seats) + 1)][0]
    except IndexError:
        return

    seats_schema.pop('seats_dict', None)

    return seats_schema


def book_seats_non_greedy(url: str, row: int, seats: list) -> None or str:
    """Books 2 seats to the left and to the right every 7 minutes"""

    seats_schema = fetch_seats_schema(url, row, seats)
    request_body = book_left_and_right_seat(seats_schema)

    try:
        data = requests.post(url, json=request_body.get("left"))
        print(data.text)
        data = requests.post(url, json=request_body.get("right"))
        print(data.text)
    except AttributeError:
        return "Row or seat number is wrong"


def book_seats_greedy(url: str, row: int, seats: list) -> None or str:
    """Books seats all around the booked seats every 7 minutes"""

    seats_schema = fetch_seats_schema(url, row, seats)
    seats_schema_front = fetch_seats_schema(url, row - 1, seats)
    seats_schema_back = fetch_seats_schema(url, row + 1, seats)
    request_body = book_seats_front_back(seats, seats_schema,
                                         seats_schema_front,
                                         seats_schema_back)

    try:
        requests.post(url, json=request_body.get("left"))
        requests.post(url, json=request_body.get("right"))

        for _ in seats:
            requests.post(url, json=request_body.get("front").get(_))
            requests.post(url, json=request_body.get("back").get(_))
    except AttributeError:
        return "Row number is wrong"


if __name__ == '__main__':
    # book_seats_non_greedy(link, user_row, user_seats)
    book_seats_greedy(link, user_row, user_seats)
