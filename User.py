from __future__ import annotations
from typing import List, Optional
from Activity import Activity
import sqlite3
import requests
from database import connection


class User:
    def __init__(
        self,
        id: str,
        name: str,
        picture: str,
        streak: int,
        token: str,
    ) -> None:
        self.id = id
        self.name = name
        self.picture = picture
        self.streak = streak
        self.token = token
        self.sync_with_database()

    def add_to_database(self) -> bool:
        "add the user if it doesn't exist"

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (self.id,))
        existing_user = cursor.fetchone()
        if existing_user:
            return False
        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?, ?, ?)",
            (self.id, self.name, self.picture, self.streak, self.token),
        )
        connection.commit()

        return True

    def sync_with_database(self) -> None:
        """Updates the already existing user in the database based on their ID."""
        if not self.add_to_database():
            return

        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET id = ?, name = ?, picture = ?, streak = ?, token = ? WHERE id = ?",
            (self.id, self.name, self.picture, self.streak, self.token, self.id),
        )
        connection.commit()

    def login(email: str, password: str) -> Optional[User]:
        """
        Login to Pomofocus with email and password.

        Args:
            email (str): The email of the user.
            password (str): The password of the user.
        Returns:
            str: The token for the logged in user.
        """

        response = requests.post(
            f"https://pomofocus.io/login-with-email",
            json={"password": password, "email": email},
        )
        if response.status_code != 200:
            # check if the user is in the database and if yes, remove them
            cursor = connection.cursor()
            cursor.execute("DELETE FROM CREDENTIALS WHERE email = ?", (email,))
            connection.commit()
            return

        data = response.json()

        return User.get_user_data(data["token"])

    def get_user_data(token: str) -> User:
        response = requests.get(
            f"https://pomofocus.io/api/user",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"token": token},
        )

        data = response.json()
        return User(
            data["_id"], data["name"], data["picture"], data["dayStreak"], token
        )

    def get_daily_work_minutes(self):
        response = requests.get(
            "https://pomofocus.io/api/daily-work-minutes?todayStr=18-Nov-2024&daysBefore=7&backCnt=0",
            headers={"Content-Type": "application/json", "Authorization": self.token},
        )
        data = response.json()
        """
        Response:
        {
            "reportsResult": [
                {
                    "dateStr": "12-Nov-2024",
                    "projectName": "",
                    "minutes": 168.49
                },
                {
                    "dateStr": "16-Nov-2024",
                    "projectName": "",
                    "minutes": 30.02
                },
                {
                    "dateStr": "13-Nov-2024",
                    "projectName": "",
                    "minutes": 240.1
                },
                {
                    "dateStr": "14-Nov-2024",
                    "projectName": "",
                    "minutes": 82.77000000000001
                },
                {
                    "dateStr": "17-Nov-2024",
                    "projectName": "",
                    "minutes": 100.66
                }
            ],
            "dateDigitStart": "20241111",
            "dateDigitEnd": "20241118"
        }
        """

        ordered_list = sorted(
            data["reportsResult"], key=lambda x: int(x["dateStr"].split("-")[0])
        )

        consecutive_days = 0
        last_day = None
        for report in ordered_list:
            if last_day is None:
                last_day = int(report["dateStr"].split("-")[0])
                consecutive_days += 1
            else:
                if int(report["dateStr"].split("-")[0]) == last_day + 1:
                    consecutive_days += 1
                    last_day += 1

        self.streak = consecutive_days
        self.sync_with_database()
        return data["reportsResult"]

    def get_activities_from_database(self) -> List[Activity]:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM activities WHERE user_id = ?", (self.id,))
        activities = cursor.fetchall()
        return [Activity(*activity) for activity in activities]

    def daily_report(self) -> List[Activity]:
        response = requests.get(
            f"https://pomofocus.io/api/daily-report-items",
            headers={"Content-Type": "application/json", "Authorization": self.token},
        )

        output: List[Activity] = []
        for item in response.json()["dailyReportItems"]:
            output.append(
                Activity(
                    item["_id"],
                    item["task"],
                    item["minutes"],
                    self.id,
                    item["created"],
                )
            )

        self.get_daily_work_minutes()
        return output

    def add_credentials(email: str, password: str) -> Optional[User]:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM CREDENTIALS WHERE email = ?", (email,))
        if cursor.fetchone():
            return None

        user = User.login(email, password)
        if user is not None:
            cursor.execute("INSERT INTO CREDENTIALS VALUES (?, ?)", (email, password))
            connection.commit()
            return user

    def get_all_users() -> List[User]:
        """
        Select all users from credentials and return them as a list of User objects while making sure they can be logged in
        """
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM CREDENTIALS")
        users = cursor.fetchall()
        for i in range(len(users)):
            user = User.login(users[i][0], users[i][1])
            if user is not None:
                users[i] = user

        return users

    def __repr__(self) -> str:
        return f"User(name={self.name}, picture={self.picture}, streak={self.streak})"

    def get_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "picture": self.picture,
            "streak": self.streak,
        }
