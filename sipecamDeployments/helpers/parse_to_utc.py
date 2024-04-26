from datetime import datetime, timezone


def parse_to_utc(date):
    """
    Given a string with the date to parse, converts
    the date to utc string that can be undertand by js.

    Parameters:
        date (string):  A string containing the date to parse.

    Returns:
        utc_date (string):  A string containing the date in utc
                            format compatible with js.
    """

    date_parsed = None
    date_ = date.replace(" ", "")
    try:
        try:
            date_parsed = datetime.strptime(date_, "%Y-%m-%dT%H:%M:%S.%f%z")
        except:
            date_str = date_[:-3] + date_[-2:]
            try:
                date_parsed = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            except:
                date_parsed = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
    except:
        try:
            date_parsed = datetime.strptime(date_, "%Y-%m-%dT%H:%M:%S%z")
        except:
            date_str = date[:-3] + date[-2:]
            date_parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f%z")

    return (
        date_parsed.astimezone(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        + "Z"
    )