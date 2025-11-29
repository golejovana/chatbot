from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# ------------------------
# BAZA ZNANJA (osnovna verzija)
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

    return jsonify({"answer": reply})


if __name__ == "__main__":
    app.run(debug=True)
