from flask import Flask, request, jsonify
from flask import Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt_header
from datetime import datetime
import psycopg2
from psql_config import load_config
from uuid import uuid4


accomodation = Blueprint('accomodation', __name__)

config  = load_config()


@accomodation.route('/get_accomodation', methods=['GET'])
@jwt_required()
def get_accomodation():
    user_details = get_jwt_header()
    user_id = user_details['sid']
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT location, check_in, check_out, food_type, cost FROM accomodated_at, accomodation WHERE participant_id='{user_id}' and accomodated_at.logistics_id = accomodation.id;")
                rows = cur.fetchall()
                if not len(rows):
                    return jsonify(None), 200
                row = rows[0]
                accomodation_obj = {
                    'location': row[0],
                    'from': row[1],
                    'to': row[2],
                    'food_type': row[3],
                    'payment_amount': row[4]
                }
                return jsonify(accomodation_obj), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Fetching accomodation'}), 404
                
@accomodation.route('/book_accomodation', methods=['POST'])
@jwt_required()
def book_accomodation():
    user_details = get_jwt_header()
    user_id = user_details.get('sid', 0)
    if user_id == 0:
        return jsonify({'message': "User does not have access here"}), 404
    data = request.get_json()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(f"SELECT * FROM accomodated_at WHERE participant_id='{user_id}';")
                    rows = cur.fetchall()
                    if rows:
                        return jsonify({'message': 'User already has accomodation'}), 404
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    return jsonify({'message': 'Error accomodating user'}), 404
                # Executing the selected query
                location_protection = data['location'].replace("'", "''")
                food_type_protection = data['food_type'].replace("'", "''")
                cur.execute(f"SELECT * FROM accomodation WHERE location='{location_protection}' and check_in = '{data['from']}' and check_out = '{data['to']}' and food_type = '{food_type_protection}';")
                # cur.execute(f"SELECT * FROM accomodation WHERE location='{data['location']}' and check_in = '{data['from']}' and check_out = '{data['to']}' and food_type = '{data['food_type']}';")
                rows = cur.fetchall()
                if not rows:
                    logistics_id = str(uuid4())
                    try:
                        location_protection = data['location'].replace("'", "''")
                        food_type_protection = data['food_type'].replace("'", "''")
                        cur.execute(f"INSERT INTO accomodation VALUES ('{logistics_id}', '{location_protection}', '{data['from']}', '{data['to']}', '{food_type_protection}', {int (data['payment'])});")
                        # cur.execute(f"INSERT INTO accomodation VALUES ('{logistics_id}', '{data['location']}', '{data['from']}', '{data['to']}', '{data['food_type']}', {int (data['payment'])});")
                    except (Exception, psycopg2.DatabaseError) as error:
                        print(error)
                        return jsonify({'message': 'Error registering logistics'}), 404
                else:
                    logistics_id = rows[0][0]
                try:
                    cur.execute(f"INSERT INTO accomodated_at VALUES ('{user_id}', '{logistics_id}', 'pending');")
                    return jsonify({'message': "Accomodation successful"}), 200
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                    return jsonify({'message': 'Error accomodating user'}), 404
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error accomodating user'}), 404