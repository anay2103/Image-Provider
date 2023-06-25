import json
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient


class TestCache:
    """Класс, заменяющий Redis в тестах."""
    __test__ = False

    def __init__(self) -> None:
        self.cache = {}

    async def get(self, key: str) -> Any:
        return self.cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        self.cache[key] = value

    async def close(self):
        self.cache.clear()


@pytest.fixture
def categories():
    """Категории и их индексы."""
    return {'apple': 0, 'cloud': 1, 'aabb': 2, 'games': 3}


@pytest.fixture
def urls():
    """Ссылки и их индексы."""
    return [
        'http://localhost:8000/static/image1.jpg',
        'http://localhost:8000/static/image2.jpg',
        'http://localhost:8000/static/image3.jpg',
        'http://localhost:8000/static/image4.jpg',
    ]


@pytest.fixture
def nums():
    """Массив с числом показов картинок."""
    return [
        [None, 5, None, None],
        [3, 3, 3, None],
        [None, 1, 1, 1],
        [1, None, 1, None],
    ]


@pytest.fixture
async def app(
    categories: Dict[str, Any],
    urls: Dict[str, Any],
    nums: List[List[Any]],
) -> FastAPI:
    """Тестовое приложение."""
    from main import app as testapp
    testapp.state.cache = TestCache()
    await testapp.state.cache.set('categories', json.dumps(categories))
    await testapp.state.cache.set('urls', json.dumps(urls))
    await testapp.state.cache.set('nums', json.dumps(nums))
    return testapp


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Тестовый клиент."""
    return TestClient(app)


async def test_get_without_parameters(
    app: FastAPI,
    client: TestClient,
) -> None:
    """Тест GET / без параметров запроса."""
    resp = client.get('/')
    assert resp.status_code == status.HTTP_200_OK


async def test_shows_decrease(
    app: FastAPI,
    client: TestClient,
    categories: Dict[str, Any],
    urls: Dict[str, Any],
    nums: List[List[Any]],
) -> None:
    """Тест GET / число показов уменьшается."""
    resp = client.get('/', params={'category[]': 'games'})
    assert resp.status_code == status.HTTP_200_OK
    col = categories['games']
    shows = nums[2][col]  # 2 - индекс url в словаре urls
    url = urls[2]
    assert url in resp.text

    upd_nums = json.loads(await app.state.cache.get('nums'))
    assert upd_nums[2][col] == shows - 1


async def test_recent_cache(
    app: FastAPI,
    client: TestClient,
    categories: Dict[str, Any],
    urls: Dict[str, Any],
    nums: List[List[Any]],
) -> None:
    """Тест GET / кэш сохраняется."""
    resp = client.get('/', params={'category[]': 'games'})
    assert resp.status_code == status.HTTP_200_OK
    recent = await app.state.cache.get('recent')
    assert 2 == int(recent)  # 2 - индекс url в словаре urls


async def test_another_img_if_in_cache(
    app: FastAPI,
    client: TestClient,
    categories: Dict[str, Any],
    urls: Dict[str, Any],
    nums: List[List[Any]],
) -> None:
    """Тест GET / картинка в кэше не выбирается, если есть другая."""
    old_cache = await app.state.cache.set('recent', 1)  # 1 - индекс url
    resp = client.get('/', params={'category[]': ['aabb', 'games']})
    assert resp.status_code == status.HTTP_200_OK
    recent_cache = await app.state.cache.get('recent')
    assert old_cache != recent_cache
