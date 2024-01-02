from vkbottle import TemplateElement, template_gen
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from config import state_dispenser
from tools.db import manager, Users
from tools import keyboard
from tools.states import SettingsState
from tools.utils import check_text

labeler = BotLabeler()
labeler.vbml_ignore_case = True


@labeler.private_message(text='Настройки⚙')
async def settings(message: Message):
    user = await manager.get(Users, user_id=message.from_id)

    await message.answer(f"Тут ты можешь изменить некоторые параметры\n\nТвои настройки:\nНик: {user.nick}",
                         keyboard=keyboard.settings)


@labeler.private_message(payload={"settings": "change_nickname"})
async def change_nickname(message: Message):
    await state_dispenser.set(message.from_id, SettingsState.CHANGE_NICKNAME)
    await message.answer(f"Пиши свой ник, он  должен быть длиной до 15 символов и может состоять только из букв, "
                         f"цифр и всяких знаков препинания")


@labeler.private_message(state=SettingsState.CHANGE_NICKNAME)
async def set_nickname(message: Message):
    if nick := check_text(message.text, 15, 1, "Твой ник слишком длинный", "Твой ник слишком короткий",
                          "Кажется ты написал какие-то посторонние символы в нике"):
        await message.answer(f'{nick}, придумай новый ник')
    else:
        await state_dispenser.delete(message.from_id)
        await manager.execute(Users.update(nick=message.text).where(Users.user_id == message.from_id))

        await message.answer(f'Теперь твой ник - {message.text}')
