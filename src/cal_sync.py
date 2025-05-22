# ✅ read iCloud calendar from yaml file
# ✅ download iCloud calendar
# filter events from iCloud calendar by tag
# download destination calendars from yaml file
# read downloaded file
# iterate through each calendar
# get events from the current calendar
# sync with iCloud

from pyicloud.pyicloud import PyiCloudService
from lib.yaml import YAMLConfig
from datetime import datetime, timedelta

cal_sync_config = YAMLConfig()
cal_sync_config.yaml_file = "cal_sync.yaml"

icloud_service = PyiCloudService(apple_id=cal_sync_config.read_yaml_setting("icloud-calendar", "user"), password=cal_sync_config.read_yaml_setting("icloud-calendar", "pass"))

if icloud_service.requires_2fa:
    code = input("Enter the security code: ")
    result = icloud_service.validate_2fa_code(code)

    if not result:
        print("Failed to verify security code")

    if not icloud_service.is_trusted_session:
        print("Session is not trusted. Requesting trust...")
        result = icloud_service.trust_session()
        print("Session trust result %s" % result)

        if not result:
            print("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

tmp_date = datetime.now().strftime("%Y-%m-%d")
# get events just for tomorrow
events_from = datetime.strptime(tmp_date, "%Y-%m-%d") + timedelta(days=1)
events_to = datetime.strptime(tmp_date, "%Y-%m-%d") + timedelta(days=1, hours=23, minutes=59, seconds=59)

with open("/Users/lrojas/Downloads/icloud_calendar.json", "w+") as ics_file:
    ics_file.write(str(icloud_service.calendar.get_events(from_dt=events_from, to_dt=events_to)))