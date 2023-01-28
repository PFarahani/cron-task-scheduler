import pandas as pd
import datetime
import croniter
import data_preprocessor

def generate_start_date(tasks):
  """
  Generates a start date for each task based on their crontab schedule.

  Parameters:
  - tasks (pandas DataFrame): A pandas DataFrame containing the tasks, their crontab schedules, their average runtime, and their category.

  Returns:
  - A pandas DataFrame with the tasks sorted by start date.
  """
  # Create an empty list to store the start dates
  start_dates = []

  # Iterate over the tasks
  for i, task in tasks.iterrows():
    # Get the crontab schedule
    crontab = task["schedule"]

    # Use croniter to find the next occurrence of the crontab schedule
    cron = croniter.croniter(crontab, datetime.datetime.now())

    # The start date is the next occurrence of the crontab schedule
    start_date = cron.get_next(datetime.datetime)

    # Add the start date to the list
    start_dates.append(start_date)

  # Add the start dates to the tasks DataFrame as a new column
  tasks["start_date"] = start_dates

  # Sort the tasks by start date
  tasks = tasks.sort_values("start_date")

  return tasks


# Define the tasks
functions_path = './functions.csv'
dags_path = './dags.csv'
priority_path = './priority.csv'
cron_data = data_preprocessor.main(functions_path, dags_path, priority_path)

# Define the free time intervals
tasks = generate_start_date(cron_data)


def find_free_times(tasks, start_time, end_time, consider_category=False):
  """
  Finds all the free times between tasks within the specified start and end time.

  Parameters:
  - tasks (pandas DataFrame): A pandas DataFrame containing the tasks, their crontab schedules, their average runtime, and their category.
  - start_time (datetime): The start of the time interval to find the free times.
  - end_time (datetime): The end of the time interval to find the free times.
  - consider_category (bool): A flag indicating whether to consider the category when finding the free times. Default is False.

  Returns:
  - A pandas DataFrame with the start and end time of all free times in each row.
  """

  # Create an empty list to store the free times
  free_times = []

  # Iterate over the tasks
  for i, task in tasks.iterrows():
    # Initialize the start time and end time of the free time
    free_start_time = None
    free_end_time = None

    # Get the crontab schedule and category
    crontab = task["schedule"]
    category = task["category"]
    runtime = task['avg_runtime']

    # Use croniter to find the next occurrence of the crontab schedule
    cron = croniter.croniter(crontab, datetime.datetime.now())

    if i == 0:
      # If this is the first task, the free time starts at the specified start time
      free_start_time = start_time
    else:
      # If this is not the first task, the free time starts at the end of the previous task
      prev_cron = croniter.croniter(tasks.iloc[i-1]["schedule"], datetime.datetime.now())
      prev_end_time = prev_cron.get_next(datetime.datetime)
      free_start_time = prev_end_time + runtime

    # The free time ends at the start of the current task
    task_start_time = cron.get_next(datetime.datetime)
    free_end_time = task_start_time

    # If the free time is not zero and is within the specified time interval, add it to the list
    if (free_end_time - free_start_time).total_seconds() > 0 and start_time <= free_start_time <= end_time:
      if consider_category:
        # If the category needs to be considered, only add the free time if it is in the same category as the current task
        if tasks.iloc[i-1]["category"] == category:
          free_times.append({
              "start_time": free_start_time,
              "end_time": free_end_time
              })
      else:
      # If the category does not need to be considered, add the free time regardless of the category
        free_times.append({
            "start_time": free_start_time,
            "end_time": free_end_time
            })

      # Convert the list of free times to a pandas DataFrame
      free_times_df = pd.DataFrame(free_times)

  return free_times_df


# Specify the start and end time of the time interval
start_time = datetime.datetime.now()
end_time = datetime.datetime.now() + datetime.timedelta(days=3)

# Find all the free times between tasks within the time interval, regardless of the category
free_times_df = find_free_times(tasks, start_time, end_time)

# Find all the free times between tasks within the time interval, only considering the same category
free_times_df = find_free_times(tasks, start_time, end_time, consider_category=True)


def generate_crontab_schedule(free_times, max_runs_per_day, min_hours_gap, average_runtime):
  """
  Generates a crontab schedule that fits within the free time intervals and takes into consideration the possibility of the task running multiple times per day with a certain number of hours gap between each run.

  Parameters:
  - free_times (list): A list of tuples containing the start and end datetimes for each free time interval.
  - max_runs_per_day (int): The maximum number of times the task can run per day.
  - min_hours_gap (int): The minimum number of hours gap between each run.
  - average_runtime (int): The average runtime of the task in minutes.

  Returns:
  - A pandas DataFrame with each row representing the task's average runtime, the possible crontab schedule, how many times it is running in the specified interval, and the number free datetimes that couldn't be assigned to this crontab.
  """
  # Create an empty list to store the results
  results = []

  # Iterate over the free time intervals
  for i, row in free_times.iterrows():
    start_datetime = row['start_time']
    end_datetime = row['end_time']
    
    # Calculate the number of minutes between the start and end datetimes
    duration = (end_datetime - start_datetime).total_seconds() / 60.0

    # Calculate the number of times the task can run within the interval
    num_runs = int(duration / max(average_runtime, min_hours_gap*60)) # Between "average_runtime" and "min_minutes_gap" take the greater one. Since I want the gap between each run, I don't care whether the gap is by the runtime or not  
    if num_runs > max_runs_per_day:
      num_runs = max_runs_per_day
    if num_runs > 0:
      frequency = int(duration / num_runs / 60)
      # Generate a crontab schedule that fits within the interval and does not exceed the maximum number of runs per day
      if frequency > 0:
        if start_datetime.hour > end_datetime.hour: # Means that part of the interval is in the next day
          crontab = f"{start_datetime.minute} {start_datetime.hour}-23/{frequency},0-{end_datetime.hour}/{frequency} * * *"
        else:
          crontab = f"{start_datetime.minute} {start_datetime.hour}-{end_datetime.hour}/{frequency} * * *"
      else:
        crontab = f"{start_datetime.minute} {start_datetime.hour} * * *"

      cron = croniter.croniter(crontab, start_datetime)

      # Calculate the number of free datetimes that couldn't be assigned to this crontab
      num_unassigned = 0
      for i in range(max_runs_per_day):
        next_run = cron.get_next(datetime.datetime)
        if next_run > end_datetime:
          num_unassigned += 1

      # Store the results in a pandas DataFrame
      results.append({
        "average_runtime": average_runtime,
        "crontab_schedule": crontab,
        "num_runs": num_runs,
        "num_unassigned": num_unassigned
      })

  return pd.DataFrame(results)


def priority_check(df, cron_data):
  """
  This function checks for overlaps between the crontab schedules in the 
  generated crontab schedules dataframe and the schedules in the main dataframe
  with priority != 5. It creates a new column 'overlap' and populates it with 
  the number of overlaps for each schedule.
  """
  df['overlap'] = None
  priority = cron_data[cron_data['priority']!=5]
  overlap_dict = {}

  for i, row in priority.iterrows():
      function_name = row['job_name']
      priority_schedule = row['schedule']
      priority_runtime = row['avg_runtime']
      priority_cron = croniter.croniter(priority_schedule)
      priority_next_run_time = priority_cron.get_next(datetime.datetime)
      count = 0
      for j, df_row in df.iterrows():
          schedule = df_row['crontab_schedule']
          df_cron = croniter.croniter(schedule)
          df_next_run_time = df_cron.get_next(datetime.datetime)
          if (priority_next_run_time < df_next_run_time) and (df_next_run_time <= priority_next_run_time + priority_runtime):
              count += 1
      if count>0:
          overlap_dict[function_name] = count

      rows = df[df['crontab_schedule']== schedule]
      df.loc[rows.index, 'overlap'] = [overlap_dict for _ in range(len(rows))]

  return df


# Set the maximum number of times the task can run
max_runs_per_day = 4

# Set the minimum number of hours gap between each run
min_hours_gap = 2

# Generate the crontab schedules for average runtimes between 1 and 15 minutes
df = pd.DataFrame()
for average_runtime in range(1, 16):
  df = df.append(generate_crontab_schedule(free_times_df, max_runs_per_day, min_hours_gap, average_runtime)).reset_index(drop=True)

# Check for priority violations
df = priority_check(df, cron_data)

df.to_csv("output.csv")