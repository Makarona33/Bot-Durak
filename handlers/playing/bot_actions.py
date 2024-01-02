import random
from typing import Union

from vkbottle import CtxStorage

from entities.card import Card
from entities.room import Room

storage = CtxStorage()

RANK_MULTIPLIER = 100
UNBALANCED_HAND_PENALTY = 200
MANY_CARDS_PENALTY = 600
OUT_OF_PLAY = 30000


# Выбор в зависимости от сложности бота
def bot_choice(difficulty: str, variants: dict):
    vals = sorted(variants.keys())

    match difficulty:
        case "easy":
            return variants[vals[0]]
        case "middle":
            return variants[vals[len(vals) // 2]]
        case "difficult":
            return variants[vals[-1]]


# Бот ходит
def bot_start_turn(user_id: int) -> Card:
    room: Room = storage[user_id]

    bonuses = [0, 0, 1, 1.5, 2.5, 2.5]
    counts_by_rank = [0] * 9

    for c in room.bot_cards:
        counts_by_rank[c.rank.value] += 1

    variants = {}
    for i in range(len(room.bot_cards)):

        c = room.bot_cards[i]

        hand = room.bot_cards.copy()
        hand.pop(i)

        val = hand_value(hand, user_id) + int(round(bonuses[counts_by_rank[c.rank.value]] * (
            6 if c.rank.value == 8 else c.rank.value - 8) * RANK_MULTIPLIER, 0))

        variants[val] = c
    return bot_choice(room.difficulty, variants)


# Бот подкидывает или бито
def bot_throw_or_done(user_id: int) -> Union[Card, str]:
    room: Room = storage[user_id]

    if len([i for i in room.game_field if i.defence_from is None]) >= 6:
        return "Бито!"

    defended_cards = set(i.defence_from for i in room.game_field if i.defence_from is not None)
    if len(room.player_cards) <= len(
            [i for i in room.game_field if i.card not in defended_cards and i.player != "Player"]):
        return "Бито!"

    ranks_present = [False] * 9
    for i in room.game_field:
        ranks_present[i.card.rank.value] = True

    bonuses = [0.0, 0.0, 1.0, 1.5, 2.5, 2.5]
    counts_by_rank = [0] * 9

    for c in room.bot_cards:
        counts_by_rank[c.rank.value] += 1

    variants = {}
    max_val = -1_000_000

    for i in range(len(room.bot_cards)):
        c = room.bot_cards[i]
        if not ranks_present[c.rank.value]:
            continue

        new_hand = room.bot_cards.copy()
        new_hand.pop(i)

        new_val = hand_value(new_hand, user_id) + int(round(bonuses[counts_by_rank[c.rank.value]] * (
            6 if c.rank.value == 8 else c.rank.value - 8) * RANK_MULTIPLIER))
        variants[new_val] = c

        if new_val > max_val:
            max_val = new_val

    penalty_base = 1200
    penalty_delta = 50

    if hand_value(room.bot_cards, user_id) - max_val < \
            penalty_base - penalty_delta * len(room.deck) and variants:
        return bot_choice(room.difficulty, variants)
    else:
        return "Бито!"


# Бот пытается побиться
def bot_try_beat(user_id: int) -> str | list[Card]:
    room: Room = storage[user_id]

    rank_present_bonus = 300
    ranks_present = [False] * 9
    hand_if_take = []

    for c in room.bot_cards:
        ranks_present[c.rank.value] = True
        hand_if_take.append(c)

    for c in room.player_cards:
        ranks_present[c.rank.value] = True
        hand_if_take.append(c)

    variants = {}
    max_val = -1_000_000

    for i in range(len(room.bot_cards)):
        c = room.bot_cards[i]
        if can_defend := cards_can_be_defended(c, user_id):
            new_hand = room.bot_cards.copy()
            new_hand.pop(i)

            new_val = hand_value(new_hand, user_id) + rank_present_bonus * (1 if ranks_present[c.rank.value] else 0)
            variants[new_val] = (c, random.choice(can_defend))

            if new_val > max_val:
                max_val = new_val

    penalty = 800
    take_penalty_base = 200
    take_penalty_delta = 40

    if ((hand_value(storage[user_id].bot_cards, user_id) - max_val < penalty or
         hand_value(hand_if_take, user_id) - max_val < take_penalty_base - take_penalty_delta * len(room.deck)
         or len(room.deck) == 0) and variants):
        return bot_choice(room.difficulty, variants)

    return "Взять"


def hand_value(hand: list[Card], user_id: int) -> int:
    def relative_card_value(cards_rank: int):
        return 4.5 if cards_rank == 8 else cards_rank + 4.5 - 14

    room: Room = storage[user_id]

    bonuses = [0.0, 0.0, 0.5, 0.75, 1.25, 1.25]
    res = 0
    counts_by_rank = [0] * 9
    counts_by_suit = [0] * 4

    for c in hand:
        res += int(relative_card_value(c.rank.value) * RANK_MULTIPLIER)
        if room.trump.suit == c.suit:
            res += 13 * RANK_MULTIPLIER
        counts_by_rank[c.rank.value] += 1
        counts_by_suit[c.suit.value] += 1

    for i in range(1, 10):
        res += int(max([relative_card_value(i), 1]) * bonuses[counts_by_rank[i - 1]])

    avg_suit = 0
    for c in hand:
        if room.trump.suit != c.suit:
            avg_suit += 1

    avg_suit /= 3
    for s in range(4):
        if s != room.trump.suit.value:
            dev = abs((counts_by_suit[s] - avg_suit) / (avg_suit if avg_suit != 0 else 1))
            res -= int(UNBALANCED_HAND_PENALTY * dev)

    cards_in_play = len(room.deck) + len(room.player_cards) - len(hand)
    card_ratio = len(hand) / cards_in_play if cards_in_play != 0 else 10
    res += int((0.25 - card_ratio) * MANY_CARDS_PENALTY)
    return res


# Карты, которые можно побить
def cards_can_be_defended(card: Card, user_id: int) -> list[Card]:
    room: Room = storage[user_id]
    defended_cards = set(i.defence_from for i in room.game_field if i.defence_from is not None)

    return [
        i.card for i in room.game_field  # Карты, находящиеся на столе,
        if i.defence_from is None and  # которые не побивают другие
        i.card not in defended_cards and  # и которые еще не побиты.
        (
           card.suit == i.card.suit and  # Масти одинаковые
           card.rank.value > i.card.rank.value  # и достоинство карты больше,
           if room.trump.suit != card.suit  # если наша карта не козырная.
           else i.card.ord_number not in range(card.ord_number, 36, 4)  # Если же наша карта козырная, то побиваемая
           # карта должна быть не больше по достоинству нашей
        )
    ]
