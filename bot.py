from vkbottle import Bot

import config
from handlers import labelers
from tools.db import Users
from tools.middlewares import RegisterMiddleware

bot = Bot(api=config.api, state_dispenser=config.state_dispenser)

for labeler in labelers:
    bot.labeler.load(labeler)

bot.labeler.message_view.register_middleware(RegisterMiddleware)

if __name__ == '__main__':
    Users.create_table()
    bot.run_forever()
