import SSHTool
from ftplib import FTP

username_AD = ''
password_AD = ''
key_file_location

schoolcores_9900 = []
with open("../data/9900.txt") as file:
    for line in file:
        print(line.strip('\n'))
        schoolcores_9900.append(line.strip('\n'))


def upload_key_9900(schoolcores, keyfile, user, password):
    for device in schoolcores:
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
    commands = ['user sshuser password SSHkeySSH read-only all',
                'installsshkey sshuser /flash/system/sshuser_dsa.pub',
                'write memory',
                'copy running certified']
    for device in schoolcores:
        if device:
            for command in commands:
                SSHTool.send_command_nokey(device, command, username=username, password=passwd)
        print(device + ': User Creation is complete.')

upload_key_9900(schoolcores_9900, '../Keys/sshuser.pub', username_AD, password_AD)
make_user_9900(schoolcores_9900, username_AD, password_AD)
