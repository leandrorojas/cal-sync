# ✅ read iCloud calendar from yaml file
# ✅ download iCloud calendar
# filter events from iCloud calendar by tag
# download destination calendars from yaml file
# read downloaded file
# iterate through each calendar
# get events from the current calendar
# sync with iCloud

#import icalendar
import urllib.request
import logging

from pyicloud.pyicloud import PyiCloudService
from lib.yaml import YAMLConfig
from datetime import datetime, timedelta

#region CONSTS
YAML_SECTION_ICLOUD = "icloud-calendar"
YAML_KEY_ICLOUD_USER = "user"
YAML_KEY_ICLOUD_PASS = "pass"
YAML_SECTION_ORIGIN_CALENDAR = "origin-calendar-"
YAML_KEY_ORIGIN_CALENDAR_TAG = "tag"
YAML_KEY_ORIGIN_CALENDAR_URL = "url"
#endregion

#region LOGGER_SETTINGS
logger = logging.getLogger("cal-sync")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(name)s (%(levelname)s): %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
#endregion

cal_sync_config = YAMLConfig()
cal_sync_config.yaml_file = "cal_sync.yaml"

logger.info("connecting to iCloud")

try:
    # connect to iCloud using the credentials from the YAML file
    icloud_service = PyiCloudService(apple_id=cal_sync_config.read_yaml_setting(YAML_SECTION_ICLOUD, YAML_KEY_ICLOUD_USER), password=cal_sync_config.read_yaml_setting(YAML_SECTION_ICLOUD, YAML_KEY_ICLOUD_PASS))
except Exception as err:
    logger.error(f"Failed to connect to iCloud: {err}")
    exit(1)

# check if 2FA is required
if icloud_service.requires_2fa:
    # if it is, ask for the code
    code = input("Enter the security code: ")
    result = icloud_service.validate_2fa_code(code)
    # once entered, clean it
    code = None

    if not result:
        logger.error("Failed to verify security code")

    if not icloud_service.is_trusted_session:
        logger.info("Session is not trusted. Requesting trust...")
        result = icloud_service.trust_session()
        logger.info("Session trust result %s" % result)

        if not result:
            logger.warning("Failed to request trust. You will likely be prompted for the code again in the coming weeks")

# setup the dates to go find the events
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
# get events just for tomorrow
events_from = datetime.strptime(tomorrow, "%Y-%m-%d")
events_to = datetime.strptime(tomorrow, "%Y-%m-%d") + timedelta(hours=23, minutes=59, seconds=59)

# fetch tomorrow's events from iCloud calendar
logger.info("Getting tomorrow's events from iCloud calendar")
tomorrow_events = icloud_service.calendar.get_events(from_dt=events_from, to_dt=events_to)

logger.info("Getting origin calendars")

EoC = False
calendar_count = 0

# EoC = End of Calendars
while EoC == False:
    try:
        calendar_tag = cal_sync_config.read_yaml_setting(YAML_SECTION_ORIGIN_CALENDAR + str(calendar_count), YAML_KEY_ORIGIN_CALENDAR_TAG)
    except Exception as err:
        logger.error(f"Failed to read calendar {calendar_count} from YAML file: {err}")
        break

    if EoC == False:
        print(f"tag: {calendar_tag}")
        print(f"url: {cal_sync_config.read_yaml_setting(YAML_SECTION_ORIGIN_CALENDAR + str(calendar_count), YAML_KEY_ORIGIN_CALENDAR_URL)}")
    
    calendar_count += 1

# fileICS = open(icsFile, "rb")
# icalendar.Calendar.from_ical(fileICS.read())