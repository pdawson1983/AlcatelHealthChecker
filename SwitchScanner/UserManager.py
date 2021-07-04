import SSHTool
import random
import configparser
import time
from threading import Thread
from queue import Queue
from ftplib import FTP

num_worker_threads = 50
parse_config = configparser.ConfigParser()
parse_config.read('../data/config.ini')
config = parse_config['DEFAULT']
username_AD = config['9900ADServiceAccountName']
password_AD = config['9900ADServiceAccountPassword']
log_file = '../logs/log.txt'
key_file_location = ''
characters = 'abcdefghijklmnopqrstuvwkyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*'


schoolcores_9900 = [] # Create empty array that holds school cores
with open(config['SchoolCoreList']) as file:
    # Populate array with school cores as tuples
    for line in file:
        entry = tuple(line.split())
        schoolcores_9900.append(entry)


def upload_key_9900(device, keyfile, user, password):
    """
    This function uploads the key to the school core using the python ftp library.
    It also uploads a python script that copies the key to cmm b.
    The file is named sshuser_rsa.pub on the end device.
    :param device: IP of device to send the keyfile
    :param keyfile: file location of keyfile
    :param user: Username for connecting to device
    :param password: Password for connecting to device
    """
    try:
        ftp = FTP(device, user, password)
        with open(keyfile, 'rb') as public_key:
            ftp.cwd('/flash/system')
            ftp.storbinary('STOR sshuser_rsa.pub', public_key)
        with open('CMMcopy.py', 'rb') as script:
            ftp.cwd('/flash/')
            ftp.storbinary('STOR CMMcopy.py', script)
        ftp.quit()
    except Exception as e:
        error = device + str(e)
        print("FTP Error: " + error)
        localtime = time.asctime( time.localtime(time.time()) )
        with open(log_file, 'a+') as log:
            log.write('\n')
            log.write(localtime + "FTP Error: " + error)
    finally:
        print(device + ': FTP is complete.')


def make_user_9900(device, username, passwd):
    """
    This function creates the sshuser on the device
    :param device: IP of device to send the keyfile
    :param user: Username for connecting to device
    :param password: Password for connecting to device
    """
    commands = [f'user sshuser password "{"""""".join(random.choice(characters) for i in range(30))}" read-only all',
                'show system',
                'installsshkey sshuser /flash/system/sshuser_rsa.pub',
                'write memory',
                'copy running certified']
    for command in commands:
        print(device + ':' + command)
        SSHTool.send_command_ad(device, command, username=username, password=passwd)
    print(device + ': User Creation is complete.')

def copy_key_to_ccmb(device, username, passwd):
    """
    This function initiates a python script to be run on the device to copy the key to CMMB.
    :param device: IP of device to send the keyfile
    :param user: Username for connecting to device
    :param password: Password for connecting to device
    """
    commands = ['python3 CMMcopy.py','rm -f CMMcopy.py']
    for command in commands:
        print(command)
        SSHTool.send_command_ad(device, command, username=username, password=passwd)
    print(device + ': User Creation is complete.')


def worker(): # Function to define what workers do
    while True:
        device = work_q.get() # get device information from queue
        print("work started on " + device)
        upload_key_9900(device, '../Keys/sshuser.pub', username_AD, password_AD)
        make_user_9900(device, username_AD, password_AD)
        copy_key_to_ccmb(device, username_AD, password_AD)
        work_q.task_done() # Pull device from queue


work_q = Queue()
for i in range(num_worker_threads):
    work_thread = Thread(target=worker)
    work_thread.daemon = True
    work_thread.start()

for device, site in schoolcores_9900: # Populate device queue
    work_q.put(device)

work_q.join()
