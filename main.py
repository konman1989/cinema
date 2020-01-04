import re
import requests
import scrapy
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

link = 'https://gate.multiplex.ua/site/seats.html?CinemaId=0000000017&SessionId=139830&anchor=04012020&back_url=https://multiplex.ua/movie/353052#04012020'
row = 11
seat = 2


# TODO {\\\"AreaCategoryCode\\\":\\\"0000000001\\\" ????


def fetch_cinema_and_session_id(url: str) -> list:
    """Getting CinemaID, sessionID from the link provided"""

    pattern = re.compile(r"[0-9]+")
    result = re.findall(pattern, url)
    return result


def fetch_booked_seat_parameters(url: str, row: int, seat: int) -> list:
    """Finds out booked seat parameters (data-rowindex, data-areanumber,
    data-columnindex) and adds them to the list"""

    driver = webdriver.Chrome('/Users/konstantin/Downloads/chromedriver')
    with driver as d:
        d.get(url)
        wait = WebDriverWait(d, 10)
        wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'seat-close')))
        data = d.page_source

    soup = BeautifulSoup(data, "html.parser")
    seat_parameters = soup.find_all('div',
                                    {"data-place": seat, "data-row": row})

    pattern = re.compile(
        r'data-rowindex="[0-9]*"|data-areanumber="['
        r'0-9]*"|data-columnindex="[0-9]*"')

    result = re.findall(pattern, str(seat_parameters))
    result[1], result[2] = result[2], result[1]
    parameters_list = []

    for _ in result:
        result = (re.finditer(r"\d+", _))
        parameters_list.append(next(result).group(0))

    return parameters_list


def book_seats(url: str, row: int, seat: int) -> None:
    """Books seats every 7 minutes"""

    cinema_session_id = fetch_cinema_and_session_id(url)
    parameters = fetch_booked_seat_parameters(url, row, seat)

    request_body = {
        "command": "getseatsplan",
        "params": "{'cinemas':%s,'sessions':%s}" % (cinema_session_id[0],
                                                    cinema_session_id[1]),
        "SessionId": None,
        "Client": "siteMX"
    }
    data = requests.post(url, json=request_body)
    session_id = data.json().get('SessionId')

    seats_to_book = "[{\"TicketTypeCode\":\"0025\",\"Qty\":\"1\",\"OptionalBarcode\":null}," \
                    "{\"TicketTypeCode\":\"0025\",\"Qty\":\"1\",\"OptionalBarcode\":null}]'," \
                    "'SelectedSeats':" \
                    "'[{\"AreaCategoryCode\":\"0000000001\",\"AreaNumber\":\"%s\",\"RowIndex\":\"%s\",\"ColumnIndex\":\"%d\"}," \
                    "{\"AreaCategoryCode\":\"0000000001\",\"AreaNumber\":\"%s\",\"RowIndex\":\"%s\",\"ColumnIndex\":\"%d\"}]" % (
                        parameters[0], parameters[1], int(parameters[2]) - 1,
                        parameters[0], parameters[1], int(parameters[2]) + 1
                    )

    request_body = {
        "command": "setorder",
        "params": "{'cinemas':%s,'sessions':%s,'TicketTypes':'%s'}"
                  % (
                      cinema_session_id[0], cinema_session_id[1],
                      seats_to_book
                  ),
        "SessionId": f"{session_id}",
        "Client": "siteMX"
    }

    data = requests.post(url, json=request_body)
    print(data.text)


if __name__ == '__main__':
    book_seats(link, row, seat)
