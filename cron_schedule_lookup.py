import pandas as pd
import croniter
import datetime
import pytz
import re

def get_task_datetimes(cron_schedule, start_date, end_date, time_interval, time_zone):
    """
    Generate a list of datetimes for tasks within a specified time interval and date range.
    
    Parameters:
    - cron_schedule (str): Cron schedule for the task.
    - start_date (str or datetime): Start date for the date range. If a string, must be in the
        format 'YYYY-MM-DD'.
    - end_date (str or datetime): End date for the date range. If a string, must be in the
        format 'YYYY-MM-DD'.
    - time_interval (tuple): Time interval for the datetimes, in the format (start_hour, end_hour).
        Both start_hour and end_hour should be integers between 0 and 23.
    - time_zone (str): Time zone of the datetimes.
    
    Returns:
    - list: List of datetime objects for the task.
    """
    # Convert start_date and end_date to datetime objects
    if isinstance(start_date, str):
        start_date = datetime.fromisoformat(start_date)
    if isinstance(end_date, str):
        end_date = datetime.fromisoformat(end_date)

    # Set the timezone for the datetime objects
    start_date = start_date.replace(tzinfo=pytz.timezone(time_zone))
    end_date = end_date.replace(tzinfo=pytz.timezone(time_zone))

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

        if start_hour > end_hour: # Means that part of the interval is in the next day
            if dt.hour >= start_hour and dt.hour != 0:
                # Add the datetime to the list if it is before midnight
                datetimes.append(datetime.datetime.strftime(dt,'%Y-%m-%d %H:%M'))
            elif dt.hour >= 0 and dt.hour < end_hour:
                # Add the datetime to the list if it is past midnight
                datetimes.append(datetime.datetime.strftime(dt,'%Y-%m-%d %H:%M'))

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


# Set the default time zone
default_time_zone = pytz.UTC
# Prompt the user to enter an offset from UTC in the format "±H:M" (e.g. "-8:00" for UTC-8, "8:00" for UTC+8, "0:00" for UTC)
offset = input("Enter an offset from UTC in the format '±H:M' (e.g. '-8:00' for UTC-8, '8:00' for UTC+8, '+0:00' for UTC) or leave blank to use the default time zone: ")
# Use the default time zone if the user didn't specify an offset
if not offset:
    time_zone = default_time_zone
else:
    # Validate the user's input
    while not re.match(r"^[+-]\d+:\d\d$", offset):  # Check that the input consists of a sign character and two numbers separated by a colon
        print("Invalid input. Please enter the offset in the format '±H:M'.")
        offset = input("Enter an offset from UTC in the format '±H:M' (e.g. '-8:00' for UTC-8, '8:00' for UTC+8, '+0:00' for UTC) or leave blank to use the default time zone: ")
    # Split the input on the ":" character
    offset_parts = offset.split(":")
    # Get the sign character and convert it to a multiplier
    sign = offset_parts[0][0]
    if sign == "+":
        sign = 1
    elif sign == "-":
        sign = -1
    else:
        raise ValueError("Invalid sign character: '{}'. Please enter '+' for positive offsets or '-' for negative offsets.".format(sign))
    # Convert the hours and minutes parts to integers
    offset_hours = int(offset_parts[0][1])
    offset_minutes = int(offset_parts[1])
    # Create a time zone object with the specified offset from UTC
    tz_offset = sign * (offset_hours * 60 + offset_minutes)  # Calculate the offset in minutes
    time_zone = pytz.FixedOffset(tz_offset)
    # Use the default time zone if the offset is 0
    if offset_hours == 0 and offset_minutes == 0:
        time_zone = default_time_zone


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
    datetimes = get_task_datetimes(cron_schedule, start_date, end_date, time_interval, time_zone)
    
    # Add the task name and datetimes to the task data list if the list is not empty
    if datetimes:
        task_data.append({'command': task_name, 'datetimes': datetimes})

# Create a new dataframe from the task data
df_output = pd.DataFrame(task_data)

# Save the output
df_output.to_csv("functions_btw_{}and{}.csv".format(start_hour,end_hour))