import SSHTool
import re
from datetime import datetime


def ap_status(wireless_controllers, username, password):
    """
    This function gathers AP status from the various controllers using an AD username and password.

    :param wireless_controllers: List of wireless controllers in the following format: deviceIP \t SiteName.
    :param username: AD username with access to wireless controllers
    :param password: AD password to username
    :return: This returns the output of the parse_wireless_out
    """
    # command to be used for gathering AP data
    command = 'no paging\nshow ap database status down\nshow ap database status up\npaging\n'
    # set all variables to 0 and text string to empty
    wireless_controller_count = 0
    ap105 = ap204 = ap225 = ap325 = ap535 = 0
    ap105_up = ap204_up = ap225_up = ap325_up = ap535_up = 0
    ap105_down = ap204_down = ap225_down = ap325_down = ap535_down = 0
    text = ''
    # iterate through controllers
    device_ip, site_name = wireless_controllers
    ap_log = ''
    # Send command set using username and password SSHTool.  Output should be a list saved to ssh_output variable
    # If there is no connecion then an error will be stored to the variable
    ssh_output = SSHTool.send_command_nokey(device_ip, command, username, password)
    # Check that the ssh_output is a list
    if type(ssh_output) is not list:
        # save sshdata variable as list
        sshdata = [ssh_output]
    else:
        # save list to sshdata variable
        sshdata = ssh_output
    if sshdata:
        wireless_controller_count += 1
        for line in sshdata:
            # Catch error states with regex
            if re.findall(r"Error:\W", line):
                # if there is already data in the ap_log variable then just append
                if ap_log:
                    ap_log += '\t' + line + '\n'
                # if not then add the site name and IP to the entry
                else:
                    ap_log += '{site}({siteip}):\n'.format(site=site_name, siteip=device_ip)
                    ap_log += '\t' + line + '\n'
            if re.findall(r"AP105", line, flags=re.IGNORECASE):
                # If match then increment device count
                ap105 += 1
                if re.findall(r'\Wup\W', line, flags=re.IGNORECASE):
                    # if up then increment device up count
                    ap105_up += 1
                if re.findall(r'\Wdown\W', line, flags=re.IGNORECASE):
                    # if down then increment device down count and add to ap_log
                    ap105_down += 1
                    if ap_log:
                        ap_log += '\t' + line + '\n'
                    else:
                        ap_log += '{site}({siteip}):\n'.format(site=site_name, siteip=device_ip)
                        ap_log += '\t' + line + '\n'
            if re.findall(r"AP204", line, flags=re.IGNORECASE):
                # If match then increment device count
                ap204 += 1
                if re.findall(r'\Wup\W', line, flags=re.IGNORECASE):
                    # if up then increment device up count
                    ap204_up += 1
                if re.findall(r'\Wdown\W', line, flags=re.IGNORECASE):
                    # if down then increment device down count and add to ap_log
                    ap204_down += 1
                    if ap_log:
                        ap_log += '\t' + line + '\n'
                    else:
                        ap_log += '{site}({siteip}):\n'.format(site=site_name, siteip=device_ip)
                        ap_log += '\t' + line + '\n'
            if re.findall(r"AP225", line, flags=re.IGNORECASE):
                # If match then increment device count
                ap225 += 1
                if re.findall(r'\Wup\W', line, flags=re.IGNORECASE):
                    # if up then increment device up count
                    ap225_up += 1
                if re.findall(r'\Wdown\W', line, flags=re.IGNORECASE):
                    # if down then increment device down count and add to ap_log
                    ap225_down += 1
                    if ap_log:
                        ap_log += '\t' + line + '\n'
                    else:
                        ap_log += '{site}({siteip}):\n'.format(site=site_name, siteip=device_ip)
                        ap_log += '\t' + line + '\n'
            if re.findall(r"AP325", line, flags=re.IGNORECASE):
                # If match then increment device count
                ap325 += 1
                if re.findall(r'\Wup\W', line, flags=re.IGNORECASE):
                    # if up then increment device up count
                    ap325_up += 1
                if re.findall(r'\Wdown\W', line, flags=re.IGNORECASE):
                    # if down then increment device down count and add to ap_log
                    ap325_down += 1
                    if ap_log:
                        ap_log += '\t' + line + '\n'
                    else:
                        ap_log += '{site}({siteip}):\n'.format(site=site_name, siteip=device_ip)
                        ap_log += '\t' + line + '\n'
            if re.findall(r"AP535", line, flags=re.IGNORECASE):
                # If match then increment device count
                ap535 += 1
                if re.findall(r'\Wup\W', line, flags=re.IGNORECASE):
                    # if up then increment device up count
                    ap535_up += 1
                if re.findall(r'\Wdown\W', line, flags=re.IGNORECASE):
                    # if down then increment device down count and add to ap_log
                    ap535_down += 1
                    if ap_log:
                        ap_log += '\t' + line + '\n'
                    else:
                        ap_log += '{site}({siteip}):\n'.format(site=site_name, siteip=device_ip)
                        ap_log += '\t' + line + '\n'
    # If there is data in ap_log variable append to the text variable
    if ap_log:
        text += ap_log
    # once completely iterated though the devices then parse the variables to a single string
    return wireless_controller_count, ap105, ap204, ap225, ap325, ap535, ap105_up, ap204_up, ap225_up, ap325_up,\
        ap535_up, ap105_down, ap204_down, ap225_down, ap325_down, ap535_down, text


def parse_wireless_out(wireless_controller_count, ap105, ap204, ap225, ap325, ap535,
                       ap105_up, ap204_up, ap225_up, ap325_up, ap535_up, ap105_down,
                       ap204_down, ap225_down, ap325_down, ap535_down, text):
    """
    This function takes all the variables from the ap status function and generates a string that will be used as
    the email body.

    :return: Return a string to be used as an email body
    """
    # Start message variable with description and date
    message = 'Wireless Access Points Health Audit\nPerformed on {datetime}\n\n'.format(
        datetime=datetime.today().strftime("%A, %B %d, %Y"))
    # Add Counts
    message += 'Wireless Controller Count:  {wc_count}\n'.format(wc_count=wireless_controller_count)
    message += 'Total Access Point Count:   {ap_count}\n'.format(ap_count=ap535 + ap325 + ap225 + ap204 + ap105)
    message += 'AP-105s Configured:         {ap105_count}\n'.format(ap105_count=ap105)
    message += 'AP-204s Configured:         {ap204_count}\n'.format(ap204_count=ap204)
    message += 'AP-225s Configured:         {ap225_count}\n'.format(ap225_count=ap225)
    message += 'AP-325s Configured:         {ap325_count}\n'.format(ap325_count=ap325)
    message += 'AP-535s Configured:         {ap535_count}\n'.format(ap535_count=ap535)
    message += 'AP-105s Up:                 {ap105up_count}\n'.format(ap105up_count=ap105_up)
    message += 'AP-204s Up:                 {ap204up_count}\n'.format(ap204up_count=ap204_up)
    message += 'AP-225s Up:                 {ap225up_count}\n'.format(ap225up_count=ap225_up)
    message += 'AP-325s Up:                 {ap325up_count}\n'.format(ap325up_count=ap325_up)
    message += 'AP-535s Up:                 {ap535up_count}\n'.format(ap535up_count=ap535_up)
    message += 'AP-105s Down:               {ap105down_count}\n'.format(ap105down_count=ap105_down)
    message += 'AP-204s Down:               {ap204down_count}\n'.format(ap204down_count=ap204_down)
    message += 'AP-225s Down:               {ap225down_count}\n'.format(ap225down_count=ap225_down)
    message += 'AP-325s Down:               {ap325down_count}\n'.format(ap325down_count=ap325_down)
    message += 'AP-535s Down:               {ap535down_count}\n\n'.format(ap535down_count=ap535_down)
    # Add AP status messages
    if text:
        message += "The following sites have down APs or other anomalies:\n"
        message += text + '\n\n'
    else:
        message += "No sites currently have down access points.\n\n"
    return message
