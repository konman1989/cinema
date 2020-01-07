def book_left_and_right_seat(schema: dict) -> dict or None:
    """Returns dictionary of requests body ready to be called to book
    left and right seats"""
    print(schema)
    try:
        request_body = {
            "left": {
                "command": "setorder",
                "params": "{\"cinemas\":\"%s\",\"sessions\":\"%s\","
                          "\"TicketTypes\":\"[{\\\"TicketTypeCode\\\":\\\"%s\\\","
                          "\\\"Qty\\\":\\\"1\\\",\\\"OptionalBarcode\\\":null}]\","
                          "\"SelectedSeats\":"
                          "\"[{\\\"AreaCategoryCode\\\":\\\"%s\\\","
                          "\\\"AreaNumber\\\":\\\"%d\\\",\\\"RowIndex\\\":\\\"%d\\\","
                          "\\\"ColumnIndex\\\":\\\"%d\\\"}]\"}" % (
                              schema['cinema_id'],
                              schema['cinema_session_id'],
                              schema['ticket_type'],
                              schema['area_category'],
                              schema['first_seat'].get('AreaNumber'),
                              schema['first_seat'].get('RowIndex'),
                              schema['first_seat'].get('ColumnIndex'),
                          ), "SessionId": f"{schema['user_session_id']}",
                "Client": "siteMX",
            }, "right": {
                "command": "setorder",
                "params": "{\"cinemas\":\"%s\",\"sessions\":\"%s\","
                          "\"TicketTypes\":\"[{\\\"TicketTypeCode\\\":\\\"%s\\\","
                          "\\\"Qty\\\":\\\"1\\\",\\\"OptionalBarcode\\\":null}]\","
                          "\"SelectedSeats\":"
                          "\"[{\\\"AreaCategoryCode\\\":\\\"%s\\\","
                          "\\\"AreaNumber\\\":\\\"%d\\\",\\\"RowIndex\\\":\\\"%d\\\","
                          "\\\"ColumnIndex\\\":\\\"%d\\\"}]\"}" % (
                              schema['cinema_id'],
                              schema['cinema_session_id'],
                              schema['ticket_type'],
                              schema['area_category'],
                              schema['last_seat'].get('AreaNumber'),
                              schema['last_seat'].get('RowIndex'),
                              schema['last_seat'].get('ColumnIndex'),
                          ),
                "SessionId": f"{schema['user_session_id']}",
                "Client": "siteMX"
            }, "front": {}, "back": {}
        }
        return request_body
    except KeyError:
        return
    except TypeError:
        return


def book_seats_front_back(seats: list, schema: dict, schema_front: dict,
                          schema_back: dict) -> dict or None:
    """Returns dictionary of requests body ready to be called to book
        front and back seats"""

    request_body = book_left_and_right_seat(schema)

    try:
        next_seat = 0
        for item in seats:
            request_body["front"].update(
                {item: {
                    "command": "setorder",
                    "params": "{\"cinemas\":\"%s\",\"sessions\":\"%s\","
                              "\"TicketTypes\":\"[{\\\"TicketTypeCode\\\":\\\"%s\\\","
                              "\\\"Qty\\\":\\\"1\\\",\\\"OptionalBarcode\\\":null}]\","
                              "\"SelectedSeats\":"
                              "\"[{\\\"AreaCategoryCode\\\":\\\"%s\\\","
                              "\\\"AreaNumber\\\":\\\"%d\\\",\\\"RowIndex\\\":\\\"%d\\\","
                              "\\\"ColumnIndex\\\":\\\"%d\\\"}]\"}" % (
                                  schema_front['cinema_id'],
                                  schema_front['cinema_session_id'],
                                  schema_front['ticket_type'],
                                  schema_front['area_category'],
                                  schema_front['first_seat'].get('AreaNumber'),
                                  schema_front['first_seat'].get('RowIndex'),
                                  schema_front['first_seat'].get(
                                      'ColumnIndex') + next_seat,
                              ),
                    "SessionId": f"{schema['user_session_id']}",
                    "Client": "siteMX"
                }})
            next_seat += 1
    except TypeError:
        pass
    try:
        next_seat = 0
        for item in seats:
            request_body["back"].update(
                {item: {
                    "command": "setorder",
                    "params": "{\"cinemas\":\"%s\",\"sessions\":\"%s\","
                              "\"TicketTypes\":\"[{\\\"TicketTypeCode\\\":\\\"%s\\\","
                              "\\\"Qty\\\":\\\"1\\\",\\\"OptionalBarcode\\\":null}]\","
                              "\"SelectedSeats\":"
                              "\"[{\\\"AreaCategoryCode\\\":\\\"%s\\\","
                              "\\\"AreaNumber\\\":\\\"%d\\\",\\\"RowIndex\\\":\\\"%d\\\","
                              "\\\"ColumnIndex\\\":\\\"%d\\\"}]\"}" % (
                                  schema_back['cinema_id'],
                                  schema_back['cinema_session_id'],
                                  schema_back['ticket_type'],
                                  schema_back['area_category'],
                                  schema_back['first_seat'].get('AreaNumber'),
                                  schema_back['first_seat'].get('RowIndex'),
                                  schema_back['first_seat'].get(
                                      'ColumnIndex') + next_seat,
                              ),
                    "SessionId": f"{schema['user_session_id']}",
                    "Client": "siteMX"
                }})
            next_seat += 1
    except TypeError:
        return
    finally:
        return request_body


