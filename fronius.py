import configparser
import datetime


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


def debug(message):
    # Logging
    if ("write_logs" in parsedConfig and parsedConfig["write_logs"] == "True"):
        timestamp = str(datetime.datetime.now()).split('.')[0]
        message = "["+timestamp+"]\t"+message
        with open("logs/"+timestamp.split(" ")[0]+".txt", "a") as f:
            f.write(message)
        print(message)


debug("Parsing config_personal.ini")
parseConfig() #Parsing config_personal.ini
