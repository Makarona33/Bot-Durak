from vkbottle import BaseStateGroup


class CreateGameState(BaseStateGroup):
    SET_BET = 0


class PlayingState(BaseStateGroup):
    ATTACKER = 0
    DEFENDER = 1
    SUCCESSFUL_DEFENCE = 2
    ABANDON_THE_DEFENCE = 3


class SettingsState(BaseStateGroup):
    CHANGE_NICKNAME = 0
