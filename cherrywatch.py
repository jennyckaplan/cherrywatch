import requests
import os
import logging
import sys
from enum import Enum
from datetime import date
import re
import json
from bs4 import BeautifulSoup
from twilio.rest import Client
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            # the default formatter
            "default": {
                # for more formatting see https://docs.python.org/3/library/logging.html#logrecord-attributes  # noqa: E501
                "format": "%(asctime)s [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d - %(funcName)s()] - %(message)s",  # noqa: E501
            }
        },
        "handlers": {
            # log to the console
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            # set the fast api logger
            "fastapi": {
                # set handlers based on the config name
                "handlers": ["console"],
                "level": "INFO",
                # don't propagate to the root logger
                "propagate": False,
            },
        },
        # set the root logger
        "root": {"level": "INFO", "handlers": ["console"]},
    }
)

ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
RECIPIENTS = os.environ.get("RECIPIENTS")

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN

client = Client(account_sid, auth_token)


class BloomStage(Enum):
    prebloom = "Prebloom"
    first_bloom = "First Bloom"
    peak_bloom = "Peak Bloom"
    post_peak_bloom = "Post-Peak Bloom"


URL = "https://www.bbg.org/collections/cherries"
page = requests.get(URL)

soup = BeautifulSoup(page.text, "html.parser")
raw_html = soup.prettify()

script_with_tree_data = soup.find_all("script")[1].string.strip()

pattern = re.compile("var prunuses = ([\s\S]*);", re.MULTILINE)

prunuses = re.match(pattern, script_with_tree_data)
prunuses = prunuses.group(1)

# remove trailing comma
prunuses = re.sub(",[ \t\r\n]+\]", "]", prunuses)

prunuses = json.loads(prunuses)

bloom_stage_count = {
    BloomStage.prebloom.value: 0,
    BloomStage.first_bloom.value: 0,
    BloomStage.peak_bloom.value: 0,
    BloomStage.post_peak_bloom.value: 0,
}

update_message = ""
tree_count = len(prunuses)
update_message += "Welcome to Jen's Cherry Blossom Watch! \n\n"
update_message += (
    f"Out of the {tree_count} cherry blossom trees at the Brooklyn Botanic Garden,\n\n"
)
update_message += "Today,\n\n"

for tree in prunuses:
    bloom_stage = tree[7]
    bloom_stage_count[bloom_stage] += 1


def get_percentage(stage: BloomStage) -> float:
    return round(bloom_stage_count[stage.value] / tree_count * 100, 2)


def get_formatted_percentage(stage: BloomStage) -> str:
    percentage = get_percentage(stage)
    return f"{percentage}%"


for stage in BloomStage:
    percentage = get_formatted_percentage(stage)
    update_message += f"{percentage} are at {stage.value}\n"

today = date.today()
today = today.strftime("%-m-%-d-%Y")

recipients = RECIPIENTS.split(",")

try:
    for recipient in recipients:
        message = client.messages.create(
            to=recipient,
            from_=TWILIO_NUMBER,
            body=update_message,
            media_url=f"https://raw.githubusercontent.com/jennyckaplan/cherrywatch/main/images/{today}.png",
        )
except Exception as error:
    logging.info(f"ERROR: {error}")
    sys.exit(1)
