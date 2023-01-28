import pandas as pd
import datetime


def convert_to_timedelta(runtime_string):
    # split the string by space
    time_parts = runtime_string.split()
    # create a dictionary to store the time parts
    time_dict = {}
    for i in range(0, len(time_parts), 2):
        if time_parts[i+1] == 'years':
            time_dict['years'] = int(time_parts[i])
        elif time_parts[i+1] == 'mons':
            time_dict['months'] = int(time_parts[i])
        elif time_parts[i+1] == 'days':
            time_dict['days'] = int(time_parts[i])
        elif time_parts[i+1] == 'hours':
            time_dict['hours'] = int(time_parts[i])
        elif time_parts[i+1] == 'mins':
            time_dict['mins'] = int(time_parts[i])
        elif time_parts[i+1] == 'secs':
            time_dict['secs'] = float(time_parts[i])
    # convert to timedelta
    time_delta = datetime.timedelta(days=time_dict.get('days',0), hours=time_dict.get('hours',0), minutes=time_dict.get('mins',0),seconds=time_dict.get('secs',0))
    return time_delta

def assign_category(df, column_name):
    """
    Assign a category based on keywords in the column_name
    """
    # Create a new column called 'category' and set all values to 'other' by default
    df['category'] = 'other'

    for index, row in df.iterrows():
        name = row[column_name]
        # Check the name and assign a category based on the keywords in the name
        if 'bus' in name:
            df.at[index, 'category'] = 'bus'
        elif 'train' in name:
            df.at[index, 'category'] = 'train'
        elif 'flight' in name:
            df.at[index, 'category'] = 'flight'
        elif 'hotel' in name:
            df.at[index, 'category'] = 'hotel'
        elif 'payment' in name:
            df.at[index, 'category'] = 'payment'
    return df

def rename_columns(df):
    if 'func_name' in df.columns:
        df.rename(columns={'func_name': 'job_name'}, inplace=True)
    elif 'dag_id' in df.columns:
        df.rename(columns={'dag_id': 'job_name'}, inplace=True)
    return df

def select_columns(df):
    selected_columns = ['job_name', 'schedule', 'avg_runtime', 'category']
    return df[selected_columns]

def process_data(functions_path, dags_path, priority_path):
    functions = pd.read_csv(functions_path)
    dags = pd.read_csv(dags_path)
    priority = pd.read_csv(priority_path)
    
    # Convert avg_runtime to timedelta
    functions['avg_runtime'] = functions['avg_runtime'].apply(convert_to_timedelta)
    
    # Assign category to functions and dags
    functions = assign_category(functions, 'func_name')
    dags = assign_category(dags, 'dag_id')

    # Rename columns
    functions = rename_columns(functions)
    dags = rename_columns(dags)

    # Select the columns of interest
    functions = select_columns(functions)
    dags = select_columns(dags)

    # Join the tables on 'job_name', 'schedule', and 'category'
    merged_data = pd.concat([functions, dags], ignore_index=True)

    # Merge with priority data
    merged_data = merged_data.join(priority.set_index('function_name').loc[:, ['priority']], on='job_name', how='left')
    merged_data.fillna({'priority':5}, inplace=True)

    return merged_data


def main(functions_path=None, dags_path=None, priority_path=None):
    if __name__ == '__main__':
        if functions_path is None:
            print("Enter path to \"functions\" dataset:")
            functions_path = input()
        if dags_path is None:
            print("Enter path to \"dags\" dataset:")
            dags_path = input()
        if priority_path is None:
            print("Enter path to \"priority\" dataset:")
            priority_path = input()
    else:
        if functions_path is None:
            functions_path = './functions.csv'
        if dags_path is None:
            dags_path = './dags.csv'
        if priority_path is None:
            priority_path = './priority.csv'

    cron_data = process_data(functions_path, dags_path, priority_path)
    return cron_data