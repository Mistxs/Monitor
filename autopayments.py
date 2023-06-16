# -*- coding: utf-8 -*-
import logging
import uuid
import requests
import json
import datetime
import re
from publishresult import publishresult
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_MISSED

current_time = datetime.datetime.utcnow()
current_time_format = datetime.datetime.utcnow().isoformat() + 'Z'
delta = datetime.timedelta(days=1)
second_time = (current_time - delta).isoformat() + 'Z'

logging.basicConfig(filename='autopayments.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
retry_counter = {}
MAX_RETRIES = 5


def getcrashes(salon):
    try:
        logging.info(f"Старт функции getcrashes")
        url = "https://logs.yclients.cloud/internal/bsearch?compress=true"

        payload = json.dumps({
            "params": {
                "ignoreThrottled": True,
                "preference": 1685645906635,
                "index": "yclients-biz-erp-daemon-*",
                "body": {
                    "version": True,
                    "size": 500,
                    "sort": [
                        {
                            "@timestamp": {
                                "order": "desc",
                                "unmapped_type": "boolean"
                            }
                        }
                    ],
                    "aggs": {
                        "2": {
                            "date_histogram": {
                                "field": "@timestamp",
                                "fixed_interval": "3h",
                                "time_zone": "Europe/Moscow",
                                "min_doc_count": 1
                            }
                        }
                    },
                    "stored_fields": [
                        "*"
                    ],
                    "script_fields": {},
                    "docvalue_fields": [
                        {
                            "field": "@timestamp",
                            "format": "date_time"
                        },
                        {
                            "field": "cloud.creation_time",
                            "format": "date_time"
                        }
                    ],
                    "_source": {
                        "excludes": []
                    },
                    "query": {
                        "bool": {
                            "must": [],
                            "filter": [
                                {
                                    "bool": {
                                        "filter": [
                                            {
                                                "bool": {
                                                    "should": [
                                                        {
                                                            "match": {
                                                                "facility": "loyalty_abonement_autopayment"
                                                            }
                                                        }
                                                    ],
                                                    "minimum_should_match": 1
                                                }
                                            },
                                            {
                                                "bool": {
                                                    "filter": [
                                                        {
                                                            "bool": {
                                                                "should": [
                                                                    {
                                                                        "match": {
                                                                            "data.context.payload.context": salon
                                                                        }
                                                                    }
                                                                ],
                                                                "minimum_should_match": 1
                                                            }
                                                        },
                                                        {
                                                            "bool": {
                                                                "should": [
                                                                    {
                                                                        "match_phrase": {
                                                                            "full_message": "Error while trying to autopay record with abonement"
                                                                        }
                                                                    }
                                                                ],
                                                                "minimum_should_match": 1
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                        ]
                                    }
                                },
                                {
                                    "range": {
                                        "@timestamp": {
                                            "gte": second_time,
                                            "lte": current_time_format,
                                            "format": "strict_date_optional_time"
                                        }
                                    }
                                }
                            ],
                            "should": [],
                            "must_not": []
                        }
                    },
                    "highlight": {
                        "pre_tags": [
                            "@kibana-highlighted-field@"
                        ],
                        "post_tags": [
                            "@/kibana-highlighted-field@"
                        ],
                        "fields": {
                            "*": {}
                        },
                        "fragment_size": 2147483647
                    }
                },
                "rest_total_hits_as_int": True,
                "ignore_unavailable": True,
                "ignore_throttled": True
            },
            "serverStrategy": "es"
        })
        headers = {
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Content-Type': 'application/json',
            'kbn-version': '7.8.0',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'sec-ch-ua-platform': '"Windows"',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'host': 'logs.yclients.cloud'
        }

        out = []
        response = requests.request("POST", url, headers=headers, data=payload)
        prettyresponse = response.json()
        logging.info(f"Ответ от Kibana {response}")
        hits = prettyresponse["rawResponse"]["hits"]["hits"]
        logging.info(f"Длина hits {len(hits)}")
        if hits:
            for item in hits:
                key = find_all_values(item, "data.context.payload.context")
                record_id_match = re.search(r'"record_id"=>(\d+)', str(key))
                if record_id_match:
                    record_id = record_id_match.group(1)
                    parsed_date = datetime.datetime.strptime(item["_source"]["@timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
                    formatted_date = parsed_date.strftime("%Y-%m-%d")
                    errors = []
                    payment = "Пока не доступно"
                    errors.append({
                        "Link": f"https://yclients.com/timetable/{salon}#main_date={formatted_date}&open_modal_by_record_id={record_id}",
                        "ExecutionStatus": payment
                    })
                    out.append({
                        "date": item["_source"]["@timestamp"],
                        "Status": "Есть ошибки",
                        "Errors": errors
                    })
                else:
                    out.append({
                        "date": item["_source"]["@timestamp"],
                        "Status": "Есть ошибки",
                        "Errors": "Record id not found"
                    })
        else:
            out = [{
                "date": current_time_format,
                "Status": "Ошибок не найдено",
                "Errors": []
            }]
        return out
    except Exception as e:
        logging.error(f"Ошибка при выполнении функции getcrashes: {e}")
        raise


def find_all_values(json_obj, target_key):
    results = []

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            if key == target_key:
                results.append(value)
            elif isinstance(value, (dict, list)):
                results.extend(find_all_values(value, target_key))

    elif isinstance(json_obj, list):
        for item in json_obj:
            results.extend(find_all_values(item, target_key))

    return results



def handle_job_missed(event):
    job_id = event.job_id
    logging.info(f"Пропущено выполнение задания: {job_id}")
    job_function = job

    if job_id not in retry_counter:
        retry_counter[job_id] = 1
    else:
        retry_counter[job_id] += 1

    if retry_counter[job_id] <= MAX_RETRIES:
        new_job_id = f"{job_id}_{uuid.uuid4()}"
        logging.info(f"Добавление повторного задания через 10 секунд (попытка {retry_counter[job_id]}/{MAX_RETRIES})")
        scheduler.add_job(job_function, 'date', run_date=datetime.datetime.now() + datetime.timedelta(seconds=10),
                          id=new_job_id)
    else:
        logging.info(f"Достигнуто максимальное количество попыток для задания: {job_id}")
        remove_job(job_id)

def job():
    try:
        out = getcrashes(780413)
        publishresult(out)
    except Exception as e:
        logging.error(f"Ошибка при выполнении задания job: {e}")
        raise


def remove_job(job_id):
    try:
        scheduler.remove_job(job_id)
        logging.info(f"Задание успешно удалено из очереди: {job_id}")
        if job_id in retry_counter:
            del retry_counter[job_id]  # Удаление информации о попытках для удаленного задания
    except Exception as e:
        logging.error(f"Ошибка при удалении задания из очереди: {e}")


# Запуск функций по расписанию
scheduler = BlockingScheduler()
scheduler.add_job(job, 'cron', hour=15, minute=00, id='job_1')
scheduler.add_job(job, 'cron', hour=17, minute=00, id='job_3')
scheduler.add_job(job, 'cron', hour=23, minute=30, id='job_2')
scheduler.add_listener(handle_job_missed, EVENT_JOB_MISSED)

job()

try:
    scheduler.start()
except KeyboardInterrupt:
    pass
