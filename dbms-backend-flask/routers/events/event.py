from flask import request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_header
import psycopg2
from psql_config import load_config
from flask import Blueprint

events = Blueprint('events', __name__)
config  = load_config()

@events.route('', methods=['GET'])
@jwt_required()
def get_all_events():
    profile_info = get_jwt_header()
    all_events_list = []
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, type, start_date_time, end_date_time FROM EVENT;")
                rows = cur.fetchall()
                sid = profile_info.get('sid', 0)
                oid = profile_info.get('oid', 0)
                for row in rows:
                    eid = row[0]
                    event = {
                        'eid': eid,
                        'name': row[1],
                        'type': row[2],
                        'start_date_time': row[3],
                        'end_date_time': row[4]
                    }
                    if sid:
                        cur.execute(f"SELECT * FROM PARTICIPATION WHERE student_id='{sid}' AND event_id='{eid}';")
                        rows = cur.fetchall()
                        if len(rows):
                            event['registered'] = True
                        else:
                            event['registered'] = False
                        cur.execute(f"SELECT * FROM VOLUNTEERS WHERE student_id='{sid}' AND event_id='{eid}';")
                        rows = cur.fetchall()
                        if len(rows):
                            event['volunteered'] = True
                        else:
                            event['volunteered'] = False
                    elif oid:
                        cur.execute(f"SELECT request_status FROM MANAGES WHERE organiser_id='{oid}' AND event_id='{eid}';")
                        rows = cur.fetchall()
                        if len(rows) == 0:
                            event['sponsored'] = "no"
                        else:
                            event['sponsored'] = rows[0][0]
                    all_events_list.append(event)
                return jsonify(all_events_list), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error fetching events'}), 404

@events.route('/<string:event_id>', methods=['GET'])
@jwt_required()
def get_an_event(event_id):
    profile_info = get_jwt_header()
    if profile_info.get('oid', 0):
        return redirect(f'/organiser/event/{event_id}')
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # print(event_id)
                # print(f"SELECT * FROM EVENT LEFT OUTER JOIN WINNERS ON id=event_id WHERE id='{event_id}';")
                cur.execute(f"SELECT * FROM EVENT LEFT OUTER JOIN WINNERS ON id=event_id WHERE id='{event_id}';")
                row = cur.fetchall()
                # print(row)
                if len(row) == 0:
                    return jsonify({'message': 'No such event exists'}), 404
                row = row[0]
                sid = profile_info.get('sid', 0)
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
                if sid:
                    cur.execute(f"SELECT * FROM PARTICIPATION WHERE student_id='{sid}' AND event_id='{eid}';")
                    rows = cur.fetchall()
                    if len(rows):
                        event['registered'] = True
                    else:
                        event['registered'] = False
                    if profile_info['type'] == 'internal':
                        cur.execute(f"SELECT * FROM VOLUNTEERS WHERE student_id='{sid}' AND event_id='{eid}';")
                        rows = cur.fetchall()
                        if len(rows):
                            event['volunteered'] = True
                        else:
                            event['volunteered'] = False
                return jsonify(event), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error fetching events'}), 404