import json
import csv

import aioredis
from fastapi import FastAPI

from app import CATEGORIES, NUMS, URLS


def connect_redis(app: FastAPI) -> None:
    """Соединение с Redis."""
    redis = aioredis.from_url(app.state.conf.REDIS_URI, encoding="utf-8", decode_responses=True)
    app.state.cache = redis


async def read_csv(app: FastAPI) -> None:
    """Загрузка кэша из файла.

    Формирует двухмерный массив NUMS, где по оси х - картинки, y - категории
    Значения массива соответствуют кол-ву показов картинки x с категорией y:

    None 11 None None 11
    5 5 None 5 None
    1 None 1 None 1

    В кэше сохраняются ключи:
        - NUMS - массив с кол-вом показов картинки;
        - CATEGORIES - маппинг названия категорий в колонки массива NUMS;
        - URLS - список ссылок на картинки, сортированный в порядке убывания показов.
    """
    categories_set = set()
    url_dict = {}
    with open('images.csv') as file:
        links = csv.reader(file)
        for link in reversed(sorted(links, key=lambda x: int(x[1]))):
            url, shows, *categories = link
            url_dict[url] = {'shows': int(shows), 'categories': categories}
            for cat in categories:
                categories_set.add(cat)

    nums = [[None for _ in range(len(categories_set))] for _ in range(len(url_dict))]

    category_nums = {v: k for k, v in enumerate(categories_set)}

    for i, url in enumerate(url_dict):
        url_shows = url_dict[url]['shows']
        url_categories = url_dict[url]['categories']
        for cat in url_categories:  # type: ignore
            loc = category_nums[cat]
            nums[i][loc] = url_shows  # type: ignore

    await app.state.cache.set(CATEGORIES, json.dumps(category_nums))
    await app.state.cache.set(URLS, json.dumps(list(url_dict.keys())))
    await app.state.cache.set(NUMS, json.dumps(nums))
