from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint
from mail import *

winner_settings = Blueprint('winner_settings', __name__)
config  = load_config()

@winner_settings.route('/set_winners/<string:event_id>', methods=['POST'])
@jwt_required()
def set_winners(event_id):
    profile_info = get_jwt_header()
    sid1 = request.get_json()['sid1']
    sid2 = request.get_json()['sid2']
    sid3 = request.get_json()['sid3']
    if profile_info.get('oid', 0) == 0:
        return jsonify({'message': 'User does not have access here'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM WINNERS WHERE event_id='{event_id}';")
                rows = cur.fetchall()
                if len(rows):
                    # print(rows)
                    return jsonify({'message': 'Winners already set'}), 404
                else:
                    cur.execute(f"INSERT INTO WINNERS VALUES ('{event_id}', '{sid1}', '{sid2}', '{sid3}');")
                    
                    try:
                        try:
                            cur.execute(f"SELECT name FROM EVENT WHERE id='{event_id}';")
                            rows = cur.fetchall()
                            event_name = rows[0][0]
                        except:
                            event_name = 'the event'

                        for i in range(1,4):
                            cur.execute(f"SELECT name, email FROM STUDENT WHERE sid='{request.get_json()[f'sid{i}']}';")
                            rows = cur.fetchall()
                            # print(rows)
                            if len(rows):
                                name = rows[0][0]
                                if i == 1:
                                    body = first_prize_body(event_name, name)
                                elif i == 2:
                                    body = second_prize_body(event_name, name)
                                else:
                                    body = third_prize_body(event_name, name)
                                send_mail(
                                    to=rows[0][1],
                                    subject=f"Congratulations! You have won a prize in {event_name}",
                                    body=body
                                )
                    except Exception as e:
                        print(e)
                        return jsonify({'message': 'Error sending mail'}), 404

                    return jsonify({'message': 'Winners set successfully'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Couldnot fetch profile'}), 404
    
    