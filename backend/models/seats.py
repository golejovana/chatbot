from db import get_db_connection

def get_free_seats():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT free_seats FROM reading_room_status WHERE id = 1")
    result = cursor.fetchone()
    db.close()
    return result[0]


def decrease_free_seats():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE reading_room_status
        SET free_seats = free_seats - 1
        WHERE id = 1 AND free_seats > 0
    """)
    db.commit()
    db.close()


def increase_free_seats():
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE reading_room_status
        SET free_seats = free_seats + 1
        WHERE id = 1
    """)
    db.commit()
    db.close()
