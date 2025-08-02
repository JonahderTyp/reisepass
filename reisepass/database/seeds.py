import csv
import os
import random

from .db import member, stufe


def seed_database():
    stufe.create_new("Wölfling")
    stufe.create_new("Juffi")
    stufe.create_new("Pfadi")
    stufe.create_new("Rover")
    stufe.create_new("Leiter")


def seed_csv(csv_file_path='./instance/seed.csv'):
    if not os.path.exists(csv_file_path):
        print(f"CSV file '{csv_file_path}' not found. Skipping seeding.")
        return

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')

        for row in reader:
            vorname = row.get('Vorname')
            nachname = row.get('Nachname')
            geburtstag = row.get('Geburtstag')
            gruppe = row.get('Gruppe', "")
            beruf = row.get('Beruf')
            if not beruf:
                beruf = generiere_pfadfinder_beruf()

            s = stufe.get_via_name(gruppe)

            m = member.create_new(
                vorname=vorname,
                nachname=nachname,
                geburtstag=geburtstag,
                jsondata={"beruf": beruf},
                stufe=s,
            )
            print(f"Added {m.to_dict()}")


def generiere_pfadfinder_beruf():
    komponenten_1 = [
        "Lagerfeuer", "Wimpel", "Zelt", "Wald", "Knoten", "Kakao", "Wander", "Schnitzel", "Abspanner",
        "Pfadfinder", "Feuerholz", "Zeltplatz", "Rucksack",
        "Kompass", "Socken", "Holz", "Seil", "Regenponcho", "Ameisen",
        "Wanderstiefel", "Stockbrot", "Tassen", "Schlammpfützen", "Mücken", "Kochtopf", "Plumpsklo"
    ]

    komponenten_2 = [
        "koch", "meister", "wart", "flüsterer", "experte", "zauberer", "verantwortlicher", "fee",
        "bändiger", "manager", "beauftragter", "gott", "drache", "elf", "guru", "pilot", "techniker",
        "agent", "botschafter", "troll", "phantom"
    ]

    komponenten_3 = [
        "des Vertrauens", "der Nacht", "im Einsatz", "für Chaos", "mit Lizenz", "fürs Feuerholz", "auf Probe",
        "der verlorenen Pfade", "mit Kompass", "für gute Laune", "bei Regen", "unter dem Sternenzelt",
        "gegen Mücken", "mit Helm", "im Tarnmodus", "in Ausbildung",
        "mit Ehre", "im Dauereinsatz", "für Abenteuer"
    ]

    anzahl = random.choice([2, 3])
    # anzahl = random.choice([1, 2])

    if anzahl == 1:
        beruf = random.choice(komponenten_1 + komponenten_2).capitalize()
    elif anzahl == 2:
        beruf = f"{random.choice(komponenten_1)}{random.choice(komponenten_2)}"
    else:
        beruf = f"{random.choice(komponenten_1)}{random.choice(komponenten_2)} {random.choice(komponenten_3)}"

    return beruf
