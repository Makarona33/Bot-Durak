import asyncio
from typing import Any

from vkbottle import ABCRequestRescheduler, API


class RequestRescheduler(ABCRequestRescheduler):
    def __init__(self, delay: int = 1):
        self.delay = delay

    async def reschedule(
        self,
        ctx_api: API,
        method: str,
        data: dict,
        recent_response: Any,
    ) -> dict:
        await asyncio.sleep(self.delay)
        return await ctx_api.request(method, data)
