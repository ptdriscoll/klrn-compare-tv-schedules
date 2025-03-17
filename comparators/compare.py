from pathlib import Path
import pandas as pd

def compare_tv_schedules(path_1, path_2, output_path, channel='9.1'):
    """
    Compares two CSV files with TV schedules to identify day and time slots that do not match, and outputs a CSV file.
    
    Args:
        path_1 (str): Path to the CSV file with the correct TV schedule:
            - Channel (str): The TV channel.
            - Date (datetime): The broadcast date.
            - Start Time (datetime): The program's start time.
            - Program Name (str): The name of the TV program.
            - Episode Number (str, optional): The episode number, if available.
            - Any other columns.
            
        path_2 (str): Path to the CSV file with the TV schedule to check for any mismatches:
            - Has same structure as path_1 file.

        output_path (str): Path where the output CSV file will be saved.
        channel (str, optional): TV channel to filter the comparison. Defaults to '9.1'.
    
    Output:
        A CSV file at `output_path` containing the combined TV schedules and a `MISMATCH` column:
            - Channel (str): The TV channel.
            - Date (datetime): The broadcast date.
            - Start Time (datetime): The program's start time.
            - Program Name - Reference (str): The name of the correct TV program.
            - Episode Number - Reference (str, optional): The episode number, if available.
            - Program Name - Comparison (str): The name of the TV program being checked.
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
        - "Episode Number - (file 1 name)" and "Episode Number - (file 2 name)" are also compared if both have values:
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

    # create column suffixes
    file_1_name = Path(path_1).stem
    file_2_name = Path(path_2).stem 
    suffixes = [f' - {file_1_name}', f' - {file_2_name}']

    # add suffixes to unique columns in each df
    merge_cols = ['Channel', 'Date', 'Start Time', 'DateTime']
    common_cols = merge_cols + ['Program Name', 'Episode Number']
    df_1_unique = df_1.columns.difference(df_2.columns).drop(common_cols, errors="ignore")
    df_2_unique = df_2.columns.difference(df_1.columns).drop(common_cols, errors="ignore")
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

    # compare episode numbers, if both numbers exist
    mask_episodes_exist = df[f'Episode Number - {file_1_name}'].notna() & df[f'Episode Number - {file_2_name}'].notna()
    mask_episodes = df[f'Episode Number - {file_1_name}'] != df[f'Episode Number - {file_2_name}']
    df.loc[mask_episodes_exist & mask_episodes, 'MISMATCH'] = 'YES'

    # compile only mismatches
    df_mis = df[df['MISMATCH'] == 'YES']

    df.to_csv(output_path, index=False)
    df_mis.to_csv(output_path.replace('.csv', '_mismatches.csv'), index=False)
