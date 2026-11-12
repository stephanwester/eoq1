from turtle import Screen, Turtle
from .snake import Snake
from .food import Food
from .scoreboard import Scoreboard
import time


def setup_screen():
    screen = Screen()
    screen.setup(width=600, height=600)
    screen.bgcolor("#17151b")
    screen.title("ROOM 13 | Cursed Snake")
    screen.tracer(0)

    return screen


def setup_controls(screen, snake):
    screen.listen()
    screen.onkey(snake.up, "Up")
    screen.onkey(snake.down, "Down")
    screen.onkey(snake.left, "Left")
    screen.onkey(snake.right, "Right")

    screen.onkey(snake.up, "w")
    screen.onkey(snake.down, "s")
    screen.onkey(snake.left, "a")
    screen.onkey(snake.right, "d")
    
    screen.onkey(snake.up, "W")
    screen.onkey(snake.down, "S")
    screen.onkey(snake.left, "A")
    screen.onkey(snake.right, "D")


def check_wall_collision(snake):
    return bool(
        snake.head.xcor() > 280
        or snake.head.xcor() < -280
        or snake.head.ycor() > 280
        or snake.head.ycor() < -280
    )


def check_tail_collision(snake):
    for segment in snake.segments[1:]:
        if snake.head.distance(segment) < 10:
            return True

    return False


def show_death_message(screen, lives):
    message = Turtle()
    message.hideturtle()
    message.penup()
    message.color("#c94b50")

    if lives == 2:
        text = "Oops... That was embarrassing."
    elif lives == 1:
        text = "Wow... You're really bad at this."
    else:
        text = "Oh dear... Was that really your best?"

    message.write(text, align="center", font=("DejaVu Sans Mono", 13, "bold"))

    screen.update()
    time.sleep(2)
    message.clear()


def show_result(screen, snake, food, scoreboard, won):
    # Hide game objects
    for segment in snake.segments:
        segment.hideturtle()

    food.hideturtle()
    scoreboard.clear()
    scoreboard.goto(0, 20)

    if won:
        scoreboard.write(
            "THE CURSE IS BROKEN", align="center", font=("DejaVu Sans Mono", 20, "bold")
        )
    else:
        scoreboard.write(
            "THE ARCADE CLAIMS YOUR SOUL",
            align="center",
            font=("DejaVu Sans Mono", 18, "bold"),
        )

    screen.update()
    screen.exitonclick()


def play_snake_game():
    """ Return a bool with won true if successful or false if fail"""
    screen = setup_screen()
    snake = Snake()
    food = Food()
    scoreboard = Scoreboard()

    setup_controls(screen, snake)

    lives = 3
    speed = 0.1
    game_is_on = True
    won = False

    while game_is_on:
        screen.update()
        time.sleep(speed)
        snake.move()

        # Detect collision with food
        if snake.head.distance(food) < 15:
            food.refresh()
            snake.extend()
            scoreboard.increase_score()

            # Win after collecting 13 souls
            if scoreboard.score >= 13:
                won = True
                game_is_on = False

            # Increase speed every 4 points
            elif scoreboard.score % 4 == 0:
                speed = max(0.05, speed - 0.01)

        if won:
            break

        # Detect collision with wall or tail
        if check_wall_collision(snake) or check_tail_collision(snake):
            lives -= 1
            scoreboard.reset()

            show_death_message(screen, lives)

            if lives == 0:
                game_is_on = False
            else:
                snake.reset_snake()

    show_result(screen, snake, food, scoreboard, won)

    return won


if __name__ == "__main__":
    play_snake_game()
