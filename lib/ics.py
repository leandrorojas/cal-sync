import urllib.request
import os
import uuid
import tempfile
import icalendar
import datetime
import sys

__ICS_FILE_EXTENSION = ".ics"

def download_calendar(url:str) -> str:
    try:
        calendar_remote_url = urllib.request.urlopen(url)
    except Exception as err:
        raise err

    if calendar_remote_url is not None:
        temp_dir = tempfile.gettempdir()
        temp_file_name = str(uuid.uuid4()) + __ICS_FILE_EXTENSION
        temp_full_path = os.path.join(temp_dir, temp_file_name)

        try:
            ics_file = open(temp_full_path, "wb")
            ics_file.write(calendar_remote_url.read())
            ics_file.close()
        except Exception as err:
            raise err

    return temp_full_path

def __normalize_date(date) -> datetime:
    return_date = date
    if isinstance(date, datetime.date):
        return_date = datetime.datetime.combine(date, datetime.time.min).astimezone()
    return return_date

def filter_events(ics_file, dt_from, dt_to) -> list:

    try:
        ical_file = open(ics_file, "r")
    except Exception as err:
        raise OSError(f"Failed to open file {ics_file}: {err}")
    
    try:
        calendar = icalendar.Calendar.from_ical(ical_file.read())
    except Exception as err:
        raise ValueError(f"Failed to read file {ical_file}: {err}")

    filtered_events = []
    event_count = 0
    
    for vevent in calendar.walk("vevent"):
        event_count += 1
        progress = (event_count / len(calendar.walk("vevent"))) * 100
        sys.stdout.write(f"walking calendar: {progress:.2f}%   \r")
        sys.stdout.flush()
        event_start = __normalize_date(vevent.get("dtstart").dt)
        event_end = __normalize_date(vevent.get("dtend").dt)
        if event_start >= dt_from and event_end <= dt_to:
            filtered_events.append(vevent)

    return filtered_events