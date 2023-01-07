# Cron Task Scheduler

This repository contains tools for scheduling tasks and finding the non-overlapping times between them within a specified interval.

## Scripts

### gantt_chart_generator.py

This script generates a Gantt chart showing the schedules of multiple jobs. The input is a pandas DataFrame with columns 'job_name', 'schedule', 'category', and 'duration', where 'schedule' is in crontab format and 'duration' is a pandas Timedelta object representing the duration of each job. The script generates a Gantt chart showing all job schedules from now until a user-specified interval.

#### Dependencies

- `pandas`
- `croniter`
- `plotly`

#### Usage

To use the script, you can follow these steps:

1. Enter the following command:
```
python gantt_chart_generator.py
```

2. The script will prompt you for the interval for the Gantt chart (e.g. "days=7, weeks=2, months=1") and a list of tasks to include in the chart (separated by commas, or enter "all" to include all tasks). The Gantt chart will be generated and displayed using `plotly`.

#### Example

Here is an example of how to use the script:
```python
import pandas as pd
from gantt_chart_generator import create_gantt_chart

# Create a sample DataFrame with job schedules
df = pd.DataFrame({'job_name': ['Job 1', 'Job 2', 'Job 3'], 'schedule': ['0 0 * * *', '0 0 * * 1', '0 0 * * 2'], 'category': ['category1', 'category1', 'category2'],'duration': [pd.Timedelta(minutes=60), pd.Timedelta(minutes=30), pd.Timedelta(minutes=45)]})

# Generate the Gantt chart
interval = {'days': 7}  # Show schedules for the next 7 days
tasks = ['Job 1', 'Job 3']  # Include only Job 1 and Job 3 in the chart
create_gantt_chart(df, interval, tasks)
```

### cron_schedule_lookup.py

This script parses and interprets crontab schedules to generate a list of datetimes for tasks within a specified time interval and date range. It takes a dataframe containing tasks' names and their crontab schedules, as well as user-specified input for the time interval, start date, and end date, and returns a dataframe containing the names of all tasks with the exact datetimes they start to run.

#### Dependencies

- `pandas`
- `croniter`

#### Usage

To use the script, call the `get_task_datetimes` function and pass in the dataframe containing the tasks and their crontab schedules, as well as the time interval, start date, and end date as arguments. The function will return a dataframe containing the task names and their corresponding datetimes within the specified time interval and date range.

### cron_task_scheduler.py

This script allows you to schedule tasks and find the non-overlapping times between them within a specified interval. It takes into account the runtime of each task and checks for overlapping based on the start and end times of each task.

#### Dependencies

- `croniter`

#### Usage

To use the script, you can follow these steps:

1. Add the tasks you want to schedule to the `tasks` dictionary using the `add_task` function, which takes the task name, category, schedule, and runtime as arguments. The schedule should be in crontab format, and the runtime should be a `datetime.timedelta` object.
```python
add_task("task1", "category1", "0 10 * * *", datetime.timedelta(hours=1))
add_task("task2", "category1", "0 9 * * *", datetime.timedelta(hours=1))
add_task("task3", "category2", "0 9 * * *", datetime.timedelta(hours=1))
```

2. Schedule a new task using the `new_task_name` and `new_task_schedule` variables, and define the start and end times for the interval using the `start_time` and `end_time` variables.
```python
new_task_name = "task4"
new_task_schedule = "0 9-11 * * *"
new_task_runtime = datetime.timedelta(hours=1)

start_time = datetime.datetime.now()
end_time = start_time + datetime.timedelta(days=7)
```

3. Find the non-overlapping times for the new task within the interval using the `find_overlapping_times_within_interval` function, which takes the new task's name, schedule, runtime, start and end times of the interval, and the `consider_category` flag as arguments, and returns a dictionary with the non-overlapping times for each task.
```python
non_overlapping_times = find_overlapping_times_within_interval(new_task_name, new_task_schedule, new_task_runtime, start_time, end_time)
```

4. You can access the non-overlapping times for each task by iterating over the dictionary and accessing the values for each key:
```python
for t in non_overlapping_times:
  print(f"Non-overlapping times for {t}:")
  for time in non_overlapping_times[t]:
    print(time)
```

## Dependencies

This repository requires the following libraries:
- `croniter`
- `pandas`
- `plotly` (for python `gantt_chart_generator` script only)

You can install these libraries using `pip`:
```
pip install croniter pandas plotly
```