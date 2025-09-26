from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint

events_register = Blueprint('events_register', __name__)
config  = load_config()

@events_register.route('/register_student/<string:event_id>', methods=['POST'])
@jwt_required()
def register_student(event_id):
    profile_info = get_jwt_header()
    if profile_info.get('sid', 0) == 0:
        return jsonify({'message': 'User doesnot have access here'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                sid = profile_info.get('sid', 0)
                cur.execute(f"SELECT * FROM VOLUNTEERS WHERE student_id='{sid}' AND event_id='{event_id}'")
                rows = cur.fetchall()
                if len(rows):
                    return jsonify({'message': 'Student is already a voluneer in this event'}), 404
                cur.execute(f"SELECT * FROM PARTICIPATION WHERE student_id='{sid}' AND event_id='{event_id}'")
                rows = cur.fetchall()
                if len(rows) == 0:
                    cur.execute(f"INSERT INTO PARTICIPATION VALUES ('{event_id}', '{sid}');")
                    return jsonify({'message': 'Registered in event successfully'}), 200
                else:
                    return jsonify({'message': 'Already registered in this event'}), 404
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error in registering'}), 404
    
@events_register.route('/volunteer_student/<string:event_id>', methods=['POST'])
@jwt_required()
def volunteer_student(event_id):
    profile_info = get_jwt_header()
    info = request.get_json()['info'].replace("'", "''")
    role = request.get_json()['role'].replace("'", "''")
    if profile_info.get('sid', 0) == 0 or profile_info['type'] == "external":
        return jsonify({'message': 'User doesnot have access here'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                sid = profile_info.get('sid', 0)
                cur.execute(f"SELECT * FROM PARTICIPATION WHERE student_id='{sid}' AND event_id='{event_id}';")
                rows = cur.fetchall()
                if len(rows):
                    return jsonify({'message': 'Already registered in this event'}), 404
                cur.execute(f"SELECT * FROM VOLUNTEERS WHERE student_id='{sid}' AND event_id='{event_id}';")
                rows = cur.fetchall()
                if len(rows) == 0:
                    cur.execute(f"INSERT INTO VOLUNTEERS VALUES ('{event_id}', '{sid}', '{info}', '{role}');")
                    return jsonify({'message': 'Volunteered in event successfully'}), 200
                else:
                    return jsonify({'message': 'Already volunteered in this event'}), 404
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error in volunteering'}), 404
    
@events_register.route('/sponsor/<string:event_id>', methods=['POST'])
@jwt_required()
def sponsor(event_id):
    profile_info = get_jwt_header()
    try:
        sponsorship_amount = request.get_json()['sponsorship_amount']
    except Exception as error:
        print(error)
        return jsonify({'message': 'Payload missing'}), 415
    if profile_info.get('oid', 0) == 0:
        return jsonify({'message': 'User doesnot have access here'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                oid = profile_info.get('oid', 0)
                cur.execute(f"SELECT * FROM MANAGES WHERE organiser_id='{oid}' AND event_id='{event_id}';")
                rows = cur.fetchall()
                if len(rows) == 0:
                    cur.execute(f"INSERT INTO MANAGES VALUES ('{event_id}', '{oid}', '{sponsorship_amount}');")
                    return jsonify({'message': 'Event has been applied for sponsoring successfully'}), 200
                else:
                    return jsonify({'message': 'Already applied for sponsoring this event'}), 404
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error in sponsoring'}), 404