import csv
import logging

logging.basicConfig(
    level=logging.DEBUG,
    # filename='main.log',
    # filemode='w'
)


def save_bs_title(file_name: str, title: list):
    with open(file_name, mode='w', encoding='utf-8') as file:
        employee_writer = csv.writer(
            file, delimiter=',',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        employee_writer.writerow(title)


def save_bs(file_name: str, content: dict):
    with open(file_name, mode='a') as employee_file:
        employee_writer = csv.writer(
            employee_file, delimiter=',',
            quotechar='"', quoting=csv.QUOTE_MINIMAL)

        for val in content.values():
            logging.debug(val)
            employee_writer.writerow(val.values())
