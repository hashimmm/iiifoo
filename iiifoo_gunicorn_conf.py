import os
import sys
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))  # required.
try:
    import settings  # NOTE: DO NOT CHANGE TO `from settings import get`
except ImportError:
    print "Unable to find `settings.py`. Please run "\
          "`python populate_settings.py` to prep configurations first."
    sys.exit(1)

bind = "0.0.0.0:{}".format(settings.get('server_port'))
workers = int(settings.get('server_processes'))
daemon = True
worker_class = "gevent"
timeout = 120
pidfile = os.path.join(settings.get('pids_dir'), 'mira_gunicorn.pid')
accesslog = os.path.join(settings.get('logs_dir'), 'mira_gunicorn_access.log')
errorlog = os.path.join(settings.get('logs_dir'), 'mira_gunicorn_error.log')
loglevel = settings.get('gunicorn_loglevel')
proc_name = settings.get('gunicorn_proc_name')
