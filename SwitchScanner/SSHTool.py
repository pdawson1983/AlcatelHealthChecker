import paramiko
import time
import configparser

parse_config = configparser.ConfigParser()
parse_config.read('../data/config.ini')
config = parse_config['DEFAULT']

sshkeyuser = config['9900KeyUser']
keyfile = config['SSHKeyFileLocation']

def send_command(device, command):
    command_output = ''
    ssh = paramiko.SSHClient()
    key = paramiko.DSSKey.from_private_key_file(keyfile)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(device, 22, username="sshuser", pkey=key)
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
        ssh_stdin.write('y' + '\n')
        ssh_stdin.flush()
        output = ssh_stdout.read()
        for line in output.strip().decode().splitlines():
            command_output += line
            command_output += '\n'
    except Exception as e:
        error = 'Error: ' + device + ' - ' + str(e)
        command_output += error
        command_output = command_output.strip().decode().splitlines()
    finally:
        ssh.close()
        return command_output


def send_command_nokey(device, command, username, password):
    command_output = ''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(device, 22, username, password)
        shell = ssh.invoke_shell()
        shell.send(command)
        time.sleep(5)
        output = shell.recv(50000)
        command_output = output.strip().decode().splitlines()
        shell.close()
    except Exception as e:
        error = 'Error: ' + device + ' - ' + str(e)
        command_output += error
        command_output = command_output.strip().decode().splitlines()
    finally:
        ssh.close()
        return command_output


if __name__ == "__main__":
    device = "10.243.255.255"
    data = send_command(device, "show \n")
    if data:
        print(data)
    else:
        print('No data')
