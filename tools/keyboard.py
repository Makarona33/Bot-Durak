from typing import Sequence

from vkbottle import Keyboard, Text, CtxStorage
from vkbottle import KeyboardButtonColor as Color

from entities.card import Card
from entities.room import Room

storage = CtxStorage()

back = (Keyboard()
        .add(Text("Меню"), Color.NEGATIVE)
        ).get_json()

menu = (Keyboard()
        .add(Text("Играть▶", {"command": "play"}), Color.POSITIVE)
        .row()
        .add(Text("Профиль📊", {"command": "profile"}), Color.SECONDARY)
        .row()
        .add(Text("Настройки⚙", {"command": "settings"}), Color.SECONDARY)
        .row()
        .add(Text("Бонус🎁", {"command": "bonus"}), Color.PRIMARY)
        ).get_json()

difficulty = (Keyboard()
              .add(Text("Лёгкий", {"difficulty": "easy"}), Color.SECONDARY)
              .row()
              .add(Text("Средний", {"difficulty": "middle"}), Color.SECONDARY)
              .row()
              .add(Text("Сложный", {"difficulty": "difficult"}), Color.SECONDARY)
              .row()
              .add(Text("Меню"), Color.NEGATIVE)
              ).get_json()


# Карты игрока
def show_cards(user_id: int, state: str) -> str:
    keyboard = Keyboard()
    room: Room = storage[user_id]

    for count, card in enumerate(sorted(room.player_cards, key=lambda c: (c.suit.value, c.rank.value)), 1):
        keyboard.add(Text(card.emoji(room.trump), {f"playing": f"choose_{state}_card", "card_id": card.ord_number}),
                     Color.PRIMARY)

        if not count % 3 and count != len(room.player_cards):
            keyboard.row()

    keyboard.row()
    if state == "defend":
        keyboard.add(Text("Взять", {f"playing": "abandon_the_defense"}))
    else:
        keyboard.add(Text("Бито!", {f"playing": "successful_defense"}))
    keyboard.row()

    keyboard.add(Text("Сдаться💀", {f"playing": "give_up", "player": f"{state}er"}), Color.NEGATIVE)

    return keyboard.get_json()


def choose_cards_to_defend(cards: Sequence[Card], users_card: Card, user_id: int) -> str:
    keyboard = Keyboard()
    room: Room = storage[user_id]

    for count, card in enumerate(sorted(cards, key=lambda c: (c.suit.value, c.rank.value)), 1):
        keyboard.add(Text(card.emoji(room.trump),
                          {"playing": "choose_card_to_defend", "card_id": card.ord_number,
                           "users_card_id": users_card.ord_number}),
                     Color.PRIMARY)

        if not count % 3 and count != len(cards):
            keyboard.row()

    keyboard.row()
    keyboard.add(Text("Отмена", {f"playing": "revoke_choose_card_to_defend"}))

    return keyboard.get_json()


give_up = Keyboard(inline=True).add(Text("Подтверждаю", {"command": "give_up"}), Color.POSITIVE).get_json()

settings = (Keyboard()
            .add(Text("Сменить ник", {"settings": "change_nickname"}), Color.POSITIVE)
            .row()
            .add(Text("Меню"), Color.SECONDARY)
            ).get_json()
