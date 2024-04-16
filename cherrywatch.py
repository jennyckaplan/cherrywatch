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
    
def get_scraped_tree_data():
    URL = "https://www.bbg.org/collections/cherries"
    page = requests.get(URL)

    soup = BeautifulSoup(page.text, "html.parser")

    script_with_tree_data = soup.find_all("script")[3].string.strip()

    pattern = re.compile("var prunuses = ([\s\S]*);", re.MULTILINE)

    prunuses = re.match(pattern, script_with_tree_data)
    prunuses = prunuses.group(1)

    # remove trailing comma
    prunuses = re.sub(",[ \t\r\n]+\]", "]", prunuses)

    prunuses = json.loads(prunuses)
    
    return prunuses


prunuses = get_scraped_tree_data()

update_message = "Welcome to Jen's Cherry Blossom Watch! \n\n"
update_message += "Today, at the Brooklyn Botanic Garden, "

kanzan_bloom_counts = defaultdict(int)
combined_other_bloom_counts = defaultdict(int)
total_kanzan = 0
total_others = 0

tree_types = set()

# Process the tree data
for tree in prunuses:
    tree_type = tree[3]
    tree_types.add(tree_type)
    bloom_stage = tree[7]
    if tree_type == "kanzan":
        kanzan_bloom_counts[bloom_stage] += 1
        total_kanzan += 1
    else:
        combined_other_bloom_counts[bloom_stage] += 1
        total_others += 1
        
# Remove 'kanzan' from the set and count the remaining types
tree_types.discard("kanzan")
non_kanzan_species_count = len(tree_types)

# Calculating percentages
kanzan_percentages = {
    stage: round((count / total_kanzan) * 100, 2)
    for stage, count in kanzan_bloom_counts.items()
}
other_percentages = {
    stage: round((count / total_others) * 100, 2)
    for stage, count in combined_other_bloom_counts.items()
}

update_message += "the Cherry Esplanade has begun blooming! \n"

desired_order = ['Prebloom', 'First Bloom', 'Peak Bloom', 'Post-Peak Bloom']

for stage in desired_order:
    if stage in kanzan_percentages:
        update_message += f"'{stage}': {kanzan_percentages[stage]}%\n"

update_message += f"\nThe remaining {non_kanzan_species_count} species are at the following bloom stages:\n"

for stage in desired_order:
    if stage in other_percentages:
        update_message += f"'{stage}': {other_percentages[stage]}%\n"

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
