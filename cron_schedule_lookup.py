import pandas as pd
import croniter
import datetime

def get_task_datetimes(cron_schedule, start_date, end_date, time_interval):
    # Create a croniter object for the given schedule and start date
    cron = croniter.croniter(cron_schedule, start_date)
    
    # Unpack the time interval into start and end hours
    start_hour, end_hour = time_interval
    
    # Initialize an empty list to store the datetimes
    datetimes = []
    
    # Iterate over the schedule until we reach the end date
    while True:
        # Get the next datetime in the schedule
        dt = cron.get_next()
        
        # Break if we've reached the end date
        if dt > datetime.datetime.timestamp(end_date):
            break
        
        # Check if the datetime is within the specified time interval
        dt = datetime.datetime.fromtimestamp(dt)
        if dt.hour >= start_hour and dt.hour < end_hour:
            # Add the datetime to the list if it is
            datetimes.append(datetime.datetime.strftime(dt,'%Y-%m-%d %H:%M'))
    
    # Return the list of datetimes, or None if the list is empty
    return datetimes if datetimes else None



# Load the dataframe containing the tasks and their crontab schedules
df = pd.read_csv('functions.csv')

# Prompt the user for the time interval
print('Enter the time interval in the format: start_hour end_hour')
print('For example, to get tasks that run between 3am and 5am, enter: 3 5')
time_interval = input('Enter the time interval: ')
start_hour, end_hour = map(int, time_interval.split())
time_interval = (start_hour, end_hour)

# Prompt the user for the start date
print('Enter the start date in the format: YYYY-MM-DD')
print('Alternatively, enter "now" to use the current date and time as the start date')
start_date_input = input('Enter the start date: ')

if start_date_input == 'now':
    # Use the current date and time if the user inputs "now"
    start_date = datetime.datetime.now()
else:
    # Parse the input date and time
    start_date = pd.to_datetime(start_date_input)

# Prompt the user for the end date
print('Enter the end date in the format: YYYY-MM-DD')
print('Alternatively, enter a time delta in the format +Xd to specify the end date as a number of days after the start date')
print('For example, to get tasks that run for a week starting from the start date, enter: +7d')
end_date_input = input('Enter the end date: ')

if end_date_input.startswith('+'):
    # Parse the time delta if the input is in the form "+Xd"
    days = int(end_date_input[1:-1])
    end_date = start_date + datetime.timedelta(days=days)
else:
    # Parse the input date and time
    end_date = pd.to_datetime(end_date_input)

# Initialize an empty list to store the task data
task_data = []

# Iterate over the tasks in the dataframe
for _, row in df.iterrows():
    # Get the task name and crontab schedule
    task_name = row['command']
    cron_schedule = row['schedule']
    # Get the list of datetimes for the task
    datetimes = get_task_datetimes(cron_schedule, start_date, end_date, time_interval)
    
    # Add the task name and datetimes to the task data list if the list is not empty
    if datetimes:
        task_data.append({'command': task_name, 'datetimes': datetimes})

# Create a new dataframe from the task data
df_output = pd.DataFrame(task_data)

# Save the dataframe
df_output.to_csv("functions_btw_{}and{}.csv".format(start_hour,end_hour))