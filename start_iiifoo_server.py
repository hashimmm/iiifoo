import logging

try:
    import settings  # NOTE: DO NOT CHANGE TO `from settings import get`
except ImportError:
    print "Unable to find `settings.py`. Please run "\
          "`python populate_settings.py` to prep configurations first."
    import sys
    sys.exit(1)

import cron_jobs
import iiifoo_utils
from iiifoo_server import create_app

iiifoo_utils.write_iiifoo_crons(jobsmap=cron_jobs.JOBSMAP)

logger = logging.getLogger('start_mira_server')
fh = logging.FileHandler('iiifoo_server.log')
fh.setLevel(logging.DEBUG)
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)


app = create_app()


if __name__ == '__main__':
    # Assumes debugging is the intent.
    port = int(settings.get("server_port"))
    if settings.get('profiler'):
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app,
            profile_dir='profiling_results_target'
        )
    app.run(host='0.0.0.0', port=port)
