from config import (
    PBS_TV_SCHEDULE_API_KEY,
    PBS_TV_SCHEDULE_ENDPOINT,
    STATION_CALL_SIGN
)
from datetime import datetime, timedelta
import requests
import json

start_url = f'{PBS_TV_SCHEDULE_ENDPOINT}{STATION_CALL_SIGN}/day/'  
headers = {
    'X-PBSAUTH': PBS_TV_SCHEDULE_API_KEY
}

def get_sched_json(url, date):
    url += date
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f'Retrieved json for {date}')
        return response.json()        
    else:
        print(f'Error: {response.status_code}, {response.text}')

print()
today = datetime.now()   
today_str = today.strftime('%Y%m%d')     
sched_today_json = get_sched_json(start_url, today_str)

result = {
    "date": today_str,
    "schedToday": sched_today_json
}

print(result)
