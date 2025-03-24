from pathlib import Path
import pandas as pd

def compare_tv_schedules(path_1, path_2, output_path, channel='9.1', start_date=None, end_date=None):
    """
    Compares two CSV files with TV schedules to identify day and time slots that do not match, and outputs a CSV file.
    
    Args:
        path_1 (str): Path to the CSV file with the correct TV schedule:
            - Channel (str): The TV channel.
            - Date (datetime): The broadcast date.
            - Start Time (datetime): The program's start time.
            - Program Name (str): The name of the TV program.
            - Nola Episode (str, optional): The Nola episode number, if available.
            - Episode Number (str, optional): The episode number, if available.
            - Any other columns.
            
        path_2 (str): Path to the CSV file with the TV schedule to check for any mismatches:
            - Has same structure as path_1 file.

        output_path (str): Path where the output CSV file will be saved.
        channel (str, optional): TV channel to filter the comparison. Defaults to '9.1'.
        start_date (datetime, optional): The start date for retrieving data. Defaults to `None`.
        end_date (datetime, optional): The end date for retrieving data. Defaults to `None`.        
    
    Output:
        A CSV file at `output_path` containing the combined TV schedules and a `MISMATCH` column:
            - Channel (str): The TV channel.
            - Date (datetime): The broadcast date.
            - Start Time (datetime): The program's start time.
            - Program Name - Reference (str): The name of the correct TV program.
            - Nola Episode - Reference (str, optional): The Nola episode number, if available.
            - Episode Number - Reference (str, optional): The episode number, if available.
            - Program Name - Comparison (str): The name of the TV program being checked.
            - Nola Episode - Comparison (str, optional): The episode number being checked, if available.
            - Episode Number - Comparison (str, optional): The episode number being checked, if available.
            - MISMATCH (str): Indicates 'YES' if there is a mismatch between program names or episode numbers, 
              or an empty string if they match.

    Notes:
        - CSV files are merged into a DataFrame on the columns: Channel, Date, and Start Time as keys.
        - All other columns are included with names concatenated with either " - (file 1 name)" or " - (file 2 name)".
        - A DateTime column is added to filter by shared timeframes, and then sort by date and time, before being dropped.
        - A MISMATCH column is added, and values in "Program Name - (file 1 name)" and "Program Name - (file 2 name)" are compared:
            - If they match, the value of MISMATCH is ''.
            - If they don't match, the value of MISMATCH is 'YES'.
        - "Nola Episode - (file 1 name)" and "Nola Episode - (file 2 name)" are also compared if both columns exist and have values:
            - If they don't match, the value of MISMATCH is set to 'YES'.
        - "Episode Number - (file 1 name)" and "Episode Number - (file 2 name)" are also compared if both columns exist and have values:
            - If they don't match, the value of MISMATCH is set to 'YES'.            
    """
    
    # read in CSV files as dataframes
    df_1 = pd.read_csv(path_1, dtype={'Channel': str})       
    df_2 = pd.read_csv(path_2, dtype={'Channel': str})  

    # filter dfs by channel
    df_1 = df_1[df_1['Channel'] == channel] 
    df_2 = df_2[df_2['Channel'] == channel] 

    # create combined DateTime column 
    df_1['Date'] = pd.to_datetime(df_1['Date'])
    df_1['DateTime'] = pd.to_datetime(df_1['Date'].dt.strftime('%Y-%m-%d') + ' ' + df_1['Start Time'], errors='coerce')

    df_2['Date'] = pd.to_datetime(df_2['Date'])
    df_2['DateTime'] = pd.to_datetime(df_2['Date'].dt.strftime('%Y-%m-%d') + ' ' + df_2['Start Time'], errors='coerce')

    # get shared time frame
    datetime_start = max(df_1['DateTime'].min(), df_2['DateTime'].min())
    datetime_end = min(df_1['DateTime'].max(), df_2['DateTime'].max())

    # if user set start and end dates, use those if they are, respectively, later and earlier
    if start_date and start_date > datetime_start: datetime_start = start_date
    if end_date and end_date < datetime_end: datetime_end = end_date

    # create column suffixes
    file_1_name = Path(path_1).stem
    file_2_name = Path(path_2).stem 
    suffixes = [f' - {file_1_name}', f' - {file_2_name}']

    # add suffixes to unique columns in each df
    merge_cols = ['Channel', 'Date', 'Start Time', 'DateTime']
    df_1_unique = [col for col in df_1.columns if col not in df_2.columns and col not in merge_cols]
    df_2_unique = [col for col in df_2.columns if col not in df_1.columns and col not in merge_cols]
    df_1 = df_1.rename(columns={col: col + suffixes[0] for col in df_1_unique})
    df_2 = df_2.rename(columns={col: col + suffixes[1] for col in df_2_unique}) 

    # merge on Channel, Date, Start Time and DateTime    
    df = pd.merge(df_1, df_2, on=merge_cols, how='outer', suffixes=suffixes)

    # trim for time frame, and then sort by DateTime before dropping that column
    df = df[(df['DateTime'] >= datetime_start) & (df['DateTime'] <= datetime_end)]
    df = df.sort_values(by='DateTime')
    df.drop(columns=['DateTime'], inplace=True)

    # create MISMATCH column
    df.insert(0, 'MISMATCH', '')

    # compare program names
    mask_names = df[f'Program Name - {file_1_name}'].str.lower() != df[f'Program Name - {file_2_name}'].str.lower()
    df.loc[mask_names, 'MISMATCH'] = 'YES'

    # Compare Nola Episode, if both columns exist
    nola_episode_col_1 = f'Nola Episode - {file_1_name}'
    nola_episode_col_2 = f'Nola Episode - {file_2_name}'
    if nola_episode_col_1 in df.columns and nola_episode_col_2 in df.columns:
        mask_nola_episode_exist = df[f'Nola Episode - {file_1_name}'].notna() & df[f'Nola Episode - {file_2_name}'].notna()
        mask_nola_episode = df[f'Nola Episode - {file_1_name}'] != df[f'Nola Episode - {file_2_name}']
        df.loc[mask_nola_episode_exist & mask_nola_episode, 'MISMATCH'] = 'YES'

    # compare Episode Number, if both columns exist
    episode_col_1 = f'Episode Number - {file_1_name}'
    episode_col_2 = f'Episode Number - {file_2_name}'
    if episode_col_1 in df.columns and episode_col_2 in df.columns:
        mask_episodes_exist = df[f'Episode Number - {file_1_name}'].notna() & df[f'Episode Number - {file_2_name}'].notna()
        mask_episodes = df[f'Episode Number - {file_1_name}'] != df[f'Episode Number - {file_2_name}']
        df.loc[mask_episodes_exist & mask_episodes, 'MISMATCH'] = 'YES'

    # compile only mismatches
    df_mis = df[df['MISMATCH'] == 'YES']

    df.to_csv(output_path, index=False)
    df_mis.to_csv(output_path.replace('.csv', '_mismatches.csv'), index=False)
