import SchoolCore
import Wireless
import Mailer
import configparser
from datetime import datetime, timedelta

parse_config = configparser.ConfigParser()
parse_config.read('../data/config.ini')
config = parse_config['DEFAULT']
wireless_controllers = []
schoolcores_9900 = []
email_target = config['EmailTarget']
username = config['9900ADServiceAccountName']
password = config['9900ADServiceAccountPassword']

with open(config['SchoolCoreList']) as file:
    for line in file:
        entry = tuple(line.split())
        schoolcores_9900.append(entry)

with open(config['WirelessControllerList']) as file:
    for line in file:
        entry = tuple(line.split())
        wireless_controllers.append(entry)

def main():
    """
    This is the main function.  This performs the data gathering and sends the emails
    using the Wireless.py, SchoolCore.py and Mailer.py modules
    """
    # Core runtime is used to time the work performed by the health audit functions.
    core_run_time = datetime.now()
    core_message = ''
    weekno = datetime.today().weekday()
    if weekno == 0:
        rawdate = datetime.today() - timedelta(hours=72)
        searchstartdate = rawdate.strftime("%m/%d/%Y")
    elif weekno >= 5:
        exit(0)
    else:
        rawdate = datetime.today() - timedelta(hours=24)
        searchstartdate = rawdate.strftime("%m/%d/%Y")
    print('Run 9900 Health Scan')
    health_9900 = SchoolCore.health_audit_9900(schoolcores_9900)
    if health_9900:
        core_message += health_9900
    print('Run 9900 loop Scan')
    switch_loops = SchoolCore.loop_finder_9900(schoolcores_9900, searchstartdate)
    if switch_loops:
        core_message += switch_loops
    print('Run 9900 WAN Health Scan')
    wanhealth = SchoolCore.wan_health_9900(schoolcores_9900, searchstartdate)
    if wanhealth:
        core_message += wanhealth
    print('Run 9900 blade Scan')
    bladehealth = SchoolCore.blade_audit_9900(schoolcores_9900, searchstartdate)
    if bladehealth:
        core_message += bladehealth
    # Append text to the core message which is used in the email.
    core_message += '\n\n' + 'Please create a ticket for any anomalies discovered\n\n'
    core_message += 'VISION STATEMENT: Our vision is to provide the highest' \
                    ' network availability through top tier expert support and fast resolutions.'
    final_core_run_time = datetime.now()
    total_core_run_time = final_core_run_time - core_run_time
    core_message += '\n\n\nThis took {time} to run'.format(time=total_core_run_time)
    # AP runtime is used to time the work performed by the AP scan functions.
    ap_run_time = datetime.now()
    print('run ap scan')
    ap_message = Wireless.ap_status(wireless_controllers, username, password)
    # Append text to the AP message which is used as the body in the email.
    ap_message += 'Please create a ticket for any anomalies discovered\n\n'
    ap_message += 'VISION STATEMENT: Our vision is to provide the' \
                  ' highest network availability through top tier expert' \
                  ' support and fast resolutions.'
    final_ap_run_time = datetime.now()
    total_ap_run_time = final_ap_run_time - ap_run_time
    ap_message += '\n\n\nThis took {time} to run'.format(time=total_ap_run_time)
    # Send all mail
    Mailer.send_apstatus_mail(email_target, ap_message)
    Mailer.send_9900_mail(email_target, core_message)


if __name__ == "__main__":
    main()
