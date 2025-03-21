import json
import pandas as pd
from datetime import datetime
import re

def parse(input_path):
    """
    Parses a JSON TV schedule file, extracts relevant TV listings, and returns a DataFrame.

    The JSON file contains TV schedule data where each top-level key (except "start_date") represents a date 
    in "yyyymmdd" format. Each date contains a "feeds" list, where each feed dictionary includes:
        - "digital_channel": The channel number (e.g., "9.1", "9.2").
        - "listings": A list of program listings for that channel on that date.

    Arg:
        input_path (Path): Path to the input JSON file containing the TV schedule.

    Notes:
        - Filters listings for digital channels 9.1, 9.2, 9.3, and 9.4.
        - Extracts the relevant fields: channel, date, start time, program name, episode details, and description.
        - Formats the date as MM/DD/YYYY and the time as HH:MM:SS.
        - Sorts the listings by Channel (ascending), Date (ascending), and Start Time (ascending).        

    Returns:
        pd.DataFrame: A DataFrame containing parsed TV schedule data with the following columns:
        - Channel (str): The TV channel identifier.
        - Date (datetime.date): The broadcast date.
        - Start Time (datetime.time): The program's start time.
        - Program Name (str): The name of the TV program.
        - Episode Name (str): The name of the TV program episode.
        - Nola Episode (str, optional): The Nola episode number if available.
        - Description (str, optional): A brief description of the program.
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
                    date = pd.to_datetime(date_key, format="%Y%m%d").date()
                    start_time = pd.to_datetime(listing["start_time"], format="%H%M").time()  
                    
                    rows.append([
                        digital_channel,
                        date,
                        start_time,                     
                        listing.get('title', ''),
                        f"#{listing.get('nola_episode', '')}" if listing.get('nola_episode') else '',
                        listing.get('episode_title', ''),                        
                        listing.get('description', '')
                    ])
    
    df = pd.DataFrame(rows, columns=[
        'Channel', 'Date', 'Start Time', 'Program Name', 'Nola Episode', 
        'Episode Name', 'Description'
    ])

    df = df.sort_values(by=['Channel', 'Date', 'Start Time']) # sort
    df = df.map(lambda x: re.sub(r'\s+', ' ', x.strip()) if isinstance(x, str) else x) # remove extra white spaces
    
    return df 
