#!/usr/bin/env python3

import os
import json
import random
import smtplib

from envs import APP_PASSWORD, USER_MAP
from email.mime.text import MIMEText

PREVIOUS_DERANGEMENT_FILE = "previous_derangement.json"


def derange_list(user_list, previous_list=None):
    """
    Randomizes a list such that no element remains in its original position.
    This function shuffles the list repeatedly until a derangement is found.
    """
    if not user_list:
        return []

    # Create a copy to avoid modifying the original during checks
    shuffled_list = list(user_list)

    while True:
        while any(shuffled_list[i] == user_list[i] for i in range(len(user_list))):
            random.shuffle(shuffled_list)

        if previous_list:
            # Ensure that everyone has a different recipient than last time
            if any(
                shuffled_list[i] == previous_list[i] for i in range(len(previous_list))
            ):
                random.shuffle(shuffled_list)
                continue

        break

    return shuffled_list


def send_email(subject, body, sender, recipients):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(sender, APP_PASSWORD)
        smtp_server.sendmail(sender, recipients, msg.as_string())


def send_email_test(subject, body, sender, recipients):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)

    print(msg.as_string())


def load_list_of_santa_maps():
    if os.path.exists(PREVIOUS_DERANGEMENT_FILE):
        with open(PREVIOUS_DERANGEMENT_FILE, "r") as f:
            list_of_santa_maps = json.load(f)
            return list(list_of_santa_maps)
    return None


def load_previous_santa_map():
    list_of_santa_maps = load_list_of_santa_maps()
    if list_of_santa_maps:
        previous_santa_map = list_of_santa_maps[-1]
        return previous_santa_map
    return {}


def get_recipients_from_santa_map(previous_santa_map:dict[str, str]):
    if previous_santa_map:
        previous_recipients = list(previous_santa_map.values())
        return previous_recipients
    return []


def save_new_santa_map(new_santa_map):
    list_of_santa_maps = load_list_of_santa_maps()
    if not list_of_santa_maps:
        list_of_santa_maps = []
    list_of_santa_maps.append(dict(new_santa_map))
    with open(PREVIOUS_DERANGEMENT_FILE, "w") as f:
        json.dump(list(list_of_santa_maps), f, indent=4)


def main():

    secret_santas = list(USER_MAP.keys())
    recipient_emails = list(USER_MAP.values())

    previous_santa_map = load_previous_santa_map()
    previous_recipients_list = get_recipients_from_santa_map(previous_santa_map)

    new_recipients_list = derange_list(secret_santas, previous_recipients_list)

    if False:
        for secret_santa, recipient_email, family_member in zip(
            secret_santas, recipient_emails, new_recipients_list
        ):
            send_email(
                subject="Cozzi Secret Santa",
                body=f"{secret_santa}, you are secret santa for {family_member} this coming week. Use the document here to record and see Secret Santa ideas: https://docs.google.com/document/d/1VWQvmUEsggtSWMkpB7U1d8athg7qmb3w86-yT94Ja0c/edit?usp=sharing",
                sender="eric@cozzi.us",
                recipients=[
                   recipient_email,
                ],
            )
            print(f"Emailed {secret_santa}.")

    new_santa_map = dict(zip(secret_santas, new_recipients_list))
    save_new_santa_map(new_santa_map)


if __name__ == "__main__":
    main()
