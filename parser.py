#!/usr/bin/python
# -*- coding: latin-1 -*-
import os
import time
import json
import requests
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from parser_base_save import save_bs_title, save_bs

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


def beatiful_req(url_name: str):
    try:
        catalog = requests.get(f"{DOMAIN}{url_name}")
        soup_catalog = BeautifulSoup(catalog.text, 'html.parser')
    except Exception as err:
        logging.debug(f"Произошла ошибка: {err}")

    return soup_catalog


def catalog_page(main_catalog: str):
    """
    Отрабатывает на главной странице
    родительский каталог
    """
    startTime = time.time()
    links_url = {}
    category = {}
    category_child = {}
    id_parent_cat = 0
    count_child = 0
    soup_catalog = beatiful_req(main_catalog)
    save_bs_title('categories.csv', ['id', 'title', 'href'])
    save_bs_title(
        'categories_child.csv',
        ['id_category', 'id_category_child', 'title', 'href'])
    save_bs_title(
        'products.csv',
        ['id_cat_child', 'title', 'price', 'article', 'shorts_code'])
    for items in soup_catalog.find_all("a", {"class": "item-depth-1"}):
        soup_sub_category = beatiful_req(items.get('href'))
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
        f"Время ожидание парсера: {elapsedTime}")
    return links_url


def get_sub_category(soup_sub_category: BeautifulSoup, links_url: dict,
                     items: BeautifulSoup, id_parent_cat: int,
                     category_child: dict, count_child: int):
    """
    Получение по родительским категориям,
    подкатегории
    """
    category_child = {}
    for items_sub_cat in (soup_sub_category.find_all(
            "a", {"class": "item-depth-1"})):
        links_url[items.get('title')][items_sub_cat.get('title')] = \
            items_sub_cat.get('href')
        soup_products = beatiful_req(items_sub_cat.get('href'))
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


def products_page(soup_products: BeautifulSoup, count_child: int):
    """
    Получение товаров в каждой подкатегории
    """
    category_product = {}
    products_lop = soup_products.select(".catalog-content-info .name")
    for key, link_product in enumerate(products_lop):
        soup_product = beatiful_req(link_product.get('href'))
        text_title = soup_product.h1
        count_prod = 0
        for val_product in soup_product.find(
                class_="b-catalog-element-offers-table").find_all('tr'):
            products_tds = val_product.find_all('b')
            try:
                if products_tds != []:
                    artic = products_tds[1]
                    shorts = products_tds[3]
                    pack = products_tds[5]
            except ValueError as err_val:
                logging.debug(f"Ошибка значения: {err_val}")

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
    """
    Отработка пагинации и получения товаров
    """
    products_paginate = soup_products.select(".navigation a")
    for prod_paginate in products_paginate:
        logging.debug(prod_paginate.get('href'))
        soup_product = beatiful_req(prod_paginate.get('href'))
        logging.info(soup_product.select("td"))
        time.sleep(0.5)


logging.info(catalog_page(CATALOG))
