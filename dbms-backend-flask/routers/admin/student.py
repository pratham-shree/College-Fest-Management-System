from flask import Flask, request, jsonify
from flask import Blueprint
import bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt_header
from datetime import datetime
import psycopg2
from psql_config import load_config
from uuid import uuid4


admin_student = Blueprint('admin_student', __name__)

config  = load_config()

@admin_student.route('/all_students', methods=['GET'])
@jwt_required()
def all_students():
    user_details = get_jwt_header()
    if(user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM STUDENT;")
                rows = cur.fetchall()
                all_students_list = []
                for row in rows:
                    student = {
                        'sid':  row[0],
                        'email': row[1],
                        'name': row[2],
                        'roll_number': row[3],
                        'phone': row[4],
                        'college': row[5],
                        'department': row[6],
                        'year': row[7],
                        'type': row[8]
                    }
                    all_students_list.append(student)
                return jsonify(all_students_list), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Fetching events'}), 404

@admin_student.route('/remove_student/<string:id>', methods=['DELETE'])
@jwt_required()
def remove_student(id):
    user_details = get_jwt_header()
    if(user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    # data = request.get_json()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"DELETE FROM STUDENT WHERE sid='{id}';")
                return jsonify({'message': 'User successfully deleted'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Deleting user'}), 404
    
@admin_student.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    email = data['email'].replace("'", "''")
    sid = str(uuid4())[:16]
    # print(f"Password: {data['password']}, Hashed Password: {hashed_password}")
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM STUDENT WHERE email='{email}';")
                rows = cur.fetchall()
                if(rows):
                    return jsonify({'message': 'User already exists'}), 404
                else:
                    cur.execute(f"SELECT * FROM ORGANISERS WHERE email='{email}';")
                    rows = cur.fetchall()
                    if(rows):
                        return jsonify({'message': 'Organiser already exists'}), 404
                    else:
                        s_name= data['name'].replace("'", "''")
                        s_roll_number= data['roll_number'].replace("'", "''")
                        s_phone= data['phone'].replace("'", "''")
                        s_college= data['college'].replace("'", "''")
                        s_department= data['department'].replace("'", "''")
                        s_type= data['type'].replace("'", "''")
                        cur.execute(f"INSERT INTO STUDENT VALUES ('{sid}', '{email}', '{s_name}', '{s_roll_number}', '{s_phone}', '{s_college}', '{s_department}', {(int)(data['year'])}, '{s_type}', '{hashed_password}');")
                        # cur.execute(f"INSERT INTO STUDENT VALUES ('{sid}', '{email}', '{data['name']}', '{data['roll_number']}', '{data['phone']}', '{data['college']}', '{data['department']}', {(int)(data['year'])}, '{data['type']}', '{hashed_password}');")
                        return jsonify({'message': 'User successfully registered'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Creating student'}), 404
    
@admin_student.route('/update_student', methods=['PUT'])
@jwt_required()
def update_student():
    user_details = get_jwt_header()
    if user_details['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    
    allowed_fields = ['sid', 'name', 'email', 'roll_number', 'phone', 'college', 'department', 'year', 'type']
    
    update_fields = {key: data[key] for key in allowed_fields if key in data}

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Constructing the SQL query dynamically based on the available fields
                cur.execute(f"SELECT * FROM STUDENT WHERE sid='{data['sid']}';")
                rows = cur.fetchall()
                # print(f"Rows: {rows}")
                if(rows):
                    query = ""
                    for key, value in update_fields.items():
                        value = value.replace("'", "''")
                        query += f"{key}='{value}', "
                    # query += f"password='{hashed_password}', "
                    query = query[:-2]
                    # print(f"Query: {query}")
                    cur.execute(f"UPDATE STUDENT SET " + query + f" WHERE sid='{data['sid']}';")
                    return jsonify({'message': 'Student has been updated successfully'}), 200
                else:
                    return jsonify({'message': 'Student doesnot exist'}), 402
                
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Updating student'}), 402