import json
import re
import requests


link = 'https://gate.multiplex.ua/site/seats.html?CinemaId=0000000017&SessionId=139986&anchor=06012020&back_url=https://multiplex.ua/movie/353052#nothing'
user_row = 11
user_seat = 4


def fetch_cinema_and_session_id(url: str) -> list:
    """Getting CinemaID, sessionID from the link provided"""

    pattern = re.compile(r"[0-9]+")
    result = re.findall(pattern, url)
    return result


def book_seats(url: str, row: int, seat: int) -> None or str:
    """Books seats every 7 minutes"""

    cinema_session_id = fetch_cinema_and_session_id(url)

    request_body = {
        "command": "getseatsplan",
        "params": "{'cinemas':%s,'sessions':%s}" % (cinema_session_id[0],
                                                    cinema_session_id[1]),
        "SessionId": None,
        "Client": "siteMX"
    }
    data = requests.post(url, json=request_body)
    session_id = data.json().get('SessionId')

    seats = data.json().get('Data')
    seats_dict = json.loads(seats)
    area_category = ""
    seat_parameters = {}
    try:
        for dict_ in seats_dict["SeatLayoutData"]["Areas"]:
            for item in dict_["Rows"]:
                if item['PhysicalName'] == str(row):
                    seat_parameters = item['Seats'][seat - 1].get("Position")
                    area_category = dict_.get("AreaCategoryCode")
                    # ticket_type_code =
    except IndexError:
        return "Seat number is wrong"

    try:
        request_body = {
            "command": "setorder",
            "params": "{\"cinemas\":\"%s\",\"sessions\":\"%s\","
                      "\"TicketTypes\":\"[{\\\"TicketTypeCode\\\":\\\"0025\\\","
                      "\\\"Qty\\\":\\\"1\\\",\\\"OptionalBarcode\\\":null}]\","
                      "\"SelectedSeats\":"
                      "\"[{\\\"AreaCategoryCode\\\":\\\"%s\\\","
                      "\\\"AreaNumber\\\":\\\"%d\\\",\\\"RowIndex\\\":\\\"%d\\\","
                      "\\\"ColumnIndex\\\":\\\"%d\\\"}]\"}" % (
                          cinema_session_id[0], cinema_session_id[1],
                          area_category,
                          seat_parameters['AreaNumber'],
                          seat_parameters['RowIndex'],
                          seat_parameters['ColumnIndex'] + 1,
                      ),
            "SessionId": f"{session_id}",
            "Client": "siteMX"
        }
    except KeyError:
        return "Row number is wrong"

    data = requests.post(url, json=request_body)
    print(data.text)

    request_body = {
        "command": "setorder",
        "params": "{\"cinemas\":\"%s\",\"sessions\":\"%s\","
                  "\"TicketTypes\":\"[{\\\"TicketTypeCode\\\":\\\"0025\\\","
                  "\\\"Qty\\\":\\\"1\\\",\\\"OptionalBarcode\\\":null}]\","
                  "\"SelectedSeats\":"
                  "\"[{\\\"AreaCategoryCode\\\":\\\"%s\\\","
                  "\\\"AreaNumber\\\":\\\"%d\\\",\\\"RowIndex\\\":\\\"%d\\\","
                  "\\\"ColumnIndex\\\":\\\"%d\\\"}]\"}" % (
                      cinema_session_id[0], cinema_session_id[1],
                      area_category,
                      seat_parameters['AreaNumber'],
                      seat_parameters['RowIndex'],
                      seat_parameters['ColumnIndex'] - 1,
                  ),
        "SessionId": f"{session_id}",
        "Client": "siteMX"
    }

    data = requests.post(url, json=request_body)
    print(data.text)


if __name__ == '__main__':
    print(book_seats(link, user_row, user_seat))
