import urllib.request
import os
import uuid
import tempfile
import icalendar

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

def filter_events(ics_file, dt_from, dt_to) -> list:

    #TODO: raise different exceptions for opening file and for reading file with icalendar
    try:
        ical_file = open(ics_file, "r")
    except Exception as err:
        raise err
    
    try:
        calendar = icalendar.Calendar.from_ical(ical_file.read())
    except Exception as err:
        raise err

    filtered_events = []
    
    for component in calendar.walk("vevent"):
        event_start = component.get("dtstart").dt
        event_end = component.get("dtend").dt
        if event_start >= dt_from and event_end <= dt_to:
            filtered_events.append(component)

    return filtered_events