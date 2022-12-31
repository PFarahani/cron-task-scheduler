import pandas as pd
import plotly.express as px
import plotly.offline as offline
import croniter

def create_gantt_chart(df, interval, tasks):
    # Convert the crontab schedules to a list of dictionaries in the form {'Start': start_time, 'Finish': end_time, 'Task': task}
    job_schedules = []
    current_time = pd.Timestamp.now()
    end_time = current_time + pd.DateOffset(**interval)  # Calculate the end time based on the user-specified interval
    for _, row in df.iterrows():
        job_name = row['job_name']
        if tasks != ['all'] and job_name not in tasks:  # Skip tasks that are not in the specified list
            continue
        schedule = row['schedule']
        duration = row['duration'].total_seconds() / 60  # Convert duration to minutes
        category = row['category']
        # Use croniter to parse the crontab schedule and generate a list of start times
        cron = croniter.croniter(schedule, current_time)
        start_times = []
        # Convert the float value returned by croniter.get_next() to a Timestamp object
        next_time = pd.Timestamp.fromtimestamp(cron.get_next())
        while next_time < end_time:
            start_times.append(next_time)
            next_time = pd.Timestamp.fromtimestamp(cron.get_next())
        # Create end times by adding the duration to each start time
        end_times = [t + pd.DateOffset(minutes=duration) for t in start_times]
        # Create a list of dictionaries from the start and end times and task name
        task_schedules = [{'Start': start, 'Finish': end, 'Task': job_name, 'Category': category} for start, end in zip(start_times, end_times)]
        job_schedules.extend(task_schedules)
    
    # Create the gantt chart using plotly.express
    fig = px.timeline(job_schedules, x_start='Start', x_end='Finish', y='Task', title='Job Schedules', 
                      color='Category', color_discrete_sequence=px.colors.sequential.Viridis
                      )
    # Save the chart to an HTML file
    offline.plot(fig, filename='gantt_chart.html')
    
    # Show the chart
    fig.show()



# Example usage
df = pd.DataFrame({'job_name': functions['command'], 'schedule': functions['schedule'], 'duration': functions['avg'], 'category': functions['category']})

# Ask the user for the interval
interval = {}
tasks = []
print("Enter the interval for the gantt chart (e.g. days=7, weeks=2, months=1):")
interval_input = input()
for item in interval_input.split(','):
    key, value = item.split('=')
    interval[key.strip()] = int(value.strip())
print("Enter the names of the tasks to include in the chart, separated by commas (or enter 'all' to include all tasks):")
tasks_input = input()
if tasks_input == 'all':
    tasks = ['all']
else:
    tasks = [task.strip() for task in tasks_input.split(',')]

create_gantt_chart(df, interval, tasks)