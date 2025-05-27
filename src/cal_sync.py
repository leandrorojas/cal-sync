# ✅ read iCloud calendar from yaml file
# ✅ download iCloud calendar
# filter events from iCloud calendar by tag
# download destination calendars from yaml file
# read downloaded file
# iterate through each calendar
# get events from the current calendar
# sync with iCloud

import logging

from pyicloud.pyicloud import PyiCloudService
from datetime import datetime, timedelta

import lib.ics
from lib.yaml import YAMLConfig

#region CLASS_FORMATTER
class CustomFormatter(logging.Formatter): 
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    blue = "\x1b[34;20m"
    light_blue = "\x1b[36;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '[%(asctime)s] %(name)s (%(levelname)s): %(message)s'

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: light_blue + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
#endregion

#region FUNCTIONS
def is_friday(to_check):
    return to_check.weekday() == 4

def get_next_friday(to_check):
    return to_check + datetime.timedelta( (4-to_check.weekday()) % 7 )
#endregion

#region CONSTS
YAML_SECTION_ICLOUD = "icloud-calendar"
YAML_KEY_ICLOUD_USER = "user"
YAML_KEY_ICLOUD_PASS = "pass"
YAML_SECTION_ORIGIN_CALENDAR = "origin-calendar-"
YAML_KEY_ORIGIN_CALENDAR_TAG = "tag"
YAML_KEY_ORIGIN_CALENDAR_URL = "url"
YAML_KEY_ORIGIN_CALENDAR_TYPE = "type"
YAML_KEY_ORIGIN_CALENDAR_TEMP_FILE_NAME = "temp-file-name"

CALENDAR_TYPE_ICS = "ics"
CALENDAR_TYPE_GOOGLE_API = "google-api"
 
DATE_FORMAT_STRING = "%Y-%m-%d %Z"
#endregion

#region LOGGER_SETTINGS
logger = logging.getLogger("cal-sync")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
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


tomorrow = datetime.strptime("2025-05-27 -03", DATE_FORMAT_STRING).astimezone().strftime(DATE_FORMAT_STRING)

# setup the dates to go find the events
#tomorrow = (datetime.now().astimezone() + timedelta(days=1)).strftime(DATE_FORMAT_STRING)
# get events just for tomorrow
events_from = datetime.strptime(tomorrow, DATE_FORMAT_STRING).astimezone()
events_to = datetime.strptime(tomorrow, DATE_FORMAT_STRING).astimezone() + timedelta(hours=23, minutes=59, seconds=59)

# fetch tomorrow's events from iCloud calendar
logger.info("Getting tomorrow's events from iCloud calendar")
icloud_events = icloud_service.calendar.get_events(from_dt=events_from, to_dt=events_to)

logger.info("Getting origin calendars")

EoC = False
calendar_count = 0
there_was_an_error = False

# EoC = End of Calendars
while EoC == False:
    try:
        calendar_type = cal_sync_config.read_yaml_setting(YAML_SECTION_ORIGIN_CALENDAR + str(calendar_count), YAML_KEY_ORIGIN_CALENDAR_TYPE)
    except Exception as err:
        EoC = True

    if EoC == False:
        if (calendar_type == CALENDAR_TYPE_ICS):
            calendar_url = cal_sync_config.read_yaml_setting(YAML_SECTION_ORIGIN_CALENDAR + str(calendar_count), YAML_KEY_ORIGIN_CALENDAR_URL)

            logger.info(f"Downloading calendar [{calendar_count}] from {calendar_url}")

            try:
                temp_ics = lib.ics.download_calendar(calendar_url)
            except Exception as err:
                logger.error(f"Failed to download calendar [{calendar_count}]: {err}")
                there_was_an_error = True
                temp_ics = ""

            if there_was_an_error == False:
                logger.info(f"Filtering events [{calendar_count}] by date")
                ics_events = lib.ics.filter_events_by_date(temp_ics, events_from, events_to)

                calendar_tag = cal_sync_config.read_yaml_setting(YAML_SECTION_ORIGIN_CALENDAR + str(calendar_count), YAML_KEY_ORIGIN_CALENDAR_TAG)
                logger.info(f"Filtering iCloud events by tag {calendar_tag}")

                filtered_icloud_events = []
                
                for icloud_event in icloud_events:
                    if icloud_event["title"] == calendar_tag:
                        filtered_icloud_events.append(icloud_event)

                

        elif (calendar_type == CALENDAR_TYPE_GOOGLE_API):
            #TODO: implement Google API calendar
            pass

    calendar_count += 1

if there_was_an_error == True:
    logger.error("Opps, there was an error 😳. Sorry 😩")
else:
    logger.info("Completed 😘")