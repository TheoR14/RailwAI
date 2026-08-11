import os
from datetime import datetime
from ftplib import FTP, error_perm, all_errors
from log import get_project_video

def video_downloader(file_pattern): # file pattern is composed of the sensor name, the datatype (arz or adz), and the day
    # FTP Access variables
    ftp_host = 'geo-amberg.ch'
    ftp_user, ftp_pass, ftp_port, ftp_remote_dir = get_project_video(file_pattern)
    # the log.py file contains every loging information for the different projects in order to download the data
    # this file is not pushed on github

    ending = '.mp4'
    
    datum = file_pattern.split('_')[-1]
    yy = int(datum[0:4])
    mm = int(datum[4:6])
    dd = int(datum[6:8])

    startdatum = datetime(yy, mm, dd)

    raw_data = f'../VIDEO/{datum}/'

    try:
        ftp = FTP()
        ftp.connect(ftp_host, ftp_port, timeout=10)
        ftp.login(ftp_user, ftp_pass)
        print(f'Connection with {ftp_host}')
    except all_errors as e:
        print(f'Connection or Login error: {e}')
        exit(1)

    try:
        ftp.cwd(ftp_remote_dir)
        print(f'Successful access to {ftp_remote_dir}')
    except error_perm as e:
        print(f'Error: {e}')
        ftp.quit()
        exit(1)

    os.makedirs(raw_data, exist_ok=True)

    # Filter and dowmload data
    try:
        files = ftp.nlst()
    except all_errors as e:
        print(f'Error: {e}')
        ftp.quit()
        exit(1)

    downloaded = 0
    for file_name in files:
        if ending in file_name: # if video ends with '.mp4
            local_path = os.path.join(raw_data, file_name)
            try:
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {file_name}', f.write)
                print(f'{file_name} successfully downloaded')
                downloaded += 1
            except all_errors as e:
                print(f'Error by downloading {file_name}')

    ftp.quit()
    print(f'All videos successfully downloadeed')
    return datum