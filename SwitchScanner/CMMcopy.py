from ftplib import FTP

user = 'admin'
password = 'n4ture_boY'

try:
    ftp = FTP("127.10.1.66", user, password)
    with open("/flash/system/sshuser_rsa.pub", 'rb') as public_key:
        ftp.cwd('/flash/system')
        ftp.storbinary('STOR sshuser_rsa.pub', public_key)
    ftp.quit()
except Exception as e:
    error = str(e)
    print("FTP Error: " + error)
finally:
    print('FTP is complete.')
