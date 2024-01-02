from vkbottle import CtxStorage
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from config import state_dispenser
from entities.room import Room
from handlers.playing.auxiliary_functions import next_turn
from tools import keyboard
from tools.db import manager, Users
from tools.states import CreateGameState
from tools.utils import amount_size

storage = CtxStorage()
labeler = BotLabeler()
labeler.vbml_ignore_case = True


@labeler.private_message(payload={"command": "play"})
async def choose_difficulty(message: Message):
    await message.answer("Выбери уровень сложности бота", keyboard=keyboard.difficulty)


@labeler.private_message(payload_map=[("difficulty", str)])
async def choose_bet(message: Message):
    await state_dispenser.set(message.from_id, CreateGameState.SET_BET,
                              difficulty=message.get_payload_json()["difficulty"])

    await message.answer("Напиши ставку", keyboard=keyboard.back)


@labeler.private_message(state=CreateGameState.SET_BET)
async def start_game(message: Message):
    user = await manager.get(Users, user_id=message.from_id)

    bet = amount_size(message.text, user.money, 0, "Слишком большая ставка!", "Слишком маленькая ставка!",
                      "Ты написал некорректное число!")

    if isinstance(bet, str):
        await message.answer(bet)
        return

    # создание игровой комнаты
    storage.set(message.from_id, Room(bet, (await state_dispenser.get(user.user_id)).payload["difficulty"]))

    await message.answer(f"Игра в была запущена\nКозырь: {storage.get(message.from_id).trump.emoji()}*")

    await next_turn(user.user_id, "user")
