from .models import User, ParkingLot, ParkingSpot, Reservation
from .database import db
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, current_user
from flask import current_app as app, jsonify, request, abort  
from flask_jwt_extended import create_access_token, current_user, jwt_required
from functools import wraps 
from sqlalchemy.orm import joinedload

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn) 
        @jwt_required()
        def decorator(*args, **kwargs):
            if current_user.role != required_role:
                return jsonify(message="Not authorized"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper



# ---------------------------------------
# 👤 Register User
# ---------------------------------------
@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    # vehicle_registration_number = data.get("vehicle_registration_number")

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify(message="User already exists"), 409

    user = User(username=username, email=email, password_hash=password, role="user")
    db.session.add(user)
    db.session.commit()
    return jsonify(message="User registered successfully",password=password)  



# ---------------------------------------
# 🔑 Login User
# ---------------------------------------
@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or user.password_hash != password:
        return jsonify(message="Invalid credentials"), 401

    # ✅ Use a serializable identity (e.g., user.id)
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token, username=user.username, role=user.role, id=user.id)




@app.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    # return jsonify(message=f"Welcome")  
    # return jsonify(message=f"Welcome {current_user.username}, role: {current_user.role}")
    history = get_user_parking_history(current_user.id)
     
    return jsonify(
        history= history,
        username= current_user.username,
        role= current_user.role
    )


def get_user_parking_history(user_id):
    reservations = (
        db.session.query(Reservation)
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter(Reservation.user_id == user_id)
        .all()
    )

    history = []
    for res in reservations:
        history.append({
            "id": res.id,
            "location": res.spot.lot.prime_location_name,  # Parking Lot Name
            "vehicle_no": res.vehicle_no,
            "timestamp": res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
            "action": "Parked Out" if res.leaving_timestamp else "Release"
        })
    return history



# ---------------------------------------
# 🧾 Admin: View All Parking Lots spots
# ---------------------------------------
@app.route("/admin/parkinglots", methods=["GET"])
@role_required("admin")
def get_parking_lots():
    lots = ParkingLot.query.all()
    result = []

    for lot in lots:
        # Fetch only the spots for this parking lot
        spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()

        # Prepare spot list for this lot
        spot_list = [
            {"id": spot.id, "status": spot.status} for spot in spots
        ]

        # Count occupied spots
        occupied_num = sum(1 for spot in spots if spot.status == 'O')

        result.append({
            "id": lot.id,
            "name": lot.prime_location_name,
            "price": lot.price,
            "address": lot.address,
            "pin_code": lot.pin_code,
            "number_of_spots": lot.number_of_spots,
            "occupied": occupied_num,
            "spots": spot_list
        })

    return jsonify(result)




# ---------------------------------------
# 🚗 Admin: Create Parking Lot
# ---------------------------------------
@app.route("/admin/parkinglots", methods=["POST"])
@role_required("admin")
def create_parking_lot():
    data = request.json
    lot = ParkingLot(
        prime_location_name=data.get("prime_location_name"),
        price=data.get("price"),
        address=data.get("address"),
        pin_code=data.get("pin_code"),
        number_of_spots=data.get("number_of_spots")
    )
    db.session.add(lot)
    db.session.commit()

    # Create empty parking spots for this lot
    for _ in range(lot.number_of_spots):
        spot = ParkingSpot(lot_id=lot.id, status='A')
        db.session.add(spot)

    db.session.commit()
    return jsonify(message="Parking lot created successfully", lot_id=lot.id)



@app.route("/admin/parkingLots/<int:lot_id>", methods=["GET"])
@role_required("admin")
def get_parking_lot_by_id(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
    return jsonify({
        "id": lot.id,
        "prime_location_name": lot.prime_location_name,
        "price": lot.price,
        "address": lot.address,
        "pin_code": lot.pin_code,
        "number_of_spots": lot.number_of_spots,
        "occupied": occupied
    })


@app.route("/admin/parkingLots/<int:lot_id>", methods=["PUT"])
@role_required("admin")
def update_parking_lot(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Parking lot not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        old_spot_count = lot.number_of_spots
        new_spot_count = int(data.get("number_of_spots", old_spot_count))

        lot.prime_location_name = data.get("prime_location_name", lot.prime_location_name)
        lot.price = float(data.get("price", lot.price))
        lot.address = data.get("address", lot.address)
        lot.pin_code = data.get("pin_code", lot.pin_code)

        # --- Adjust parking spots dynamically ---
        if new_spot_count > old_spot_count:
            for _ in range(new_spot_count - old_spot_count):
                new_spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(new_spot)

        elif new_spot_count < old_spot_count:
            to_remove = old_spot_count - new_spot_count

            removable_spots = (
                ParkingSpot.query.filter_by(lot_id=lot.id, status='A')
                .order_by(ParkingSpot.id.desc())
                .limit(to_remove)
                .all()
            )

            # if there are not enough available spots to remove -> reject
            if len(removable_spots) < to_remove:
                return jsonify({"error": "Cannot reduce spots — not enough available (some are occupied)"}), 400

            for spot in removable_spots:
                db.session.delete(spot)

        # --- IMPORTANT: sync the count to actual DB value ---
        # Option 1: set to requested new_spot_count
        lot.number_of_spots = new_spot_count

        # Option 2 (safer): explicitly count rows remaining and use that
        # remaining = ParkingSpot.query.filter_by(lot_id=lot.id).count()
        # lot.number_of_spots = remaining

        db.session.commit()
        return jsonify({"message": "Parking lot updated successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
 


# @app.route("/admin/parkingLots/<int:lot_id>", methods=["PUT"])
# def update_parking_lot(lot_id):
#     lot = ParkingLot.query.get(lot_id)
#     if not lot:
#         return jsonify({"error": "Parking lot not found"}), 404

#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "No data provided"}), 400

#     try:
#         old_spot_count = lot.number_of_spots
#         new_spot_count = int(data.get("number_of_spots", old_spot_count))

#         lot.prime_location_name = data.get("prime_location_name", lot.prime_location_name)
#         lot.price = float(data.get("price", lot.price))
#         lot.address = data.get("address", lot.address)
#         lot.pin_code = data.get("pin_code", lot.pin_code)
#         lot.number_of_spots = new_spot_count

#         # --- Adjust parking spots dynamically ---
#         if new_spot_count > old_spot_count:
#             for _ in range(new_spot_count - old_spot_count):
#                 new_spot = ParkingSpot(lot_id=lot.id, status='A')
#                 db.session.add(new_spot)
#         elif new_spot_count < old_spot_count:
#             removable_spots = (
#                 ParkingSpot.query.filter_by(lot_id=lot.id, status='A')
#                 .order_by(ParkingSpot.id.desc())
#                 .limit(old_spot_count - new_spot_count)
#                 .all()
#             )
#             for spot in removable_spots:
#                 db.session.delete(spot)

#         db.session.commit()
#         return jsonify({"message": "Parking lot updated successfully"})

#     except Exception as e:
#         db.session.rollback()
#         print("Error:", str(e))
#         return jsonify({"error": str(e)}), 500

# ---------------------------------------
# 🗑️ Admin: Delete Parking Lot
# ---------------------------------------
@app.route("/admin/parkinglots/<int:lot_id>", methods=["DELETE"])
@role_required("admin")
def delete_parking_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # Delete related spots and reservations first
    for spot in lot.spots:
        Reservation.query.filter_by(spot_id=spot.id).delete()
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()
    return jsonify(message="Parking lot deleted")



@app.route("/api/parkinglot/<int:lot_id>/<int:spot_id>", methods=["GET"])
@role_required("admin")
def get_parking_spot_by_id(lot_id, spot_id):
    """
    Fetch details of a specific parking spot within a parking lot.
    Example: GET /api/parkinglot/3/5
    """
    # Find the parking lot
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Parking lot not found"}), 404

    # Find the specific spot
   
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, id=spot_id).first()
    if not spot:
        return jsonify({"error": "Parking spot not found"}), 404

    # Build response
    response = {
        "lot_id": lot.id,
        "prime_location_name": lot.prime_location_name,
        "address": lot.address,
        "pin_code": lot.pin_code,
        "price": lot.price,
        "number_of_spots": lot.number_of_spots,
        "spot_id": spot.id,
        "spot_status": spot.status,
        
    }

    return jsonify(response), 200


@app.route("/api/delete-spot/<int:lot_id>/<int:spot_id>", methods=["DELETE"])
@role_required("admin")
def delete_spot(lot_id, spot_id):
    """
    Delete a specific parking spot by its lot_id and spot_id.
    Only admin can delete, and occupied spots cannot be deleted.
    """

    # ✅ Find the lot
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Parking lot not found"}), 404

    # ✅ Find the specific spot in that lot
    spot = ParkingSpot.query.filter_by(lot_id=lot_id, id=spot_id).first()
    if not spot:
        return jsonify({"error": "Parking spot not found"}), 404

    # ✅ Prevent deleting occupied spot
    if spot.status == "O":
        return jsonify({"error": "Cannot delete an occupied spot"}), 403

    
    
    # ✅ Delete the spot from DB
    db.session.delete(spot)
    remaining = ParkingSpot.query.filter_by(lot_id=lot.id).count()
    lot.number_of_spots = remaining
    db.session.commit()

    return jsonify({"message": f"Spot {spot_id} deleted successfully from lot {lot_id}"}), 200





@app.route('/admin/users', methods=['GET'])
@jwt_required("admin")
def get_users():
    users = User.query.all()
    user_list = [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.username,
            "password": user.password_hash,
            "role": user.role
        }
        for user in users
    ]
    return jsonify({"users": user_list}), 200



# @app.route('/admin/search', methods=['GET'])
# @jwt_required("admin")
# def admin_search():
#     search_by = request.args.get('by')
#     query = request.args.get('q')

#     if not search_by or not query:
#         return jsonify({'error': 'Missing parameters'}), 400

#     results = []
#     if search_by == 'location':
#         lots = ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{query}%")).all()
#         for lot in lots:
#             occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
#             results.append({
#                 'id': lot.id,
#                 'prime_location_name': lot.prime_location_name,
#                 'address': lot.address,
#                 'price': lot.price,
#                 'pin_code': lot.pin_code,
#                 'number_of_spots': lot.number_of_spots,
#                 'occupied': occupied
#             })
#     elif search_by == 'id':
#         lot = ParkingLot.query.filter_by(id=query).first()
#         if lot:
#             occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
#             results.append({
#                 'id': lot.id,
#                 'prime_location_name': lot.prime_location_name,
#                 'address': lot.address,
#                 'price': lot.price,
#                 'pin_code': lot.pin_code,
#                 'number_of_spots': lot.number_of_spots,
#                 'occupied': occupied
#             })
#     else:
#         return jsonify({'error': 'Invalid search type'}), 400

#     return jsonify({'results': results})



# ---------------------------------------
# 🔍 Admin: Search Parking Lots (improved)
# ---------------------------------------
@app.route('/admin/search', methods=['GET'])
@role_required("admin")
def admin_search():
    """
    Query parameters:
      - by: location | id | address | pin_code
      - q: search string (required except when searching by id with numeric)
      - page: optional (default 1)
      - per_page: optional (default 20)
    Response: { results: [...], page: n, per_page: m, total: t, total_pages: p }
    """
    search_by = request.args.get('by', default='location').strip().lower()
    query = request.args.get('q', default='').strip()
    page = max(int(request.args.get('page', 1)), 1)
    per_page = max(int(request.args.get('per_page', 20)), 1)
    # guard: don't allow huge pages
    per_page = min(per_page, 100)

    if search_by not in ('location', 'id', 'address', 'pin_code'):
        return jsonify({'error': 'Invalid search type. Use location|id|address|pin_code'}), 400

    if search_by != 'id' and not query:
        return jsonify({'error': 'Missing query parameter q for this search type'}), 400

    results = []
    try:
        base_query = ParkingLot.query

        # --- Build query depending on type ---
        if search_by == 'location':
            # case-insensitive partial match on prime_location_name
            base_query = base_query.filter(ParkingLot.prime_location_name.ilike(f"%{query}%"))
        elif search_by == 'address':
            base_query = base_query.filter(ParkingLot.address.ilike(f"%{query}%"))
        elif search_by == 'pin_code':
            base_query = base_query.filter(ParkingLot.pin_code.ilike(f"%{query}%"))
        elif search_by == 'id':
            # allow numeric id or exact match
            try:
                lot_id = int(query)
                base_query = base_query.filter(ParkingLot.id == lot_id)
            except ValueError:
                return jsonify({'error': 'Search by id requires a numeric value'}), 400

        # --- Count total for pagination ---
        total = base_query.count()
        total_pages = (total / per_page) if total > 0 else 0

        # --- Apply pagination & eager load spots if you want ---
        lots = (
            base_query
            .order_by(ParkingLot.id.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

        # --- Build results with occupied count and spot summary ---
        for lot in lots:
            occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            # create spot_list small summary (id + status) — careful with large lots
            spots = ParkingSpot.query.with_entities(ParkingSpot.id, ParkingSpot.status).filter_by(lot_id=lot.id).all()
            spot_list = [{"id": s.id, "status": s.status} for s in spots]

            results.append({
                'id': lot.id,
                'prime_location_name': lot.prime_location_name,
                'address': lot.address,
                'price': lot.price,
                'pin_code': lot.pin_code,
                'number_of_spots': lot.number_of_spots,
                'occupied': occupied,
                'spots': spot_list
            })

        return jsonify({
            'results': results,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages
        }), 200

    except Exception as e:
        app.logger.exception("admin_search error")
        return jsonify({'error': 'Server error', 'detail': str(e)}), 500





# ---------------------------------------
# 📊 Admin Summary: Revenue & Spot Stats
# ---------------------------------------
@app.route('/admin/summary', methods=['GET'])
@role_required("admin")
def admin_summary():
    """
    Returns aggregated summary data for admin dashboard charts.

    Response:
    {
      "revenue_by_lot": [
        {"lot_id": 1, "prime_location_name": "Downtown", "revenue": 2500},
        {"lot_id": 2, "prime_location_name": "City Mall", "revenue": 1800},
        ...
      ],
      "spot_summary": {
        "total_spots": 120,
        "available": 90,
        "occupied": 30
      }
    }
    """

    try:
        # ---- Revenue from each parking lot ----
        # Assuming each occupied spot contributes revenue = lot.price
        lots = ParkingLot.query.all()
        revenue_by_lot = []
        total_available = 0
        total_occupied = 0

        for lot in lots:
            occupied_count = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            available_count = lot.number_of_spots - occupied_count
            total_available += available_count
            total_occupied += occupied_count

            revenue = occupied_count * lot.price  # total revenue for this lot

            revenue_by_lot.append({
                "lot_id": lot.id,
                "prime_location_name": lot.prime_location_name,
                "revenue": revenue
            })

        spot_summary = {
            "total_spots": total_available + total_occupied,
            "available": total_available,
            "occupied": total_occupied
        }

        return jsonify({
            "revenue_by_lot": revenue_by_lot,
            "spot_summary": spot_summary
        }), 200

    except Exception as e:
        app.logger.exception("admin_summary error")
        return jsonify({"error": "Server error", "detail": str(e)}), 500




# ✅ View Admin Profile
@app.route('/admin/profile', methods=['GET'])
@role_required("admin")
def view_profile():
    admin = current_user

    return jsonify({
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
         
        "created_at": admin.created_at.strftime("%Y-%m-%d %H:%M:%S")
    }), 200


# ✅ Edit/Update Admin Profile
@app.route('/admin/profile', methods=['PUT'])
@role_required("admin")
def edit_profile():
    admin = current_user  # no need to fetch again from DB
    data = request.get_json()

    # Fields you allow to be edited
    admin.username = data.get("username", admin.username)
    admin.email = data.get("email", admin.email)
    admin.password_hash = data.get("password", admin.password_hash)

    db.session.commit()

    return jsonify({"msg": "Profile updated successfully"}), 200


# ---------------------------------------------
# user dashboard
# ---------------------------------------------


# ---------------------------------------
# 📍 User: View Available Parking Lots
# ---------------------------------------
@app.route("/user/parkinglots", methods=["GET"])
@role_required("user")
def list_available_lots():
    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        available = sum(1 for spot in lot.spots if spot.status == 'A')
        data.append({
            "id": lot.id,
            "location": lot.prime_location_name,
            "price": lot.price,
            "available_spots": available
        })
    return jsonify(data)


@app.route("/api/me", methods=["GET"])
@jwt_required()
def get_my_profile():
    user = current_user  # Already the logged-in user
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })



# -------------------------------------------
# USER DASHBOARD ROUTE (User sees only own data)
# -------------------------------------------
@app.route("/api/user/parkinglots", methods=["GET"])
@jwt_required()
def user_dashboard():

    user_id = current_user.id

    # -------------------------------
    # Fetch User Reservations + Spot + Lot
    # -------------------------------
    reservations = (
        db.session.query(Reservation)
        .options(joinedload(Reservation.spot).joinedload(ParkingSpot.lot))
        .filter(Reservation.user_id == user_id)
        .all()
    )

    history = []
    total_spent = 0
    active_reservation = None

    for res in reservations:
        lot = res.spot.lot

        history.append({
            "reservation_id": res.id,
            "location": lot.prime_location_name,
            "price": lot.price,
            "parking_timestamp": res.parking_timestamp.strftime("%Y-%m-%d %H:%M"),
            "leaving_timestamp": (
                res.leaving_timestamp.strftime("%Y-%m-%d %H:%M")
                if res.leaving_timestamp
                else None
            ),
            "status": "Parked" if not res.leaving_timestamp else "Completed"
        })

        # Calculate money spent
        total_spent += res.parking_cost

        # Identify currently active parking
        if not res.leaving_timestamp:
            active_reservation = {
                "reservation_id": res.id,
                "location": lot.prime_location_name,
                "price": lot.price,
                "spot_id": res.spot_id,
                "parking_timestamp": res.parking_timestamp.strftime("%Y-%m-%d %H:%M")
            }

    # -------------------------------
    # Available Parking Lots
    # -------------------------------
    lots = ParkingLot.query.all()
    available_lots = []

    for lot in lots:
        available_spots = sum(1 for s in lot.spots if s.status == "A")
        available_lots.append({
            "lot_id": lot.id,
            "location": lot.prime_location_name,
            "price": lot.price,
            "available_spots": available_spots
        })

    # -------------------------------
    # Final Response
    # -------------------------------
    return jsonify({
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
            "created_at": current_user.created_at.strftime("%Y-%m-%d %H:%M")
        },
        "history": history,
        "total_spent": total_spent,
        "active_reservation": active_reservation,
        "available_parking_lots": available_lots
    }), 200


    # ---------------------------------------
# 📍 USER: View spots inside a parking lot
# ---------------------------------------
@app.route("/user/parkinglots/<int:lot_id>/spots", methods=["GET"])
@role_required("user")
def get_user_parking_spots(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Parking lot not found"}), 404

    spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()

    spot_list = [
        {
            "id": spot.id,
            "status": spot.status
        }
        for spot in spots
    ]

    return jsonify({
        "lot_id": lot.id,
        "location": lot.prime_location_name,
        "address": lot.address,
        "price": lot.price,
        "pin_code": lot.pin_code,
        "number_of_spots": lot.number_of_spots,
        "spots": spot_list
    })


@app.route("/api/reserve", methods=["POST"])
@jwt_required()
def reserve_spot():
    data = request.json

    user_id = data.get("user_id")
    lot_id = data.get("lot_id")
    spot_id = data.get("spot_id")
    vehicle_no = data.get("vehicle_no")

    # ---------------------------
    # Validate Required Fields
    # ---------------------------
    if not all([user_id, lot_id, spot_id, vehicle_no]):
        return jsonify({"error": "Missing fields"}), 400

    # ---------------------------
    # Validate User
    # ---------------------------
    if current_user.id != user_id:
        return jsonify({"error": "Unauthorized useraa"}), 403

    # ---------------------------
    # Validate parking lot
    # ---------------------------
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({"error": "Parking lot not found"}), 404

    # ---------------------------
    # Validate spot
    # ---------------------------
    spot = ParkingSpot.query.filter_by(id=spot_id, lot_id=lot_id).first()
    if not spot:
        return jsonify({"error": "Spot not found"}), 404

    if spot.status == "O":
        return jsonify({"error": "Spot already occupied"}), 400

    # ---------------------------
    # Create Reservation
    # ---------------------------
    reservation = Reservation(
        user_id=user_id,
        spot_id=spot_id,
        vehicle_no=vehicle_no, 
        parking_timestamp=datetime.utcnow(),
        leaving_timestamp=None,
        parking_cost=0.0
    )

    # Mark spot as occupied
    spot.status = "O"

    # Save to DB
    db.session.add(reservation)
    db.session.commit()

    return jsonify({
        "message": "Spot reserved successfully!",
        "reservation_id": reservation.id,
        "vehicle_no" : vehicle_no,
        "spot_id": spot_id,
        "lot_id": lot_id
    }), 201



@app.route("/api/release", methods=["POST"])
@jwt_required()
def release_spot():
    data = request.json

    reservation_id = data.get("reservation_id")

    if not reservation_id:
        return jsonify({"error": "Reservation ID is required"}), 400

    # Find reservation
    reservation = Reservation.query.get(reservation_id)
    
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    # User authorization check
    if reservation.user_id != current_user.id:
        return jsonify({"error": "Not authorized to release this reservation"}), 403

    # Find spot
    spot = ParkingSpot.query.get(reservation.spot_id)

    # Calculate cost
    parking_time = reservation.parking_timestamp
    releasing_time = datetime.utcnow()

    duration_hours = (releasing_time - parking_time).total_seconds() / 3600
    duration_hours = max(1, round(duration_hours))   # at least 1 hour

    # Get price per hour from lot
    lot = ParkingLot.query.get(spot.lot_id)
    cost = duration_hours * lot.price

    # Update reservation
    reservation.leaving_timestamp = releasing_time
    reservation.parking_cost = cost

    # Mark spot as available
    spot.status = "A"

    db.session.commit()

    return jsonify({
        "message": "Spot released successfully!",
        "reservation_id": reservation.id,
        "spot_id": spot.id,
        "vehicle_no": reservation.vehicle_no,
        "parking_time": parking_time.strftime("%Y-%m-%d %H:%M"),
        "releasing_time": releasing_time.strftime("%Y-%m-%d %H:%M"),
        "total_cost": cost
    }), 200


@app.route("/user/summary", methods=["GET"])
@jwt_required()
def user_summary():
    user_id = current_user.id

    # Query: count reservations per parking lot
    results = (
        db.session.query(
            ParkingLot.prime_location_name,
            db.func.count(Reservation.id)
        )
        .join(ParkingSpot, ParkingSpot.id == Reservation.spot_id)
        .join(ParkingLot, ParkingLot.id == ParkingSpot.lot_id)
        .filter(Reservation.user_id == user_id)
        .group_by(ParkingLot.prime_location_name)
        .all()
    )

    summary = [
        {"location": r[0], "count": r[1]}
        for r in results
    ]

    return jsonify(summary), 200




@app.route("/user/profile", methods=["GET"])
@jwt_required()
def user_profile():
    user = current_user
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route("/user/profile", methods=["PUT"])
@jwt_required()
def update_user_profile():
    user = current_user
    data = request.get_json()

    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.password_hash = data.get("password", user.password_hash)

    db.session.commit()

    return jsonify({"msg": "Profile updated successfully"}), 200
