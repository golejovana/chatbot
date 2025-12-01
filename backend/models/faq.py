import re
from difflib import SequenceMatcher

# MODELI ZA RAD SA BAZOM
from models.seats import get_free_seats
from models.reservation_model import reserve_seat, cancel_reservation


# =======================================
#  GLOBAL SESSION QUESTION HISTORY
# =======================================
asked_history = []


# =======================================
#  FAQ DEFINICIJA
# =======================================
FAQ = [
    {
        "category": "Radno vreme",
        "question": "Koje je radno vreme čitaonice?",
        "answer": "Radno vreme čitaonice je radnim danima od 08:00 do 22:00, a vikendom od 10:00 do 18:00.",
        "keywords": ["radno vreme", "kada radi", "otvoreno", "dokle", "radite", "otvaranje", "zatvaranje"],
    },
    {
        "category": "Članarina",
        "question": "Da li postoji članarina za čitaonicu?",
        "answer": "Korišćenje čitaonice je besplatno za studente, a ostali plaćaju simboličnu članarinu.",
        "keywords": ["clanarina", "članarina", "placanje", "plaća", "koliko košta", "uplata", "članstvo"],
    },
    {
        "category": "Rezervacije",
        "question": "Kako mogu da rezervišem mesto?",
        "requires_login": True,
        "keywords": ["rezervacija", "rezervisati", "mesto", "mjesto", "zakazati", "rezervisem", "sto", "stol"],
    },
    {
        "category": "Pravila",
        "question": "Da li se knjige mogu iznositi iz čitaonice?",
        "answer": "Knjige se ne iznose iz čitaonice, osim ako je to izričito dozvoljeno.",
        "keywords": ["knjige", "iznositi", "pozajmica", "poneti", "iznosenje"],
    },
    {
        "category": "Učlanjenje",
        "question": "Kako da postanem član čitaonice?",
        "answer": "Potrebno je popuniti pristupnicu na info-pultu uz ličnu kartu ili indeks.",
        "keywords": ["učlanjenje", "clan", "pristupnica", "postati član", "učlaniti"],
    },
    {
        "category": "WiFi",
        "question": "Da li postoji Wi-Fi?",
        "answer": "Da, Wi-Fi je dostupan svim korisnicima. Podaci se nalaze na oglasnoj tabli.",
        "keywords": ["wifi", "wi-fi", "internet", "mreža", "šifra", "lozinka"],
    },
    {
        "category": "Kapacitet",
        "question": "Koliko mesta ima čitaonica?",
        "answer": "Čitaonica ima ukupno 120 mesta.",
        "keywords": ["kapacitet", "mesta", "koliko mesta", "slobodna mesta"],
    },
    {
        "category": "Grupni rad",
        "question": "Da li postoji sala za grupni rad?",
        "answer": "Da, postoji posebna sala za grupni rad koju je potrebno rezervisati.",
        "keywords": ["grupni rad", "tim", "sala", "rad u grupi"],
    },
    {
        "category": "Klima",
        "question": "Da li prostor ima klimatizaciju?",
        "answer": "Da, čitaonica ima i grejanje i klimatizaciju tokom cele godine.",
        "keywords": ["klima", "klimatizacija", "grejanje", "hladno", "toplo"],
    },
    {
        "category": "Izgubljene stvari",
        "question": "Šta da radim ako izgubim neku stvar?",
        "answer": "Obrati se info-pultu, oni čuvaju pronađene stvari.",
        "keywords": ["izgubio", "izgubila", "izgubljeno", "stvar", "lost", "found"],
    },
    {
        "category": "Kontakt",
        "question": "Kako mogu da kontaktiram čitaonicu?",
        "answer": "Možeš nas pozvati na +381 11 123 4567 ili poslati mejl na info@citaonica.rs.",
        "keywords": ["kontakt", "broj", "telefon", "mail", "email", "kontaktirati"],
    },
    {
        "category": "Lokacija",
        "question": "Gde se nalazi čitaonica?",
        "answer": "Nalazimo se u Bulevaru kralja Aleksandra 73.",
        "keywords": ["lokacija", "adresa", "gde je", "nalazi se"],
    },
    {
        "category": "Utičnice",
        "question": "Da li mogu da punim telefon ili laptop?",
        "answer": "Da, većina stolova ima utičnice za punjenje uređaja.",
        "keywords": ["utičnica", "punjenje", "struja", "laptop", "telefon"],
    },
    {
        "category": "Štampač",
        "question": "Da li postoji štampač?",
        "answer": "Da, tu je multifunkcionalni uređaj za štampanje i kopiranje.",
        "keywords": ["štampač", "stampac", "printer", "kopiranje"],
    },
]


# =======================================
#  HELPER FUNKCIJE
# =======================================
def normalize(text: str) -> str:
    return re.sub(r"[^\wšđčćž ]", " ", text.lower())


def similar(a, b) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _add_to_history(message: str):
    if not any(similar(normalize(message), normalize(q)) > 0.7 for q in asked_history):
        asked_history.append(message)


# =======================================
#  GLAVNA CHATBOT FUNKCIJA
# =======================================
def find_answer(user_message: str, is_logged: bool, user_id=None) -> str:
    _add_to_history(user_message)

    msg = normalize(user_message)
    words = msg.split()

    # ------------------------
    # Pozdravi
    # ------------------------
    if any(g in msg for g in ["cao", "ćao", "zdravo", "hej", "hello", "hi", "pozdrav"]):
        return "Ćao! Kako mogu da ti pomognem? 😊" if not is_logged else "Ćao! Drago mi je što si opet tu 😊 Kako mogu da pomognem?"

    # Zahvale
    if any(t in msg for t in ["hvala", "tnx", "thx"]):
        return "Nema na čemu! Tu sam ako ti još nešto treba 😊"

    if any(b in msg for b in ["laku noć", "laku noc", "vidimo se"]):
        return "Vidimo se! 👋"

    # ============================================================
    #  OTKAZIVANJE REZERVACIJE
    # ============================================================
    cancel_words = ["otkazi","otkazem","ponistim", "otkazujem", "ponisti", "ponistiti", "obrisi", "obriši", "cancel"]

    if any(word in msg for word in cancel_words):

        if not is_logged:
            return "Da bi otkazao rezervaciju moraš biti ulogovan 🙂."

        # Pokušaj da pronađe broj mesta
        cancel_match = re.search(r"(mesto|broj)\s*(\d+)", msg)
        seat_number = int(cancel_match.group(2)) if cancel_match else None

        success, message = cancel_reservation(user_id, seat_number)
        return message

    # ============================================================
    #  DIREKTNA REZERVACIJA
    # ============================================================
    seat_match = re.search(r"(rezervi[šs]i|rezervacija|mesto|mjesto)\s*(broj)?\s*(\d+)", msg)
    if seat_match:
        if not is_logged:
            return "Da bi rezervisao mesto moraš biti ulogovan 🙂."
        seat_number = int(seat_match.group(3))
        success, message = reserve_seat(user_id, seat_number)
        return message

    # Pitanje koliko ima mesta
    if "slobodn" in msg or "koliko mesta" in msg or "koliko mjesta" in msg:
        free = get_free_seats()
        return f"Trenutno imamo {free} slobodnih mesta."

    # ============================================================
    #   FAQ PRETRAGA
    # ============================================================
    best_match = None
    best_score = 0

    for item in FAQ:
        score = 0
        for kw in item["keywords"]:
            kw_norm = normalize(kw)
            if kw_norm in msg:
                score += 2
            if any(similar(w, kw_norm) > 0.7 for w in words):
                score += 1

        if score > best_score:
            best_score = score
            best_match = item

    if not best_match or best_score == 0:
        return "Trenutno nemam odgovor na ovo pitanje. Pokušaj malo drugačije 🙂."

    # LOGIN LOGIKA
    if best_match.get("requires_login"):
        if not is_logged:
            return "Da bi rezervisao mesto moraš biti ulogovan 🙂."
        else:
            if "answer" not in best_match:
                return "Možeš rezervisati svoje mesto! Samo mi reci broj mesta 😊"

    return best_match["answer"]


# =======================================
#  SUGESTIJE
# =======================================
def suggest_questions(user_message: str, limit=5):
    msg = normalize(user_message)
    suggestions = []

    for item in FAQ:

        if any(similar(normalize(item["question"]), normalize(q)) > 0.7 for q in asked_history):
            continue

        score = 0
        for kw in item["keywords"]:
            kw_norm = normalize(kw)

            if kw_norm in msg:
                score += 2

            if similar(kw_norm, msg) > 0.65:
                score += 1

        if score > 0:
            suggestions.append((score, item["question"]))

    suggestions.sort(reverse=True, key=lambda x: x[0])

    cleaned = [q for _, q in suggestions[:limit]]

    if not cleaned:
        cleaned = [
            item["question"]
            for item in FAQ[:limit]
            if item["question"] not in asked_history
        ]

    return cleaned
