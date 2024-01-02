from vkbottle import CtxStorage
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from config import state_dispenser
from tools import keyboard


labeler = BotLabeler()
labeler.vbml_ignore_case = True


@labeler.private_message(payload={"command": "start"})
async def start(message: Message):
    await message.answer("Меню", keyboard=keyboard.menu)


@labeler.private_message(text=["начать", "привет", "меню", "команды"])
async def menu(message: Message):
    state = await state_dispenser.get(message.from_id)

    if state:
        if "Playing" in state.state:
            return
        await state_dispenser.delete(message.from_id)

    if CtxStorage().get(message.from_id):
        CtxStorage().delete(message.from_id)

    await message.answer("Меню", keyboard=keyboard.menu)
