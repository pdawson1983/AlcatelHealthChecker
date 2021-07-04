import SchoolCore
import Wireless
import Mailer
import configparser
from threading import Thread
from queue import Queue
from datetime import datetime, timedelta

parse_config = configparser.ConfigParser()
parse_config.read('../data/config.ini')
config = parse_config['DEFAULT']
wireless_controllers = []
schoolcores_9900 = []
email_target = config['EmailTarget']
username = config['9900ADServiceAccountName']
password = config['9900ADServiceAccountPassword']
num_worker_threads = 50


class scanresults():
    switchcount = wan_isc = wan_west = cfm_a = cfm_b = watts2400 = watts3600 = \
        cmm_a_up = cmm_b_up = cmm_a_secondary = cmm_b_secondary = 0
    devices_with_issues = ''
    switchloops_results = ''
    wanhealth_results = ''
    bladehealth_results = ''
    wireless_controller_count = ap105 = ap204 = ap225 = ap325 = ap535 = ap105_up = ap204_up = ap225_up = ap325_up =\
        ap535_up = ap105_down = ap204_down = ap225_down = ap325_down = ap535_down = 0
    ap_text = ''


with open(config['SchoolCoreList']) as file:
    for line in file:
        entry = tuple(line.split())
        schoolcores_9900.append(entry)


with open(config['WirelessControllerList']) as file:
    for line in file:
        entry = tuple(line.split())
        wireless_controllers.append(entry)


def os9900_worker(searchstartdate):
    while True:
        device = OS9900_q.get()
        add_switchcount, add_wan_isc, add_wan_west, add_cfm_a, add_cfm_b, add_watts2400,\
        add_watts3600, add_cmm_a_up, add_cmm_b_up, add_cmm_a_secondary, add_cmm_b_secondary,\
        add_devices_with_issues = SchoolCore.health_audit_9900(device)
        scanresults.switchcount += add_switchcount
        scanresults.wan_isc += add_wan_isc
        scanresults.wan_west += add_wan_west
        scanresults.cfm_a += add_cfm_a
        scanresults.cfm_b += add_cfm_b
        scanresults.watts2400 += add_watts2400
        scanresults.watts3600 += add_watts3600
        scanresults.cmm_a_up += add_cmm_a_up
        scanresults.cmm_b_up += add_cmm_b_up
        scanresults.cmm_a_secondary += add_cmm_a_secondary
        scanresults.cmm_b_secondary += add_cmm_b_secondary
        scanresults.devices_with_issues += add_devices_with_issues
        switch_loops = SchoolCore.loop_finder_9900(device, searchstartdate)
        if switch_loops:
            scanresults.switchloops_results += switch_loops
        wanhealth = SchoolCore.wan_health_9900(device, searchstartdate)
        if wanhealth:
            scanresults.wanhealth_results += wanhealth
        bladehealth = SchoolCore.blade_audit_9900(device, searchstartdate)
        if bladehealth:
            scanresults.bladehealth_results += bladehealth
        OS9900_q.task_done()


def wireless_worker():
    while True:
        device = wireless_q.get()
        wireless_controller_count, ap105, ap204, ap225, ap325, ap535, ap105_up, ap204_up, ap225_up, ap325_up, \
        ap535_up, ap105_down, ap204_down, ap225_down, ap325_down,\
        ap535_down, ap_text = Wireless.ap_status(device, username, password)
        scanresults.wireless_controller_count += wireless_controller_count
        scanresults.ap105 += ap105
        scanresults.ap204 += ap204
        scanresults.ap225 += ap225
        scanresults.ap325 += ap325
        scanresults.ap535 += ap535
        scanresults.ap105_up += ap105_up
        scanresults.ap204_up += ap204_up
        scanresults.ap225_up += ap225_up
        scanresults.ap325_up += ap325_up
        scanresults.ap535_up += ap535_up
        scanresults.ap105_down += ap105_down
        scanresults.ap204_down += ap204_down
        scanresults.ap225_down += ap225_down
        scanresults.ap325_down += ap325_down
        scanresults.ap535_down += ap535_down
        scanresults.ap_text += ap_text
        wireless_q.task_done()


if __name__ == "__main__":
    '''
    Gather time information.  Do not run on the weekend.  
    '''
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

    # Create queues for threads
    OS9900_q = Queue()
    wireless_q = Queue()

    for i in range(num_worker_threads):  # Create 9900 scan threads
        print("Creating Thread #" + str(i+1) )
        work_thread = Thread(target=os9900_worker, args=(searchstartdate,))
        work_thread.daemon = True
        work_thread.start()

    for location in schoolcores_9900:  # populate queue with 9900 schoolcores
        OS9900_q.put(location)

    # Join 9900 threads
    OS9900_q.join()
    # Format core email message
    core_message += SchoolCore.parse_health_audit_9900(scanresults.switchcount, scanresults.wan_isc,
                                                       scanresults.wan_west, scanresults.cfm_a, scanresults.cfm_b,
                                                       scanresults.watts2400, scanresults.watts3600,
                                                       scanresults.cmm_a_up, scanresults.cmm_b_up,
                                                       scanresults.cmm_a_secondary, scanresults.cmm_b_secondary,
                                                       scanresults.devices_with_issues)
    if scanresults.bladehealth_results or scanresults.switchloops_results or scanresults.wanhealth_results:
        core_message += "\nThe following deficiencies were discovered as part of the extended scan\n"
    core_message += scanresults.switchloops_results
    core_message += scanresults.wanhealth_results
    core_message += scanresults.bladehealth_results
    core_message += '\n\n' + 'Please create a ticket for any anomalies discovered\n\n'
    core_message += 'VISION STATEMENT: Our vision is to provide the highest' \
                    ' network availability through top tier expert support and fast resolutions.'
    final_core_run_time = datetime.now()
    total_core_run_time = final_core_run_time - core_run_time
    core_message += '\n\n\nThis took {time} to run'.format(time=total_core_run_time)
    # AP runtime is used to time the work performed by the AP scan functions.
    ap_run_time = datetime.now()
    ap_message = ''
    for i in range(num_worker_threads):
        print("Creating wireless Thread #" + str(i+1) )
        work_thread = Thread(target=wireless_worker)
        work_thread.daemon = True
        work_thread.start()

    for location in wireless_controllers:
        wireless_q.put(location)

    wireless_q.join()

    ap_message += Wireless.parse_wireless_out(scanresults.wireless_controller_count, scanresults.ap105,
                                              scanresults.ap204, scanresults.ap225, scanresults.ap325,
                                              scanresults.ap535, scanresults.ap105_up, scanresults.ap204_up,
                                              scanresults.ap225_up, scanresults.ap325_up, scanresults.ap535_up,
                                              scanresults.ap105_down, scanresults.ap204_down, scanresults.ap225_down,
                                              scanresults.ap325_down, scanresults.ap535_down, scanresults.ap_text)

    # Append text to the AP message which is used as the body in the email.
    ap_message += 'Please create a ticket for any anomalies discovered\n\n'
    ap_message += 'VISION STATEMENT: Our vision is to provide the' \
                  ' highest network availability through top tier expert' \
                  ' support and fast resolutions.'
    final_ap_run_time = datetime.now()
    total_ap_run_time = final_ap_run_time - ap_run_time
    ap_message += '\n\n\nThis took {time} to run'.format(time=total_ap_run_time)
    print(ap_message)
    Mailer.send_apstatus_mail(email_target, ap_message)
    Mailer.send_9900_mail(email_target, core_message)
