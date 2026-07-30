import random
import time
import re
import smtplib
import os

from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
MY_EMAIL = os.getenv("MY_EMAIL")
PASSWORD = os.getenv("PASSWORD")


def read_csv(data):
    emails_with_pdfs = {}

    email_pattern = r"^[\w\.-]+@(edu\.hse\.ru|mail\.ru|google\.com|yandex\.ru)$"

    with open(data, encoding="utf-8") as file:
        for counter, row in enumerate(file, start=1):
            frame = row.strip().split(",")

            if len(frame) < 4:
                print(f"Строка {counter} повреждена")
                continue

            email = frame[0]
            name = frame[1]
            surname = frame[2]
            documents = frame[3:]

            if not re.match(email_pattern, email):
                print(f"{email} -> некорректный email, строка {counter}")
                continue

            emails_with_pdfs[email] = {
                "name": name,
                "surname": surname,
                "pdfs": documents
            }

    return emails_with_pdfs


def send_email(server, email, name, surname, pdfs, subject):
    msg = EmailMessage()

    msg["From"] = MY_EMAIL
    msg["To"] = email
    msg["Subject"] = subject

    msg.set_content(
        f"""
    Здравствуйте, {name} {surname}!

    Во вложении находятся Ваши документы.

    С уважением,
    Организационный отдел
    """
    )

    for pdf in pdfs:
        path = f"pdf_files/{pdf}"

        with open(path, "rb") as file_to_send:
            msg.add_attachment(
                file_to_send.read(),
                maintype="application",
                subtype="pdf",
                filename=pdf
            )

    server.send_message(msg)


def send_batch(batch, server):
    for email, data in batch:

        name = data["name"]
        surname = data["surname"]
        pdfs = data["pdfs"]

        print(f"\nОтправка для {email}")

        try:
            send_email(
            server,
            email,
            name,
            surname,
            pdfs,
            f"Документы для {name}"
            )       

            print(
                f"Письмо отправлено на {email}"
            )

        except Exception as e:
            print(
                f"Письмо не отправлено на {email}"
            )
            print(
                f"Причина: {e}"
            )

        finally:
            pause = random.randint(10, 30)

            print(
                f"Ожидание {pause} секунд..."
            )

            time.sleep(pause)


def split_batches(data, size):
    return [
        data[i:i + size]
        for i in range(0, len(data), size)
    ]


def main():

    data = "addresses.csv"

    emails_with_pdfs = read_csv(data)
    emails_list = list(emails_with_pdfs.items())

    BATCH_SIZE = 100

    batches = split_batches(
        emails_list,
        BATCH_SIZE
    )

    for number, batch in enumerate(batches, start=1):
        print(f"\nНачинаем партию №{number}")

        server = smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        )

        server.starttls()

        server.login(
            MY_EMAIL,
            PASSWORD
        )

        try:
            send_batch(
                batch,
                server
            )

        finally:
            server.quit()

        print(f"Партия №{number} завершена")

        if number < len(batches):
            batch_pause = random.randint(300, 900)

            print(f"Пауза {batch_pause} секунд")

            time.sleep(batch_pause)


if __name__ == "__main__":
    main()
