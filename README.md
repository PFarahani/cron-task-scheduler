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

To use the script, call the `get_task_datetimes` function and pass in the dataframe containing the tasks and their crontab schedules, as well as the time interval, time zone, start date, and end date as arguments. The function will return a dataframe containing the task names and their corresponding datetimes within the specified time interval and date range.

You can also specify the `time_zone` argument to set the time zone for the datetimes returned by the function. The default time zone is UTC. If you don't specify a time zone, the datetimes will be in UTC. To specify a different time zone, pass the name of the time zone as a string (e.g. "Asia/Tokyo" for Tokyo time). You can find a list of available time zones [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

### cron_task_scheduler.py

This script is a tool for scheduling tasks using crontab schedules. The new version of the script takes into account the possibility of running the task multiple times in different free times instead of just one to minimize the number of times that the task cannot be assigned in those intervals.

#### New Features in version 2.0.0:

- The script now considers the possibility of running the task multiple times in different free times instead of just one, this feature is intended to minimize the number of times that the task cannot be assigned in those intervals.
- The script now includes a flag `consider_category` which will limit the free times to the category of the task.
- The script now includes `min_gap_time` to specify the minimum time gap between each run.

#### Dependencies

- `croniter`
- `pandas`

#### Usage

```python
from cron_task_scheduler import *

# to generate start date for each task
generate_start_date(df: pandas.DataFrame, start_time: datetime, end_time: datetime)

# to find all the free times between all tasks 
find_free_times(df: pandas.DataFrame, start_time: datetime, end_time: datetime, consider_category = False)

# to generate crontab schedule that fits within the time interval
generate_crontab_schedule(df: pandas.DataFrame, max_runs_per_day: int, min_hours_gap: int, average_runtime: datetime.timedelta)
```

#### Note

- The input dataset should have the following columns: task name, crontab_schedule, average_runtime and category
- The generate_start_date function will add a new column "start_date" to the input dataframe
- The input dataset should be sorted by the "start_date" column, otherwise, the function will sort it by itself
- The input dataset should be in the csv format
- The consider_category flag is set to False by default


#### Version

2.0.0

## Dependencies

This repository requires the following libraries:
- `croniter`
- `pandas`
- `plotly` (for python `gantt_chart_generator` script only)

You can install these libraries using `pip`:
```
pip install croniter pandas plotly
```