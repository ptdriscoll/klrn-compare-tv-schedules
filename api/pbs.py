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

def get_schedule_day(url, date):
    url += date
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f'Retrieved json for {date}')
        return response.json()        
    else:
        print(f'Error: {response.status_code}, {response.text}')

def get_schedule(days=7, output_path=''):
    day = datetime.now() 
    today_str = day.strftime('%Y%m%d')
    output = f'{output_path}pbs.json'    
    result = {
        "date": today_str
    }

    for x in range(days):
        day += timedelta(days=x)
        day_str = day.strftime('%Y%m%d')
        result[day_str] = get_schedule_day(start_url, day_str)         

    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2) 

    print(f"Schedule saved to {output}")       
    