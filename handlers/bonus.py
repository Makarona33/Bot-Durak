import datetime

from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from tools.db import Users, manager

labeler = BotLabeler()
labeler.vbml_ignore_case = True


@labeler.message(text=["бонус", "Бонус🎁"])
async def give_bonus(message: Message):
    user = await manager.get(Users, user_id=message.from_id)
    delta = user.bonus_time - datetime.datetime.now()

    if delta.total_seconds() > 0:
        await message.answer(f"Ты уже брал бонус\nОсталось для взятия бонуса - "
                             f"{delta.seconds // 3600} ч. {(delta.seconds // 60) % 60} мин.")
        return

    await message.answer("Ты воспользовался бонусом, тебе начислено +50 монет, следующий бонус ты сможешь "
                         "получить через 24 часа")

    user.money += 50
    user.bonus_time = datetime.datetime.now() + datetime.timedelta(days=1)

    await manager.update(user, [Users.money, Users.bonus_time])
