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
    """

    # import parse
    if source in PARSERS: parse = getattr(__import__(PARSERS[source], fromlist=['parse']), 'parse')
    else: raise ValueError(f"Unknown source: {source}")
    
    # parse each file using the selected parsing function
    dfs = []
    for path in input_paths:
        df = parse(path)
        dfs.append(df)
    
    # concatenate all DataFrames
    df = pd.concat(dfs, ignore_index=True)
    
    # remove duplicates
    df = df.drop_duplicates()

    # save result to output_path
    df.to_csv(output_path, index=False)
    print(f"\nData from {len(input_paths)} files concatenated and saved to {output_path}")
