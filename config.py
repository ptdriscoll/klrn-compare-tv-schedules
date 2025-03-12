from dotenv import load_dotenv
import os

load_dotenv()

# names of raw files to parse, in format {'parser': 'file_name'}
FILES = {
    'protrack': 'February 2025 Schedule.pdf', # .pdf format
    'titan': 'MediaStar_9.1.mhtml', # .mhtml format
    'pbs': 'pbs.json' # .json format
}

# variables for call to PBS TV Schedules API
PBS_TV_SCHEDULE_API_KEY = os.getenv('PBS_TV_SCHEDULE_API_KEY') 
PBS_TV_SCHEDULE_ENDPOINT = 'https://tvss.services.pbs.org/tvss/'
STATION_CALL_SIGN = 'klrn'
