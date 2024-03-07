# built-in imports
# standard library imports
import collections
import csv
import pickle
from datetime import datetime

import requests

# external imports
from flask import current_app

# internal imports
from codeapp import db
from codeapp.models import GoogleplayApps

# Function responsible for downloading the dataset from the source, translating it
# into a list of Python objects, and saving it to a Redis list.


def get_data_list() -> list[GoogleplayApps]:
    if db.exists("dataset_list") > 0:  # checks if the `dataset` key already exists
        current_app.logger.info("Dataset already downloaded.")
        dataset_stored: list[GoogleplayApps] = []  # empty list to be returned
        raw_dataset: list[bytes] = db.lrange("dataset_list", 0, -1)  # get list from DB
        for item in raw_dataset:
            dataset_stored.append(pickle.loads(item))  # load item from DB
        return dataset_stored

    r = requests.get(
        "https://onu1.s2.chalmers.se/datasets/googleplaystore.csv", timeout=10
    )
    with open("googleplaystore.csv", "w", encoding="utf-8") as file:
        file.write(r.text)
    print("CSV file downloaded successfully as 'googleplaystore.csv'")

    dataset_base: list[GoogleplayApps] = []  # list to store the items
    with open("googleplaystore.csv", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # create a new object
            try:
                last_updated = datetime.strptime(
                    row["Last Updated"], "%B %d, %Y"
                ).date()
                new_app = GoogleplayApps(
                    app=row["App"],
                    rating=float(row["Rating"]),
                    reviews=int(row["Reviews"]),
                    size=row["Size"],
                    installs=row["Installs"],
                    type=row["Type"],
                    price=int(row["Price"]),
                    content_rating=row["Content Rating"],
                    genres=row["Genres"],
                    last_updated=last_updated,
                )
                # push object to the database list
                db.rpush("dataset_list", pickle.dumps(new_app))
                dataset_base.append(new_app)  # append to the list
            except ValueError:
                continue

    print("len of dataset = ", len(dataset_base))

    return dataset_base


#    Receives the dataset in the form of a list of Python objects, and calculates the
#   statistics necessary.
def calculate_statistics(dataset: list[GoogleplayApps]) -> dict[int, int]:
    counter: dict[int, int] = collections.defaultdict(lambda: 0)
    for googleapp in dataset:
        year = googleapp.last_updated.year
        counter[year] += 1
    counter = {year: int(count) for year, count in counter.items()}
    return counter


def prepare_figure(input_figure: str) -> str:
    """
    Method that removes limits to the width and height of the figure. This method must
    not be changed by the students.
    """
    output_figure = input_figure.replace('height="345.6pt"', "").replace(
        'width="460.8pt"', 'width="100%"'
    )
    return output_figure
