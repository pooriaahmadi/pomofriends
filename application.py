from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from database import initialize
from User import User
from actions import get_leaderboard
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

load_dotenv()
initialize()


users = User.get_all_users()
for user in users:
    user.daily_report()


app = Flask(__name__)


def scheduled_task():
    for user in users:
        user.daily_report()


# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_task, trigger="interval", minutes=60)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


@app.route("/")
def landing_page():
    past_two_days = map(lambda x: [x[0].get_dict(), x[1]], get_leaderboard(users, 2))
    past_seven_days = map(lambda x: [x[0].get_dict(), x[1]], get_leaderboard(users, 7))

    return render_template(
        "index.html", past_two_days=past_two_days, past_seven_days=past_seven_days
    )


@app.route("/add_account", methods=["GET", "POST"])
def add_account():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username and password:
            return jsonify({"error": "Please provide both username and password."}), 400

        result = User.add_credentials(username, password)
        if result is None:
            return (
                jsonify({"error": "Account already exists or credential is invalid"}),
                400,
            )

        result.daily_report()
        users.append(result)

        return jsonify({"message": "Account added successfully."}), 200

    return render_template("add_account.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)
