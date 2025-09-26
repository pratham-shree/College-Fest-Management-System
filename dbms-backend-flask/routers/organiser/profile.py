from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint

profiles = Blueprint('profiles', __name__)
config  = load_config()

@profiles.route('/student/<string:student_id>', methods=['GET'])
@jwt_required()
def get_student_profile(student_id):
    profile_info = get_jwt_header()
    if profile_info.get('oid', 0) == 0:
        return jsonify({'message': 'Not an organiser!! Cannot access the route'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM STUDENT WHERE sid='{student_id}';")
                rows = cur.fetchall()
                if len(rows) == 0:
                    return jsonify({'message': 'No such student exists'}), 404
                row = rows[0]
                profile_info = {
                    'email': row[1],
                    'name': row[2],
                    'roll_number': row[3],
                    'phone': row[4],
                    'college': row[5],
                    'department': row[6],
                    'year': row[7],
                    'type': row[8]
                }
                return jsonify(profile_info), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Couldnot fetch profile'}), 404