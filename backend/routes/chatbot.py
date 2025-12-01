from flask import Blueprint, request, jsonify, render_template, session
from models.faq import find_answer, suggest_questions

chatbot_bp = Blueprint("chatbot_bp", __name__)

@chatbot_bp.route("/")
def home():
    return render_template("index.html")

@chatbot_bp.route("/api/message", methods=["POST"])
def api_message():
    data = request.get_json()
    user_message = data.get("message", "")

    is_logged = session.get("user_id") is not None
    user_id = session.get("user_id")

    reply = find_answer(user_message, is_logged, user_id)
    suggestions = suggest_questions(user_message)

    return jsonify({
        "answer": reply,
        "suggestions": suggestions
    })
