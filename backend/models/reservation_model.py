from db import cursor, db
from datetime import datetime

def cancel_reservation(user_id, seat_number=None):
    """
    Otkazuje rezervaciju korisnika.
    Ako seat_number nije prosleđen → otkazuje njegovu AKTIVNU rezervaciju.
    """

    # 1. Pronađi aktivnu rezervaciju korisnika
    if seat_number:
        cursor.execute(
            "SELECT * FROM reservations WHERE user_id = %s AND seat_number = %s AND status = 'active'",
            (user_id, seat_number)
        )
    else:
        cursor.execute(
            "SELECT * FROM reservations WHERE user_id = %s AND status = 'active'",
            (user_id,)
        )

    reservation = cursor.fetchone()
    if not reservation:
        return False, "Nemaš aktivnu rezervaciju koju možeš otkazati."

    seat_number = reservation["seat_number"]

    # 2. Oslobodi mesto u tabeli seats
    cursor.execute(
        "UPDATE seats SET is_reserved = 0 WHERE seat_number = %s",
        (seat_number,)
    )

    # 3. Obeleži rezervaciju kao otkazanu
    cursor.execute(
        "UPDATE reservations SET status = 'cancelled' WHERE id = %s",
        (reservation["id"],)
    )

    db.commit()

    return True, f"Rezervacija mesta broj {seat_number} je uspešno otkazana. 😊"

def reserve_seat(user_id: int, seat_number: int):
    try:
        # 1. Da li mesto postoji uopšte
        cursor.execute("SELECT id, is_reserved FROM seats WHERE seat_number = %s", (seat_number,))
        seat = cursor.fetchone()

        if not seat:
            return False, "To mesto ne postoji."

        if seat["is_reserved"] == 1:
            return False, "To mesto je već rezervisano."

        # 2. Da li korisnik već ima rezervaciju
        cursor.execute("SELECT id FROM reservations WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()

        if existing:
            return False, "Već imaš rezervisano mesto."

        # 3. Rezerviši mesto
        cursor.execute(
    "INSERT INTO reservations (user_id, seat_number, date, status) VALUES (%s, %s, %s, %s)",
    (user_id, seat_number, datetime.now().date(), "active")
)


        cursor.execute(
            "UPDATE seats SET is_reserved = 1 WHERE seat_number = %s",
            (seat_number,),
        )

        db.commit()

        return True, f"Uspešno si rezervisao mesto broj {seat_number}! 📚"

    except Exception as e:
        print("GRESKA U REZERVACIJI:", e)
        db.rollback()
        return False, "Došlo je do greške prilikom rezervacije."
