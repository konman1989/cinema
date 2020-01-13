import json
import requests

from requests_body import book_left_and_right_seat, book_seats_front_back
from showtime import fetch_cinema_and_session_id


user_data = {
    'link': 'https://multiplex.ua/movie/353005',
    'date': "15 января",
    'time': "21:55"
}

user_row = 10
user_seats = [14, 15, 16]


def fetch_seats_schema(data: dict, row: int,
                       seats: list) -> dict or None:
    """Finds left and right seats to the booked ones"""

    cinema_session_id = fetch_cinema_and_session_id(data)
    url = cinema_session_id[2]

    request_body = {
        "command": "getseatsplan",
        "params": "{'cinemas':%s,'sessions':%s}" % (cinema_session_id[0],
                                                    cinema_session_id[1]),
        "SessionId": None,
        "Client": "siteMX"
    }

    request = requests.post(url, json=request_body)
    seats_schema = {
        'cinema_id': cinema_session_id[0],
        'cinema_session_id': cinema_session_id[1],
        'user_session_id': request.json().get('SessionId'),
        'seats_dict': json.loads(request.json().get('Data')),
        'link': url
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
        if dict_.get('AreaCategoryCode') == seats_schema.get('area_category') \
                and dict_.get('PriceInCents') > 0:
            seats_schema['ticket_type'] = dict_.get("TicketTypeCode")

    list_ = []
    for index, i in enumerate(seats_list):
        if int(i.get('Id')) in seats:
            list_.append(index)
    seats_schema['seats_list'] = dict(zip(seats, list_))

    try:
        seats_schema['first_seat'] = [i.get('Position') for i in seats_list
                                      if i.get('Id') == str(min(seats) - 1)][0]
        seats_schema['last_seat'] = [i.get('Position') for i in seats_list
                                     if i.get('Id') == str(max(seats) + 1)][0]
    except IndexError:
        return

    seats_schema.pop('seats_dict', None)

    return seats_schema


def book_seats_non_greedy(data: dict, row: int,
                          seats: list) -> None or str:
    """Books 2 seats to the left and to the right every 7 minutes"""

    seats_schema = fetch_seats_schema(data, row, seats)
    request_body = book_left_and_right_seat(seats_schema)
    url = seats_schema.get('link')

    try:
        requests.post(url, json=request_body.get("left"))
        requests.post(url, json=request_body.get("right"))
    except AttributeError:
        return "Row or seat number is wrong"


def book_seats_greedy(data: dict, row: int,
                      seats: list) -> None or str:
    """Books seats all around the booked seats every 7 minutes"""

    seats_schema = fetch_seats_schema(data, row, seats)
    url = seats_schema.get('link')
    seats_schema_front = fetch_seats_schema(data, row - 1, seats)
    seats_schema_back = fetch_seats_schema(data, row + 1, seats)
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
    # book_seats_non_greedy(user_data, user_row, user_seats)
    book_seats_greedy(user_data, user_row, user_seats)

