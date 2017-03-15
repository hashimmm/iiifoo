"""Sets up environment for testing (using `behave`).

Mock methods on external interface classes like:
>>> from external_interfaces import my_interface
>>> my_interface_patcher = patch.object(my_interface.MyInterface, 'da_method',
...                                     return_value=mock_data.some_data)
...
>>> patchers.append(my_interface_patcher)

For convenience, mock data is also placed on the context for all tests as
`context.mock_data`.
"""
from datetime import datetime

from mock import patch

import settings
import mock_data
from iiifoo_server import create_app, db
from external_interfaces import *
from external_interfaces import iiif_interface


dateformat = "%Y-%m-%d_%H-%M-%S"
test_db_name = "iiifoo_test_{}.db".format(datetime.now().strftime(dateformat))


class SettingsMocker(object):

    """For mocking settings.

    Usage:
    For the case of `import settings` in the module using settings:
    >>> with SettingsMocker(setting_to_mock="mock_value", ... ):
    ...     # run tests or do something
    ...

    Else if it uses 'from settings import get':
    >>> with SettingsMocker(importing_module="module_name",
    ...                     setting_to_mock="mock_value", ... ):
    ...     # run tests or do something
    ...

    """

    mocked_settings = {}

    def __init__(self, importing_module=None, **kwargs):
        """Create an object that can mock settings with the given values.

        :param importing_module: The name of the module that imports `get`.
            If the module only imports `settings`, leave it as None.
        :type importing_module: str
        :param kwargs: The names of and corresponding new values for properties
            to mock. Property names not provided will not be changed.
        """
        for k in kwargs:
            if k not in settings.ENV_VAR_DEFAULTS:
                raise ValueError("SettingsMocker is not for mocking settings "
                                 "that do not exist.")
        if "property_tester" in kwargs:
            raise ValueError("Changing the value of property_tester is "
                             "not allowed.")
        kwargs['property_tester'] = "MOCKED"
        self.mocked_settings = settings.ENV_VAR_DEFAULTS.copy()
        self.mocked_settings.update(kwargs)
        self._to_replace = 'settings.get' if not importing_module \
            else '{}.get'.format(importing_module)
        self.patcher = None

    def start(self):
        """Begin patching.

        Use this when not using a 'with' statement.
        """
        self.patcher = patch(self._to_replace, self._get_mocked_config)
        self.patcher.start()

    def stop(self):
        """Stop patching.

        Use this when not using a 'with' statement.
        """
        if self.patcher:
            self.patcher.stop()

    def _get_mocked_config(self, name):
        return self.mocked_settings[name]

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()


settings_patcher = SettingsMocker(db_dialect="sqlite", db_host="", db_user="",
                                  db_pass="", db_port="", db_name=test_db_name,
                                  server_debug="True")

iiif_patcher = patch.object(iiif_interface.IIFInterface, 'get_info',
                            return_value=mock_data.iiif_info)

patchers = [settings_patcher, iiif_patcher]


def start_patching():
    for patcher in patchers:
        patcher.start()


def stop_patching():
    for patcher in patchers:
        patcher.stop()


def before_all(context):
    start_patching()

    context.mock_data = mock_data

    context.app = create_app().test_client()
    context.db = db


def after_all(context):
    stop_patching()


BEHAVE_DEBUG_ON_ERROR = settings.get('test_debug_on_fail')


def after_step(context, step):
    if BEHAVE_DEBUG_ON_ERROR and step.status == "failed":
        # -- ENTER DEBUGGER: Zoom in on failure location.
        # NOTE: Use IPython debugger, same for pdb (basic python debugger).
        import pdb
        pdb.post_mortem(step.exc_traceback)
