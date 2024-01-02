from vkbottle import BaseMiddleware
from vkbottle.bot import Message

from tools.db import Users, manager


class RegisterMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        peer_id = self.event.peer_id

        if peer_id > 2000000000:
            self.stop("Сообщение из беседы")

        await manager.create_or_get(Users, user_id=peer_id, nick=f'User{peer_id}')
