from flask import Flask, request, jsonify
from flask import Blueprint
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt_header
from datetime import datetime
import psycopg2
from psql_config import load_config
from uuid import uuid4


admin_organiser = Blueprint('admin_organiser', __name__)

config = load_config()


@admin_organiser.route('/all_organisers', methods=['GET'])
@jwt_required()
def all_organisers():
    user_details = get_jwt_header()
    if (user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM ORGANISERS;")
                organiser_rows = cur.fetchall()
                all_organisers_list = []
                
                for organiser_row in organiser_rows:
                    oid = organiser_row[0]
                    events_sponsored = []
                    try:
                        cur.execute(
                            f"SELECT * FROM MANAGES WHERE organiser_id='{oid}';")
                        manages_rows = cur.fetchall()
                        if len(manages_rows):
                            for manages_row in manages_rows:
                                event_id = manages_row[0]
                                try:
                                    cur.execute(
                                        f"SELECT * FROM EVENT WHERE id='{event_id}';")
                                    event_rows = cur.fetchall()
                                    if len(event_rows):
                                        events_sponsored.append(
                                            {
                                                'eid': event_id,
                                                'name': event_rows[0][1],
                                                'sponsor_status': manages_row[4]
                                            }
                                        )
                                except:
                                    print(
                                        f'Error fetching event {event_id}')
                    except:
                        print(f'Error fetching events for organiser {oid}')
                    # print(events_sponsored)
                    # print("here here")
                    # print(organiser_row)
                    organiser = {
                        'oid':  organiser_row[0],
                        'email': organiser_row[1],
                        'name': organiser_row[2],
                        'phone': organiser_row[3],
                        'events_sponsored': events_sponsored,
                    }
                    # print(organiser)
                    all_organisers_list.append(organiser)
                return jsonify(all_organisers_list), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Fetching organisers'}), 404


@admin_organiser.route('/remove_organiser/<string:id>', methods=['DELETE'])
@jwt_required()
def remove_organiser(id):
    # print(f"ID : {id}")
    user_details = get_jwt_header()
    if (user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    # data = request.get_json()
    # print(f"payload : {data}")
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                try:
                    cur.execute(f"SELECT * FROM ORGANISERS WHERE oid='{id}';")
                    rows = cur.fetchall()
                    if not rows:
                        print("No organiser found")
                        return jsonify({'message': 'No organiser found'}), 404
                except:
                    print("Error fetching organiser")
                    return jsonify({'message': 'Error fetching organiser'}), 404
                cur.execute(f"DELETE FROM ORGANISERS WHERE oid='{id}';")
                return jsonify({'message': 'User successfully deleted'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Deleting organiser'}), 404


@admin_organiser.route('/add_organiser', methods=['POST'])
@jwt_required()
def add_organiser():
    user_details = get_jwt_header()
    if (user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    hashed_password = bcrypt.hashpw(data['password'].encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')
    email = data['email'].replace("'", "''")  
    oid = str(uuid4())[:16]
    # print(f"data : {data}")
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM ORGANISERS WHERE email='{email}';")
                rows = cur.fetchall()
                if (rows):
                    print("Organiser already exists")
                    return jsonify({'message': 'Organiser already exists'}), 404
                else:
                    cur.execute(
                        f"SELECT * FROM STUDENT WHERE email='{email}';")
                    rows = cur.fetchall()
                    if (rows):
                        print("User already exists")
                        return jsonify({'message': 'User already exists'}), 404
                    else:
                        name=data['name'].replace("'", "''")                        
                        cur.execute(
                            f"INSERT INTO ORGANISERS VALUES ('{oid}', '{email}', '{name}', '{data['phone']}', '{hashed_password}');")
                        return jsonify({'message': 'Organiser successfully registered'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Creating organiser'}), 404


@admin_organiser.route('/update_organiser', methods=['PUT'])
@jwt_required()
def update_organiser():
    user_details = get_jwt_header()
    if user_details['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    
    allowed_fields = ['oid', 'name', 'email', 'phone']
    
    update_fields = {key: data[key] for key in allowed_fields if key in data}

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Constructing the SQL query dynamically based on the available fields
                cur.execute(f"SELECT * FROM ORGANISERS WHERE oid='{data['oid']}';")
                rows = cur.fetchall()
                if(rows):
                    query = ""
                    for key, value in update_fields.items():
                        value = value.replace("'", "''")
                        query += f"{key}='{value}', "
                    query = query[:-2]
                    cur.execute(f"UPDATE ORGANISERS SET " + query + f" WHERE oid='{data['oid']}';")
                    return jsonify({'message': 'Organiser has been updated successfully'}), 200
                else:
                    return jsonify({'message': 'Organiser does not exist'}), 402
                
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Updating organiser'}), 402