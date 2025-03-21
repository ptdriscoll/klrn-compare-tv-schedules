import pandas as pd

PARSERS = {
    'protrack': 'parsers.protrack.process',
    'titan': 'parsers.titan.process',
    'pbs': 'parsers.pbs.process'
}   

def parse(input_paths, output_path, source):
    """
    Parses multiple files for a given source (pbs, protrack, titan), concatenates their data, 
    removes duplicates, and saves the final result to a CSV file.

    Args:
        input_paths (list[Path]): List of file paths to parse.
        output_path (Path): Path to save the concatenated CSV file.
        source (str): The source module to use ('pbs', 'protrack' or 'titan').

    Output:
        A CSV file containing parsed TV schedule data with the following columns:
        - Channel (str): The TV channel identifier.
        - Date (datetime.date): The broadcast date.
        - Start Time (datetime.time): The program's start time.
        - Program Name (str): The name of the TV program.
        - Episode Name (str): The name of the TV program episode.
        - Nola Episode (str, optional): The Nola episode number if available.
        - Description (str, optional): A brief description of the program.         
    """

    # import parse
    if source in PARSERS: parse = getattr(__import__(PARSERS[source], fromlist=['parse']), 'parse')
    else: raise ValueError(f"Unknown source: {source}")
    
    # parse each file using the selected parsing function
    dfs = []
    for path in input_paths:
        df = parse(path)
        dfs.append(df)
    
    # concatenate all DataFrames, remove duplicates, and sort 
    df = pd.concat(dfs, ignore_index=True)
    df = df.drop_duplicates()
    df = df.sort_values(by=['Channel', 'Date', 'Start Time'])

    # save result to output_path
    df.to_csv(output_path, index=False)
    print(f"\nData from {len(input_paths)} files concatenated and saved to {output_path}")
