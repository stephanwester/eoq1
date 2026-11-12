"""Scenes are the places in your game. Options are the choices the player can make there."""
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from textquest.game import Game

# Text can be a string, or a function that gets the game and returns a string.
Text = str | Callable[["Game"], str]
# A function you give to an option or scene. It may return the name of a scene to go to.
GameFunction = Callable[["Game"], "str | None"]
Items = str | list[str]


class Scene:
    """A place in your game.

    name        A short unique name, like 'crypt'. Options use it to go here.
    title       Shown at the top of the screen.
    text        What the player sees. Can use tags like [red]...[/].
                Can also be a function that takes game and returns the text.
    options     A list of Option(...) the player can choose from.
    first_text  Shown instead of text the first time the player is here.
    art         ASCII art shown above the text.
    art_color   Color for the art, like 'green'.
    on_enter    A function that takes game. It runs every time the player arrives.
                If it returns a scene name, the player goes there instead.
    ending      Makes this scene an end of the game, like ending='win' or ending='lose'.
    sound       A sound file to play when the player arrives.
    video       A video file to play when the player arrives, before the text.
    """

    def __init__(self, name: str, *, title: str = "", text: Text = "",
                 options: list[Option] | None = None, first_text: Text | None = None,
                 art: str | None = None, art_color: str | None = None,
                 on_enter: GameFunction | None = None, ending: str | bool | None = None,
                 sound: str | Path | None = None, video: str | Path | None = None):
        self.name = name
        self.title = title
        self.text = text
        self.options = options or []
        self.first_text = first_text
        self.art = art
        self.art_color = art_color
        self.on_enter = on_enter
        self.ending = ending
        self.sound = sound
        self.video = video

    def __repr__(self):
        return f"Scene({self.name!r})"


class Option:
    """A choice the player can make in a scene.

    label        The text the player sees, like 'Open the coffin'.
    target       The name of the scene to go to. Leave it out to stay in this scene.
    text         Shown after the player picks this option.

    Items and stats:
    give         An item (or list of items) the player gets.
    take         An item (or list of items) the player loses.
    needs        Only show this option if the player has these items.
    cost         Stats the player pays, like cost={'gold': 5}. Only shown if they can pay.
    change       Stats that go up or down, like change={'health': -2}.
    requires     Only show this option if stats are high enough, like requires={'strength': 3}.

    Flags (things you want to remember, like 'talked_to_witch'):
    flag         Remember this flag when the option is picked.
    needs_flag   Only show this option if this flag was set.
    unless_flag  Hide this option once this flag was set.

    More:
    once         Hide this option after it was picked once.
    action       A function that takes game. If it returns a scene name, the player goes there.
    condition    A function that takes game and returns True to show this option.
    show_locked  Show this option as locked when it is not available, instead of hiding it.
    """

    def __init__(self, label: str, target: str | Scene | None = None, *,
                 text: str | None = None,
                 give: Items | None = None, take: Items | None = None, needs: Items | None = None,
                 cost: dict[str, int] | None = None, change: dict[str, int] | None = None,
                 requires: dict[str, int] | None = None,
                 flag: str | None = None, needs_flag: str | None = None, unless_flag: str | None = None,
                 once: bool = False, action: GameFunction | None = None,
                 condition: Callable[[Game], bool] | None = None, show_locked: bool = False):
        self.label = label
        self.target = target
        self.text = text
        self.give = as_list(give)
        self.take = as_list(take)
        self.needs = as_list(needs)
        self.cost = cost or {}
        self.change = change or {}
        self.requires = requires or {}
        self.flag = flag
        self.needs_flag = needs_flag
        self.unless_flag = unless_flag
        self.once = once
        self.action = action
        self.condition = condition
        self.show_locked = show_locked

    def is_available(self, game: Game) -> bool:
        """True if the player may pick this option right now."""
        if any(not game.has(item) for item in self.needs):
            return False
        for stat, amount in list(self.requires.items()) + list(self.cost.items()):
            if game.stats.get(stat, 0) < amount:
                return False
        if self.needs_flag and not game.state.get(self.needs_flag):
            return False
        if self.unless_flag and game.state.get(self.unless_flag):
            return False
        if self.condition:
            return bool(self.condition(game))
        return True

    def does_something(self):
        """True if picking this option shows a message or changes anything."""
        return bool(self.text or self.give or self.take or self.cost or self.change or self.action)

    def __repr__(self):
        return f"Option({self.label!r})"


def as_list(value: Items | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return list(value)
    return [value]
