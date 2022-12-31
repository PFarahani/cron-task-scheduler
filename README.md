# Cron Task Scheduler

This script allows you to schedule tasks and find the non-overlapping times between them within a specified interval. It takes into account the runtime of each task and checks for overlapping based on the start and end times of each task.

## Usage

To use the script, you can follow these steps:

1. Clone the repository to your local machine:
```
git clone https://github.com/<your_username>/cron-task-scheduler.git
```

2. Navigate to the cron-task-scheduler directory:
```
cd cron-task-scheduler
```

3. Add the tasks you want to schedule to the `tasks` dictionary using the `add_task` function, which takes the task name, category, schedule, and runtime as arguments. The schedule should be in crontab format, and the runtime should be a `datetime.timedelta` object.
```python
add_task("task1", "category1", "0 10 * * *", datetime.timedelta(hours=1))
add_task("task2", "category1", "0 9 * * *", datetime.timedelta(hours=1))
add_task("task3", "category2", "0 9 * * *", datetime.timedelta(hours=1))
```

4. Schedule a new task using the `new_task_name` and `new_task_schedule` variables, and define the start and end times for the interval using the `start_time` and `end_time` variables.
```python
new_task_name = "task4"
new_task_schedule = "0 9-11 * * *"
new_task_category = "category2"
new_task_runtime = datetime.timedelta(hours=1)

start_time = datetime.datetime.now()
end_time = start_time + datetime.timedelta(days=7)
```

5. Find the non-overlapping times for the new task within the interval using the `find_overlapping_times_within_interval` function, which takes the new task's name, schedule, runtime, start and end times of the interval, and the `consider_category` flag as arguments, and returns a dictionary with the non-overlapping times for each task.
```python
non_overlapping_times = find_overlapping_times_within_interval(new_task_name, new_task_schedule, new_task_category, new_task_runtime, start_time, end_time, consider_category)
```

6. You can access the non-overlapping times for each task by iterating over the dictionary and accessing the values for each key:
```python
for t in non_overlapping_times:
  print(f"Non-overlapping times for {t}:")
  for time in non_overlapping_times[t]:
    print(time)
```

## Dependencies
This script uses the `croniter` library to parse the crontab schedules and find the next execution time. You can install it using `pip`:
```
pip install croniter
```