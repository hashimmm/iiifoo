"""Contains any cron jobs required to be added with the project.

The constant JOBSMAP can be modified to add more jobs.
When the server is started, these jobs are generated automatically.

The data structure for JOBSMAP is as follows:
{
 "meaningful_name": ("command", ("minute", "hour", "dayofmonth",
                                 "month", "dayofweek")), ...
 }

Refer to the documentation for python-crontab (or for CRON) to see how to
specify schedules.
"""
import os


workspace = os.path.dirname(os.path.abspath(__file__))

JOBSMAP = {
    "no_op":
        ("cd {workspace}".format(workspace=workspace), (0, 0, 1, "*", "*"))
}
