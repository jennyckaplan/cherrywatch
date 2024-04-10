import requests
import html
import os
import logging
import sys
from enum import Enum
from datetime import date
from collections import defaultdict
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

script_with_tree_data = soup.find_all("script")[3].string.strip()

pattern = re.compile("var prunuses = ([\s\S]*);", re.MULTILINE)

prunuses = re.match(pattern, script_with_tree_data)
prunuses = prunuses.group(1)

# remove trailing comma
prunuses = re.sub(",[ \t\r\n]+\]", "]", prunuses)

prunuses = json.loads(prunuses)

bloom_counts = defaultdict(lambda: defaultdict(int))
total_counts = defaultdict(int)

update_message = ""
tree_count = len(prunuses)
update_message += "Welcome to Jen's Cherry Blossom Watch! \n\n"
update_message += "Today, at the Brooklyn Botanic Garden, the following cherries are at 80% or more peak bloom:\n\n"

tree_type_names = {}

def fix_encoding(text):
    fixed_text = text.encode('windows-1252', errors='ignore').decode('utf-8', errors='ignore')
    # Replace multiple spaces with a single space
    fixed_text = re.sub(r'\s+', ' ', fixed_text).strip()
    return fixed_text

for tree in prunuses:
    tree_type = tree[3]
    bloom_stage = tree[7]
    bloom_counts[tree_type][bloom_stage] += 1
    total_counts[tree_type] += 1
    tree_type_names[tree_type] = html.unescape(fix_encoding(tree[1]))
    
    
percentages = defaultdict(dict)

for tree_type in bloom_counts:
    for stage in BloomStage:
        stage_count = bloom_counts[tree_type].get(stage.value, 0)
        total_count = total_counts[tree_type]
        percentages[tree_type][stage.value] = round((stage_count / total_count) * 100, 2)

for tree_type, stages in percentages.items():
    peak_bloom_percentage = stages.get(BloomStage.peak_bloom.value, 0)
    if peak_bloom_percentage > 80:
        tree_type_name = tree_type_names.get(tree_type, "Unknown Type")
        update_message += f"\n{tree_type_name}:\n"
        update_message += f"Images: https://www.bbg.org/collections/cherry_stages#{tree_type}\n"
        update_message += f"Peak Bloom: {peak_bloom_percentage}%\n"

today = date.today()
today = today.strftime("%-m-%-d-%Y")

recipients = RECIPIENTS.split(",")

print(f"Message: {update_message}")

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
