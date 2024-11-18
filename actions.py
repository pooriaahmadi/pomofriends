import requests
from User import User
from Activity import Activity
from typing import List
from database import connection
from datetime import datetime, timedelta, timezone


def get_leaderboard(users: List[User], time_frame_days=2) -> list:
    """
    Get the leaderboard for today. based off of most hours of studied today.

    Args:
        users (List[User]): The list of users to get the leaderboard for.
    Returns:
        List[User]: The list of users sorted by their studying today.
    """
    tmp = []
    for user in users:
        activities = user.get_activities_from_database()

        # Filter out the activities that are not from today
        today = datetime.now(timezone.utc)
        day_limit = today - timedelta(days=time_frame_days)
        for activity in activities:
            print(activity.created.date())
        activities = [
            activity for activity in activities if activity.created >= day_limit
        ]
        total_minutes = sum(activity.minutes_spent for activity in activities)
        tmp.append([user, total_minutes])

    return sorted(tmp, key=lambda x: x[1], reverse=True)


def get_streak(users: List[User]) -> list:
    """
    Get the streak for today. based off of consecutive days studied.

    Args:
        users (List[User]): The list of users to get the streak for.
    Returns:
        List[User]: The list of users sorted by their streak.
    """
    return sorted(users, key=lambda x: x.streak, reverse=True)
