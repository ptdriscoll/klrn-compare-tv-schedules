from dotenv import load_dotenv
import os

load_dotenv()

# dictionary mapping parser names to lists of raw file names to parse.
# each parser corresponds to a specific file format.
# example: {'parser': ['file_name_1.pdf', 'file_name_2.pdf']}
FILES = {
    'protrack': [  # pdf format
        'Protrack_2025-04-13_2025-05-03.pdf'
    ], 
    'titan': [  # mhtml format
        'MediaStar_2025-04-15_9.1.mhtml',
        'MediaStar_2025-04-15_9.2.mhtml'      
    ], 
    'pbs': [  # json format
        'pbs.json'
    ] 
}

# variables for call for PBS TV Schedules API
PBS_TV_SCHEDULE_API_KEY = os.getenv('PBS_TV_SCHEDULE_API_KEY') 
PBS_TV_SCHEDULE_ENDPOINT = 'https://tvss.services.pbs.org/tvss/'
STATION_CALL_SIGN = 'klrn'
