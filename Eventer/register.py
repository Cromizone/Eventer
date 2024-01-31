import uuid
import datetime
import logging

logger = logging.getLogger(__name__)

template = "BEGIN:VEVENT\nUID:{uuid}\nDTSTAMP:{timestamp}\nDTSTART;VALUE=DATE:{start_date}\nDTEND;VALUE=DATE:{end_date}\nSUMMARY:{message}\nSEQUENCE:1\nCREATED:{timestamp}\nLAST-MODIFIED:{timestamp}\nEND:VEVENT\n"

def register_event(message : str, date : dict[str, int]) -> None:
    logger.info(f'registering `{message}`:event in system calendar')

    logger.debug('opening system calendar file')
    with open('~/.local/share/evolution/calendar/system/calendar.ics', "r+") as calendar_metadata:
        event_uuid = uuid.uuid4().hex + uuid.uuid4().hex[:8]
        time_stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") 

        start = f"{date['year']}{str(date['month']).zfill(2)}{str(date['day']).zfill(2)}"
        end = f"{date['year']}{str(date['month']).zfill(2)}{str(date['day']+1).zfill(2)}"

        logger.debug('generating system calendar entry')
        entry = template.format(uuid=event_uuid, timestamp=time_stamp, start_date=start, end_date=end, message=message)
        
        logger.debug('reading system calendar file')
        content = calendar_metadata.read()
        calendar_metadata.seek(0)

        logger.debug('removing last line')
        content = content[:-14]

        logger.debug('writing to system calendar file')
        calendar_metadata.write(f"{content}\n{entry}END:VCALENDAR")

    logger.info('registered event')
