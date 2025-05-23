# ✅ read iCloud calendar from yaml file
# ✅ download iCloud calendar
# filter events from iCloud calendar by tag
# download destination calendars from yaml file
# read downloaded file
# iterate through each calendar
# get events from the current calendar
# sync with iCloud

import icalendar
import urllib.request

from pyicloud.pyicloud import PyiCloudService
from lib.yaml import YAMLConfig
from datetime import datetime, timedelta

cal_sync_config = YAMLConfig()
cal_sync_config.yaml_file = "cal_sync.yaml"

icloud_service = PyiCloudService(apple_id=cal_sync_config.read_yaml_setting("icloud-calendar", "user"), password=cal_sync_config.read_yaml_setting("icloud-calendar", "pass"))

if icloud_service.requires_2fa:
    code = input("Enter the security code: ")
    result = icloud_service.validate_2fa_code(code)
    code = None

    if not result:
        print("Failed to verify security code")

    if not icloud_service.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = icloud_service.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
# get events just for tomorrow
events_from = datetime.strptime(tomorrow, "%Y-%m-%d")
events_to = datetime.strptime(tomorrow, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)

tomorrow_events = icloud_service.calendar.get_events(from_dt=events_from, to_dt=events_to)

fileICS = open(icsFile, "rb")
icalendar.Calendar.from_ical(fileICS.read())