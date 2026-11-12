# Room 13 kit

The starter kit for Room 13. You build a text adventure, and you can add minigames, sounds and videos to it.

- **textquest**: text adventures in the terminal, with a horror look. You write scenes and options, textquest runs the game.
- **Minigames**: any function can be a minigame. Build your own, or use **tetris**, a plain Tetris that's made to be changed.
- **Videos**: play your own short clips inside the game.

The code in `textquest/` and `tetris/` is yours too: read it, change it.

The project brief is in `website/index.html`. Open it in your browser.

## Start

```bash
poetry install
poetry run python examples/room_13.py
```

Works on Linux, macOS and WSL. On WSL, Tetris and videos need Windows 11 (WSLg), and sound needs one extra step:

```bash
sudo apt install libpulse0
```

## Examples

They're short. Read them, run them, copy one to start your own game.

| File | Shows |
| --- | --- |
| `examples/first_game.py` | textquest basics: three scenes. |
| `examples/room_13.py` | Items, stats, flags, a riddle, art, sound, jump scares, and losing when your courage runs out. |
| `examples/hold_your_breath.py` | A small minigame in the terminal. |
| `examples/click_the_monster.py` | A small minigame in a window: click the monster for 10 seconds. |
| `examples/video.py` | A scene that plays a video. |
| `examples/tetris_minigame.py` | Tetris inside an adventure, with your own piece and a time limit. |

`examples/media/` has sounds, a clip and a monster you may use.

## textquest

```python
from textquest.game import Game
from textquest.scene import Scene, Option
from textquest.effects import say, ask, choose, pause, wait, wait_for_key, clear, boxed, show_art
from textquest.effects import flicker, static, jumpscare
from textquest.sound import play_sound
from textquest.video import play_video
```

### The basics

- `Game("Title", start="hall")` holds your game. `game.add(...)` adds scenes, `game.run()` starts it.
- `Scene("hall", title=..., text=..., options=[...])` is a place. Every scene needs its own name.
- `Option("Go north", "kitchen")` is a choice: the label, then the scene it goes to. Leave out the scene to stay.
- `Scene(..., ending="win")` ends the game. Any word works: `"win"`, `"lose"`, `"secret"`.
- `Game(..., stats={"courage": 10}, inventory=["map"], items={"map": "A torn map."})` sets up stats and items. Stats are shown at the top. Item descriptions are shown when the player presses `i`.

### The look

The game is dark by default. Change it in `Game(...)`:

| Setting | What it does |
| --- | --- |
| `title_color="red"` | The color of titles and option numbers. |
| `background="#0a0506"`, `text_color="#d8d0c4"` | The terminal's colors while the game runs. `background=None` keeps your own. |
| `subtitle="..."`, `title_art=MY_ART` | More on the title screen. |
| `warning=None` | Hides the warning about flashes and scares. Only do this if your game has none! |
| `text_speed=0.03` | Seconds per letter. `0` turns the typing off. |

### Options

| Setting | What it does |
| --- | --- |
| `text="..."` | Message after picking it. |
| `give="torch"` / `take="torch"` | Give or take an item (or a list of items). |
| `needs="key"` | Only shown if the player has the item. |
| `cost={"gold": 5}` | The player pays. Only shown if they can. |
| `change={"health": -2}` | Stats go up or down. |
| `requires={"strength": 3}` | Only shown if the stat is high enough. |
| `flag="met_witch"` | Remember that this happened. |
| `needs_flag="met_witch"` / `unless_flag=...` | Only shown if the flag is set / not set. |
| `once=True` | Gone after picking it once. |
| `show_locked=True` | Show it as locked instead of hiding it. |
| `action=my_function` | Run your own function. |
| `condition=my_function` | Your function decides if the option is shown. |

### Scenes

| Setting | What it does |
| --- | --- |
| `first_text="..."` | Shown the first time only. After that, `text` is shown. |
| `art=MY_ART, art_color="green"` | ASCII art above the text. Write it as `r"""..."""`. |
| `sound="creak.wav"` | Plays when the player arrives. |
| `video="clip.mp4"` | Plays when the player arrives, before the text. |
| `on_enter=my_function` | Runs when the player arrives. |
| `text=my_function` | Text that changes: your function returns it. |

### Tags

Add style to any text, close it with `[/]`:

| Tag | What it does |
| --- | --- |
| `[red]`, `[white]`, `[orange]`, `[purple]`... | Color. `[on_red]` colors the background. |
| `[bold]`, `[dim]`, `[italic]`, `[underline]` | Style. Combine them: `[bold red]`. |
| `[slow]`, `[fast]`, `[instant]` | Typing speed. |
| `[pause]`, `[pause=2]` | Wait 1 or 2 seconds. |
| `[glitch]` | Letters flicker before they appear. |
| `[whisper]` | Dim, slanted and slow. |
| `[blood]` | Bold and red. |

Add your own, like `[whisper]`, to `MOODS` in `textquest/markup.py`.

Text types itself. The player can press a key to skip.

### Your own functions

Your function always gets `game`. If it returns a scene name, the player goes there.

Besides `action`, `condition`, `on_enter` and `text`, there's one for the whole game: `Game(..., on_turn=my_function)` runs after every option the player picks.

| Code | Does |
| --- | --- |
| `game.has("key")` | `True` if the player has it. |
| `game.give("key")`, `game.take("key")` | Give or take an item. |
| `game.change("gold", 5)` | Change a stat. |
| `game.get("gold")`, `game.set("met_witch")` | Read a stat or flag, set a flag. |
| `game.was_visited("crypt")` | `True` if the player has been there. |
| `game.roll(0.3)` | `True` 30% of the time. |
| `game.stats`, `game.inventory`, `game.state` | Everything the player has, as a dict, a list and a dict. |
| `say(text)` | Show text with tags. Use it instead of `print`. |
| `ask("Your name?")` | Returns what the player typed. |
| `choose("Which door?", ["Left", "Right"])` | Returns the one they picked. |
| `pause()`, `wait(2)`, `clear()` | Wait for Enter, wait 2 seconds, clear the screen. |
| `wait_for_key(3)` | Wait up to 3 seconds. `True` if a key was pressed. |
| `boxed(text, "red")`, `show_art(art, "green")` | A box around text, ASCII art. |
| `play_sound("boom.wav")` | Play a sound. |
| `play_video("clip.mp4")` | Play a video. Any key skips it. `fullscreen=False` shows it in a small window. |

### Scares

| Code | Does |
| --- | --- |
| `flicker()` | The screen flashes, like failing lights. |
| `static(1)` | TV noise for 1 second. |
| `jumpscare()` | A face fills the screen, with one flash. |
| `jumpscare(MY_ART, sound="sting.wav")` | Your own art, with a sound. |

Scares work best when they're rare. A long quiet part makes the next one much worse.

Keep it scary, not gross: no gore. And don't make flashes faster than 3 per second, because that can be dangerous for people with epilepsy.

### Playing and testing

The player types a number, or `i` (items), `h` (help) or `q` (run away). While building:

- `Game(..., debug=True)` shows the scene name, and lets you type `goto crypt` or `state`.
- `game.run(title_screen=False)` skips the title screen.
- Before the game starts, textquest checks it. A typo in a scene name gives a clear message, like *"...goes to scene 'kitchn', but there is no scene with that name. Did you mean 'kitchen'?"*
- A tag that shows up as text, like `[rde]`, is misspelled.

### Ideas for textquest

None of these are built in. Each one needs only a few lines with the tools above.

| Idea | Look at |
| --- | --- |
| A fear meter that changes the text | `text=my_function`, `game.get("fear")` |
| A flashlight with a battery that runs out | `on_turn`, `game.change` |
| A narrator who lies | `first_text`, `game.was_visited` |
| Random events: a noise that happens sometimes | `on_enter`, `game.roll` |
| Using the player's name in scary places | `ask`, `game.set`, `text=my_function` |
| Saving and loading | `json`, `game.stats`, `game.inventory`, `game.state`, `game.current` |
| Your own text effect, next to `[glitch]` | `textquest/markup.py` and `textquest/effects.py` |

## Minigames

A minigame is a function. An option runs it, it does what it wants, and it returns the name of the next scene:

```python
def pick_the_lock(game):
    ...
    return "inside"

Option("Pick the lock", action=pick_the_lock)
```

That's all. There's nothing to register and no class to inherit from. It can use `say`, `ask`, `choose` and `wait_for_key` in the terminal, or open its own pygame window. `examples/hold_your_breath.py` and `examples/click_the_monster.py` show one of each.

### Ideas for minigames

| Idea | Look at |
| --- | --- |
| Remember the code on the wall | `say`, `clear`, `ask` |
| Choose the right wire before time runs out | `choose`, `wait_for_key` |
| Press the right key at the right moment | `wait_for_key`, `game.random` |
| Walk through a dark maze | `ask`, a list of strings |
| Your own pygame game | `examples/click_the_monster.py` |
| Tetris | See below |

## tetris

```python
from tetris.game import Tetris
from tetris.pieces import Piece, CLASSIC
from tetris.themes import Theme, THEMES
from tetris.window import KEYS
```

`Tetris(...).play()` opens a window. When the game is over, you get the result back. Every setting is optional.

To use it as a minigame, start it in your function and use the result:

- `result["won"]` decides where the player goes: return a scene name.
- `result["score"]`, `result["cleared"]` and your own `result["info"]` can become stats or items.

`examples/tetris_minigame.py` shows all of it in one short file.

### The result

`play()` returns a dict:

| Key | What it is |
| --- | --- |
| `won` | `True` if your code ended the game with `game.end(won=True)`. Filling the board to the top loses. |
| `score`, `lines`, `level` | The numbers at the end. |
| `time`, `pieces` | Seconds played, pieces used. |
| `quit` | `True` if the player pressed Esc or closed the window. |
| `cleared` | Cleared blocks per piece, like `{"T": 8, "skull": 3}`. |
| `info` | Your own numbers, see `info=` below. |

### Settings

| Setting | What it does |
| --- | --- |
| `title="..."`, `message="..."` | Shown at the top, and on the start screen. |
| `columns=10`, `rows=20` | Board size. Wide and low works too. |
| `level=1` | Start level. Higher is faster. |
| `lines_per_level=10` | Lines needed for the next level. `None` keeps the speed the same. |
| `pieces=[...]` | Which pieces fall. See [Pieces](#pieces). |
| `hold=False`, `ghost=False`, `preview=1` | Turn off hold, the landing outline, or show fewer next pieces. |
| `theme="retro"` | How it looks. See [Themes](#themes). |
| `intro=False` | Skip the start screen. |
| `info={"Boss": 10}` | Your own numbers, shown next to the board. |

### Pieces

Draw a piece with `#` and `.`, then give it a name and a color:

```python
CROSS = Piece("cross", """
    .#.
    ###
    .#.
""", "red")
```

`examples/tetris_minigame.py` has one too. Colors can be names (`"red"`, `"hotpink"`), codes (`"#ff8800"`) or `(255, 136, 0)`. Use it with `pieces=[*CLASSIC, CROSS]`.

| Option | What it does |
| --- | --- |
| `weight=2` | Falls twice as often. `0.5` is half as often. |
| `image="skull.png"` | Draw a picture on every block of this piece. |
| `on_lock=my_function` | Runs when this piece lands. |

### Your own functions in tetris

Your function always gets `game`, just like in textquest.

| Setting | Runs |
| --- | --- |
| `on_start=f` | Before the first piece falls. |
| `on_lock=f` | When a piece lands. |
| `on_clear=f` | When lines are cleared. |
| `on_second=f` | Every second. |
| `keys={"b": f}` | When the player presses B. The start screen lists it, named after your function. |

| Code | Does |
| --- | --- |
| `game.end(won=True)` | Stop the game. |
| `game.say("Boo!")` | Show a message on the board. |
| `game.shake()`, `game.flash("red")` | Shake the board, flash the screen. |
| `game.lights_out(3)` | Only the falling piece can be seen for 3 seconds. |
| `game.add_block(x, y, "red")`, `game.remove_block(x, y)` | Change the board. (0, 0) is the top left. |
| `game.blocks` | Every block on the board: `{(x, y): Block}`. |
| `game.set_next("I")` | Choose the next piece, by name or as a `Piece`. |
| `game.queue` | The next pieces. |
| `game.gravity = False` | Pieces only fall when the player pushes them. |
| `game.info["Boss"] -= 1` | Change your own numbers. |
| `game.score`, `game.lines`, `game.level`, `game.time`, `game.pieces_used` | Read or change them. |
| `game.just_cleared` | Lines cleared by the last piece. |
| `game.just_cleared_blocks` | The names of the pieces those blocks came from. |
| `game.landed` | Where the last piece landed, as `(x, y)` spots. |

### Themes

`spooky` (the default), `neon`, `retro` and `dungeon`. Change one with `THEMES["spooky"].change(block_style="round")`, or make your own with `Theme(...)`:

| Setting | What it does |
| --- | --- |
| `background`, `board`, `grid`, `border`, `text`, `title` | Colors. `grid=None` hides the grid. |
| `block_style` | `glow`, `classic`, `flat`, `round`, `outline` or `pixel`. Or your own function: see the bottom of `tetris/window.py`. |
| `bloom` | Blocks give off light. |
| `flicker` | The lights fail now and then. |
| `piece_colors={"T": "hotpink"}` | Change the color of a piece. |
| `background_image`, `font` | Your own picture or font file. |
| `sounds={"clear": "boom.wav"}` | Your own sounds for `rotate`, `lock`, `hold`, `clear`, `tetris`, `level`, `win` and `lose`. |
| `beeps=False` | Turn off the built-in beeps. |
| `music="song.ogg"` | Music that loops while playing. |

### Controls

Arrows move and rotate, Z rotates back, Space drops, C holds, P pauses and Esc gives up. Change them in `KEYS`, for example `KEYS["drop"] = [pygame.K_RETURN]`.

### Ideas for tetris

None of these are built in. Each one needs only a few lines with the tools above.

| Idea | Look at |
| --- | --- |
| Sprint: clear 40 lines, the best time wins | `on_clear`, `game.lines`, `game.end()` |
| Puzzle: a filled board and a few pieces | `on_start`, `add_block`, `set_next`, `gravity` |
| Rising floor: a row of junk every 10 seconds | `on_second`, `game.blocks` |
| A cursed piece that explodes | `Piece(on_lock=...)`, `game.landed`, `remove_block` |
| Invisible blocks, or lights out every 13 seconds | `on_lock` or `on_second`, `game.lights_out()` |
