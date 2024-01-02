import random
from dataclasses import dataclass, field

from entities.card import cards, Card


@dataclass(frozen=True)
class CardsStack:
    player: str  # Бот или игрок
    card: Card  # карта
    defence_from: Card = None  # карта, которую побили


@dataclass()
class Room:
    def __init__(self, bet: int, difficulty: str):
        self.bet = bet  # ставка
        self.difficulty = difficulty  # сложность бота

        self._shuffled_cards = random.sample(cards, len(cards))  # перемешанные карты
        self.deck = self._shuffled_cards[12:]  # колода
        self.trump = self._shuffled_cards[-1]  # козырная карта
        self.game_field = []  # стол, где происходит сама игра
        self.player_cards = self._shuffled_cards[:6]  # карты игрока
        self.bot_cards = self._shuffled_cards[6:12]  # карты бота
