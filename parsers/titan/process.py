import sys
import email
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime


def split_cell(row):
    """
    Extracts time, program name, episode number, and episode description from a TV schedule row cell.

    Args:
        row (str): A string containing program information details.

    Returns:
        pandas.Series: A Series containing:
            - start_time (str or pandas.NaT): The extracted start time (HH:MM) or NaT if missing.
            - program_name (str): The extracted program name.
            - episode (str): The formatted episode number (e.g., "#12") or an empty string if not found.
            - description (str): The episode description or an empty string if not found.
    
    Notes:
        - If the time pattern is not found, `start_time` is set to `NaT`, and `program_name` is empty.
        - If no program name is extracted, a message is printed.
        - If time is found, it is formatted as HH:MM using `pd.to_datetime`.
    """
    
    pattern_time = r"\d{1,2}:\d{2}"
    pattern_episode = r"Epi#:\s*(\d+[a-zA-Z]?)"
    pattern_description = r"Epi#:\s*\d+[a-zA-Z]?\s*(.*)"

    time_match = re.search(pattern_time, row)
    episode_match = re.search(pattern_episode, row)
    description_match = re.search(pattern_description, row)

    episode = f'#{episode_match.group(1)}' if episode_match else ''
    description = description_match.group(1) if description_match else ''

    if time_match:
        start_time = time_match.group()
        program_name = row.split(start_time)[0].strip()
        start_time = pd.to_datetime(start_time, format='%H:%M').strftime('%H:%M')        
    else:
        start_time = pd.NaT
        program_name = ''
        print(f'Could not find time, or split for name, in row:', row)
    
    if not program_name: print(f'Could not find name in row:', row)     

    return pd.Series([start_time, program_name, episode, description]) 

def adjust_dates_times(df):
    """
    Adjusts dates and times in a DataFrame to handle AM/PM transitions correctly.

    Args:
        df (pandas.DataFrame): A DataFrame that includes columns "Date" and "Start Time".

    Returns:
        pandas.DataFrame: A modified copy of the input DataFrame with adjusted "Date" and "Start Time" columns.

    Notes:
        - Ensures that the "Date" column remains synchronized with "Start Time".
        - Detects AM/PM transitions and updates "Start Time" accordingly.
        - If the current date gets more than one day ahead of the row's "Date", the script exits with an error message.
        - Uses a flag (`is_am`) to track transitions between AM and PM.
        - Adjusts "Start Time" when crossing from PM back to AM.
        - When transitioning back to AM (after PM), the day is incremented.
    """

    print_variables = False

    df = df.copy()  

    new_dates = []
    new_times = []
    
    is_am = True 
    current_date = None
    last_time = None
    noon = pd.to_datetime("1900-01-01 12:00:00")
    midnight = pd.to_datetime("1900-01-01 00:00:00")

    for i, row in df.iterrows():
        if not current_date: current_date = row['Date']
        if not last_time: last_time = row['Start Time']
        start_time = row['Start Time']
        new_time = start_time
        
        # ensure current_date does not get more than a day ahead of row['Date']
        if current_date > (row['Date'] + pd.Timedelta(days=1)):
            print('==================================================')
            print('==================================================')
            print(f"current_date is out of sync with row['Date'] at row {i}.")
            print()
            print('current_date:', current_date)
            print('last_time:', last_time)
            print('is_am:', is_am)
            print()
            print('ROW:\n')
            print(row)   
            print()        
            sys.exit('Exiting due to mismatch.')

        if print_variables:
            print('==================================================')
            print('==================================================')
            print('current_date:', current_date)
            print('start_time:', start_time)
            print('last_time:', last_time)
            print('is_am:', is_am)  
            print()  
            print('start_time < last_time:', start_time < last_time)
            print('start_time.hour == 12:', start_time.hour == 12)
            print('last_time.hour != 12:', last_time.hour != 12)
            print('is_am:', is_am)
            print()
            print('is_am and start_time.hour == 12:', is_am and start_time.hour == 12)
            print('not is_am and start_time.hour < 12:', not is_am and start_time.hour >= 12)
            print()        
            print('ROW:\n')
            print(row)  
            print()                

        # track transition from am to pm and back
        if (start_time < last_time or start_time.hour == 12) and last_time.hour != 12:
            is_am = not is_am #toggle am/pm flag

            # transition to a new day (am coming after pm)
            if is_am: 
                current_date += pd.Timedelta(days=1) # add a day when switching back to am   

        # modify time and/or date based on am/pm transitions
        if is_am and start_time.hour == 12: # hour after midnight should be 00, so subract 12 hours
            new_time = start_time - pd.Timedelta(hours=12) 

        elif not is_am and start_time.hour < 12: # time is am but should be pm, so add 12 hours
                new_time = start_time + pd.Timedelta(hours=12) 

        if print_variables:
            print('==================================================')
            print('current_date:', current_date)
            print('new_time:', new_time)
            print('start_time:', start_time)
            print('is_am:', is_am)  
            print()       
        
        new_dates.append(current_date)
        new_times.append(new_time)
        last_time = start_time

    df["Date"] = new_dates
    df["Start Time"] = new_times
    return df

def parse(input_path, output_path):
    """
    Parses a comparison file in Edge's .mhtml format and outputs a CSV file.

    Args:
        input_path (str): Path to the input .mhtml file.
        output_path (str): Path to the output CSV file.

    Output:
        A CSV file containing parsed TV schedule data with the following columns:
        - Channel (str): The TV channel.
        - Date (datetime): The broadcast date.
        - Start Time (datetime): The program's start time.
        - Program Name (str): The name of the TV program.
        - Episode Number (str, optional): The episode number, if available.
        - Description (str, optional): A brief description of the program.        

    Notes:
        - Extracts program schedule data from the .mhtml file.
        - Adjusts dates and times for AM/PM transitions.
        - Cleans up extra whitespace in extracted data.
        - Splits "Program Info" into separate columns.
        - Writes the final structured data to a CSV file.
    """     
    
    with open(input_path, 'rb') as f:        
        msg = email.message_from_binary_file(f) 
 
    html = None
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            html = part.get_payload(decode=True).decode("utf-8", errors="ignore")     

    if html:
        soup = BeautifulSoup(html, 'lxml')
        
        data = {}
        
        grid = soup.find('form', id='gridForm')
        if grid:
            # get columns and data
            for div in grid.find_all('div', id=True):
                id = div['id']
                if id.startswith('gCol'):
                    cells = div.find_all('div', class_='cellBase normal pointerCursor')
                    data[id] = [cell.get_text(separator=' ', strip=True) for cell in cells]  
                    
            #get headers
            dates = []
            header_div = soup.find('div', id='dateHeaderDiv') 
            if header_div:
                headers = headers = header_div.select('div.cellBase.dateHdrCell')
                for header in headers:
                    date = header['title']
                    date_parts = date.split(' - ')
                    if len(date_parts) == 2:
                        dates.append(date_parts[1])
                    
        if data:
            df = pd.DataFrame.from_dict(data, orient='index').transpose()            
            
            # replace column headers with dates
            if len(df.columns) == len(dates):
                df.columns = dates
            else: print('Number of dates did not match number of columns') 
            
            # collapse headers into one column, and data from columns into second column  
            df = df.melt(var_name='Date', value_name='Program Info').dropna(subset=['Program Info'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            # get TV channel from file name, and add as column to df
            match = re.search(r'_(.*?)\.mhtml$', input_path)
            channel = match.group(1) if match else '9.1'
            print(channel)
            df.insert(0, 'Channel', channel) 
            df['Channel'] = df['Channel'].astype(str) 

            # remove extra white spaces
            df = df.map(lambda x: re.sub(r'\s+', ' ', x.strip()) if isinstance(x, str) else x)            

            # split Program Info column
            new_cols = ['Start Time', 'Program Name', 'Episode Number', 'Description']
            df[new_cols] = df['Program Info'].apply(split_cell)
            df.drop(columns=['Program Info'], inplace=True)
            df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M', errors='coerce')

            # adjust times in afternoons, and dates past midnight
            df = adjust_dates_times(df)
            df['Start Time'] = df['Start Time'].dt.strftime('%H:%M:%S') # format for later comparison 
       
            df.to_csv(output_path, index=False) 
            
        else: print('No data found in comparison file')   

    else: print('No HTML content found in comparison file')
    