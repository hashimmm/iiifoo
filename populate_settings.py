"""Config file (settings.py) creator.

Configuration variable value priorities:
 1. Environment variable
 2. Pre-existing settings file
 3. Default (ENV_VAR_DEFAULTS)

Note: To set values to be treated as boolean "false", set them as empty strings.

This script must be run (`python populate_settings.py`) in order to create the
settings module for IIIFOO. The application will not otherwise run.

To add configuration variables to IIIFOO, just add an entry to the
ENV_VAR_DEFAULTS mapping, with the key being the configuration/setting name and
the value a reasonable default.

Please keep names in lowercase.

To override settings when starting IIIFOO, set an environment variable of
the same name in uppercase.
"""
import os
import sys
import uuid
import traceback
from pprint import pprint
from jinja2 import Environment, FileSystemLoader

try:
    import settings
except ImportError:
    class Settings(object):
        ENV_VAR_DEFAULTS = {}
    settings = Settings

ENV_VAR_DEFAULTS = {
    # database settings
    "db_dialect": "postgresql",
    "db_name": "iiifoo",
    "db_user": "iiifoo",
    "db_pass": "iiifoo",
    "db_host": "localhost",
    "db_port": "5432",
    # server settings
    "secret_key": os.urandom(24).encode('hex'),
    "server_port": "5678",
    "server_processes": "4",
    "instance_name": str(uuid.uuid4()),
    "server_debug": "",
    "profiler": "",
    "gunicorn_proc_name": "iiifoo_gunicorn",
    "gunicorn_loglevel": "info",
    "test_debug_on_fail": "",
    "server_path": "http://localhost:5678",
    "cache_type": "file",
    # directories, paths, locations
    "logs_dir": '',
    "pids_dir": '',
    # redis
    "redis_port": "6379",
    "redis_host": "localhost",
    "redis_cache_key_prefix": "iiifoo-cache",
    "redis_db": "0",
    "redis_pw": "",
    "redis_cache_default_timeout": "86400",
    # file cache
    "file_cache_dir": 'file_cache',
    "file_cache_threshold": '500',
    "file_cache_default_timeout": '86400',
    "file_cache_file_mode": '384',
}


ENV_VAR_DEFAULTS.update(settings.ENV_VAR_DEFAULTS)


def _get(name):
    if name not in ENV_VAR_DEFAULTS:
        raise ValueError("Not a valid configuration variable. Check the name. "
                         "If some arbitrary environment variable is required, "
                         "use os.environ.get(name) instead.")
    else:
        return os.environ.get(
            name.upper(), ENV_VAR_DEFAULTS[name]
        ).strip()


env = Environment(
    loader=FileSystemLoader('.')
)
settings_template = env.get_template('settings_template.jinja2')


if __name__ == '__main__':
    try:
        settings_from_env = {
            v[0]: v[1] for v in [(k, _get(k)) for k in ENV_VAR_DEFAULTS.keys()]
        }
        rendered = settings_template.render(settings_from_env=settings_from_env)
    except StandardError as e:
        exc_info = sys.exc_info()
        print "Failed to create the settings file. Error info:"
        traceback.print_exception(*exc_info)
        sys.exit(1)
    else:
        with open("settings.py", "w") as fp:
            fp.write(rendered)
        print "Settings file created with the following settings:"
        pprint(settings_from_env, width=1)
