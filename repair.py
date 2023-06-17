import requests
import json
from datetime import datetime, timedelta
from slack_sdk import WebClient
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

from config import headers, api_token

salon_id = 520298

def getstaff(salon_id):
    url = f"https://api.yclients.com/api/v1/company/{salon_id}/staff/"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    staff = [master['id'] for master in response["data"]]
    return staff

staff = getstaff(salon_id)

def slots(staff,date):
    url = f"https://api.yclients.com/api/v1/timetable/seances/{salon_id}/{staff}/{date}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    totalslot = len(response["data"])
    false = 0
    dates = []
    # print(response)
    if len(response["data"]) > 0:
        for i in range(len(response["data"])):
            if response["data"][i]["is_free"] == False:
                false += 1
        if false == totalslot:
            dates.append(date)
    print(date, false, totalslot)
    return dates


def getshedule(staff, date):
    url = f"https://api.yclients.com/api/v1/schedule/{salon_id}/{staff}/{date}/{date}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    print(response["data"])
    return response["data"]

def putshedule(staff, response):
    url = f"https://api.yclients.com/api/v1/schedule/{salon_id}/{staff}"
    payload = json.dumps(response)
    response = requests.request("PUT", url, headers=headers, data=payload).json()
    print(response)


def repairslots(staff, dates):
    for date in dates:
        response = getshedule(staff,date)
        putshedule(staff,response)
        slots(staff,date)


    repairslots(1661618,['2023-06-02'])