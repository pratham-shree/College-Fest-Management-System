from flask import Flask, request, jsonify
from flask import Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt_header
from datetime import datetime
import psycopg2
from psql_config import load_config
from uuid import uuid4

admin_event = Blueprint('admin_event', __name__)
config  = load_config()

@admin_event.route('/events', methods=['GET'])
@jwt_required()
def all_events():
    user_details = get_jwt_header()
    if(user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM EVENT;")
                rows = cur.fetchall()
                all_events_list = []
                # if not rows:
                #     return jsonify(all_events_list), 200
                
                for row in rows:
                    eid = row[0]
                    event = {
                        'eid': eid,
                        'name': row[1],
                        'type': row[2],
                        'info': row[3],
                        'start_date_time': row[4],
                        'end_date_time': row[5],
                        'location': row[6],
                        'first_prize': row[7],
                        'second_prize': row[8],
                        'third_prize': row[9]
                    }
                    all_events_list.append(event)
                # print(all_events_list)
            return jsonify(all_events_list), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Fetching events'}), 404

@admin_event.route('/add_event', methods=['POST'])
@jwt_required()
def add_event():
    user_details = get_jwt_header()
    if(user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM EVENT WHERE name='{data['name']}';")
                rows = cur.fetchall()
                if rows:
                    return jsonify({'message': 'Event already exists'}), 404
                else:
                    event_id = str(uuid4())
                    if data['type'] == 'competition':
                        name = data['name'].replace("'", "''")
                        info = data['info'].replace("'", "''")
                        location = data['location'].replace("'", "''")
                        cur.execute(f"INSERT INTO EVENT VALUES ('{event_id}', '{name}', '{data['type']}', '{info}', '{data['start_date_time']}', '{data['end_date_time']}', '{location}', '{data['first_prize']}', '{data['second_prize']}', '{data['third_prize']}');")
                    else:
                        name = data['name'].replace("'", "''")
                        info = data['info'].replace("'", "''")
                        location = data['location'].replace("'", "''")
                        cur.execute(f"INSERT INTO EVENT VALUES ('{event_id}', '{name}', '{data['type']}', '{info}', '{data['start_date_time']}', '{data['end_date_time']}', '{location}', NULL, NULL, NULL);")

                    return jsonify({'event_id': event_id}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Adding event'}), 404

@admin_event.route('/delete_event/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_event(id):
    user_details = get_jwt_header()
    if(user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                try:
                    cur.execute(f"DELETE FROM EVENT WHERE id='{id}';")
                except Exception as e:
                    print(e)
                return jsonify({'message': 'Event successfully deleted'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Deleting event'}), 404
    
@admin_event.route('/update_event/<string:id>', methods=['PUT'])
@jwt_required()
def update_event(id):
    user_details = get_jwt_header()
    if user_details['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    
    allowed_fields = ['name', 'type', 'info', 'start_date_time', 'end_date_time', 'location', 'first_prize', 'second_prize', 'third_prize']
    
    update_fields = {key: data[key] for key in allowed_fields if key in data}

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Constructing the SQL query dynamically based on the available fields
                if data['type'] != 'competition':
                    query = ", ".join([f"{key} = %s" for key in update_fields])
                    query += f" WHERE id = %s;"
                    values = [update_fields[key] for key in update_fields] + [id]
                else:
                    for key, value in update_fields.items():
                        if value == 'None':
                            return jsonify({'message': 'Competition cannot have null values'}), 402
                    query = ", ".join([f"{key} = %s" for key in update_fields])
                    query += f" WHERE id = %s;"
                    values = [update_fields[key] for key in update_fields] + [id]
                
                cur.execute('UPDATE EVENT SET ' + query, values)
                return jsonify({'message': 'Event successfully updated'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Updating event'}), 402

