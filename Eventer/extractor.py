from dataclasses import dataclass
import logging
import os
from typing import Any

import requests
from selectolax.parser import HTMLParser

logger = logging.getLogger(__name__)


@dataclass
class Day:
    index: int
    month: int
    year: int
    events: list[str]


@dataclass()
class Calendar:
    year: int
    January: dict[int, Day] | None = None
    February: dict[int, Day] | None = None
    March: dict[int, Day] | None = None
    April: dict[int, Day] | None = None
    May: dict[int, Day] | None = None
    June: dict[int, Day] | None = None
    July: dict[int, Day] | None = None
    August: dict[int, Day] | None = None
    September: dict[int, Day] | None = None
    October: dict[int, Day] | None = None
    November: dict[int, Day] | None = None
    December: dict[int, Day] | None = None


def read(filePath: str) -> str:
    with open(filePath, "r") as file:
        return file.read()


def getCalendarMetadata(month: str, year: int, country: str) -> Calendar:
    if os.path.exists("./page.html"):
        logger.info("using local file as source for calendar data")
        return parseDocument(read("./page.html"), month, year)

    logger.info("gathering calendar data from `www.calendarr.com`")

    country = country.replace(" ", "-").lower()
    respones = requests.get(f"https://www.calendarr.com/{country}/observances-{year}/")

    logger.debug("checking status code, expected status code is 200[ok]")
    respones.raise_for_status()

    logger.debug("passing document to parser")
    return parseDocument(respones.text, month, year)


def parseDocument(document: str, month: str, year: int) -> Calendar:
    logger.info("parsing HTML document")

    logger.debug("converting HTML document to python object")
    data = {}
    monthIndex = 0
    HTML = HTMLParser(document)

    logger.debug("selecting month nodes from HTML object")
    for monthNode in HTML.css(".holiday-month"):
        monthIndex += 1
        targetMonth = monthNode.text(False)

        if monthNode.next is None:
            logger.error("corrupt table structure")
            raise SyntaxError("Can't find associated HTML tag")

        logger.debug("selecting data container from month node")
        for container in monthNode.next.css(".list-holiday-box"):
            day = container.css_first(".holiday-day").text(False)
            event = container.css_first(".holiday-name").text(False)

            if day == "" or event == "":
                logger.error("Can't find required HTML tag")
                raise SyntaxError("Can't find HTML tag")

            if month.lower() == "all" or month.lower() == targetMonth:
                logger.debug(f"got extended data for {day}:day in {targetMonth}:month")

                if not data.__contains__(targetMonth):
                    data[targetMonth] = {}
                if not data[targetMonth].__contains__(day):
                    data[targetMonth][day] = {"month": monthIndex, "year": year, "events": []}

                data[targetMonth][day]["events"].append(event)

            else:
                logger.warn(f"ignoring data for {day}:day in {targetMonth}:month")

    return serializeData(year, data)


def serializeData(year: int, data: dict[str, dict[str, dict[str, Any]]]) -> Calendar:
    logger.info("serializing data[dict] into python objects")
    monthIndex = 0
    eventsObj = {}
    serialized = Calendar(year)

    for month in data:
        monthIndex += 1
        eventsObj = {}
        logger.info(f"serializing {month}:month into python objects")
        logger.debug(f"not serialized data: {data}")

        for index in range(1, 32):
            index = str(index).zfill(2)

            if not data[month].__contains__(index):
                logger.debug(f"Adding default dictionary structure to {index}:day in {month}:month")
                data[month][index] = {"month": monthIndex, "year": year, "events": []}

            eventsObj[int(index)] = Day(
                int(index),
                data[month][index]["month"],
                data[month][index]["year"],
                data[month][index]["events"],
            )
            logger.debug(f"python `day` objects contains {eventsObj}")

        logger.debug(f"Data of {month}:month has been serialized into python object")
        logger.debug(f"Data details [month: {month}, events : {eventsObj}]")
        serialized.__setattr__(month, eventsObj)

    logger.info("successfully gathered data for calendar")
    return serialized
