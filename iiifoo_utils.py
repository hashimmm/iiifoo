"""Utility methods for iiifoo."""
import itertools
from datetime import timedelta
from urllib import unquote, quote
from functools import update_wrapper

import requests
import validators
import requests.exceptions
try:
    from crontab import CronTab
except:
    CronTab = None
from flask import make_response, request, current_app

import settings
import exception
from caching import cached
from external_interfaces.iiif_interface import IIFInterface


# from http://flask.pocoo.org/snippets/56/
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


# See also: http://iiif.io/api/annex/notes/semver.html
def iiif_presentation_api_view(f):
    def wrapped_function(*args, **kwargs):
        resp = make_response(f(*args, **kwargs))
        if not resp.status_code == 200:
            return resp
        if 'application/ld+json' in request.accept_mimetypes.values():
            resp.headers['Content-Type'] = 'application/ld+json'
        else:
            resp.headers['Content-Type'] = 'application/json'
            resp.headers.add("Link", '<http://iiif.io/api/presentation/2/'
                                     'context.json>;rel="http://www.w3.org'
                                     '/ns/json-ld#context";'
                                     'type="application/ld+json"')
        resp.data = '{"@context": "http://iiif.io/api/' \
                    'presentation/2/context.json",\n%s' % resp.data.lstrip('{')
        return resp

    return update_wrapper(wrapped_function, f)


def request_caching_check():
    if request:
        if request.cache_control.no_cache:
            return True
        return False
    return True


@cached(timeout=86400, skip_lookup_if=request_caching_check)
def cached_request(method, url, **kwargs):
    return requests.request(method, url, **kwargs)


def parse_rest_options(path):
    """Get the options specified by the path.

    Options specified like key/value (which means that an
    even number of path subsections is REQUIRED; i.e. k/v/k2/v2 is valid,
    but k/v/bleh is invalid.

    :param path: The part of the URL containing the options.
        Note: Please double-encode slashes! (i.e. %252F instead of %2F)
    """
    sanitized = [unquote(part) for part in path.split('/') if part]
    if len(sanitized) % 2:
        raise exception.InvalidAPIAccess("Incorrect REST options string. "
                                         "Must contain an even number of "
                                         "sections.")
    options = {sanitized[i]: sanitized[i+1]
               for i in xrange(0, len(sanitized), 2)}
    return options


def parse_mapped_rest_options(path, optmap):
    sanitized = [unquote(part) for part in path.split('/') if part]
    if not len(optmap) == len(sanitized):
        raise exception.InvalidAPIAccess(
            "Incorrect REST options string. "
            "Please conform to '{}'".format('/'.join(optmap))
        )
    return {optmap[i]: sanitized[i] for i in xrange(len(optmap))}


def dict_to_rest_options(d):
    """Convert a dict-like object to REST options for parse_rest_options."""
    quoted = [(quote(k.replace('/', '%2F')),
               quote(v.replace('/', '%2F'))) for k, v in d.items()]
    opt_list = itertools.chain(*quoted)
    return "/".join(opt_list)


def list_to_rest_options(l):
    """Convert a list into REST options for parse_mapped_rest_options."""
    quoted = [quote(i.replace('/', '%2F')) for i in l]
    return "/".join(quoted)


def http_request(method, url, silent=False, raise_for_status=False,
                 onerror=None, get_json=False, cache=True, **kwargs):
    """Perform an HTTP request.

    Wrapper for methods provided by the `requests` library to repetition of
    common tasks like exception handling.

    Cache lookups are skipped outside of a request context.

    :param method: The type of request. Must be one of ['get', 'post',
        'options', 'head', 'put', 'delete']
    :type method: str
    :param silent: Silently return None on non-status code errors;
        eg. connection errors. You should probably not want this.
    :type silent: bool
    :param raise_for_status: Raise an exception when the status code is between
        [400, 600). Independent of 'silent'.
    :type raise_for_status: bool
    :param onerror: If provided, called with a single argument - the error
        object - instead when an error occurs. In cases where the error is
        generated by status code, the status code is accessible as
        error_object.response.status_code.
    :type onerror: any callable/function
    :param get_json: parse response as json.
    :param cache: whether to cache the response
    :type cache: bool
    :param args: Positional arguments to pass to requests' request method.
    :param kwargs: Keyword arguments to pass to requests' request method.
    :returns: The response object returned by requests' request method;
        None if there was a non-status error and `silent` is True, or a
        JSON serializable object if get_json was truthy.
    :raises: subclasses of requests.exceptions.RequestException, or
        the value of the `onerror` parameter.
    """
    request_method = cached_request if cache else requests.request
    try:
        r = request_method(method, url, **kwargs)
    except requests.exceptions.RequestException as e:
        if silent:
            return None
        if onerror:
            return onerror(e)
        else:
            raise e
        # return None  # never called unless onerror doesn't raise an error.
    if raise_for_status:
        try:
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            if onerror:
                return onerror(e)
            else:
                raise e
    if get_json:
        try:
            r = r.json()
        except ValueError as e:  # because json and simplejson both raise this.
            if onerror:
                return onerror(e)
            else:
                raise e
    return r


def get_generic_external_url_error_method_generator(name):
    generator_doc = "Obtain a method to raise an ExternalInterfaceError for "\
        """{name}.

        Resulting method takes one argument (an error object).
        """.format(name=name)

    def err_generator(url):
        _error_message = "Call to {} endpoint {} failed with error {}"
        _public_error_message = "Error contacting external service."

        def f(e):
            msg = _error_message.format(name, url, e.message)
            raise exception.ExternalInterfaceError(
                message=msg,
                public_message=_public_error_message
            )
        return f
    err_generator.__doc__ = generator_doc
    return err_generator


def image_id_from_canvas_id(canvas_id):
    """Extract the relevant image's `@id` from the canvas' `@id`."""
    return canvas_id.split('/')[-1].replace('.json', '')


def write_crons(jobsmap):
    """Write crons related to the project (if missing).

    :param jobsmap: A mapping of job names to commands and schedules, like so:
        {"job1_name": ("cd /foobar; ./foo.bar", ("0", "0", "*", "*", "*"))}
    :type jobsmap: dict
    """
    if CronTab is None:
        return
    crontab = CronTab(user=True)
    changes = 0
    for name, (command, schedule) in jobsmap.items():
        found_jobs = tuple(crontab.find_comment(name))
        if not found_jobs:
            changes = 1
            j = crontab.new(command=command)
            j.set_comment(name)
            j.setall(*schedule)
        elif len(found_jobs) > 1:
            print "WARNING: Found duplicate jobs for {} (command: '{}')"\
                .format(name, command)
    if changes:
        crontab.write()


def write_iiifoo_crons(jobsmap):
    for k in jobsmap.keys():
        newk = "iiifoo-{}-{}".format(settings.get("instance_name"), k)
        jobsmap[newk] = jobsmap[k]
        del jobsmap[k]
    write_crons(jobsmap=jobsmap)


def get_context_and_profile_for_iiif_url(iiif_url):
    """Given a IIIF base URL, gets the @context and profile.

    This is done by calling info.json on the IIIF URL provided.
    :param iiif_url: The IIIF base URL.
    """
    info = IIFInterface.get_info(iiif_url)
    profile = []
    for item in info.get("profile", []):
        if validators.url(item):
            profile.append(item)
            break
    return {
        "@context": info.get("@context",
                             "http://iiif.io/api/image/2/context.json"),
        "profile": profile
    }
