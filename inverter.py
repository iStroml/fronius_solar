import requests
from requests.exceptions import ConnectionError
import re
import enum


#Creates a new Inverter
class Inverter:
    def __init__(self, hostname="fronius", apiversion="1.8.1-9", location=None,nickname=None):
        self.hostname = hostname
        self.apiversion = apiversion
        self.location = location
        self.nickname = nickname
        self.responsedict = {}
        self.inverternr = 1
        self.SENSOR = enum.Enum('DynamicEnum', {})
        self.isconnected = True


    def getHostname(self):
        return self.hostname

    def getAPIVersion(self):
        return self.apiversion

    def getCurrentProduction(self):
        try:
            return self.SENSOR.REALTIMEW.value
        except KeyError as e:  # Currently no production
            print(e)
            return 0

    def getAlltimeProduction(self):
        try:
            return self.SENSOR.REALTIMETOTALENERGY.value
        except KeyError as e:  # Currently no production
            print(e)
            return 0

    def getCurrentConsumptionPercentage(self):
        try:
            return self.SENSOR.RELSELFCONSUMPTION.value/100
        except KeyError as e:  # No Self-Consumption
            return 0
        except AttributeError as e:  # No Self-Consumption
            return 0

    def getTodayProduction(self):
        try:
            return self.SENSOR.REALTIMEDAYENERGY.value
        except KeyError as e:  # Currently no production
            print(e)
            return 0

    def getCurrentConsumption(self):
        return round(self.getCurrentConsumptionPercentage()*self.getCurrentProduction(),2)

    def getErrors(self):
        try:
            return self.SENSOR.INVERTERERRORCODE.value
        except KeyError as e:  # Currently no production
            return 0

    def e_request(self,endpoint, hostname="fronius", apiversion="1.8.1-9"):
        m = re.match(r".*/(.*)\..*", endpoint)
        requestname = m.group(1)
        try:
            print("Fetching " + endpoint)
            url = "http://" + hostname + endpoint
            r = requests.get(url, timeout=30)
            self.responsedict[requestname] = r.json()
            self.isconnected = True

        except ConnectionError as e:  # Connection Error or wrong hostname
            print(e)
            print("Check your Internet Connection")
            self.responsedict[requestname] = {}
            self.isconnected = False
        except ValueError as e:  # Error for example no battery connected
            print(e)
            print("Probably no energy storage system connected")

    def update(self):
        #requests all API information
        self.e_request("/solar_api/v1/GetActiveDeviceInfo.cgi?DeviceClass=System", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetInverterInfo.cgi", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetInverterRealtimeData.cgi?Scope=System", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetLoggerInfo.cgi", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetLoggerLEDInfo.cgi", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetMeterRealtimeData.cgi?Scope=System", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetPowerFlowRealtimeData.fcgi", self.hostname, self.apiversion)
        self.e_request("/solar_api/v1/GetStorageRealtimeData.cgi?Scope=System", self.hostname, self.apiversion)

        if self.responsedict["GetInverterInfo"] != {}:
            for key in self.responsedict["GetInverterInfo"]["Body"]["Data"]:
                self.inverternr = key

            local_enum = {}

            if "GetLoggerInfo" in self.responsedict:
                local_enum.update({
                'TIMEZONENAME': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["TimezoneName"],   # eg CEST
                'CASHFACTOR': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["CashFactor"],       # eg 0.125
                'PLATFORMID': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["PlatformID"],       # eg wilma
                'SWVERSION': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["SWVersion"],         # eg 3.10.1-7
                'TIMEZONELOCATION': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["TimezoneLocation"],  # eg Berlin
                'DEFAULTLANGUAGE': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["DefaultLanguage"],  # eg en
                'UTCOFFSET': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["UTCOffset"],  # eg 7200
                'CASHCURRENCY': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["CashCurrency"],  # eg EUR
                'LOGGERUNIQUEID': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["UniqueID"],  # eg 240.45562
                'DELIVERYFACTOR': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["DeliveryFactor"],  # eg 0.25
                'CO2FACTOR': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["CO2Factor"],  # eg 0.5299999713897705
                'HWVERSION': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["HWVersion"],  # eg 2.2B
                'CO2UNIT': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["CO2Unit"],  # eg kg
                'PRODUCTID': self.responsedict["GetLoggerInfo"]["Body"]["LoggerInfo"]["ProductID"]})  # eg fronius-datamanager-card

            if "GetLoggerLEDInfo" in self.responsedict:
                local_enum.update({
                'SOLARNETLED': self.responsedict["GetLoggerLEDInfo"]["Body"]["Data"]["SolarNetLED"]["State"],  # eg on
                'WLANLED': self.responsedict["GetLoggerLEDInfo"]["Body"]["Data"]["WLANLED"]["State"],  # eg on
                'POWERLED': self.responsedict["GetLoggerLEDInfo"]["Body"]["Data"]["PowerLED"]["State"],  # eg on
                'SOLARWEBLED': self.responsedict["GetLoggerLEDInfo"]["Body"]["Data"]["SolarWebLED"]["State"]}) # eg on

            if "GetInverterInfo" in self.responsedict:
                local_enum.update({
                'INVERTERUNIQUEID': self.responsedict["GetInverterInfo"]["Body"]["Data"][self.inverternr]["UniqueID"],  # eg 12093
                'INVERTERERRORCODE': self.responsedict["GetInverterInfo"]["Body"]["Data"][self.inverternr]["ErrorCode"],  # eg 0
                'INVERTERPVPOWER': self.responsedict["GetInverterInfo"]["Body"]["Data"][self.inverternr]["PVPower"],  # eg 4500
                'INVERTERDT': self.responsedict["GetInverterInfo"]["Body"]["Data"][self.inverternr]["DT"],  # eg 126
                'INVERTERSTATUSCODE': self.responsedict["GetInverterInfo"]["Body"]["Data"][self.inverternr]["StatusCode"]})  # eg 7

            if "GetInverterRealtimeData" in self.responsedict:
                local_enum.update({
                'REALTIMEW': self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["PAC"]["Values"][self.inverternr], # eg 2607 (W)
                'REALTIMEWUNIT': self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["PAC"]["Unit"], # eg W
                'REALTIMEDAYENERGY': self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["DAY_ENERGY"]["Values"][self.inverternr], # eg 23955 (Wh)
                'REALTIMEDAYENERGYUNIT': self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["DAY_ENERGY"]["Unit"], # eg Wh
                'REALTIMETOTALENERGY':self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["TOTAL_ENERGY"]["Values"][ self.inverternr],  # eg 16931924 (Wh)
                'REALTIMETOTALENERGYUNIT':self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["TOTAL_ENERGY"]["Unit"],# eg Wh
                'REALTIMEYEARENERGY': self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["YEAR_ENERGY"]["Values"][self.inverternr],  # eg 16931924 (Wh)
                'REALTIMEYEARENERGYUNIT': self.responsedict["GetInverterRealtimeData"]["Body"]["Data"]["YEAR_ENERGY"]["Unit"]}) # eg Wh

            if "GetPowerFlowRealtimeData" in self.responsedict:
                local_enum.update({
                'ETOTAL': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Inverters"][self.inverternr]["E_Total"],  # eg 16931924
                'DT': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Inverters"][self.inverternr]["DT"],  # eg 126
                'EDAY': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Inverters"][self.inverternr]["E_Day"],  # eg 23956
                'EYEAR': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Inverters"][self.inverternr]["E_Year"],  # eg 1088664
                'P': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Inverters"][self.inverternr]["P"],  # eg 2588
                'PAKKU': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Site"]["P_Akku"],# eg None
                'RELSELFCONSUMPTION': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Site"]["rel_SelfConsumption"],  # eg 7.34
                'RELAUTONOMY': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Site"]["rel_Autonomy"],  # eg 100
                'PLOAD': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Site"]["P_Load"],  # eg -190.1291
                'PPV': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Site"]["P_PV"],  # eg 2588
                'PGRID': self.responsedict["GetPowerFlowRealtimeData"]["Body"]["Data"]["Site"]["P_Grid"]  # eg -2397.870

                })

            self.SENSOR = enum.Enum('DynamicEnum', local_enum)
