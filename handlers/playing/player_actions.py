import asyncio

from vkbottle import CtxStorage
from vkbottle.bot import Message
from vkbottle.framework.labeler import BotLabeler

from config import state_dispenser
from entities.card import cards, Card
from entities.room import Room, CardsStack
from handlers.playing.auxiliary_functions import photo, check_winner, give_cards, next_turn, end_game
from handlers.playing.bot_actions import bot_try_beat, bot_throw_or_done, cards_can_be_defended
from tools import keyboard
from tools.states import PlayingState

storage = CtxStorage()
labeler = BotLabeler()
labeler.vbml_ignore_case = True


@labeler.private_message(payload_contains={"playing": "choose_attack_card"})
async def lay_attackers_card(message: Message):
    room: Room = storage[message.from_id]
    users_card: Card = cards[message.get_payload_json()["card_id"]]

    # Если почему-то эта карта уже есть на столе
    if [i for i in room.game_field if i.card == users_card]:
        return

    # Если карт на столе уже максимальное количество
    if len([i for i in room.game_field if i.defence_from is None]) >= 6:
        await message.answer('Ты не можешь подкинуть ещё одну карту, так как их уже максимальное количество')
        return

    # Если непобитых на столе карт больше, чем у бота
    defended_cards = set(i.defence_from for i in room.game_field if i.defence_from is not None)   # Побитые карты
    if len(room.bot_cards) <= len([i for i in room.game_field if i.card not in defended_cards and i.player != "Бот"]):
        await message.answer("Ты не можешь подкинуть ещё одну карту, так как их больше чем у бота")
        return

    # Если на столе нет карт с таким же достоинством
    if not [i for i in room.game_field if i.card.rank == users_card.rank] and len(room.game_field):
        await message.answer("Ты не можешь подкинуть эту карту")
        return

    room.game_field.append(CardsStack("Player", users_card))
    room.player_cards.remove(users_card)

    await message.answer(f'Ты сходил картой {users_card.emoji(room.trump)}',
                         await photo(message.from_id),
                         keyboard=keyboard.show_cards(message.from_id, "attack"))

    if not await check_winner(message.from_id):
        return

    bot_answer = bot_try_beat(message.from_id)

    if bot_answer == "Взять":
        room.bot_cards.extend(i.card for i in room.game_field)

        give_cards(message.from_id)
        await state_dispenser.set(message.from_id, PlayingState.ABANDON_THE_DEFENCE)

        await message.answer("Бот взял карты")
        await next_turn(message.from_id, "player")  # Игрок опять ходит
    else:
        await state_dispenser.set(message.from_id, PlayingState.ATTACKER)

        room.game_field.append(CardsStack("Бот", bot_answer[0], bot_answer[1]))
        room.bot_cards.remove(bot_answer[0])

        await message.answer(f"Бот побил картой {bot_answer[0].emoji(room.trump)} карту "
                             f"{bot_answer[1].emoji(room.trump)}", await photo(message.from_id),
                             keyboard=keyboard.show_cards(message.from_id, "attack"))

    await check_winner(message.from_id)


@labeler.private_message(payload_contains={"playing": "successful_defense"}, state=PlayingState.ATTACKER)
async def successful_defense(message: Message):
    room: Room = storage[message.from_id]

    # Если пустой стол
    if not room.game_field:
        await message.answer("Эта кнопка недоступна, так как на столе ещё нет карт")
        return

    # Если количество побитых карт не равно количеству побивающих карт
    if len([i for i in room.game_field if i.defence_from is None]) != len(
            [i for i in room.game_field if i.defence_from is not None]):
        await message.answer("Эта кнопка недоступна, так как ещё не все карты отбиты")
        return

    give_cards(message.from_id)
    await state_dispenser.set(message.from_id, PlayingState.SUCCESSFUL_DEFENCE)

    await message.answer("Бито!")
    await next_turn(message.from_id, "Бот")


@labeler.private_message(payload_contains={"playing": "choose_defend_card"}, state=PlayingState.DEFENDER)
async def choose_defenders_card(message: Message):
    room: Room = storage[message.from_id]
    users_card: Card = cards[message.get_payload_json()["card_id"]]

    if [i for i in room.game_field if i.card == users_card]:
        return

    cards_can_defend = cards_can_be_defended(users_card, message.from_id)

    cards_list = '\n'.join([c.emoji(room.trump) for c in cards_can_defend])

    if cards_can_defend:
        await message.answer(f"Карты, которые можно побить картой {users_card.emoji(room.trump)}:\n{cards_list}",
                             keyboard=keyboard.choose_cards_to_defend(cards_can_defend, users_card, message.from_id))
    else:
        await message.answer("Не найдено карт, которые ты бы мог побить этой картой")


@labeler.private_message(payload_contains={"playing": "choose_card_to_defend"}, state=PlayingState.DEFENDER)
async def lay_defenders_card(message: Message):
    room: Room = storage[message.from_id]

    payload = message.get_payload_json()
    users_card = cards[payload["users_card_id"]]
    defended_card = cards[payload["card_id"]]

    room.game_field.append(CardsStack("Player", users_card, defended_card))
    room.player_cards.remove(users_card)

    await message.answer(f"Ты побил картой {users_card.emoji(room.trump)} карту {defended_card.emoji(room.trump)}",
                         await photo(message.from_id),
                         keyboard=keyboard.show_cards(message.from_id, "defend"))

    if not await check_winner(message.from_id):
        return

    bot_answer = bot_throw_or_done(message.from_id)

    if bot_answer == "Бито!":
        give_cards(message.from_id)
        await state_dispenser.set(message.from_id, PlayingState.SUCCESSFUL_DEFENCE)

        await message.answer("Бито!")
        await next_turn(message.from_id, "Player")
    else:
        await state_dispenser.set(message.from_id, PlayingState.DEFENDER)

        room.game_field.append(CardsStack("Бот", bot_answer))
        room.bot_cards.remove(bot_answer)

        await message.answer(f"Бот сходил картой {bot_answer.emoji(room.trump)}", await photo(message.from_id),
                             keyboard=keyboard.show_cards(message.from_id, "defend"))

    await check_winner(message.from_id)


@labeler.private_message(payload_contains={"playing": "revoke_choose_card_to_defend"}, state=PlayingState.DEFENDER)
async def revoke_choose_card_to_defend(message: Message):
    await message.answer(f'Ты отменил выбор карты, которую можно побить',
                         keyboard=keyboard.show_cards(message.from_id, "defend"))


@labeler.private_message(payload_contains={"playing": "abandon_the_defense"}, state=PlayingState.DEFENDER)
async def abandon_the_defense(message: Message):
    room: Room = storage[message.from_id]

    # Пустой стол
    if not len(room.game_field):
        await message.answer("Эта кнопка недоступна, так как на столе ещё нет карт")
        return

    room.player_cards.extend(i.card for i in room.game_field)
    give_cards(message.from_id)
    await state_dispenser.set(message.from_id, PlayingState.ABANDON_THE_DEFENCE)

    await message.answer("Ты взял карты")

    await next_turn(message.from_id, "Бот")


@labeler.private_message(payload_contains={"playing": "give_up"})
async def give_up(message: Message):
    await message.answer('Ты подтверждаешь, что сдаешься?', keyboard=keyboard.give_up)


@labeler.private_message(payload={"command": "give_up"})
async def give_up_confirmation(message: Message):
    state = await state_dispenser.get(message.from_id)

    if state and "Playing" in state.state:
        await end_game(message.from_id)

