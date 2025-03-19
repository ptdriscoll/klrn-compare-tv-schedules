from pypdf import PdfReader
import re
import pandas as pd
import re


def parse(input_path, output_path):
    """
    Parses a reference PDF file and outputs a structured CSV file.

    Args:
        input_path (Path): Path to the input PDF file.
        output_path (Path): Path to the output CSV file.

    Output:
        A CSV file containing parsed TV schedule data with the following columns:
        - Channel (str): The TV channel identifier.
        - Date (datetime): The broadcast date.
        - Start Time (datetime): The program's start time.
        - Program Name (str): The name of the TV program.
        - Nola Episode (str, optional): The Nola episode number if available.

    Notes:
        - Extracts text from each page of the PDF file.
        - Identifies structured data using regex patterns.
        - Cleans and formats extracted data.
        - Converts dates and times to appropriate formats.
        - Sorts the output by Channel, Date, and Start Time.
        - Writes the final structured data to a CSV file.
    """
        
    reader = PdfReader(input_path)
    num_pages = len(reader.pages)
    line_count = 0
    
    print('\nEXTRACTING DATA FROM ' + str(num_pages) + ' PAGES')
    
    data = []
    columns = ['Channel', 'Date', 'Start Time', 'Program Name', 'Nola Episode']
    pattern_time = r'\d{2}:\d{2}:\d{2}:\d{2}'
    pattern_channel = r'KLRN(\d+\.\d+|\w{2})'
    pattern_date = r'\b\d{2}/\d{2}/\d{4}\b'
    pattern_episode = r'#(\d+)'
    
    for x in range(num_pages):
        page = reader.pages[x]
        text = page.extract_text()
        lines = text.split('\n')    
        
        #print('\n\n============================== PAGE', x+1 ,'==============================\n')  
        
        for line in lines:
            time = re.search(pattern_time, line)
            if time:                 
                line_count += 1    
                
                channel = re.search(pattern_channel, line)
                date = re.search(pattern_date, line) 
                program = line.split(time.group())[0].strip()
                episode = re.search(pattern_episode, program)
                
                if episode: 
                    episode = episode.group()
                    program = program.split(episode)[0].rstrip()
                else: episode = ''     
                
                fields = [
                    channel.group(1),
                    date.group(),
                    time.group(),
                    program,
                    episode
                ]
                
                data.append(fields)
                #print('\n\n========== LINE ' + str(line_count) + ' ==========\n\n', line, '\n\n', fields)
    
    df = pd.DataFrame(data, columns=columns)  
    df['Channel'] = df['Channel'].astype(str) 
    df['Date'] = pd.to_datetime(df['Date'])
    df['Start Time'] = pd.to_datetime(df['Start Time'], format='%H:%M:%S:%f').dt.strftime('%H:%M:%S')
    df = df.sort_values(by=['Channel', 'Date', 'Start Time'])
    df = df.map(lambda x: re.sub(r'\s+', ' ', x.strip()) if isinstance(x, str) else x)
    
    print('\n' + str(line_count) + ' LINES EXTRACTED')
    print('\n', df.head(20))  
    
    df.to_csv(output_path, index=False)   
    