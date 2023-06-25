import json
import random
from typing import Set

from fastapi.responses import HTMLResponse
from fastapi import APIRouter, HTTPException, Query, Request
from jinja2 import Template
from pydantic import conlist

from app import CATEGORIES, RECENT, NUMS, URLS
from app.route import Route

TEMPLATE = '<html><image src="{{ url }}"></html>'
router = APIRouter(route_class=Route)


@router.get('/', summary='Get image', response_class=HTMLResponse)
async def get_image(
    request: Request,
    categories: conlist(str, max_items=10) = Query(None, alias='category[]'),  # type: ignore
) -> HTMLResponse:
    """Получение картинки по категориям. \f

    В цикле while рандомно перебираются категории, во внутреннем цикле for
    перебираются ряды массива NUMS c показами картинок.

    Если найдена непустая ячейка NUMS с запрошенной категорией,
    и она не равная ячейке из предыдущего показа, оба цикла прерываются.
    """
    nums_cache = await request.app.state.cache.get(NUMS)
    recent = await request.app.state.cache.get(RECENT)
    categories_cache = await request.app.state.cache.get(CATEGORIES)

    nums = json.loads(nums_cache)
    all_categories = json.loads(categories_cache)
    recent = int(recent) if recent else recent

    available = categories or list(all_categories.keys())

    nrow = None
    seen: Set[str] = set()
    while len(available) > len(seen):
        cat = random.choice(available)
        seen.add(cat)
        col = all_categories[cat]
        for row in range(len(nums)):
            if nums[row][col]:
                nrow = row
                if nrow != recent:
                    break
        if nrow is not None and nrow != recent:
            break

    if nrow is None:
        raise HTTPException(status_code=404, detail='Not found')

    urls_cache = await request.app.state.cache.get(URLS)
    urls = json.loads(urls_cache)

    url = urls[nrow]  # получаем url картинки
    for i in range(len(nums[nrow])):  # вычитаем 1 из ряда выбранной картинки
        if nums[nrow][i]:
            nums[nrow][i] -= 1

    await request.app.state.cache.set(RECENT,  nrow)
    await request.app.state.cache.set(NUMS, json.dumps(nums))
    resp = Template(TEMPLATE).render({'url': url})
    return HTMLResponse(resp)
