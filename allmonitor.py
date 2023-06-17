# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime, timedelta
from slack_sdk import WebClient
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

from config import headers, api_token

channel = "#innachannel"  # Замените на имя канала, в который хотите отправить сообщение

salon_id = [273375, 664254, 790306, 782956, 211064, 510498, 825891, 37975, 199571, 839311, 791402, 572443, 299750, 366632, 406486, 594845, 717580, 673200, 782406, 748906, 75968, 117573, 748745, 749448, 835978, 328439, 450695, 840648, 651229, 434964, 731305, 162492, 694198, 514626, 813954, 712743, 187376, 777266, 265610, 656237, 484051, 560239, 229228, 842084, 841976, 89777, 759018, 229231, 833096, 819060, 407743, 208538, 769986, 167609, 671907, 513602, 598662, 556540, 440555, 645840, 835285, 176628, 272064, 651398, 385777, 361493, 643889, 814950, 403753, 174780, 283899, 238997, 549042, 735807, 800935, 810726, 560335, 149043, 761963, 467501, 827801, 610519, 38215, 544384, 440051, 697633, 321163, 833193, 398679, 770570, 797785, 471843, 434929, 503675, 490978, 843746, 759106, 721696, 849043, 101020, 386045, 453351, 700885, 316690, 815918, 372201, 520298, 573762, 276375, 857186, 481565, 834474, 837295, 637825, 827862, 209397, 810777, 581241, 712946, 81861, 542219, 822469, 760090, 805983, 272301, 669998, 166813, 544568, 638485, 624697, 178090, 382186, 406744, 794605, 233782, 210428, 700717, 137743, 652952, 404568, 819100, 684392, 520779, 830965, 384261, 450457, 422723, 782251, 435680, 181157, 598133, 775904, 371653, 824849, 83206, 840402, 822701, 629033, 845577, 177812, 727474, 834531, 471634, 837646, 668421, 820292, 835203, 156852, 245611, 707986, 468030, 834109, 805504, 223445, 407732, 278128, 396831, 476207, 819054, 108153, 771568, 841264, 229456, 782626, 541582, 807468, 210429, 537365, 326529, 783175, 767291, 626052, 802061, 322580, 647213, 856483, 298983, 347619, 465162, 822671, 35139, 210426, 714023, 128197, 809994, 791014, 829895, 407708, 803100, 553587, 751697, 438234, 834953, 317844, 544931, 710876, 858682, 528085, 561458, 734968, 855717, 382187, 382188, 683165, 807473, 836168, 837880, 561571, 109321, 113236, 674156, 781922, 574045, 520729, 181548, 679407, 759947, 806010, 380088, 473113, 665514, 698806, 778633, 814198, 173066, 775639, 567645, 765584, 837757, 287330, 141103, 404128, 31892, 409614, 477925, 489433, 170845, 790969, 857001, 585781, 813930, 848311, 218410, 720172, 778357, 780105, 120941, 398948, 488692, 830142, 834737, 171775, 701319, 347364, 407699, 124547, 563322, 773243, 834541, 202827, 804162, 851223, 264362, 834539, 331424, 405724, 834540, 106908, 366671, 557352, 788642, 230488, 218855, 219193, 266545, 702769, 523837, 838274, 839629, 113555, 179614, 187296, 187571, 380085, 389049, 467564, 552130, 560791, 648827, 720165, 730934, 820976, 828060, 33783, 166738, 781743, 309549, 264665, 812100, 170458, 301529, 325252, 658039, 658274, 658276, 717209, 800256, 183165, 38820, 106968, 210432, 318267, 470731, 514515, 625446, 723942, 743634, 802217, 810309, 813024, 814333, 822231, 837057, 846840, 849887, 508096, 515750, 530428, 574590, 808786, 836021, 100588, 251658, 401463, 431678, 432150, 482136, 525085, 526397, 530447, 638974, 773684, 812400, 837267, 850668, 51029, 205789, 291262, 112345, 225344, 245284, 246592, 264439, 303189, 346890, 349770, 402851, 556297, 559872, 560024, 598026, 621212, 627473, 628952, 645921, 722339, 737064, 739296, 773433, 780229, 835542, 835862, 847810, 81703, 133434, 134924, 181170, 215089, 259819, 266033, 320629, 337941, 50120]



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
logging.basicConfig(filename=f'allmonitor.txt', level=logging.INFO, format='%(asctime)s - %(message)s')


def getstaff(salon):
    url = f"https://api.yclients.com/api/v1/company/{salon}/staff/"
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload).json()
    staffs = []
    for i in range(len(response["data"])):
        staffs.append(response["data"][i]["id"])
    return staffs

def slots(salon_id, date, staff):
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
    for salons in salon_id:
        staff = getstaff(salons)
        for i in range(len(staff)):
            current_date = start
            logging.info(f"Филиал {salons}. Сотрудник: {staff[i]}")
            dates = []
            while current_date <= end:
                date = slots(salons, current_date.strftime("%Y-%m-%d"), staff[i])
                if date:
                    dates.append(date)
                current_date += timedelta(days=1)
            if len(dates) > 0:
                message = f"Филиал {salons} Есть сломанные дни у сотрудника {staff[i]}: {dates}"
                logging.info(message)
                send_slack_message(message)
                # repairslots(staff[i], dates)
            else:
                message = f"Сломанных дней нет (len(dates) = 0)"
                logging.info(message)

# scheduler = BlockingScheduler()
# scheduler.add_job(job, 'interval', minutes=30)
# scheduler.start()

job()