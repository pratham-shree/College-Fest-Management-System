from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint

organiser_event = Blueprint('organiser_event', __name__)
config  = load_config()

@organiser_event.route('/event/<string:event_id>', methods=['GET'])
@jwt_required()
def get_an_event(event_id):
    profile_info = get_jwt_header()
    if profile_info.get('oid', 0) == 0:
        return jsonify({'message': 'Method not allowed'}), 404
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT * FROM EVENT LEFT OUTER JOIN WINNERS ON id=event_id WHERE id='{event_id}';")
                row = cur.fetchall()
                if len(row) == 0:
                    return jsonify({'message': 'No such event exists'}), 404
                row = row[0]
                oid = profile_info.get('oid', 0)
                eid = row[0]
                f_prize = row[12]
                s_prize = row[13]
                t_prize = row[14]
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
                    'third_prize': row[9],
                    'created_at': row[10]
                }
                if f_prize:
                    cur.execute(f"SELECT name, email FROM STUDENT WHERE sid='{f_prize}';")
                    row = cur.fetchall()[0]
                    event['first_winner'] = {
                        'sid': f_prize,
                        'name': row[0],
                        'email': row[1]
                    }
                    cur.execute(f"SELECT name, email FROM STUDENT WHERE sid='{s_prize}';")
                    row = cur.fetchall()[0]
                    event['second_winner'] = {
                        'sid': s_prize,
                        'name': row[0],
                        'email': row[1]
                    }
                    cur.execute(f"SELECT name, email FROM STUDENT WHERE sid='{t_prize}';")
                    row = cur.fetchall()[0]
                    event['third_winner'] = {
                        'sid': t_prize,
                        'name': row[0],
                        'email': row[1]
                    }
                # print(f"oid = {oid}, eid = {eid}")
                # print(f"Query: SELECT request_status FROM MANAGES WHERE organiser_id='{oid}' AND event_id='{eid}';")
                cur.execute(f"SELECT request_status FROM MANAGES WHERE organiser_id='{oid}' AND event_id='{eid}';")
                rows = cur.fetchall()
                # print(rows)
                if len(rows) == 0:
                    event['sponsored'] = "no"
                else:
                    event['sponsored'] = rows[0][0]
                if event['sponsored'] != "approved":
                    return jsonify(event), 200
                cur.execute(f"SELECT DISTINCT student_id FROM PARTICIPATION WHERE event_id='{eid}';")
                rows = cur.fetchall()
                event['participants'] = []
                for sid in rows:
                    sid = sid[0]
                    cur.execute(f"SELECT name, email FROM STUDENT WHERE sid='{sid}';")
                    student = cur.fetchall()[0]
                    participant = {}
                    participant['sid'] = sid
                    participant['name'] = student[0]
                    participant['email'] = student[1]
                    event['participants'].append(participant)
                cur.execute(f"SELECT logistics_id, quantity FROM EVENT_LOGISTICS WHERE event_id='{eid}';")
                rows = cur.fetchall()
                event['logistics'] = []
                for lid in rows:
                    quantity = lid[1]
                    lid = lid[0]
                    cur.execute(f"SELECT item_name, item_price FROM EVENT_LOGISTICS_ITEM WHERE logistics_id='{lid}';")
                    logistic = cur.fetchall()[0]
                    logistic_details = {}
                    logistic_details['lid'] = lid
                    logistic_details['name'] = logistic[0]
                    logistic_details['price'] = logistic[1]
                    logistic_details['quantity'] = quantity
                    event['logistics'].append(logistic_details)
                cur.execute(f"SELECT student_id, info, role FROM VOLUNTEERS WHERE event_id='{eid}';")
                rows = cur.fetchall()
                event['volunteers'] = []
                for vid in rows:
                    info = vid[1]
                    role = vid[2]
                    vid = vid[0]
                    cur.execute(f"SELECT name, email FROM STUDENT WHERE sid='{vid}';")
                    volunteer = cur.fetchall()[0]
                    volunteer_details = {}
                    volunteer_details['vid'] = vid
                    volunteer_details['name'] = volunteer[0]
                    volunteer_details['email'] = volunteer[1]
                    volunteer_details['info'] = info
                    volunteer_details['role'] = role
                    event['volunteers'].append(volunteer_details)
                # print(event)
                return jsonify(event), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error fetching events'}), 404