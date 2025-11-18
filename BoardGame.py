#Example Flask App for a hexaganal tile game
#Logic is in this python file
from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

# ---------------------------------------------
# GAME DATA
# ---------------------------------------------

players = ["Messi", "Ronaldo", "Salah"]
positions = {p: 0 for p in players}
current_player_index = 0

# A simple "world board" in order
world_board = [
    "USA", "Brazil", "England", "Spain", "Germany",
    "Egypt", "Argentina", "France", "Portugal", "Japan"
]

# Harder soccer/world-cup-themed trivia
questions = {
    "USA": ("Which US city hosted the 1994 World Cup Final?", "Pasadena"),
    "Brazil": ("Who scored the winning penalty in the 1994 World Cup for Brazil?", "Dunga"),
    "England": ("Which English team did Cristiano Ronaldo first play for?", "Manchester United"),
    "Spain": ("Which club has Lionel Messi scored the most goals for?", "Barcelona"),
    "Germany": ("Germany won the 2014 World Cup. Who scored the winning goal?", "Mario Gotze"),
    "Egypt": ("What club did Mohamed Salah play for before joining Liverpool?", "Roma"),
    "Argentina": ("Diego Maradona scored the famous 'Hand of God' goal in what year?", "1986"),
    "France": ("Who was the captain of France when they won the 2018 World Cup?", "Lloris"),
    "Portugal": ("Which club did Ronaldo play for before Manchester United signed him?", "Sporting"),
    "Japan": ("Japan and which other country co-hosted the 2002 World Cup?", "South Korea"),
}

# Tracks whether each player got the question right at each country
player_correct_answers = {p: set() for p in players}

# ---------------------------------------------
# HTML TEMPLATE (all inside Python for simplicity)
# ---------------------------------------------

page = """
<!DOCTYPE html>
<html>
<head>
    <title>World Soccer Trivia Board Game</title>
</head>
<body style="font-family:Arial; max-width:800px; margin:auto;">

<h1>🌍 World Soccer Trivia Game</h1>

<h2>Players:</h2>
<ul>
{% for p in players %}
    <li>{{ p }} — Position: {{ positions[p] }} ({{ world_board[positions[p]] }}) — Correct Answers: {{ player_correct_answers[p]|length }}</li>
{% endfor %}
</ul>

<h2>Current turn: {{ current_player }}</h2>

<form action="/roll" method="post">
    <button type="submit">Roll Dice 🎲</button>
</form>

{% if question %}
    <h2>Trivia for {{ country }}:</h2>
    <p><b>{{ question }}</b></p>

    <form action="/answer" method="post">
        <input type="text" name="answer" placeholder="Your answer">
        <button type="submit">Submit</button>
    </form>
{% endif %}

{% if winner %}
    <h1>🏆 WINNER: {{ winner }} !!!</h1>
    <p>They answered all questions correctly!</p>
{% endif %}

</body>
</html>
"""

# ---------------------------------------------
# ROUTES
# ---------------------------------------------

@app.route("/")
def index():
    global current_player_index
    return render_template_string(
        page,
        players=players,
        positions=positions,
        world_board=world_board,
        current_player=players[current_player_index],
        question=None,
        country=None,
        player_correct_answers=player_correct_answers,
        winner=check_winner()
    )

@app.route("/roll", methods=["POST"])
def roll():
    """Roll dice and move player."""
    global current_player_index

    player = players[current_player_index]
    roll = random.randint(1, 6)
    positions[player] = (positions[player] + roll) % len(world_board)

    return redirect(url_for("ask_question"))

@app.route("/ask")
def ask_question():
    """Ask trivia question for the country the player landed on."""
    global current_player_index
    player = players[current_player_index]

    country = world_board[positions[player]]
    question, _ = questions[country]

    return render_template_string(
        page,
        players=players,
        positions=positions,
        world_board=world_board,
        current_player=player,
        question=question,
        country=country,
        player_correct_answers=player_correct_answers,
        winner=check_winner()
    )

@app.route("/answer", methods=["POST"])
def answer():
    global current_player_index

    player = players[current_player_index]
    country = world_board[positions[player]]
    correct_answer = questions[country][1].lower().strip()
    user_answer = request.form["answer"].lower().strip()

    if user_answer == correct_answer:
        player_correct_answers[player].add(country)

    # Move to next player's turn
    current_player_index = (current_player_index + 1) % len(players)

    return redirect(url_for("index"))

# ---------------------------------------------
# WIN CONDITION
# ---------------------------------------------

def check_winner():
    for p in players:
        if len(player_correct_answers[p]) == len(world_board):
            return p
    return None

# ---------------------------------------------
# START GAME
# ---------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
