# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime, timedelta
from slack_sdk import WebClient
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

from config import headers, api_token

channel = "#innachannel"  # Замените на имя канала, в который хотите отправить сообщение
salon_id =840402



def send_slack_message(message):
    client = WebClient(token=api_token)
    response = client.chat_postMessage(
        channel=channel,
        text=message
    )
    if response["ok"]:
        return True
    return False


# Настройка логирования
logging.basicConfig(filename=f'{salon_id}.txt', level=logging.INFO, format='%(asctime)s - %(message)s')


def getstaff(salon):
    url = f"https://api.yclients.com/api/v1/company/{salon}/staff/"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    staffs = []
    for i in range(len(response["data"])):
        staffs.append(response["data"][i]["id"])
    return staffs

def slots(date, staff):
    url = f"https://api.yclients.com/api/v1/timetable/seances/{salon_id}/{staff}/{date}"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    totalslot = len(response["data"])
    false = 0
    # print(response)
    if len(response["data"]) > 0:
        for i in range(len(response["data"])):
            if response["data"][i]["is_free"] == False:
                false += 1
        if false == totalslot:
            return date
    print(date, staff, false, totalslot)


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

def job():
    start = datetime(2023, 5, 30)
    end = datetime(2023, 8, 1)

    staff = getstaff(salon_id)
    for i in range(len(staff)):
        current_date = start
        logging.info(f"Филиал {salon_id}. Сотрудник: {staff[i]}")
        dates = []
        while current_date <= end:
            date = slots(current_date.strftime("%Y-%m-%d"), staff[i])
            if date:
                dates.append(date)
            current_date += timedelta(days=1)
        if len(dates) > 0:
            message = f"Филиал {salon_id} (Hushpeak) Есть сломанные дни у сотрудника {staff[i]}: {dates}"
            logging.info(message)
            send_slack_message(message)
            repairslots(staff[i], dates)
        else:
            message = f"Сломанных дней нет (len(dates) = 0)"
            logging.info(message)

scheduler = BlockingScheduler()
scheduler.add_job(job, 'interval', minutes=30)
scheduler.start()
