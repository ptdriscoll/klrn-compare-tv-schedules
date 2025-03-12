import os
from pathlib import Path
import argparse
from config import FILES

PARSERS = {
    'protrack': 'parsers.protrack.process',
    'titan': 'parsers.titan.process',
    'pbs': 'parsers.pbs.process'
}   

def get_input_output_paths(source):
    """
    Gets absolute paths of input and output files, based on source, which comes from a 
    command-line argument. 

    Arg:
        source (str): Name of module in parsers. 

    Returns:
        Tuple[str, str]: Absolute paths of input and output files.        
    """
    
    # set up absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.normpath(os.path.join(base_dir, '.')) 
    output_dir = os.path.join(ROOT_DIR, 'output')

    # create input and output paths
    input_path = os.path.join(ROOT_DIR, 'data', FILES[source])
    output_path = os.path.join(output_dir, f'{source}.csv') 

    return input_path, output_path    

def parse_schedule(source, input_path='', output_path=''):
    """
    Parses TV schedule by running process.parse() from a module in parsers. The module is
    determined by `source`, which comes from a command-line argument. The result is
    saved as 'output/{source}.csv'. 

    Arg:
        source (str): Name of module in parsers, from which process.parse() will be run. 
        input_path (str, optional): Path to the input file. Defaults to an empty string.
        output_path (str, optional): Path to the output file. Defaults to an empty string.   
    """
    
    # import parse
    if source in PARSERS:
        parse = getattr(__import__(PARSERS[source], fromlist=['parse']), 'parse')

    # check for input and output paths, and get if needed
    if not input_path and not output_path: 
        input_path, output_path = get_input_output_paths(source)

    parse(input_path, output_path)

def compare_schedules(source_1, source_2, channel='9.1'):
    """
    Compares two TV schedules by running compare.compare_tv_schedules from a module in comparators. 
    The files are determined by `source_1` and `source_2`, which comes from a command-line argument. 
    The result is saved as 'output/{source_1}_{source_2}.csv'. 

    Args:
        source_1 (str): Name of first parsed file, excluding the '.csv' extension.
        source_2 (str): Name of second parsed file, excluding the '.csv' extension.
        channel (str, optional): TV channel to filter the comparison. Defaults to '9.1'.
    """    

    from comparators.compare import compare_tv_schedules as compare

    # get first parsed file
    input_path_1, parsed_path_1 = get_input_output_paths(source_1)
    if not os.path.exists(parsed_path_1): parse_schedule(source_1, input_path_1, parsed_path_1)

    # get second parsed file
    input_path_2, parsed_path_2 = get_input_output_paths(source_2)
    if not os.path.exists(parsed_path_2): parse_schedule(source_2, input_path_2, parsed_path_2)
    
    # compare files
    output_dir = os.path.dirname(parsed_path_1)
    output_file = f'{source_1}_{source_2}.csv'
    output_path = os.path.join(output_dir, output_file)
    if channel == '9': channel = '9.1'
    compare(parsed_path_1, parsed_path_2, output_path, channel)

def get_schedule_from_api(source, days):
    """
    Retrieve raw TV schedule data from an API and store it for later processing.

    Args:
        source (str): The source of the TV schedule data (e.g., 'pbs').
        days (int): The number of days of data to retrieve.

    Returns:
        None: The retrieved data is saved to a designated location.
    """

    from api.pbs import get_schedule
    input_path, _ = get_input_output_paths(source) # output will go to data folder, as an input later
    get_schedule(input_path, days)

def explore_file(input_path, level=3, items=3):
    """
    Explore a JSON file by calling the `explore_json` function with specified levels and items.

    Args:
        input_path (str): Path to the JSON file to explore.
        level (int): Number of levels to explore in the JSON structure.
        items (int): Number of items to show from each list in the JSON data.
    """

    from utils.json_explorer import explore_json_file
    base_dir = Path(__file__).resolve().parent
    input_path = base_dir / input_path
    explore_json_file(input_path, max_level=level, max_items=items)   

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse or compare TV schedules, or get schedule data')
    subparsers = parser.add_subparsers(dest='command', required=True)
    choices = list(PARSERS.keys()) 

    # parse command
    parse = subparsers.add_parser('parse', help='Parse a TV schedule from source')
    parse.add_argument('source', choices=choices, help='Source to parse')

    # compare command
    compare = subparsers.add_parser('compare', help='Compare two parsed TV schedules')
    compare.add_argument('sources', nargs=2, choices=choices, help='Sources to compare')
    compare.add_argument('--channel', default='9.1', help='Optional channel to filter for (default: 9.1)')

    # get command
    get_parser = subparsers.add_parser('get', help='Get raw TV schedule data from a source')
    get_parser.add_argument('source', choices=['pbs'], help='Source to get data from')
    get_parser.add_argument('--days', type=int, default=7, help='Number of days of data to retrieve (default: 7)')

    # explore json data command
    explore = subparsers.add_parser('explore', help='Explore a JSON file')
    explore.add_argument('file', help='Relative path to the JSON file from root directory')
    explore.add_argument('--level', type=int, default=4, help='Number of levels to explore (default: 4)')
    explore.add_argument('--items', type=int, default=6, help='Number of items to show per list (default: 6)')

    args = parser.parse_args()

    if args.command == 'parse': parse_schedule(args.source)
    elif args.command == 'compare': compare_schedules(args.sources[0], args.sources[1], args.channel)
    elif args.command == 'get': get_schedule_from_api(args.source, args.days)
    elif args.command == 'explore': explore_file(args.file, args.level, args.items)
