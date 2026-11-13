"""The Game holds all scenes and everything the player has, and runs the game loop."""
from __future__ import annotations

import difflib
import random

from textquest import effects, screen
from textquest.effects import boxed, choose, clear, drips, pause, say, show_art, jumpscare
from textquest.errors import TextQuestError
from textquest.scene import GameFunction, Option, Scene
from textquest.sound import play_sound
from textquest.video import play_video

WARNING = "Warning: this game has flashing lights and sudden scares."
BAD_ENDING = """
The arcade machines slowly shut down.

Everything goes quiet.

...

You wake up in your own bed.

Just a nightmare...

Then, from underneath your bed, a familiar voice whispers:

"Silly... silly..."
"""

GOOD_ENDING = """
The exit door finally opens.

You step through...

And find yourself in your bedroom.

On your bedside table lies an old photograph.

It's the arcade, dated 1986.

You look closer.

There you are, standing next to Lily.

She's holding your hand.

Suddenly, you hear a little girl giggling.

"Hihi... silly!"

The screen fades to black.
"""

NO_ENDING = """
You didn't even try.

The arcade machines flicker one last time.

A little girl giggles somewhere in the distance.

"Already giving up?"

The exit door slowly disappears.

Looks like you're staying here forever...
"""


class Game:
    """Your whole game.

    title        The name of your game, shown on the title screen.
    start        The name of the scene where the player starts.
    scenes       A list of scenes (you can also add them later with game.add()).
    stats        Numbers the player has, like {'health': 10, 'gold': 0}. Shown at the top.
    inventory    Items the player starts with, like ['map'].
    items        Descriptions of items, like {'torch': 'It smells of tar.'}.
    subtitle     A line shown under the title on the title screen.
    title_art    ASCII art for the title screen.
    title_color  The color of titles and numbers.
    background   The color of the terminal while the game runs, like '#0a0506'. None keeps the terminal's own.
    text_color   The color of normal text. Only used together with background.
    warning      A line on the title screen. Keep it if your game has flashes or scares. None hides it.
    text_speed   Seconds per letter for the typewriter. 0 shows all text at once.
    on_turn      A function that takes game. It runs after every option the player picks.
                 If it returns a scene name, the player goes there.
    debug        True shows scene names and lets you type 'goto <scene>' and 'state'.
    """

    def __init__(self, title: str, start: str, *, scenes: list[Scene] | None = None,
                 stats: dict[str, int] | None = None, inventory: list[str] | None = None,
                 items: dict[str, str] | None = None, subtitle: str | None = None,
                 title_art: str | None = None, title_color: str = "red",
                 background: str | None = "#0a0506", text_color: str = "#d8d0c4",
                 warning: str | None = WARNING, text_speed: float = 0.03,
                 on_turn: GameFunction | None = None, debug: bool = False):
        self.title = title
        self.start = start
        self.scenes = {}
        self.stats = dict(stats or {})
        self.inventory = list(inventory or [])
        self.items = dict(items or {})
        self.state: dict = {}
        self.subtitle = subtitle
        self.title_art = title_art
        self.title_color = title_color
        self.background = background
        self.text_color = text_color
        self.warning = warning
        self.text_speed = text_speed
        self.on_turn = on_turn
        self.debug = debug

        self.current: str | None = None
        self.visited: set[str] = set()
        self.used: set[str] = set()  # options with once=True that were picked, as "scene/label"
        self._next: str | None = None
        self.random = random.Random()

        for scene in scenes or []:
            self.add(scene)

    # ------------------------------------------------------------------
    # Building the game
    # ------------------------------------------------------------------

    def add(self, *scenes: Scene | list[Scene]):
        """Add one or more scenes: game.add(hall, kitchen)."""
        for scene in scenes:
            if isinstance(scene, (list, tuple)):
                self.add(*scene)
                continue
            if scene.name in self.scenes:
                raise TextQuestError(f"There are two scenes called '{scene.name}'. "
                                     "Every scene needs its own name.")
            self.scenes[scene.name] = scene

    def check(self) -> None:
        """Look for mistakes, like an option that goes to a scene that doesn't exist."""
        if not self.scenes:
            raise TextQuestError("Your game has no scenes yet. Add them with game.add(...).")
        self._check_name(self.start, "The start scene")
        for scene in self.scenes.values():
            for option in scene.options:
                if not isinstance(option, Option):
                    raise TextQuestError(f"Scene '{scene.name}' has {option!r} in its options. "
                                         "Only Option(...) can go in there.")
                where = f"Option '{option.label}' in scene '{scene.name}'"
                option.target = self._check_name(option.target, where)

    def _check_name(self, name, where):
        if name is None:
            return None
        if isinstance(name, Scene):
            name = name.name
        if name not in self.scenes:
            raise TextQuestError(f"{where} goes to scene '{name}', but there is no scene "
                                 f"with that name.{_did_you_mean(name, self.scenes)}")
        return name

    # ------------------------------------------------------------------
    # Things you can use in your own functions
    # ------------------------------------------------------------------

    def has(self, item: str) -> bool:
        """True if the player has this item."""
        return item in self.inventory

    def give(self, item: str, quiet: bool = False) -> None:
        """Give the player an item."""
        self.inventory.append(item)
        if not quiet:
            say(f"[bold]+ {item}[/]", speed=0)

    def take(self, item: str, quiet: bool = False) -> None:
        """Take an item away from the player (if they have it)."""
        if item in self.inventory:
            self.inventory.remove(item)
            if not quiet:
                say(f"[red]- {item}[/]", speed=0)

    def change(self, stat: str, amount: int, quiet: bool = False) -> None:
        """Make a stat go up or down: game.change('health', -2)."""
        self.stats[stat] = self.stats.get(stat, 0) + amount
        if not quiet and amount:
            style = "bold" if amount > 0 else "red"
            say(f"[{style}]{stat} {amount:+}[/]", speed=0)

    def get(self, name: str, default=None):
        """Get a stat or a flag by its name."""
        if name in self.stats:
            return self.stats[name]
        return self.state.get(name, default)

    def set(self, name: str, value=True) -> None:
        """Set a stat or a flag: game.set('talked_to_witch')."""
        if name in self.stats:
            self.stats[name] = value
        else:
            self.state[name] = value

    def was_visited(self, scene_name: str) -> bool:
        """True if the player has been in this scene before."""
        return scene_name in self.visited

    def roll(self, chance: float) -> bool:
        """True with the given chance: game.roll(0.25) is True one in four times."""
        return self.random.random() < chance

    def go(self, scene_name: str) -> None:
        """Go to another scene, from inside an on_enter or action function."""
        self._next = self._check_name(scene_name, "game.go()")

    # ------------------------------------------------------------------
    # Running the game
    # ------------------------------------------------------------------

    def run(self, title_screen: bool = True) -> str | bool | None:
        """Start the game. Returns the ending the player reached, like 'win'."""
        self._check_or_stop()
        effects.settings["text_speed"] = self.text_speed
        if self.background:
            screen.current.set_colors(self.background, self.text_color)
        try:
            return self._play(title_screen)
        finally:
            if self.background:
                screen.current.reset_colors()

    def _play(self, title_screen):
        """The game loop."""
        self.current = self.start
        if title_screen:
            self._title_screen()

        typed = True
        while True:
            scene = self.scenes[self.current]

            if typed and scene.on_enter:
                target = self._run(scene.on_enter, f"on_enter of scene '{scene.name}'")
                if target:
                    self.visited.add(scene.name)
                    self.current = target
                    continue

            self._show_scene(scene, typed)
            self.visited.add(scene.name)
            if scene.ending is not None:
                return _show_end(scene.ending)

            option = self._pick_option(scene)
            if option == "quit":
                return None
            typed = False
            if option is None:
                continue

            target = self._after_option(option, self._use_option(scene, option))
            if target:
                self.current = target
                typed = True

    def _check_or_stop(self):
        """Check the game. Show the mistake and stop if there is one."""
        try:
            self.check()
        except TextQuestError as error:
            say(boxed("Oops! " + str(error), "red"), speed=0)
            raise SystemExit(1) from None

    def _after_option(self, option, target):
        """Wait for the player to read, then run on_turn. It can send the player somewhere else."""
        if option.does_something():
            pause()
        if self.on_turn:
            return self._run(self.on_turn, "on_turn") or target
        return target

    def _run(self, function, where):
        """Run one of your functions. Returns the scene it sends the player to, or None."""
        self._next = None
        result = function(self)
        return self._next or self._check_name(result if isinstance(result, str) else None, where)

    def _title_screen(self):
        clear()
        if self.title_art:
            show_art(self.title_art, self.title_color)
            say()
        say(boxed(self.title.upper(), self.title_color), speed=0)
        say(f"[{self.title_color}]{drips(len(self.title) + 4)}[/]", speed=0)
        if self.subtitle:
            say(f"[whisper]{self.subtitle}[/]")
        say()
        if self.warning:
            say(f"[dim]{self.warning}[/]", speed=0)
            say()
        pause("Press Enter if you dare...")

    def _show_scene(self, scene, typed):
        clear()
        self._status_bar()
        if scene.title:
            say(f"[bold {self.title_color}]{scene.title}[/]", speed=0)
            say()
        if scene.art:
            show_art(scene.art, scene.art_color)
            say()
        if typed and scene.video:
            play_video(scene.video)
        if typed and scene.sound:
            play_sound(scene.sound)

        text = scene.text
        if scene.first_text and scene.name not in self.visited:
            text = scene.first_text
        if not isinstance(text, str):
            text = text(self)  # text is a function that makes the text
        say(text, speed=None if typed else 0)
        say()

    def _status_bar(self):
        parts = [f"[dim]{name.upper()}[/] [bold]{value}[/]" for name, value in self.stats.items()]
        if self.inventory:
            parts.append(f"[dim]ITEMS[/] [bold]{len(self.inventory)}[/]")
        if self.debug:
            parts.append(f"[magenta]scene: {self.current}[/]")
        if parts:
            say("   ".join(parts), speed=0)
            say("[dim]" + "─" * int(min(screen.current.width, effects.settings["max_width"])) + "[/]", speed=0)

    def _visible_options(self, scene):
        shown = []
        for option in scene.options:
            if option.once and f"{scene.name}/{option.label}" in self.used:
                continue
            available = option.is_available(self)
            if available or option.show_locked:
                shown.append((option, available))
        return shown

    def _pick_option(self, scene):
        """Show the options and wait for a choice. Returns an Option, None to redraw, or 'quit'."""
        shown = self._visible_options(scene)
        if not shown:
            say("[yellow](There is nothing to do here. Add an option to this scene, "
                "or make it an ending with ending='...'.)[/]", speed=0)
            pause("Press Enter to quit.")
            return "quit"

        numbered = {}
        for option, available in shown:
            if available:
                numbered[len(numbered) + 1] = option
                say(f"  [bold {self.title_color}]{len(numbered)}.[/] {option.label}", speed=0)
            else:
                say(f"  [dim]-  {option.label} (locked)[/]", speed=0)
        say("\n[dim]i: items   h: help   q: run away[/]", speed=0)

        while True:
            answer = screen.current.read_line("> ").strip().lower()
            if answer.isdigit() and int(answer) in numbered:
                return numbered[int(answer)]
            if answer in {"i", "inventory", "h", "help", "q", "quit"}:
                return self._menu(answer[0])
            if self.debug and (answer.startswith("goto ") or answer == "state"):
                if self._debug_command(answer):
                    return None
            else:
                say(f"[red]Type a number from 1 to {len(numbered)}.[/]", speed=0)

    def _menu(self, letter):
        """i, h or q. Returns 'quit' or None (to show the scene again)."""
        if letter == "i":
            self._show_inventory()
        elif letter == "h":
            self._show_help()
        elif choose("Run away and quit the game?", ["No", "Yes"]) == "Yes":
            return "quit"
        return None

    def _debug_command(self, answer):
        """'goto <scene>' or 'state'. Returns True if the player moved."""
        if answer == "state":
            say(f"stats: {self.stats}\ninventory: {self.inventory}\nstate: {self.state}", speed=0)
            return False
        name = answer[5:].strip()
        if name not in self.scenes:
            say(f"[red]No scene called '{name}'.{_did_you_mean(name, self.scenes)}[/]", speed=0)
            return False
        self.current = name
        return True

    def _use_option(self, scene, option):
        """Do everything the option says. Returns the scene to go to, or None to stay."""
        if option.once:
            self.used.add(f"{scene.name}/{option.label}")
        say()

        self._apply(option)
        if option.action:
            return self._run(option.action, f"The action of option '{option.label}'") or option.target
        return option.target

    def _apply(self, option):
        """Text, cost, items, stats and flag of an option."""
        if option.text:
            say(option.text)
        for stat, amount in option.cost.items():
            self.change(stat, -amount)
        for item in option.take:
            self.take(item)
        for item in option.give:
            self.give(item)
        for stat, amount in option.change.items():
            self.change(stat, amount)
        if option.flag:
            self.state[option.flag] = True

    def _show_inventory(self):
        say("[bold]You are carrying:[/]", speed=0)
        if not self.inventory:
            say("  nothing at all.", speed=0)
        for item in self.inventory:
            description = self.items.get(item)
            say(f"  - [bold]{item}[/]" + (f": {description}" if description else ""), speed=0)
        say()
        pause()

    def _show_help(self):
        say("Type the number of an option and press Enter.\n"
            "i shows your items, q runs away.", speed=0)
        if self.debug:
            say("[magenta]Debug: 'goto <scene>' jumps to a scene, 'state' shows everything.[/]", speed=0)
        say()
        pause()


def _show_end(ending):
    say()
    if ending == "lose":
        say(BAD_ENDING)
        jumpscare()
    elif ending == "win":
        say(GOOD_ENDING)
    else:
        say(NO_ENDING)
    say()
    pause("Press Enter to leave...")
    return ending


def _did_you_mean(name, options):
    close = difflib.get_close_matches(str(name), list(options), n=1)
    return f" Did you mean '{close[0]}'?" if close else ""
