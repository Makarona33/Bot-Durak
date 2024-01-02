from . import menu, playing, profile, settings, bonus

labelers = [menu.labeler, *playing.labelers, profile.labeler, settings.labeler, bonus.labeler]

__all__ = ["labelers"]
