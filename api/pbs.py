from config import (
    PBS_TV_SCHEDULE_API_KEY,
    PBS_TV_SCHEDULE_ENDPOINT,
    STATION_CALL_SIGN
)
from datetime import datetime, timedelta
import requests
import json

def get_schedule_day(start_url, date, headers):
    """
    Retrieves TV schedule for a specific day using the PBS TV schedule API.

    Args:
        start_url (str): Base URL for the PBS TV schedule API endpoint. 
        date (str): The date for the schedule, formatted as 'YYYYMMDD', which gets appended to start_url.
        headers (dict): The headers to include in the API request (e.g., authorization).

    Returns:
        dict: The parsed JSON response if the request is successful (status code 200).
        None: If the request fails, an error message is printed with the HTTP status code and response text.

    Example:
        headers = {'X-PBSAUTH': 'your_api_key'}
        schedule = get_schedule_day("https://tvss.services.pbs.org/tvss/klrn/day/", '20250311', headers)
    """

    url = start_url + date
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f'Retrieved json for {date}')
        return response.json()        
    else:
        print(f'Error: {response.status_code}, {response.text}')

def get_schedule(    
    output_path,
    startdate=None,
    days=7,
    api_endpoint=PBS_TV_SCHEDULE_ENDPOINT,
    station=STATION_CALL_SIGN,
    api_key=PBS_TV_SCHEDULE_API_KEY
):
    """
    Retrieves a TV schedule for the specified number of days from the PBS TV Schedule API.

    Args:
        output_path (str): The directory path where the output JSON file will be saved.
        startdate (str, optional): The start for retrieving the schedule, in 'YYYYMMDD' format. Defaults to today's date. 
        days (int, optional): The number of days for which the schedule is to be retrieved. Default is 7.
        api_endpoint (str, optional): The PBS TV schedule API endpoint. Default is `PBS_TV_SCHEDULE_ENDPOINT` in config.py.
        station (str, optional): The PBS station call sign. Default is `STATION_CALL_SIGN` in config.py.
        api_key (str, optional): The PBS TV schedule API key for authorization. Default is set in .env.

    Returns:
        None: The function saves the schedule to a JSON file at the specified output path.

    Example:
        get_schedule('path/to/output/', days=7)
    """    

    # determine start date
    if startdate is None:
        day = datetime.now()
        startdate = day.strftime('%Y%m%d')
    else:
        day = datetime.strptime(startdate, '%Y%m%d')

    start_url = f'{api_endpoint}{station}/day/'  
    headers = {'X-PBSAUTH': api_key}
    result = {"start_date": startdate}

    print()
    for x in range(days):
        day_str = (day + timedelta(days=x)).strftime('%Y%m%d')
        result[day_str] = get_schedule_day(start_url, day_str, headers)         

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2) 

    print(f"Schedule saved to {output_path}")       
