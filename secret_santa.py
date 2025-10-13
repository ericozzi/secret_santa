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


def load_previous_santa_map():
    if os.path.exists(PREVIOUS_DERANGEMENT_FILE):
        with open(PREVIOUS_DERANGEMENT_FILE, "r") as f:
            previous_derangement_map = json.load(f)
            return list(previous_derangement_map.values())
    return None


def save_new_santa_map(santa_map):
    with open(PREVIOUS_DERANGEMENT_FILE, "w") as f:
        json.dump(dict(santa_map), f)


def main():

    secret_santas = list(USER_MAP.keys())
    recipient_emails = list(USER_MAP.values())

    previous_santa_map = load_previous_santa_map()

    # this call will ensure no one is their own secret santa
    # and no one has the same secret santa as last week
    family_members = derange_list(secret_santas, previous_santa_map)

    for secret_santa, recipient_email, family_member in zip(
        secret_santas, recipient_emails, family_members
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

    save_new_santa_map(zip(secret_santas, family_members))


if __name__ == "__main__":
    main()
