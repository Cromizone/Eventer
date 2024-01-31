import argparse
from datetime import datetime
import logging

date = datetime.now()
argparser = argparse.ArgumentParser(prog="Eventer", description="A gnome utility to add historical or important events to system calendar")

argparser.add_argument('--verbose', '-v', action='store_true', help='Enable debug messages')
argparser.add_argument('--year', '-y', default=date.year, type=int, help='Filter events based on year, defaults to current year')
argparser.add_argument('--month', '-m', default='All', help='Filter results based on month, defaults to all months')
argparser.add_argument('--country', '-c', required=True, help='filter events based on your country')

args = argparser.parse_args()

if __name__ == "__main__":
    import extractor
    import register

    if not ['All', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'].__contains__(args.month):
        raise ValueError(f"'month' must be a value month not '{args.month}'")

    if not ['Australia', 'España', 'Argentina', 'India', 'Brasil', 'México', 'Canada', 'Perú', 'Chile', 'Portugal', 'Colombia', 'United Kingdom', 'Ecuador', 'United States'].__contains__(args.country):
        raise ValueError(f"please select on of this ['Australia', 'España', 'Argentina', 'India', 'Brasil', 'México', 'Canada', 'Perú', 'Chile', 'Portugal', 'Colombia', 'United Kingdom', 'Ecuador', 'United States'] as country")

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.info(f'fetching calendar metadata from source')
    calendar = extractor.getCalendarMetadata(args.month, args.year, args.country)

    if calendar == None: raise ValueError("Can't find calendar")
    logger.info(f'registering events from calendar metadata')

    for month_key in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']:
        
        if calendar.__getattribute__(month_key) == None:
            logger.warning(f'No data available for {month_key}:month')
            continue

        for dayIndex in calendar.__getattribute__(month_key):
            date = {"day" : calendar.__getattribute__(month_key)[dayIndex].index, "month" : calendar.__getattribute__(month_key)[dayIndex].month, "year" : calendar.year}

            for event in calendar.__getattribute__(month_key)[dayIndex].events:
                logger.debug(f'added `{event}` event to system calendar')
                register.register_event(event, date)
