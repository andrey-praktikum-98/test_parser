#!/usr/bin/python
# -*- coding: latin-1 -*-
import os
import time
import csv
import json
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    # filename='main.log',
    # filemode='w'
)

DOMAIN = os.getenv('DOMAIN')
CATALOG = os.getenv('CATALOG')

with open('config.json', 'r') as f:
    config = json.load(f)


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


def catalog_page(main_catalog: str):
    """
    Ãëàâíàÿ ôóíêöèÿ è îòðàáîòêà êàòåãîðèè ñ ñîõðàíåíèåì â áàçó
    """
    startTime = time.time()
    links_url = {}
    category = {}
    category_child = {}
    id_parent_cat = 0
    count_child = 0
    try:
        catalog = requests.get(f"{DOMAIN}{main_catalog}")
        soup_catalog = BeautifulSoup(catalog.text, 'html.parser')
    except Exception as err:
        logging.debug(f"Ïðîèçîøëà îøèáêà: {err}")
    save_bs_title('categories.csv', ['id', 'title', 'href'])
    save_bs_title('categories_child.csv', ['id_category', 'id_category_child', 'title', 'href'])
    save_bs_title('products.csv', ['id_cat_child', 'title', 'price', 'article', 'shorts_code'])
    for items in soup_catalog.find_all("a", {"class": "item-depth-1"}):
        try:
            sub_category = requests.get(f"{DOMAIN}{items.get('href')}")
            soup_sub_category = BeautifulSoup(sub_category.text, 'html.parser')
        except Exception as err:
            logging.debug(f"Ïðîèçîøëà îøèáêà: {err}")
        links_url[items.get('title')] = {}
        id_parent_cat += 1
        category[id_parent_cat] = {
            'id_cat': id_parent_cat,
            'title': items.get('title'),
            'href': items.get('href')
        }
        get_sub_category(soup_sub_category, links_url,
                         items, id_parent_cat, category_child, count_child)

    
    save_bs('categories.csv', category)
    endTime = time.time()
    elapsedTime = endTime - startTime
    logging.info(
        f"Çàòðà÷åíîå âðåìÿ íà çàïðîñû: {elapsedTime}")
    return links_url


def get_sub_category(soup_sub_category, links_url, items,
                     id_parent_cat, category_child, count_child):
    """Ïîëó÷åíèå ïîäêàòåãîðèé è ñîõðàíåíèå â áàçó"""

    category_child = {}
    for items_sub_cat in (soup_sub_category.find_all(
            "a", {"class": "item-depth-1"})):
        links_url[items.get('title')][items_sub_cat.get('title')] = \
            items_sub_cat.get('href')
        try:
            products = requests.get(f"{DOMAIN}{items_sub_cat.get('href')}")
            soup_products = BeautifulSoup(products.text, 'html.parser')
        except Exception as err:
            logging.debug(f"Ïðîèçîøëà îøèáêà: {err}")
        count_child += 1
        category_child[count_child] = {
            'id_cat': id_parent_cat,
            'id_category_child': count_child,
            'title': items_sub_cat.get('title'),
            'href': items_sub_cat.get('href')
        }
        
        time.sleep(0.5)
        products_page(soup_products, count_child)
        # paginate(soup_products)
    save_bs('categories_child.csv', category_child)
    


def products_page(soup_products, count_child):
    """Ïîëó÷åíèå ïðîäóêòîâ"""

    category_product = {}
    products_lop = soup_products.select(".catalog-content-info .name")
    for key, link_product in enumerate(products_lop):
        try:
            product_single = requests.get(
                f"{DOMAIN}{link_product.get('href')}")
            soup_product = BeautifulSoup(product_single.text, 'html.parser')
        except Exception as err:
            logging.debug(f"Ïðîèçîøëà îøèáêà: {err}")
        text_title = soup_product.h1
        logging.debug(text_title.text)
        count_prod = 0
        for val_product in soup_product.find(class_="b-catalog-element-offers-table").find_all('tr'):
            products_tds = val_product.find_all('b')
            if products_tds != []:
               artic = products_tds[1]
               shorts = products_tds[3]
               pack = products_tds[5]
            
            count_prod += 1

            category_product[count_prod] = {
                'id_cat_child': count_child,
                'text_title': text_title.text,
                'articule': artic.text,
                'shorts': shorts.text,
                'pack': pack.text,
            }

        time.sleep(0.5)

    save_bs('products.csv', category_product)


def paginate(soup_products):
    """Ïàëó÷åíèÿ ññûëîê íà ïàãèíàöèè è îáðàáîòêà êàæäîé ñòðàíèöû"""
    products_paginate = soup_products.select(".navigation a")
    for prod_paginate in products_paginate:
        logging.debug(prod_paginate.get('href'))
        product_single = requests.get(f"{DOMAIN}{prod_paginate.get('href')}")
        soup_product = BeautifulSoup(product_single.text, 'html.parser')
        logging.info(soup_product.select("td"))

        time.sleep(0.5)


logging.info(catalog_page(CATALOG))
