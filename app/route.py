from typing import Callable

from fastapi import Request, Response, status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.routing import APIRoute


class Route(APIRoute):
    """Кастомный класс APIRoute для обработки исключений приложения."""

    def get_route_handler(self) -> Callable:
        """https://fastapi.tiangolo.com/advanced/custom-request-and-route/."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:
                body = await request.body()
                detail = {'errors': exc.errors(), 'body': body.decode()}
                raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
            except HTTPException:
                raise
            except Exception as exc:
                detail = {exc.__class__.__name__: exc.args}
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail)

        return custom_route_handler
