import csv

from .db import member


def seed_database():
    pass


def seed_demo(csv_file_path='./reisepass/database/seed.csv'):

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        # Specify delimiter as semicolon
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            # Extract values from the row (handling missing data with default values)
            code = row.get('vorname')[:2] \
                + row.get('nachname')[:2] \
                + row.get('geburtstag')[:2]
            vorname = row.get('vorname')
            nachname = row.get('nachname')
            geburtstag = row.get('geburtstag')
            groeße = row.get('groesse', "")

            # Create the member in the database
            # Since the CSV doesn't have all the details, we assume some defaults for "groeße" and handle possible None values
            m = member.create(
                code,
                vorname,
                nachname,
                geburtstag,
                groeße
            )
            print(f"Added {m.to_dict()}")
