import SSHTool
import random
import configparser
from ftplib import FTP

parse_config = configparser.ConfigParser()
parse_config.read('../data/config.ini')
config = parse_config['DEFAULT']
username_AD = config['9900ADServiceAccountName']
password_AD = config['9900ADServiceAccountPassword']
key_file_location = ''
characters = 'abcdefghijklmnopqrstuvwkyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*'

schoolcores_9900 = []
with open(config['SchoolCoreList']) as file:
    for line in file:
        entry = tuple(line.split())
        schoolcores_9900.append(entry)

def upload_key_9900(schoolcores, keyfile, user, password):
    for device, site in schoolcores:
        if device:
            try:
                ftp = FTP(device, user, password)
                with open(keyfile, 'rb') as public_key:
                    ftp.cwd('/flash/system')
                    ftp.storbinary('STOR sshuser_dsa.pub', public_key)
                ftp.quit()
            except Exception as e:
                error = device + str(e)
                print("FTP Error: " + error)
            finally:
                print(device + ': FTP is complete.')


def make_user_9900(schoolcores, username, passwd):
    for device, site in schoolcores:
        if device:
            commands = ['user sshuser password {randstring} '
                        'read-only all'.format(randstring=''.join(random.choice(characters) for i in range(30))),
                        'installsshkey sshuser /flash/system/sshuser_dsa.pub',
                        'write memory',
                        'copy running certified']
            for command in commands:
                print(command)
                SSHTool.send_command_nokey(device, command, username=username, password=passwd)
        print(device + ': User Creation is complete.')

upload_key_9900(schoolcores_9900, '../Keys/sshuser.pub', username_AD, password_AD)
make_user_9900(schoolcores_9900, username_AD, password_AD)
