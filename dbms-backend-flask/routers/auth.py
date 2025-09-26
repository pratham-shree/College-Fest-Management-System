from flask import request, jsonify
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint
from uuid import uuid4
from mail import *
auth = Blueprint('auth', __name__)

# Function to connect to the PostgreSQL database server
def connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

config  = load_config()

@auth.route('/signup_student', methods=['POST'])
def signup_student():
    data = request.get_json()
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    email = data['email'].replace("'", "''")
    sid = '24ST' + str(uuid4())[:16]
    print(f"Password: {data['password']}, Hashed Password: {hashed_password}")
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
                        cur.execute(f"INSERT INTO STUDENT VALUES ('{sid}', '{email}', '{data['name']}', '{data['roll_number']}', '{data['phone']}', '{data['college']}', '{data['department']}', {(int)(data['year'])}, '{data['type']}', '{hashed_password}');")
                        return jsonify({'message': 'User successfully registered'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Creating user'}), 404
    
@auth.route('/signup_organiser', methods=['POST'])
def signup_organiser():
    data = request.get_json()
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    email = data['email'].replace("'", "''")
    oid = '24OR' + str(uuid4())[:16]
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM ORGANISERS WHERE email='{email}';")
                rows = cur.fetchall()
                if(rows):
                    return jsonify({'message': 'Organiser already exists'}), 404
                else:
                    cur.execute(f"SELECT * FROM STUDENT WHERE email='{email}';")
                    rows = cur.fetchall()
                    if(rows):
                        return jsonify({'message': 'User already exists'}), 404
                    else:
                        cur.execute(f"INSERT INTO ORGANISERS VALUES ('{oid}', '{email}', '{data['name']}', '{data['phone']}', '{hashed_password}');")
                        return jsonify({'message': 'Organiser successfully registered'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Creating organiser'}), 404

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email'].replace("'", "''")
    # print(email)
    password = data['password']
    # print(email, password)
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM STUDENT WHERE email='{email}';")
                rows = cur.fetchall()
                # print(rows)
                if rows:
                    hashed_password = rows[0][9]
                    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                        profile_info = {
                            'sid': rows[0][0],
                            'email': rows[0][1],
                            'name': rows[0][2],
                            'phone': rows[0][4],
                            'roll_number': rows[0][3],
                            'college': rows[0][5],
                            'department': rows[0][6],
                            'year': rows[0][7],
                            'type': rows[0][8]
                        }
                        access_token = create_access_token(identity=email, additional_headers=profile_info, expires_delta=False)
                        return jsonify({'access_token': access_token}), 200
                    else:
                        return jsonify({'message': 'Invalid credentials'}), 404
                else:
                    cur.execute(f"SELECT * FROM ORGANISERS WHERE email='{email}';")
                    rows = cur.fetchall()
                    if rows:
                        hashed_password = rows[0][4]
                        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                            profile_info = {
                                'oid': rows[0][0],
                                'email': rows[0][1],
                                'name': rows[0][2],
                                'phone': rows[0][3]
                            }
                            access_token = create_access_token(identity=email, additional_headers=profile_info, expires_delta=False)
                            return jsonify({'access_token': access_token}), 200
                        else:
                            return jsonify({'message': 'Invalid credentials'}), 404
                    
                    else:
                        cur.execute(f"SELECT * FROM ADMIN WHERE email='{email}';")
                        rows = cur.fetchall()
                        if rows:
                            hashed_password = rows[0][3]
                            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                                profile_info = {
                                    'id': rows[0][0],
                                    'role': 'admin'
                                }
                                access_token = create_access_token(identity=email,additional_headers=profile_info, expires_delta=False)
                                return jsonify({'access_token': access_token}), 200
                            else:
                                return jsonify({'message': 'Invalid credentials'}), 404
                        else:
                            return jsonify({'message': 'User does not exist'}), 404
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'User does not exist'}), 404

@auth.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    profile_info = get_jwt_header()
    print(profile_info)
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                if profile_info.get('sid', 0):
                    cur.execute(f"SELECT * FROM STUDENT WHERE sid='{profile_info.get('sid', 0)}'")
                    rows = cur.fetchall()[0]
                    profile_content = {
                        'sid': rows[0],
                        'email': rows[1],
                        'name': rows[2],
                        'phone': rows[4],
                        'roll_number': rows[3],
                        'college': rows[5],
                        'department': rows[6],
                        'year': rows[7],
                        'type': rows[8]
                    }
                elif profile_info.get('oid', 0):
                    cur.execute(f"SELECT * FROM ORGANISERS WHERE oid='{profile_info.get('oid', 0)}'")
                    rows = cur.fetchall()[0]
                    profile_content = {
                        'oid': rows[0],
                        'email': rows[1],
                        'name': rows[2],
                        'phone': rows[3]
                    }
                elif profile_info.get('role', 0):
                    cur.execute(f"SELECT * FROM ADMIN WHERE id='{profile_info.get('id', 0)}'")
                    rows = cur.fetchall()[0]
                    profile_content = {
                        'id': rows[0],
                        'email': rows[1],
                        'name': rows[2],
                        'role': 'admin'
                    }
                else:
                    return jsonify({'message': 'Not valid user'}), 404
                return jsonify(profile_content), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error fetching profile'}), 404


@auth.route('/create_admin', methods=['POST'])
def create_admin():
    # password is 'admin'
    data = request.get_json()
    admin_id = "24AD" + str(uuid4())[:16]
    admin_email = data['email'].replace("'", "''")
    admin_password = data['password']
    admin_name = data['name']
    data = request.get_json()
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM ADMIN WHERE email='{admin_email}';")
                rows = cur.fetchall()
                if(rows):
                    return jsonify({'message': 'Admin already exists'}), 404
                else:
                    cur.execute(f"INSERT INTO ADMIN VALUES ('{admin_id}', '{admin_name}', '{admin_email}', '{hashed_password}');")
                    return jsonify({'message': 'Admin successfully registered'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Creating admin'}), 404


@auth.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data['email'].replace("'", "''")
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM STUDENT WHERE email='{email}';")
                rows = cur.fetchall()
                if not rows:
                    cur.execute(f"SELECT * FROM ORGANISERS WHERE email='{email}';")
                    rows2 = cur.fetchall()
                    if not rows2:
                        return jsonify({'message': 'User does not exist'}), 404
                    else:
                        new_password = str(uuid4())[:8]
                        print(new_password)
                        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        cur.execute(f"UPDATE ORGANISERS SET password='{hashed_password}' WHERE email='{email}';")
                        print('Password updated')
                        user_name = rows2[0][2]
                        body = forgot_pass_body(new_password, user_name)
                        send_mail(email, 'Forgot Password', body)
                        return jsonify({'message': 'Password reset successfully'}), 200
                else:
                    new_password = str(uuid4())[:8]
                    print(new_password)
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cur.execute(f"UPDATE STUDENT SET password='{hashed_password}' WHERE email='{email}';")
                    print('Password updated')
                    user_name = rows[0][2]
                    body = forgot_pass_body(new_password, user_name)
                    send_mail(email, 'Forgot Password', body)
                    return jsonify({'message': 'Password reset successfully'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error resetting password'}), 404
    


# # Route for token refresh
# @auth.route('/refresh_token', methods=['GET'])
# @jwt_required(refresh=True)
# def refresh_token():
#     current_user = get_jwt_identity()
#     new_token = create_access_token(identity=current_user)
#     return jsonify({'access_token': new_token}), 200

