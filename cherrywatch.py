import json
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import date
from logging.config import dictConfig

import requests
from bs4 import BeautifulSoup
from twilio.rest import Client


dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d - %(funcName)s()] - %(message)s",
            }
        },
        "handlers": {
            "console": {
                "level": "INFO",
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
)

ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")
RECIPIENTS = os.environ.get("RECIPIENTS")

URL = "https://www.bbg.org/collections/cherries"
REQUEST_TIMEOUT_SECONDS = 30
MEDIA_REQUEST_TIMEOUT_SECONDS = 10
PRUNUSES_PATTERN = re.compile(r"var prunuses = (\[.*?\]);", re.DOTALL)
DESIRED_ORDER = ["Prebloom", "First Bloom", "Peak Bloom", "Post-Peak Bloom"]


def extract_prunuses_script(soup):
    for script in soup.find_all("script"):
        script_content = script.string or script.get_text()
        if script_content and "var prunuses =" in script_content:
            return script_content

    raise ValueError("Could not find the BBG prunuses data script on the page.")


def parse_prunuses(script_with_tree_data):
    match = PRUNUSES_PATTERN.search(script_with_tree_data)
    if not match:
        raise ValueError("Could not parse the BBG prunuses array from the page.")

    prunuses = match.group(1)
    prunuses = re.sub(r",[ \t\r\n]+\]", "]", prunuses)
    return json.loads(prunuses)


def get_scraped_tree_data():
    response = requests.get(
        URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
        headers={"User-Agent": "cherrywatch/1.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    script_with_tree_data = extract_prunuses_script(soup)
    prunuses = parse_prunuses(script_with_tree_data)
    logging.info("Scraped %s cherry tree rows from BBG.", len(prunuses))
    return prunuses


def build_update_message(prunuses):
    kanzan_bloom_counts = defaultdict(int)
    combined_other_bloom_counts = defaultdict(int)
    total_kanzan = 0
    total_others = 0
    tree_types = set()

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

    tree_types.discard("kanzan")
    non_kanzan_species_count = len(tree_types)

    kanzan_percentages = {
        stage: round((count / total_kanzan) * 100, 2)
        for stage, count in kanzan_bloom_counts.items()
    }
    other_percentages = {
        stage: round((count / total_others) * 100, 2)
        for stage, count in combined_other_bloom_counts.items()
    }

    update_message = "Welcome to Jen's Cherry Blossom Watch! \n\n"
    update_message += "Today, at the Brooklyn Botanic Garden, "
    peak_bloom_percentage = kanzan_percentages.get("Peak Bloom", 0)
    if peak_bloom_percentage >= 80:
        update_message += "the double-blossom Kanzan trees on Cherry Esplanade and Cherry Walk are at peak bloom! 🚨\n"
    else:
        update_message += (
            "the double-blossom Kanzan trees on Cherry Esplanade and Cherry Walk "
            "are at the following bloom stages:\n"
        )

    for stage in DESIRED_ORDER:
        if stage in kanzan_percentages:
            update_message += f"'{stage}': {kanzan_percentages[stage]}%\n"

    update_message += (
        f"\nThe remaining {non_kanzan_species_count} species are at the following bloom stages:\n"
    )

    for stage in DESIRED_ORDER:
        if stage in other_percentages:
            update_message += f"'{stage}': {other_percentages[stage]}%\n"

    return update_message


def get_recipients():
    if not RECIPIENTS:
        raise ValueError("RECIPIENTS is not set.")

    recipients = [recipient.strip() for recipient in RECIPIENTS.split(",") if recipient.strip()]
    if not recipients:
        raise ValueError("RECIPIENTS does not contain any valid phone numbers.")

    return recipients


def get_twilio_client():
    missing_vars = [
        env_name
        for env_name, value in {
            "ACCOUNT_SID": ACCOUNT_SID,
            "AUTH_TOKEN": AUTH_TOKEN,
            "TWILIO_NUMBER": TWILIO_NUMBER,
        }.items()
        if not value
    ]

    if missing_vars:
        raise ValueError(f"Missing required Twilio env vars: {', '.join(missing_vars)}")

    return Client(ACCOUNT_SID, AUTH_TOKEN)


def get_media_url():
    today = date.today().strftime("%-m-%-d-%Y")
    media_url = f"https://raw.githubusercontent.com/jennyckaplan/cherrywatch/main/images/{today}.png"

    try:
        response = requests.get(media_url, timeout=MEDIA_REQUEST_TIMEOUT_SECONDS, stream=True)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            logging.warning(
                "Skipping media URL because content type was not an image: %s",
                content_type,
            )
            return None
        return media_url
    except requests.RequestException as error:
        logging.warning("Skipping media URL because it is not available yet: %s", error)
        return None
    finally:
        if "response" in locals():
            response.close()


def send_notifications(update_message):
    client = get_twilio_client()
    recipients = get_recipients()
    media_url = get_media_url()

    logging.info("Sending update to %s recipient(s).", len(recipients))
    logging.info("Message: %s", update_message)

    for recipient in recipients:
        message_options = {
            "to": recipient,
            "from_": TWILIO_NUMBER,
            "body": update_message,
        }
        if media_url:
            message_options["media_url"] = media_url

        client.messages.create(**message_options)


def main():
    prunuses = get_scraped_tree_data()
    update_message = build_update_message(prunuses)
    send_notifications(update_message)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logging.exception("ERROR: %s", error)
        sys.exit(1)
