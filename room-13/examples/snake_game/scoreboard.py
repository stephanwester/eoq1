from turtle import Turtle

ALIGNMENT = "center"
FONT = ("DejaVu Sans Mono", 15, "bold")


class Scoreboard(Turtle):

    def __init__(self):
        super().__init__()
        self.score = 0
        self.color("#c94b50")
        self.penup()
        self.goto(0, 260)
        self.hideturtle()
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(
            f"Souls: {self.score}/13",
            align=ALIGNMENT,
            font=FONT
        )

    def reset(self):
        self.score = 0
        self.update_scoreboard()

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()
