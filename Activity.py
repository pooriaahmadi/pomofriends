from database import connection
from datetime import datetime, timezone
from dateutil.parser import isoparse


class Activity:
    def __init__(
        self, id: str, task_name: str, minutes_spent: float, user_id: str, created: str
    ) -> None:
        self.id = id
        self.task_name = task_name
        self.minutes_spent = minutes_spent
        self.user_id = user_id
        self.created = isoparse(created)

        self.add_to_database()

    def add_to_database(self) -> None:
        "add the activity if it doesn't exist"

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM activities WHERE id = ?", (self.id,))
        existing_activity = cursor.fetchone()
        if existing_activity:
            return

        self.created = datetime.now(timezone.utc)
        cursor.execute(
            "INSERT INTO activities VALUES (?, ?, ?, ?, ?)",
            (
                self.id,
                self.task_name,
                self.minutes_spent,
                self.user_id,
                self.created.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            ),
        )
        connection.commit()

    def __repr__(self) -> str:
        return f"Activity(id={self.id}, task_name={self.task_name}, minutes_spent={self.minutes_spent}, user_id={self.user_id}, created={self.created})"
