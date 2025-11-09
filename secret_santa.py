#!/usr/bin/env python3

import os
import json
import random
import smtplib

from envs import APP_PASSWORD, USER_MAP
from email.mime.text import MIMEText

PREVIOUS_DERANGEMENT_FILE = "previous_derangement.json"
DEFAULT_CHECK_HISTORICAL_DEPTH = 2


def check_historical_derangements(user_list, historical_derangements):
    """
    Checks if the current derangement has occurred in previous derangements.
    """
    # print(f"{user_list=}")

    from pprint import pprint

    pprint(historical_derangements)
    if historical_derangements is not None:
        check_historical_depth = min(
            DEFAULT_CHECK_HISTORICAL_DEPTH, len(historical_derangements)
        )
        for d in range(check_historical_depth):
            derangement = list(historical_derangements[-(d + 1)].values())
            # print(f"Checking against historical derangement {d} of {len(historical_derangements)}: {derangement}")
            if any(
                user_list[i - 1] == derangement[i - 1] for i in range(len(user_list))
            ):
                # print("Match found with historical derangement.")
                return False
        # print("No matches found with historical derangements.")
        return True
    # print("No historical derangements to check against.")
    return True


def derange_list(user_list, historical_assignments=None):
    """
    Randomizes a list such that no element remains in its original position.
    This function shuffles the list repeatedly until a derangement is found.
    """
    random.seed()
    # print(f"{user_list=}")
    if not user_list:
        return []

    # Create a copy to avoid modifying the original during checks
    shuffled_list = user_list.copy()
    # random.shuffle(shuffled_list)
    # print(f"{user_list=}")
    # print(f"{shuffled_list=}")

    while True:
        for _ in range(random.randint(1, 100)):
            random.shuffle(shuffled_list)

        while any(shuffled_list[i] == user_list[i] for i in range(len(user_list))):
            for _ in range(random.randint(1, 100)):
                random.shuffle(shuffled_list)

        # print(f"trying {shuffled_list=}")

        if check_historical_derangements(shuffled_list, historical_assignments):
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


def load_previous_santa_map(list_of_santa_maps=None):
    if list_of_santa_maps:
        previous_santa_map = list_of_santa_maps[-1]
        return previous_santa_map
    return {}


def get_recipients_from_santa_map(previous_santa_map: dict[str, str]):
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

    list_of_santa_maps = load_list_of_santa_maps()
    previous_santa_map = load_previous_santa_map(list_of_santa_maps)
    previous_recipients_list = get_recipients_from_santa_map(previous_santa_map)

    new_recipients_list = derange_list(secret_santas, list_of_santa_maps)

    if True:
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


def test():
    from pprint import pprint
    from prettytable import PrettyTable

    historical = []
    users = USER_MAP.copy()
    for _ in range(20):
        secret_santas = list(users.keys())
        # pprint(historical, indent=4)
        new_recipients_list = derange_list(secret_santas, historical)
        new_santa_map = dict(zip(secret_santas, new_recipients_list))
        # pprint(new_santa_map, sort_dicts=False, indent=4)
        historical.append(new_santa_map)

    table = PrettyTable(users.keys())
    for derangement in historical:
        row = [derangement[user] for user in users.keys()]
        table.add_row(row)

    print(table)


if __name__ == "__main__":
    # test()
    main()
