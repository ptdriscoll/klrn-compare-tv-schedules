import json
import pandas as pd
from datetime import datetime

def parse(input_path, output_path):
    """
    Parses a JSON TV schedule file, extracts relevant TV listings, and saves them as a CSV file.

    The JSON file contains TV schedule data where each top-level key (except "start_date") represents a date 
    in "yyyymmdd" format. Each date contains a "feeds" list, where each feed dictionary includes:
        - "digital_channel": The channel number (e.g., "9.1", "9.2").
        - "listings": A list of program listings for that channel on that date.

    Args:
        json_file (str): Path to the input JSON file containing the TV schedule.
        output_csv (str): Path to the output CSV file.

    Output:
        A CSV file containing parsed TV schedule data with the following columns:
        - Channel (str): The TV channel identifier.
        - Date (datetime): The broadcast date.
        - Start Time (datetime): The program's start time.
        - Program Name (str): The name of the TV program.
        - Episode Name (str): The name of the TV program episode.
        - Episode Number (str, optional): The episode number if available.
        - Description (str, optional): A brief description of the program. 

    Notes:
        - Filters listings for digital channels 9.1, 9.2, 9.3, and 9.4.
        - Extracts the relevant fields: channel, date, start time, program name, episode details, and description.
        - Formats the date as MM/DD/YYYY and the time as HH:MM:SS.
        - Sorts the listings by Channel (ascending), Date (ascending), and Start Time (ascending).
        - Saves the processed data as a CSV file.
    """

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    valid_channels = {'9.1', '9.2', '9.3', '9.4'}
    rows = []
    
    for date_key, date_value in data.items():
        if date_key == 'start_date': continue  # skip metadata        
        feeds = date_value.get('feeds', [])
        
        for feed in feeds:
            digital_channel = str(feed.get('digital_channel', ''))
            if digital_channel in valid_channels:
                listings = feed.get('listings', [])
                if not listings: continue  # skip if no listings
                
                for listing in listings:
                    start_time = listing.get('start_time', '')
                    if not start_time: continue # skip if not start time
                    formatted_time = f'{start_time[:2]}:{start_time[2:]}:00'                    
                    formatted_date = datetime.strptime(date_key, "%Y%m%d").strftime("%m/%d/%Y")
                    sort_date = pd.to_datetime(date_key, format="%Y%m%d"),  # for sorting 
                    sort_time = pd.to_datetime(listing["start_time"], format="%H%M").time()  # for sorting
                    
                    rows.append([
                        digital_channel,
                        formatted_date,
                        formatted_time,
                        listing.get('title', ''),
                        listing.get('episode_title', ''),
                        f"#{listing.get('episode_number', '')}" if listing.get('episode_number') else '',
                        listing.get('description', ''),
                        sort_date,
                        sort_time
                    ])
    
    df = pd.DataFrame(rows, columns=[
        'Channel', 'Date', 'Start Time', 'Program Name', 'Episode Name', 
        'Episode Number', 'Description', 'sort date', 'sort time'
    ])

    # sort by Channel (as float), Date, and Start Time
    df['Channel'] = df['Channel'].astype(float)  # ensures proper numeric sorting
    df = df.sort_values(by=['Channel', 'sort date', 'sort time'])
    df = df.drop(columns=['sort date', 'sort time']) # drop columns added for sorting
    
    df.to_csv(output_path, index=False)
    print(f'CSV file saved: {output_path}')

if __name__ == '__main__':  
    parse('./data/pbs.json', './output/pbs.csv')
