import croniter
import datetime

tasks = {}

def add_task(name, category, schedule, runtime):
  # create a croniter object from the schedule
  schedule = croniter.croniter(schedule)

  # add the task to the tasks dictionary
  tasks[name] = {
    "category": category,
    "schedule": schedule,
    "runtime": runtime,
  }

def find_overlapping_times_within_interval(task, schedule, runtime, start_time, end_time):
  # create a croniter object from the schedule
  schedule = croniter.croniter(schedule)

  # a dictionary to store the non-overlapping times for each task
  non_overlapping_times = {}

  # find the non-overlapping times for the task overall
  for t in tasks:
    # skip the task itself
    if t == task:
      continue

    # get the schedule and runtime for the other task
    other_schedule = tasks[t]["schedule"]
    other_runtime = tasks[t]["runtime"]

    # find the non-overlapping times between the two tasks
    non_overlap = []
    time = schedule.get_next(start_time=start_time)
    other_time = other_schedule.get_next(start_time=start_time)
    while time < other_time and time < end_time:
      # add the runtime of the new task to the start time
      time_with_runtime = datetime.datetime.fromtimestamp(time) + runtime
      time_with_runtime = datetime.datetime.timestamp(time_with_runtime)
      # check if the end time of the new task overlaps with the start time of the other task
      if time_with_runtime > other_time:
        break
      non_overlap.append(datetime.datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))
      time = schedule.get_next()
      other_time = other_schedule.get_next()

    # store the non-overlapping times in the dictionary
    if t not in non_overlapping_times:
      non_overlapping_times[t] = []
    non_overlapping_times[t] += non_overlap

  # return the dictionary with the non-overlapping times for each task
  return non_overlapping_times



# add some tasks to the tasks dictionary
add_task("task1", "category1", "0 10 * * *", datetime.timedelta(minutes=30))
add_task("task2", "category1", "0/30 9-10 * * *", datetime.timedelta(minutes=30))
add_task("task3", "category2", "0 9 * * *", datetime.timedelta(hours=1))

# schedule a new task
new_task_name = "task4"
new_task_schedule = "0/30 8-11 * * *"
new_task_runtime = datetime.timedelta(minutes=30)

# define the start and end times for the interval
start_time = datetime.datetime.now()
end_time = start_time + datetime.timedelta(days=1)

start_time = datetime.datetime.timestamp(start_time)
end_time = datetime.datetime.timestamp(end_time)

# find the non-overlapping times for the new task within the interval
non_overlapping_times = find_overlapping_times_within_interval(new_task_name, new_task_schedule, new_task_runtime, start_time, end_time)

# print the non-overlapping times for each task
for t in non_overlapping_times:
  print(f"Non-overlapping times for {t}:")
  for time in non_overlapping_times[t]:
    print(time)