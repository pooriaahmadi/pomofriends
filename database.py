import sqlite3


connection = sqlite3.connect("database.db", check_same_thread=False)


def initialize():
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id TEXT, name TEXT, picture TEXT, streak INTEGER, token TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS activities (id TEXT, task_name TEXT, minutes_spent REAL, user_id TEXT, created TEXT)"
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS CREDENTIALS (email TEXT, password TEXT)")
    connection.commit()
