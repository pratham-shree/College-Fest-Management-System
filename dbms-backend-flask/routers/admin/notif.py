from flask import Flask, request, jsonify
from flask import Blueprint
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt_header
from datetime import datetime
import psycopg2
from psql_config import load_config
from uuid import uuid4
from mail import *

admin_notif = Blueprint('admin_notif', __name__)

config  = load_config()

@admin_notif.route('/notifs', methods=['GET'])
@jwt_required()
def all_notifs():
    user_details = get_jwt_header()
    if(user_details['role'] != 'admin'):
        return jsonify({'message': 'Unauthorized'}), 401
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT event_id, organiser_id, ORGANISERS.name, ORGANISERS.email, sponsorship_amount, EVENT.name FROM EVENT, MANAGES, ORGANISERS WHERE organiser_id=oid AND event_id=id AND request_status='pending';")
                rows = cur.fetchall()
                all_notifs_list = []
                for row in rows:
                    notif = {
                        'event_id': row[0],
                        'organiser_id': row[1],
                        'oname': row[2],
                        'email': row[3],
                        'sponsorship_amount': row[4],
                        'ename': row[5]
                    }
                    all_notifs_list.append(notif)
                return jsonify(all_notifs_list), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error Fetching events'}), 404
    
@admin_notif.route('/approve_organiser', methods=['POST'])
@jwt_required()
def approve_organiser():
    user_details = get_jwt_header()
    if user_details['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    oid = data['oid']
    event_id = data['eid']
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM MANAGES WHERE organiser_id='{oid}' AND event_id='{event_id}';")
                rows = cur.fetchall()
                # organiser_name = rows[0][2]
                if not rows:
                    return jsonify({'message': 'No organiser found'}), 404
                else:
                    cur.execute(f"UPDATE MANAGES SET request_status='approved' WHERE organiser_id='{oid}' AND event_id='{event_id}';")
                    # cur.execute(f"UPDATE MANAGES SET request_status='rejected' WHERE organiser_id<>'{oid}' AND event_id='{event_id}';")
                    # print(f"organiser_name: {organiser_name}, event_id: {event_id}")
                    # body = sponsor_approval_body(organiser_name, event_id)
                    # print(rows[0])
                    cur.execute(f"SELECT email,name FROM ORGANISERS WHERE oid='{oid}';")
                    org_details = cur.fetchall()
                    orgnaiser_name = org_details[0][1]
                    print(f"orgnaiser_name: {orgnaiser_name}")
                    print(f"email: {org_details[0][0]}")
                    cur.execute(f"SELECT name FROM EVENT WHERE id='{event_id}';")
                    event_name = cur.fetchall()[0][0]
                    body = sponsor_approval_body(event_name,orgnaiser_name)
                    send_mail(org_details[0][0], 'Congratulations!!!', body)
                    return jsonify({'message': 'Organiser successfully approved'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error approving organiser'}), 402
    
@admin_notif.route('/reject_organiser', methods=['POST'])
@jwt_required()
def reject_organiser():
    user_details = get_jwt_header()
    if user_details['role'] != 'admin':
        return jsonify({'message': 'Unauthorized'}), 401
    data = request.get_json()
    oid = data['oid']
    event_id = data['eid']
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # Executing the selected query
                cur.execute(f"SELECT * FROM MANAGES WHERE organiser_id='{oid}' AND event_id='{event_id}';")
                rows = cur.fetchall()
                if not rows:
                    return jsonify({'message': 'No organiser found'}), 404
                else:
                    cur.execute(f"UPDATE MANAGES SET request_status='rejected' WHERE organiser_id='{oid}' AND event_id='{event_id}';")
                    return jsonify({'message': 'Organiser successfully rejected'}), 200
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return jsonify({'message': 'Error rejecting organiser'}), 402