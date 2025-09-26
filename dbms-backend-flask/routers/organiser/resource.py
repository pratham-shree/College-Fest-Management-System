from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint

resource = Blueprint('resource', __name__)
config  = load_config()

@resource.route('/add_resource/<string:eid>', methods=['POST'])
@jwt_required()
def add_resource(eid):
    profile_info = get_jwt_header()
    if profile_info.get('oid', 0) == 0:
        return jsonify({'message': 'Not an organiser!! Cannot access the route'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                lid = request.get_json()['lid']
                quantity = request.get_json()['quantity']
                cur.execute(f"SELECT quantity FROM EVENT_LOGISTICS WHERE event_id='{eid}' AND logistics_id='{lid}';")
                rows = cur.fetchall()
                if len(rows) == 0:
                    cur.execute(f"INSERT INTO EVENT_LOGISTICS VALUES ('{eid}', '{lid}', {quantity});")
                else:
                    quantity += rows[0][0]
                    cur.execute(f"UPDATE EVENT_LOGISTICS SET quantity={quantity} WHERE event_id='{eid}' AND logistics_id='{lid}';")
                return jsonify({'message': 'Logistics added successfully'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Couldnot fetch profile'}), 404
    
@resource.route('/get_resources/<string:eid>', methods=['POST'])
@jwt_required()
def get_all_resources(eid):
    profile_info = get_jwt_header()
    if profile_info.get('oid', 0) == 0:
        return jsonify({'message': 'Not an organiser!! Cannot access the route'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                all_logistics = []
                cur.execute(f"SELECT logistics_id, item_name, item_price, quantity FROM EVENT_LOGISTICS_ITEM NATURAL JOIN EVENT_LOGISTICS WHERE event_id='{eid}';")
                rows = cur.fetchall()
                for row in rows:
                    logistic = {
                        'logistics_id': row[0],
                        'item_name': row[1],
                        'item_price': row[2],
                        'quantity': row[3]
                    }
                    all_logistics.append(logistic)
                return jsonify(all_logistics), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Couldnot fetch profile'}), 404