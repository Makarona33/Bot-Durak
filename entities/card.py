from dataclasses import dataclass
from enum import Enum


class Suit(Enum):
    SPADES = 0
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3


class Rank(Enum):
    SIX = 0
    SEVEN = 1
    EIGHT = 2
    NINE = 3
    TEN = 4
    JACK = 5
    QUEEN = 6
    KING = 7
    ACE = 8


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    @property
    def ord_number(self):  # порядковый номер
        return self.rank.value * 4 + self.suit.value

    def emoji(self, trump=None):
        ranks = ['6', '7', '8', '9', '10', 'В', 'Д', 'К', 'Т']
        suits = ['♠', '♣', '♦', '♥']

        is_trump = self.suit == trump.suit if trump else False
        return "{}{}{}".format(ranks[self.rank.value], suits[self.suit.value], '*' if is_trump else '')


cards = [
    Card(Rank.SIX, Suit.SPADES),
    Card(Rank.SIX, Suit.CLUBS),
    Card(Rank.SIX, Suit.DIAMONDS),
    Card(Rank.SIX, Suit.HEARTS),

    Card(Rank.SEVEN, Suit.SPADES),
    Card(Rank.SEVEN, Suit.CLUBS),
    Card(Rank.SEVEN, Suit.DIAMONDS),
    Card(Rank.SEVEN, Suit.HEARTS),

    Card(Rank.EIGHT, Suit.SPADES),
    Card(Rank.EIGHT, Suit.CLUBS),
    Card(Rank.EIGHT, Suit.DIAMONDS),
    Card(Rank.EIGHT, Suit.HEARTS),

    Card(Rank.NINE, Suit.SPADES),
    Card(Rank.NINE, Suit.CLUBS),
    Card(Rank.NINE, Suit.DIAMONDS),
    Card(Rank.NINE, Suit.HEARTS),

    Card(Rank.TEN, Suit.SPADES),
    Card(Rank.TEN, Suit.CLUBS),
    Card(Rank.TEN, Suit.DIAMONDS),
    Card(Rank.TEN, Suit.HEARTS),

    Card(Rank.JACK, Suit.SPADES),
    Card(Rank.JACK, Suit.CLUBS),
    Card(Rank.JACK, Suit.DIAMONDS),
    Card(Rank.JACK, Suit.HEARTS),

    Card(Rank.QUEEN, Suit.SPADES),
    Card(Rank.QUEEN, Suit.CLUBS),
    Card(Rank.QUEEN, Suit.DIAMONDS),
    Card(Rank.QUEEN, Suit.HEARTS),

    Card(Rank.KING, Suit.SPADES),
    Card(Rank.KING, Suit.CLUBS),
    Card(Rank.KING, Suit.DIAMONDS),
    Card(Rank.KING, Suit.HEARTS),

    Card(Rank.ACE, Suit.SPADES),
    Card(Rank.ACE, Suit.CLUBS),
    Card(Rank.ACE, Suit.DIAMONDS),
    Card(Rank.ACE, Suit.HEARTS)
]
