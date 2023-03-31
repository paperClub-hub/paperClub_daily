#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Projecte : PyCharm
# @Date     : 2022-11-21 13:35
# @Author   : paperclub
# @Desc     : paperclub@163.com



from fastapi import APIRouter, FastAPI, Request, Response, Body
from fastapi.routing import APIRoute

from typing import Callable, List
from uuid import uuid4


#  获取请求参数到日志中
class ContextIncludedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            request_id = str(uuid4())
            response: Response = await original_route_handler(request)

            if await request.body():
                print(await request.body())

            response.headers["Request-ID"] = request_id
            return response

        return custom_route_handler



router = APIRouter(route_class=ContextIncludedRoute)
@router.post("/context")
async def non_default_router(bod: List[str] = Body(...)):
    return bod

app = FastAPI()
app.include_router(router)



if __name__ == '__main__':
    pass
    # demo_loguru()
    import uvicorn
    ip = "127.0.0.1"
    port = 5000
    uvicorn.run(app='api_query:app', host=ip, port=port, reload=True, debug=True)
