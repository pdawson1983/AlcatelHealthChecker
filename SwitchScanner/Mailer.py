import smtplib
from email.message import EmailMessage
from datetime import datetime
import configparser

parse_config = configparser.ConfigParser()
parse_config.read('../data/config.ini')
config = parse_config['DEFAULT']
mailserver = config['MailServer']


def send_9900_mail(recipients, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = '9900 Health Report: {timestamp}'.format(timestamp=datetime.today().strftime("%A, %B %d, %Y"))
    msg['From'] = 'NIS_Health_Checks'
    msg['To'] = recipients
    send = smtplib.SMTP(mailserver)
    send.send_message(msg)

def send_apstatus_mail(recipients, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = 'AP Status Report: {timestamp}'.format(timestamp=datetime.today().strftime("%A, %B %d, %Y"))
    msg['From'] = 'NIS_Health_Checks'
    msg['To'] = recipients
    send = smtplib.SMTP(mailserver)
    send.send_message(msg)