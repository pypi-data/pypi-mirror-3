admin_emails = ['morten@nidelven-it.no']

import smtplib

def send_email(email):
    smtp = smtplib.SMTP('localhost')
    smtp.sendmail(admin_emails[0], admin_emails, email)

