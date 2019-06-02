import configparser
import datetime
import smtplib
import json
import requests
import os
import re

from inverter import Inverter


parsedConfig = {}

def parseConfig():
    config = configparser.ConfigParser()
    config.read('config_personal.ini')
    for section in config.sections():
        if ("General" in section):
            parsedConfig["fronius_apiversion"] = config['General']['apiversion']
            parsedConfig["fronius_timeout_sek"] = config['General']['timeout_sek']
            parsedConfig["write_logs"] = config['General']['write_logs']

        elif ("Accuweather" in section):
            parsedConfig["accuweather_enabled"] = config['Accuweather']['enabled']
            parsedConfig["accuweather_key"] = config['Accuweather']['api_key']

        elif ("Email" in section):
            parsedConfig["email_enabled"] = config['Email']['enabled']
            parsedConfig["email_from_gmailaddress"] = config['Email']['from_gmailaddress']
            parsedConfig["email_from_gmailpw"] = config['Email']['from_gmailpw']
            parsedConfig["email_to_address"] = config['Email']['to_address']
            parsedConfig["email_notify_on_error"] = config['Email']['notify_on_error']
            parsedConfig["notify_daily_report"] = config['Email']['notify_daily_report']
            parsedConfig["notify_weekly_report"] = config['Email']['notify_weekly_report']
            parsedConfig["notify_monthly_report"] = config['Email']['notify_monthly_report']
            parsedConfig["notify_yearly_report"] = config['Email']['notify_yearly_report']

        elif ("Database" in section):
            parsedConfig["db_host"] = config['Database']['db_host']
            parsedConfig["db_name"] = config['Database']['db_name']
            parsedConfig["db_user"] = config['Database']['db_user']
            parsedConfig["db_pass"] = config['Database']['db_pass']
            parsedConfig["db_port"] = config['Database']['db_port']


def sendMail(from_addr, to_addr_list, cc_addr_list, subject, message, login, password, smtpserver='smtp.gmail.com:587'):
    debug("Sending Error notification email to "+str(to_addr_list))
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(smtpserver)
    server.starttls()
    server.login(login, password)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()
    return problems


def debug(message):
    # Logging
    if ("write_logs" in parsedConfig and parsedConfig["write_logs"] == "True"):
        timestamp = str(datetime.datetime.now()).split('.')[0]
        message = "["+timestamp+"]\t"+message
        with open("logs/"+timestamp.split(" ")[0]+".txt", "a") as f:
            f.write(message)
        print(message)

#192.168.188.74


debug("Parsing config_personal.ini")
parseConfig() #Parsing config_personal.ini
inv = Inverter("INSERTIPADDRESS")
inv.update()
print("current production: "+str(inv.getCurrentProduction())+" W")