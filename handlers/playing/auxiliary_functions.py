import random
from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from vkbottle import PhotoMessageUploader, CtxStorage

from config import api, state_dispenser
from entities.room import Room, CardsStack
from handlers.playing.bot_actions import bot_start_turn
from tools import keyboard
from tools.db import manager, Users
from tools.states import PlayingState

storage = CtxStorage()


async def next_turn(user_id: int, attacker: str) -> None:
    room: Room = storage[user_id]
    room.game_field = []

    if attacker == "Бот":
        await state_dispenser.set(user_id, PlayingState.DEFENDER)

        bots_card = bot_start_turn(user_id)

        room.game_field.append(CardsStack("Бот", bots_card))
        room.bot_cards.pop(room.bot_cards.index(bots_card))

        await api.messages.send(user_id, 0, attachment=await photo(user_id),
                                message=f"Бот сходил картой {bots_card.emoji(room.trump)}",
                                keyboard=keyboard.show_cards(user_id, "defend"))

        await check_winner(user_id)
    else:
        await state_dispenser.set(user_id, PlayingState.ATTACKER)
        await api.messages.send(user_id, 0, keyboard=keyboard.show_cards(user_id, "attack"),
                                message=f"Твоя очередь ходить к боту, выбери карту, чтобы сходить")


def give_cards(user_id: int) -> None:
    room: Room = storage[user_id]

    count = 0
    for _ in range(6):
        for i in (room.player_cards, room.bot_cards):
            if len(i) < 6:
                try:
                    i.append(room.deck[count])
                    count += 1
                except IndexError:
                    break

    room.deck = room.deck[count:]


async def photo(user_id: int) -> str:
    room: Room = storage[user_id]

    background = Image.open(f"sources/backgrounds/for_playing.jpg")

    cards = {}

    for i in [i for i in room.game_field if i.defence_from is None]:
        card_style = "for_bot" if i.player == "Бот" else "classic"

        card = Image.open(f"sources/cards/{card_style}/{i.card.ord_number}.png").rotate(random.randint(-3, 3),
                                                                                        expand=True)
        card_background = Image.new(mode="RGBA", size=(1180, 1530), color=(0, 0, 0, 0))
        card_background.paste(card, (225, 225), card)
        cards[i.card] = card_background

    for i in [i for i in room.game_field if i.defence_from is not None]:
        if i.defence_from not in cards:
            continue

        card_style = "for_bot" if i.player == "Бот" else "classic"
        card = Image.open(f"sources/cards/{card_style}/{i.card.ord_number}.png").rotate(random.randint(-21, -19),
                                                                                        expand=True)
        card_background = cards[i.defence_from]
        card_background.paste(card, (random.randint(90, 110), random.randint(190, 210)), card)

    cards = list(i.resize((393, 510)) for i in cards.values())

    positions = {1: [(763, 285)],
                 2: [(613, 285), (1163, 285)],
                 3: [(413, 285), (913, 285), (1413, 285)],
                 4: [(613, 0), (1163, 0), (613, 540), (1163, 540)],
                 5: [(613, 0), (1163, 0), (413, 540), (913, 540), (1413, 540)],
                 6: [(413, 0), (913, 0), (1413, 0), (413, 540), (913, 540), (1413, 540)]}

    for count, i in enumerate(positions[len(cards)]):
        background.paste(cards[count], i, cards[count])

    draw = ImageDraw.Draw(background)
    main_font = ImageFont.truetype('sources/fonts/Bebas Neue Cyrillic.ttf', 70)

    draw.text((100, 320), f'{len(room.deck)}', 'white', main_font, 'mm', stroke_width=2, stroke_fill=(137, 137, 137))

    draw.text((100, 980), f"У тебя {len(room.player_cards)} карт", "white", main_font, "lm", stroke_width=2,
              stroke_fill=(137, 137, 137))
    draw.text((100, 100), f"У бота {len(room.bot_cards)} карт", "white", main_font, "lm", stroke_width=2,
              stroke_fill=(137, 137, 137))

    if len(room.deck) > 0:
        card = Image.open(f"sources/cards/classic/{room.trump.ord_number}.png").rotate(random.randint(89, 91),
                                                                                       expand=True)
        card.thumbnail((352, 230))
        background.paste(card, (random.randint(-50, -45), random.randint(435, 440)), card)

        if len(room.deck) > 1:
            back = Image.open(f"sources/cards/back.png").rotate(random.randint(-3, 3), resample=2, expand=True)
            background.paste(back, (random.randint(-20, -15), random.randint(370, 385)), back)

    else:
        suit = Image.open(f"sources/cards/suits/{room.trump.suit.value}.png")
        suit.thumbnail((150, 250))
        background.paste(suit, (30, 450), suit)

    background = background.resize((1280, 720))

    image_content = BytesIO()
    background.save(image_content, format='JPEG')
    return await PhotoMessageUploader(api).upload(image_content)


async def check_winner(user_id: int) -> Optional[bool]:
    room: Room = storage[user_id]

    if room.deck:
        return True
    elif room.player_cards and room.bot_cards:
        return True

    await end_game(user_id)


async def end_game(user_id: int) -> None:
    room: Room = storage[user_id]

    if await state_dispenser.get(user_id):
        await state_dispenser.delete(user_id)

    if not room.bot_cards:
        winner, durak = "Бот", "Ты"
        await manager.execute(Users.update(money=Users.money - room.bet, loses=Users.loses + 1)
                              .where(Users.user_id == user_id))
    else:
        winner, durak = "Ты", "Бот"
        await manager.execute(Users.update(money=Users.money + room.bet, wins=Users.wins + 1)
                              .where(Users.user_id == user_id))

    await api.messages.send(user_id, 0, message=f"Игра окончена!\n\nПобедитель:\n{winner} - {room.bet * 2:,} монет"
                                                f"\nДурак: {durak}",
                            keyboard=keyboard.menu)

    storage.delete(user_id)
