import re
import os

website_url = "https://dbms-frontend-flask.vercel.app"

def isValidEmail(email):
    email_regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+([.]\w{2,})+$'
    return re.match(email_regex, email)

def forgot_pass_body(new_pass, name):
    return f"Dear {name},\n\nYour account has been succesfully restored.\n Your new password is: {new_pass}. For security reasons, we recommend changing it after logging in.\n\nThank you for registering in our fest. We look forward to your presence.\n\nThe link to login is {website_url}/login\n\nBest regards,\nTech Team"

def first_prize_body(event_name, username):
    return f"Dear {username},\n\nWe are thrilled to inform you that you have been selected as the first prize winner in the event {event_name}. Congratulations! Your outstanding achievement deserves recognition, and we are delighted to award you this honor. Please contact the organising team for the prizes.\n\nThank you for your participation and dedication.\n\nThe link to login is {website_url}/login\n\nWarm regards,\nThe Organizing Committee"

def second_prize_body(event_name, username):
    return f"Dear {username},\n\nWe are pleased to announce that you have secured the second prize in the event {event_name}. Congratulations on this remarkable accomplishment! Your hard work and talent have not gone unnoticed. Please contact the organising team for the prizes.\n\nThank you for being a part of this event.\n\nThe link to login is {website_url}/login\n\nSincerely,\nThe Organizing Committee"

def third_prize_body(event_name, username):
    return f"Dear {username},\n\nWe are writing to inform you that you have won the third prize in the event {event_name}. Congratulations on this well-deserved recognition! Your dedication and efforts have paid off, and we are honored to award you this prize. Please contact the organising team for the prizes.\n\nThank you for your participation and enthusiasm.\n\nThe link to login is {website_url}/login\n\nKind regards,\nThe Organizing Committee"

def sponsor_approval_body(event_name, sponsor_name):
    return f"Dear {sponsor_name},\n\nWe are pleased to inform you that your sponsorship request for the event {event_name} has been approved. We greatly appreciate your support and commitment to our cause. Your contribution will play a significant role in the success of the event.\n\nThank you for your generosity and partnership.\n\nThe link to login is {website_url}/login\n\nWarm regards,\nThe Event Management Team"


def send_mail(to, subject, body):
    from app import mail  
    sender_email = os.environ.get("MAIL_USERNAME")
    print(sender_email)
    print(os.environ.get("MAIL_PASSWORD"))
    print(to)
    if not isValidEmail(to):
        print("Invalid email")
        return False
    try:
        mail.send_message(
            subject=subject,
            sender=sender_email,
            recipients=[to],
            body=body
        )
        print(f"body: {body}")
        
        return True
    except Exception as e:
        print(e)
        print("Error sending mail")
        return False
