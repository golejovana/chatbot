from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from models.reservation_model import reserve_seat

reservations_bp = Blueprint("reservations_bp", __name__)

@reservations_bp.route("/reserve-seat", methods=["POST"])
@login_required
def reserve_seat_route():
    user_id = session["user_id"]
    data = request.get_json()
    seat_number = data.get("seat_number")

    success, message = reserve_seat(user_id, seat_number)

    return jsonify({"success": success, "message": message})

