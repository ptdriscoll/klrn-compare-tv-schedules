import os
import argparse
from config import FILES

PARSERS = {
    'protrack': 'parsers.protrack.process',
    'titan': 'parsers.titan.process'
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse and/or compare TV schedules')
    subparsers = parser.add_subparsers(dest='command', required=True)
    choices = list(PARSERS.keys()) 

    # parse command
    parse = subparsers.add_parser('parse', help='Parse a TV schedule from source')
    parse.add_argument('source', choices=choices, help='Source to parse')

    # compare command
    compare = subparsers.add_parser('compare', help='Compare two parsed TV schedules')
    compare.add_argument('sources', nargs=2, choices=choices, help='Sources to compare')
    compare.add_argument('channel', nargs='?', default='9.1', help='Optional channel to filter for (default: 9.1)')

    args = parser.parse_args()

    if args.command == 'parse': parse_schedule(args.source)
    elif args.command == 'compare': compare_schedules(args.sources[0], args.sources[1], args.channel)
