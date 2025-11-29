from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ------------------------
# BAZA ZNANJA
# ------------------------

FAQ = [
    {
        "question": "Koje je radno vreme čitaonice?",
        "answer": "Radno vreme čitaonice je radnim danima od 08:00 do 22:00, a vikendom od 10:00 do 18:00.",
        "keywords": ["radno vreme", "radno", "vreme", "otvoreno", "kada radi", "dokle radi"]
    },
    {
        "question": "Kako mogu da rezervišem mesto u čitaonici?",
        "answer": "Mesto u čitaonici se može rezervisati putem studentskog portala ili na info-pultu lično.",
        "keywords": ["rezervacija", "rezervisati", "rezervisem", "rezervišem", "zakazati", "mesto", "sto", "stol"]
    },
    {
        "question": "Da li postoji članarina za čitaonicu?",
        "answer": "Korišćenje čitaonice je besplatno za studente fakulteta, a za ostale korisnike se plaća simbolična članarina.",
        "keywords": ["clanarina", "članarina", "placa", "plaća", "uplata", "besplatno"]
    },
    {
        "question": "Da li se knjige mogu iznositi iz čitaonice?",
        "answer": "Knjige se u pravilu ne iznose iz čitaonice, osim u slučaju kada je to posebno naznačeno.",
        "keywords": ["knjige", "iznositi", "poneti", "iznosi", "pozajmica", "pozajmljivanje"]
    },

    # 5) Učlanjenje
    {
        "question": "Kako da postanem član čitaonice?",
        "answer": "Član čitaonice možeš postati popunjavanjem pristupnice na info-pultu uz indeks ili ličnu kartu.",
        "keywords": ["uclanjenje", "učlanjenje", "postanem član", "postati clan", "pristupnica"]
    },

    # 6) Wi-Fi
    {
        "question": "Da li postoji wi-fi u čitaonici?",
        "answer": "Da, čitaonica ima besplatan wi-fi za studente. Podatke za pristup dobijaš na info-pultu.",
        "keywords": ["wifi", "wi-fi", "internet", "mreza", "šifra za wifi", "sifra za wifi"]
    },

    # 7) Hrana i piće
    {
        "question": "Da li je dozvoljeno unošenje hrane i pića?",
        "answer": "Dozvoljeno je unošenje vode u flaši, ali hrana i zaslađena pića nisu dozvoljeni u prostoru čitaonice.",
        "keywords": ["hrana", "piće", "pice", "voda", "unos hrane", "da li smem da jedem"]
    },

    # 8) Pretraga knjiga
    {
        "question": "Kako da pronađem određenu knjigu?",
        "answer": "Knjigu možeš pronaći preko online kataloga biblioteke ili uz pomoć osoblja na info-pultu.",
        "keywords": ["pronađem knjigu", "nadjem knjigu", "katalog", "pretraga knjiga", "gde je knjiga"]
    },

    # 9) Pravila ponašanja
    {
        "question": "Koja su osnovna pravila ponašanja u čitaonici?",
        "answer": "U čitaonici je obavezna tišina, telefoni na silent modu, a razgovor je dozvoljen samo u za to predviđenim zonama.",
        "keywords": ["pravila ponasanja", "ponašanje", "tišina", "telefon", "pravila u čitaonici"]
    },

    # 10) Laptop i utičnice
    {
        "question": "Da li mogu da koristim laptop i da li ima utičnica?",
        "answer": "Korišćenje laptopa je dozvoljeno, a većina stolova ima dostupne utičnice za napajanje.",
        "keywords": ["laptop", "racunar", "kompjuter", "utičnica", "uticnice", "struja"]
    },

    # 11) Trajanje rezervacije
    {
        "question": "Koliko dugo važi rezervacija mesta?",
        "answer": "Rezervacija važi 30 minuta od naznačenog početka, nakon čega se mesto može dodeliti drugom korisniku.",
        "keywords": ["koliko dugo", "vazi rezervacija", "trajanje rezervacije", "koliko traje rezervacija"]
    },

    # 12) Kazne
    {
        "question": "Da li postoje kazne ako se ne poštuju pravila?",
        "answer": "Za učestale prekršaje pravila moguće je privremeno uskraćivanje prava korišćenja čitaonice.",
        "keywords": ["kazna", "kazne", "opomena", "prekrsaj", "prekršaj", "nepoštovanje pravila"]
    },

    # 13) Štampa i skener
    {
        "question": "Da li postoji mogućnost štampe ili skeniranja?",
        "answer": "U sklopu čitaonice postoji multifunkcionalni uređaj za štampu i skeniranje, usluga je dostupna uz doplatu.",
        "keywords": ["štampa", "stampanje", "štampanje", "skener", "skaniranje", "printanje"]
    },

    # 14) Rad praznicima
    {
        "question": "Da li čitaonica radi za vreme praznika?",
        "answer": "Tokom državnih praznika čitaonica može raditi skraćeno ili biti zatvorena, raspored se objavljuje na sajtu i oglasnoj tabli.",
        "keywords": ["praznik", "praznici", "radi praznicima", "radno vreme praznik", "da li radi za praznik"]
    }
]


# ------------------------
# POMOĆNE FUNKCIJE
# ------------------------

def normalize(text: str) -> str:
    """Normalizuje tekst: mala slova + uklanja specijalne znakove."""
    text = text.lower()
    text = re.sub(r"[^\wšđčćž ]", " ", text)
    return text


def find_answer(user_message: str) -> str:
    """Pronalazi najbolji odgovor na osnovu ključnih reči/sintagmi."""
    msg = normalize(user_message)
    words = msg.split()

    best_match = None
    best_score = 0

    for item in FAQ:
        score = 0
        for kw in item["keywords"]:
            kw_norm = normalize(kw)

            # 1) cela fraza u poruci -> veći score
            if kw_norm in msg:
                score += 2

            # 2) pojedinačne reči iz fraze -> manji score
            for w in kw_norm.split():
                if w in words:
                    score += 1

        if score > best_score:
            best_score = score
            best_match = item

    if best_score == 0 or best_match is None:
        return "Trenutno nemam odgovor na ovo pitanje. Pokušaj da pitaš drugačije 🙂."

    return best_match["answer"]


def suggest_questions(user_message: str, limit: int = 5):
    """
    Vraća listu sličnih pitanja na osnovu korisničkog unosa.
    Gleda preklapanje ključnih reči i sortira po 'score'-u.
    """
    msg = normalize(user_message)
    words = msg.split()

    scored = []

    for item in FAQ:
        score = 0
        for kw in item["keywords"]:
            kw_norm = normalize(kw)

            if kw_norm in msg:
                score += 2

            for w in kw_norm.split():
                if w in words:
                    score += 1

        if score > 0:
            scored.append((score, item["question"]))

    # sort po score-u (veći prvi)
    scored.sort(key=lambda x: x[0], reverse=True)

    suggestions = []
    for _, q in scored:
        if q not in suggestions:
            suggestions.append(q)
        if len(suggestions) >= limit:
            break

    # ako nema ničeg sličnog, vrati par "default" pitanja
    if not suggestions:
        suggestions = [item["question"] for item in FAQ[:limit]]

    return suggestions


# ------------------------
# RUTE
# ------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/message", methods=["POST"])
def api_message():
    data = request.get_json()
    user_message = data.get("message", "")

    reply = find_answer(user_message)
    suggestions = suggest_questions(user_message)

    return jsonify({
        "answer": reply,
        "suggestions": suggestions
    })


if __name__ == "__main__":
    app.run(debug=True)
