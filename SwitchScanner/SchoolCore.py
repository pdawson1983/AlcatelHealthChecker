import SSHTool
import re
from datetime import datetime, timedelta


def loop_finder_9900(schoolcores_9900, searchstartdate):
    """
    This function sends commands to the 9900 core that searches log messes for entries that are indicative of a loop.
    :param schoolcores_9900: List of school cores
    :param searchstartdate: Start date for searches
    :return: return the text variable
    """
    # Set the empty text variable and commands
    text = ''
    commands = ['show log swlog timestamp {date} 00:00:00 slot 1/3 | grep -i arp-flood'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 slot 1/4 | grep -i arp-flood'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 slot 1/5 | grep -i arp-flood'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 slot 1/7 | grep -i arp-flood'.format(date=searchstartdate)]
    for device, site_name in schoolcores_9900:  # Iterate through devices
        # for each device reset data to blank string
        data = ''
        for command in commands:  # iterate through commands
            # store command output to sshdata variable
            sshdata = SSHTool.send_command(device, command)
            # If there is data returned then add to data string and append new line
            if re.findall(r'Error:', sshdata):
                break
            elif sshdata:
                data += sshdata + '\n'
        if data:  # After iterating through commands if there is anything stored to the data variable...
            # Split data into an array
            data_array = data.split("\n")
            if len(data_array) > 10:  # If array has more than 10 entries...
                # Add "multiple log messages" string
                text += '{sitename}({device}): Investigate multiple log messages that indicate a loop:\n'\
                    .format(device=device,sitename=site_name)
                for log_entry in range(10):  # Iterate through first 10 log messages...
                    if data_array[log_entry]:  # Ensure entry is not blank...
                        # append entry to text string adding a tab to the front message as an indent and new line.
                        text += '\t' + data_array[log_entry] + '\n'
                # Append truncated message to string
                text += '\t' + 'Data Truncated... Please log into device to get more information\n'
            else:  # if < 10 log messages
                # Add log message string
                text += '{sitename}({device}): Investigate the following possible loop log messages:\n'\
                    .format(device=device,sitename=site_name)
                for log_entry in data_array:  # iterate through log messages
                    if log_entry:  # If message is not blank...
                        #  Append to text string with indent and newline
                        text += '\t' + log_entry + '\n'
    return text


def wan_health_9900(schoolcores_9900, searchstartdate):
    """
    This function sends commands to the 9900 core that searches log messes for entries that are show OSPF issues or
    issues on WAN uplink ports.
    :param schoolcores_9900: List of school cores
    :param searchstartdate: Start date for searches
    :return: return the text variable
    """
    # Set the empty text variable and commands variable
    text = ''
    commands = ['show log swlog timestamp {date} 00:00:00 | grep -i ospf'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 | grep -i "1/3/1\s"'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 | grep -i "1/3/2\s"'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 | grep -i "1/3/3\s"'.format(date=searchstartdate),
                'show log swlog timestamp {date} 00:00:00 | grep -i "1/3/4\s"'.format(date=searchstartdate)]
    for device, site_name in schoolcores_9900:  # Iterate through devices
        # for each device reset data to blank string
        data = ''
        for command in commands:  # iterate through commands
            # store command output to sshdata variable
            sshdata = SSHTool.send_command(device, command)
            if re.findall(r'Error:', sshdata):
                break
            elif sshdata:
                data += sshdata + '\n'
        if data:  # After iterating through commands if there is anything stored to the data variable...
            # Split data into an array
            data_array = data.split("\n")
            if len(data_array) > 10:  # If array has more than 10 entries...
                # Add "multiple log messages" string
                text += '{sitename}({device}): Investigate multiple WAN health issues\n'\
                    .format(device=device, sitename=site_name)
                for log_entry in range(10):  # Iterate through first 10 log messages...
                    if data_array[log_entry]:  # If message is not blank...
                        # append entry to text string adding a tab to the front message as an indent and new line.
                        text += '\t' + data_array[log_entry] + '\n'
                # Append truncated message to string
                text += '\t' + 'Data Truncated... Please log into device to get more information\n'
            else:  # if < 10 log messages
                # Add log message string
                text += '{sitename}({device}): Investigate the following possible WAN health issues:\n'\
                    .format(device=device, sitename=site_name)
                for log_entry in data_array:  # iterate through log messages
                    if log_entry:  # If message is not blank...
                        #  Append to text string with indent and newline
                        text += '\t' + log_entry + '\n'
    return text


def blade_audit_9900(schoolcores_9900, searchstartdate):
    """
    This function sends commands to the 9900 core that searches log messes for Blade specific issues
    :param schoolcores_9900: List of school cores
    :param searchstartdate: Start date for searches
    :return: return the text variable
    """
    # Set the empty text variable and commands variable
    text = ''
    commands = \
        ['show log swlog timestamp {date} 00:00:00 slot 1/1 | grep -i "is down'
         ' | grep -Ei "chas:1 slot:(1|2|3|4|5|6|7) is down"'.format(date=searchstartdate),
            'show log swlog timestamp {date} 00:00:00 slot 1/1 | grep -i "NI_Down"'.format(date=searchstartdate),
            'show log swlog timestamp {date} 00:00:00 | grep -i "fabric main error'.format(date=searchstartdate),
            'show log swlog timestamp {date} 00:00:00 slot 1/1 | grep -i timeout'.format(date=searchstartdate),
            'show log swlog timestamp {date} 00:00:00 slot 1/1 | grep -i timeout'.format(date=searchstartdate),
            'show log swlog timestamp {date} 00:00:00 slot 1/1 | grep -i power-off'.format(date=searchstartdate)]
    for device, site_name in schoolcores_9900:  # Iterate through devices
        # for each device reset data to blank string
        data = ''
        for command in commands:  # iterate through commands
            # store command output to sshdata variable
            sshdata = SSHTool.send_command(device, command)
            # If there is data returned then add to data string and append new line
            if re.findall(r'Error:', sshdata):
                break
            elif sshdata:
                data += sshdata + '\n'
        if data:  # After iterating through commands if there is anything stored to the data variable...
            # Split data into an array
            data_array = data.split("\n")
            if len(data_array) > 10:  # If array has more than 10 entries...
                # Add "multiple log messages" string
                text += '{sitename}({device}): Investigate multiple 9900 blade log messages:\n'\
                    .format(device=device, sitename=site_name)
                for log_entry in range(10):  # Iterate through first 10 log messages...
                    if data_array[log_entry]:  # If message is not blank...
                        # append entry to text string adding a tab to the front message as an indent and new line.
                        text += '\t' + data_array[log_entry] + '\n'
                # Append truncated message to string
                text += '\t' + 'Logs Truncated... More than 10 messages...' \
                               ' Please log into device to get more information' + '\n'
            else:  # if < 10 log messages
                # Add log message string
                text += '{sitename}({device}): Investigate the following possible 9900 blade issues\n'\
                    .format(device=device, sitename=site_name)
                for log_entry in data_array:  # iterate through log messages
                    if log_entry:  # If message is not blank...
                        #  Append to text string with indent and newline
                        text += '\t' + log_entry + '\n'
    return text


def health_audit_9900(schoolcores_9900):
    """
    This function performs 9900 counts and identifies 9900s that are running on secondary, running in certified,
    not in sync, and/or shows down statuses.
    :param schoolcores_9900:
    :return: This function returns text that parses the log audit for the email body
    """
    # Set counting variables to 0 and set devices_with_issues variable to a blank string
    switchcount = wan_isc = wan_west = cfm_a = cfm_b = 0
    watts2400 = watts3600 = cmm_a_up = cmm_b_up = 0
    cmm_a_secondary = cmm_b_secondary = 0
    devices_with_issues = ''
    # Set command variable
    commands = ['show running-directory',
                'show microcode',
                'show module status',
                'show ip ospf neighbor',
                'show ip ospf interface',
                'show fabric',
                'show cmm',
                'show powersupply']
    for device, site_name in schoolcores_9900:  # Iterate through devices
        # For each device set empty device log array and empty data string
        issue_log = []
        data = ''
        for command in commands:  # iterate through commands
            # store command output to sshdata variable
            sshdata = SSHTool.send_command(device, command)
            # If there is data returned then add to data string and append new line
            if sshdata and not re.findall(r'Error:', sshdata):
                data += sshdata + '\n'
            else:
                issue_log.append('Not scanned: {error}\n'.format(error=sshdata))
                data = ''
                break
        if data:
            switchcount += 1
            if re.findall(r"WAN-ISC", data, flags=re.IGNORECASE):  # match WAN-ISC -> iterate the WAN ISC count
                wan_isc += 1
            if re.findall(r"WAN-West", data, flags=re.IGNORECASE):  # match WAN-West -> iterate the WAN West count
                wan_west += 1
            if re.findall(r"CFMA", data, flags=re.IGNORECASE):  # match CFMA -> iterate the CFMA count
                cfm_a += 1
            if re.findall(r"CFMB", data, flags=re.IGNORECASE):  # match CFMB -> iterate the CFMB count
                cfm_b += 1
            # match 2400 watts -> iterate the 2400 watts count
            if re.findall(r"Total.+2400", data, flags=re.IGNORECASE):
                watts2400 += 1
            # match 3600 watts -> iterate the 3600 watts count
            if re.findall(r"Total.+3600", data, flags=re.IGNORECASE):
                watts3600 += 1
            if re.findall(r"CMM-A.+UP", data, flags=re.IGNORECASE):  # match CMMA -> iterate the CMMA count
                cmm_a_up += 1
            if re.findall(r"CMM-B.+UP", data, flags=re.IGNORECASE):  # match CMMB -> iterate the CMMB count
                cmm_b_up += 1
            if re.findall(r"CMM-A.+SECONDARY", data, flags=re.IGNORECASE):  # match CMMA-secondary
                # iterate the WAN West count
                cmm_a_secondary += 1
                # Add message to issue log array
                issue_log.append('CMMA is secondary.\n'.format(device=device))
            if re.findall(r"CMM-B.+SECONDARY", data, flags=re.IGNORECASE):  # match CMMB-secondary
                # iterate the WAN West count
                cmm_b_secondary += 1
            if re.findall(r"Running.+configuration.+:.+CERTIFIED", data, flags=re.IGNORECASE):  # Match certified
                # Add message to issue log array
                issue_log.append('Running in certified mode.\n')
            if re.findall(r"Running.+Configuration.+:.+NOT.+SYNCHRONIZED", data, flags=re.IGNORECASE):
                # Add message to issue log array
                issue_log.append('Running configuration is not in sync.\n')
            if re.findall(r"unpowered", data, flags=re.IGNORECASE):
                # Add message to issue log array
                issue_log.append('Check Module status.\n')
            if re.findall(r"down", data, flags=re.IGNORECASE):
                # Add message to issue log array
                issue_log.append('Down state discovered.  Check all modules on this device for down status.\n')
        if issue_log:
            if devices_with_issues is '':
                devices_with_issues += "Deficiencies have been found on the following devices:\n"
            devices_with_issues += "{sitename}({device}):\n".format(device=device, sitename=site_name)
            for entry in issue_log:
                devices_with_issues += "\t" + entry
    return parse_health_audit_9900(switchcount, wan_isc, wan_west, cfm_a, cfm_b, watts2400, watts3600,
                                   cmm_a_up, cmm_b_up, cmm_a_secondary, cmm_b_secondary, devices_with_issues)


def parse_health_audit_9900(switchcount, wan_isc, wan_west, cfm_a, cfm_b, watts2400, watts3600,
                            cmm_a_up, cmm_b_up, cmm_a_secondary, cmm_b_secondary, devices_with_issues):
    text = '9900 Alcatel Core Switch Health Audit\nPerformed at {datetime}\n\n'\
        .format(datetime=datetime.today().strftime("%A, %B %d, %Y"))
    text += "========Switch Count=========\n"
    text += '9900 switch count:   {switchcount}\n\n'.format(switchcount=switchcount)
    text += "===========WAN===============\n"
    text += 'WAN-ISC:             {count}\n'.format(count=wan_isc)
    text += 'WAN-West:            {count}\n\n'.format(count=wan_west)
    text += "===========CFM===============\n"
    text += 'CFMA:                {count}\n'.format(count=cfm_a)
    text += 'CFMB:                {count}\n\n'.format(count=cfm_b)
    text += "==========Power==============\n"
    text += '2400 Watts:          {count}\n'.format(count=watts2400)
    text += '3600 Watts:          {count}\n\n'.format(count=watts3600)
    text += "===========CMM===============\n"
    text += 'CMM-A up:            {count}\n'.format(count=cmm_a_up)
    text += 'CMM-B up:            {count}\n'.format(count=cmm_b_up)
    text += 'CMM-A SECONDARY:     {count}\n'.format(count=cmm_a_secondary)
    text += 'CMM-B SECONDARY:     {count}\n\n'.format(count=cmm_b_secondary)
    if devices_with_issues:
        for item in devices_with_issues:
            text += item
    else:
        text += 'No issues were discovered in the 9900 General Health Scans.\n\n'
    return text

